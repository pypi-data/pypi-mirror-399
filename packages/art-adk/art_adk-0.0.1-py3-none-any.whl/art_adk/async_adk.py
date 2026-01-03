import os
import json
import asyncio
import aiohttp
import logging
import time
from typing import Optional, Dict, Any, Callable
from urllib.parse import urlencode
from .constant import Constant
from .socket import Socket
from .subscription import Subscription
from .interception import Interception
from .auth import Auth
from .cryptobox import CryptoBox
from .exceptions import ValidationError, EncryptionError, DecryptionError, NotConnectedError, APIError
logger = logging.getLogger(__name__)

class AsyncAdk():
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        logger.info("Initializing AsyncAdk")
        self.config = config
        if not config or not config.get('ROOT'):
            logger.error("Initialization failed: ROOT directory not provided")
            raise ValidationError("Need to pass __directory root")
        Constant.ROOT = config["ROOT"]
        raw_url = config.get('Uri', '') if config else ''
        Constant.BASE_URL = f"https://{raw_url}"
        Constant.WS_URL = f"wss://{raw_url}/v1/connect"
        Constant.SSE_URL = f"https://{raw_url}/v1/connect/sse"
        Constant.LPOLL = f"https://{raw_url}/v1/connect/longpoll"
        logger.debug("Configured endpoints - BASE: %s, WS: %s, SSE: %s, LPOLL: %s",
                    Constant.BASE_URL, Constant.WS_URL, Constant.SSE_URL, Constant.LPOLL)

        self.socket = None
        self.connection = None
        self.credentials = None
        self.auth = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 3
        self._ready_event = asyncio.Event()
        self.key_pair = None
        self.is_paused = False
        self.is_connectable = False
        self.max_delay = 30
        self._reconnection_scheduled = False  # Prevents duplicate reconnection scheduling
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = None
        logger.info("AsyncAdk initialized successfully")

    async def __aenter__(self) -> "AsyncAdk":
        """Enter async context manager - connects to ADK."""
        await self.connect()
        return self

    async def __aexit__(self, _exc_type: Any, _exc_val: Any, _exc_tb: Any) -> bool:
        """Exit async context manager - disconnects from ADK."""
        await self.disconnect()
        return False

    async def connect(self, config: Optional[Dict[str, Any]] = None) -> None:
        if config:
            self.config = config
        if not self.config:
            raise ValidationError("No configuration provided. Pass config to constructor or connect()")
        if not self.loop:
            self.loop = asyncio.get_event_loop()
        self.is_connectable = True
        await self._initiate_socket_connection()

    async def _initiate_socket_connection(self) -> None:
        logger.info("Initiating socket connection")
        self.credentials = await self.load_config()
        self.credentials['config'] = self.config

        if self.auth is None:
            self.auth = Auth(self.credentials)
            logger.debug("Auth instance created")

        if self.socket is None:
            self.socket = Socket(self._ready_event, self.loop, self.encrypt, self.decrypt, self.auth)
            logger.debug("Socket instance created")
            self.socket.on("connection", self._on_connection_event)
            self.socket.on("close", self._on_close_event)
        else:
            logger.debug("Reusing existing socket for reconnection")

        await self.socket.initiate_socket(self.credentials)
        logger.info("Socket connection initiated successfully")

    async def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from credentials file.
        """
        try:
            file_path = os.path.join(Constant.ROOT, Constant.CONFIG_FILE_NAME)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug("Configuration file parsed successfully")
                logger.info("Configuration loaded for environment: %s, project: %s", 
                           data.get("Environment"), data.get("ProjectKey"))
            return {
                "ClientID": data["Client-ID"],
                "ClientSecret": data["Client-Secret"],
                "Environment": data["Environment"],
                "ProjectKey": data["ProjectKey"],
                "OrgTitle": data["Org-Title"]
            }
        except Exception as e:
            logger.error("Configuration loading failed: %s", e, exc_info=True)
            raise ValidationError(f"Python configuration loading failed: {str(e)}")

    def _on_connection_event(self, connection_detail: Dict[str, Any]) -> None:
        """
        Called when WebSocket connects.
        """
        self.connection = connection_detail
        self.reconnect_attempts = 0
        self.reconnect_delay = 3
        self._reconnection_scheduled = False
        self._ready_event.set()
        logger.info("Connection established - ConnectionID: %s, Transport: %s", connection_detail.get('ConnectionId'), connection_detail.get('transport'))

    def _on_close_event(self, event: Optional[Any] = None) -> None:
        """
        Called on WebSocket close. Attempt reconnection.
        """
        self._ready_event.clear()

        if not self.is_paused and self.is_connectable and not self._reconnection_scheduled:
            self._reconnection_scheduled = True
            self.socket.is_reconnecting = True
            asyncio.create_task(self._handle_reconnection())

    def on(self, event: str, callback: Callable) -> "AsyncAdk":
        """
        Generic event registration. For 'open', 'error', 'close', or 'connection' events,
        this method delegates to the underlying Socket.
        """
        self.socket.on(event, callback)
        return self
    
    def off(self, event: str, callback: Callable) -> "AsyncAdk":
        """
        Remove event listener from socket
        """
        if self.socket:
            self.socket.off(event, callback)
        return self

    async def fetch_presence(self, channel: str, callback: Callable) -> Any:
        """
        Fetch presence data for a channel with updates.
        """
        await self._ready_event.wait()
        sub = await self.subscribe(channel)
        return await sub.fetch_presence(callback)

    async def subscribe(self, channel: str) -> Subscription:
        """Subscribe to a channel"""
        return await self.socket.subscribe(channel)
    
    async def unsubscribe(self, channel: str) -> bool:
        await self._ready_event.wait()
        
        if channel not in self.socket.subscriptions:
            logger.warning("Cannot unsubscribe: not subscribed to channel '%s'", channel)
            return False
            
        subscription = self.socket.subscriptions[channel]
        return await subscription.unsubscribe()

    def intercept(self, interceptor: str, fn: Callable) -> Interception:
        while self.socket is None:
            time.sleep(0.1)
        return self.socket.intercept(interceptor=interceptor, fn=fn)

    async def _handle_reconnection(self) -> None:
        """
        Handle reconnection with linear backoff strategy.

        Schedules connection attempts with increasing delays. The close event handler
        will trigger the next attempt if this one fails.
        """
        if self.is_paused or not self.is_connectable:
            logger.info("Connection is paused or not connectable, skipping reconnection")
            self._reconnection_scheduled = False
            return

        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            logger.warning("Reconnection attempt %d/%d scheduled in %ds",
                          self.reconnect_attempts, self.max_reconnect_attempts,
                          self.reconnect_delay)

            await asyncio.sleep(self.reconnect_delay)
            self.reconnect_delay = min(self.reconnect_delay + 2, self.max_delay)

            # Reset flag before connect so next failure can schedule reconnection
            self._reconnection_scheduled = False
            # Schedule connection attempt asynchronously
            asyncio.create_task(self.connect())
        else:
            # Phase 2: Infinite retry with fixed 30s delay
            logger.warning("Max reconnection attempts (%d) reached. Will retry every 30s",
                          self.max_reconnect_attempts)

            await asyncio.sleep(self.max_delay)

            # Reset flag before connect so next failure can schedule reconnection
            self._reconnection_scheduled = False
            # Schedule connection attempt asynchronously
            asyncio.create_task(self.connect())

    async def update_profile(self, data: Dict[str, Any]) -> None:
        """
        Update user profile on server.

        Args:
            data: Profile data dict with keys: FirstName, LastName, Username, Attributes

        Raises:
            RuntimeError: If not connected
            Exception: If profile update fails
        """
        await self._ready_event.wait()
        if not self.connection:
            raise NotConnectedError("Cannot update profile: no connection.")

        await self.auth.update_profile(self.connection.get('ConnectionId'), data)

    async def generate_key_pair(self) -> Dict[str, str]:
        logger.info("Generating encryption key pair")
        self.key_pair =  CryptoBox.generate_key_pair()
        logger.debug("Key pair generated successfully (public key length: %d)", 
                    len(self.key_pair.get("publicKey", "")))
        await self._save_public_key()
        return self.key_pair
    
    async def encrypt(self, data: str, recipient_public_key: str) -> str:
        """
        Encrypt data using the recipient's public key and our private key.
        """
        if not self.key_pair:
            await self._ensure_key_pair()

        try:
            return await CryptoBox.encrypt(data, recipient_public_key, self.key_pair["privateKey"])
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {str(e)}")

    async def decrypt(self, encrypted_data: str, sender_public_key: str) -> str:
        """
        Decrypt data using the sender's public key and our private key.
        """
        if not self.key_pair:
            await self._ensure_key_pair()

        try:
            return await CryptoBox.decrypt(encrypted_data, sender_public_key, self.key_pair["privateKey"])
        except Exception as e:
            raise DecryptionError(f"Decryption failed: {str(e)}")

    async def set_key_pair(self, key_pair: Dict[str, str]) -> None:
        """
        Set an existing key pair (public API method).
        Use this when you already have a key pair to use.
        """
        # Validate
        if not key_pair or \
        not isinstance(key_pair.get('publicKey'), str) or \
        not isinstance(key_pair.get('privateKey'), str) or \
        not key_pair.get('publicKey') or \
        not key_pair.get('privateKey'):
            raise ValidationError("Invalid KeyPair: publicKey and privateKey must be non-empty strings")
        # Set and save
        self.key_pair = key_pair
        await self._save_public_key()

    async def _ensure_key_pair(self) -> None:
        """
        Internal helper to ensure we have a key pair.
        Generates one if needed.
        """
        if not self.key_pair:
            self.key_pair = CryptoBox.generate_key_pair()
            await self._save_public_key()

    async def _save_public_key(self) -> None:
        """
        Save our public key to the server so others can encrypt messages for us.
        """
        try:
            auth_data = await self.auth.authenticate()
            url = f"{Constant.BASE_URL}/v1/update-publickey"
            logger.debug("Saving public key to: %s", url)
            headers = {
                'Content-Type': 'application/json',
                "Authorization": f"Bearer {auth_data.get('AccessToken')}",
                "X-Org": self.credentials.get("OrgTitle"),
                "Environment": self.credentials.get("Environment"),
                "ProjectKey": self.credentials.get("ProjectKey"),
            }
            payload = {
                "public_key": self.key_pair["publicKey"]
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if not response.ok:
                        try:
                            response_text = await response.text()
                        except Exception:
                            response_text = f"(Unable to read response body)"
                        error_msg = f"HTTP {response.status}: {response_text}"
                        logger.error("Failed to save public key - %s", error_msg)
                        raise APIError(f"Failed to save public key: {error_msg}")
                    logger.info("Public key saved to server successfully")

        except asyncio.TimeoutError:
            logger.error("Timeout while saving public key to server")
            raise APIError("Timeout while saving public key to server")
        except aiohttp.ClientError as e:
            logger.error("Network error while saving public key: %s", e)
            raise APIError(f"Network error while saving public key: {e}")
        except Exception as e:
            logger.error("Failed to save public key: %s", e, exc_info=True)
            raise
        
    async def call(self, endpoint: str, options: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """
        Make authenticated API calls.
        """
        options = options or {}
        try:
            await self.auth.authenticate()
            auth_data = self.auth.get_auth_data()

            url = f"{Constant.BASE_URL}{endpoint}"
            if options.get('queryParams'):
                url += f"?{urlencode(options['queryParams'])}"

            headers = {
                'Authorization': f"Bearer {auth_data.get('AccessToken')}",
                'Accept': 'application/json',
                'X-Org': self.credentials.get('OrgTitle'),
                'Environment': self.credentials.get('Environment'),
                'ProjectKey': self.credentials.get('ProjectKey'),
            }
            if options.get('headers'):
                headers.update(options['headers'])

            method = (options.get('method') or 'GET').upper()
            json_data = None
            if options.get('payload') is not None:
                headers['Content-Type'] = 'application/json'
                json_data = options['payload']
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    # Handle errors
                    if not response.ok:
                        error_msg = await response.text()
                        try:
                            error_body = await response.json()
                            error_msg = error_body.get('message', error_msg)
                        except:
                            pass
                        raise APIError(f"API {endpoint} failed: {error_msg}")
                    # Handle 204 No Content
                    if response.status == 204:
                        return None
                    # Parse and return response
                    return await response.json()
            logger.debug("Success API call to endpoint: %s", endpoint)
                        
        except Exception as e:
            logger.error("API call error: %s %s - %s", method, endpoint, e, exc_info=True)
            raise
        
    def pause(self) -> None:
        """
        Pause the connection. This stops reconnection attempts and closes the socket.
        """
        if self.is_paused:
            return
        logger.info("Pausing connection")
        self.is_paused = True
        self.reconnect_attempts = self.max_reconnect_attempts

        if self.socket:
            try:
                # Try to get the running loop (works in async context)
                loop = asyncio.get_running_loop()
                # If we're already in an async context, create task directly
                asyncio.create_task(self._close_socket())
            except RuntimeError:
                # No running loop - we're being called from sync context
                if self.loop and self.loop.is_running():
                    asyncio.run_coroutine_threadsafe(self._close_socket(), self.loop)
                else:
                    logger.warning("No event loop available to close socket during pause")

    async def _close_socket(self) -> None:
        """Helper to close socket asynchronously"""
        if self.socket:
            await self.socket.close_websocket()

    async def resume(self) -> None:
        """
        Resume a paused connection. Resets reconnection parameters and attempts to connect.

        Returns:
            None
        """
        if not self.is_paused:
            return

        logger.info("Resuming connection")
        self.is_paused = False
        self.reconnect_attempts = 0
        self.reconnect_delay = 3
        self._ready_event.clear()
        # Attempt to reconnect
        try:
            await self.socket.connect_websocket(self._ready_event)
        except Exception as e:
            logger.error("Failed to resume connection: %s", e, exc_info=True)
            await self._handle_reconnection()

    async def disconnect(self) -> None:
        """
        Completely disconnect from the server. This stops all reconnection attempts
        and clears the connection state. Unlike pause(), this is intended to be final.
        """
        logger.info("Disconnecting from server")
        # Stop reconnection logic
        self.is_connectable = False
        self.reconnect_attempts = self.max_reconnect_attempts
        # Close the underlying WebSocket
        if self.socket:
            await self.socket.close_websocket(clear_connection=True)
            # Clear socket state
            self.socket.is_connection_active = False
            self.socket.pending_send_messages = []
        # Clear the ready event
        self._ready_event.clear()
        # Remove event listeners to avoid memory leaks
        if self.socket:
            self.socket.remove_all_listeners()
        logger.debug("Connection state cleared, all event listeners removed")

    def get_state(self) -> str:
        """
        Get the current connection state.
        
        Returns:
            str: One of 'paused', 'connected', 'retrying', or 'stopped'
        """
        if self.is_paused:
            return 'paused'
        
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            return 'stopped'
        
        if self.reconnect_attempts > 0:
            return 'retrying'
        
        if self.socket and self.socket.is_connection_active:
            return 'connected'
        
        return 'stopped'
    
    async def get_security_code(self, user_payload: Dict[str, str]) -> str:
        """
        Get security passcode through WebSocket secure line.

        Args:
            user_payload: Dict with keys 'Username', 'FirstName', 'LastName'

        Returns:
            The passcode string
        """
        await self.socket.wait()

        if not self.socket.get_connection():
            raise NotConnectedError('Establish connection first')

        payload = {
            "username": user_payload.get("Username"),
            "first_name": user_payload.get("FirstName"),
            "last_name": user_payload.get("LastName")
        }
        response = await self.socket.push_for_secure_line("pass_code", payload, listen=True)
        if response and 'data' in response:
            return response['data'].get('passcode')

        raise APIError("Failed to get passcode")