import logging
import asyncio
import urllib.parse
import aiohttp
import json
import random
import time
from typing import Optional, Dict, Any, Callable, List
try:
    import websockets
    from websockets.protocol import State
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    websockets = None
    State = None
    WEBSOCKETS_AVAILABLE = False
from .subscription import Subscription
from .interception import Interception
from .constant import Constant
from .utils.event_emitter import EventEmitter
from .sse_client import SSEClient
from .http_poll import LongPollClient
from .utils.server_data_utils import subscribe_to_channel
from .exceptions import AuthenticationError, ChannelError
logger = logging.getLogger(__name__)

class Socket(EventEmitter):
    def __init__(self, ready_event: asyncio.Event, loop: asyncio.AbstractEventLoop, encrypt: Optional[Callable] = None, decrypt: Optional[Callable] = None, auth: Optional[Any] = None) -> None:
        super().__init__()
        self.ready_event = ready_event
        self.loop = loop
        self.encrypt = encrypt
        self.decrypt = decrypt
        self.auth = auth
        self.websocket = None                     
        self.credentials = None                    
        self.subscriptions = {}                     
        self.interceptors = {}                    
        self.secure_callbacks = {}
        self.connection = None
        self.is_connection_active = None
        self.heartbeat_interval = None 
        self.pending_send_messages = []           
        self.sse_client = None
        self.lp_client = None
        self.pull_source = 'socket'  # 'socket', 'sse', or 'http'
        self.push_source = 'socket'  # 'socket' or 'http'
        self.is_connecting = False
        self.is_reconnecting = False
        self.auto_reconnect = False
        self.pending_incoming_messages = {}

    async def initiate_socket(self, credentials: Dict[str, Any]) -> None:
        logger.info("Initiating socket connection with fallback strategy")
        self.credentials = credentials

        if WEBSOCKETS_AVAILABLE:
            try:
                await self.connect_websocket(self.ready_event)
                # Check if connection actually succeeded
                if self.is_connection_active:
                    self.pull_source = "socket"
                    self.push_source = "socket"
                    logger.info("Connected successfully via WebSocket")
                    return
                # Auth failed or connection not active - let reconnection handle it
                logger.info("WebSocket connection returned without active connection, reconnection will retry")
                return
            except Exception as ws_err:
                # Connection error - let reconnection handle it, don't fallback
                logger.warning("WebSocket connection error: %s, reconnection will retry", ws_err)
                return

        # Only reach here if WEBSOCKETS_AVAILABLE is False - fallback to SSE/HTTP
        logger.info("WebSocket not available, falling back to SSE")
        try:
            await self.connect_sse()
            self.pull_source = "sse"
            self.push_source = "http"
            logger.info("Connected successfully via SSE (Server-Sent Events)")
            return
        except Exception as sse_err:
            logger.warning("SSE connection failed, falling back to HTTP long polling: %s", sse_err)
        logger.info("Using HTTP long polling as connection method")
        self.pull_source = "http"
        self.push_source = "http"
        self.listen_configuration()
        await self.start_http_polling()
        
    async def start_http_polling(self) -> None:
        """Start HTTP long polling as final fallback"""
        try:
            if not self.lp_client:
                self.lp_client = LongPollClient({
                    'endpoint': Constant.LPOLL,
                    'get_auth_params': self._get_auth_params,
                    'on_message': self._on_lp_message,   
                    'on_open': self._on_lp_open,     
                    'on_error': self._on_lp_error,       
                    'on_close': self._on_lp_close,     
                    'initial_connection_id': self.connection.get('ConnectionId') if self.connection else None
                })
            
            self.lp_client.start(self.connection.get('ConnectionId') if self.connection else None)
        except Exception as e:
            logger.error("Failed to start HTTP polling: %s", e, exc_info=True)
            raise     
        
    def _on_lp_open(self) -> None:
        """Handle long poll connection established"""
        logger.info("HTTP long poll connection established")
        self.is_connection_active = True
        self.emit("open", None)

    def _on_lp_close(self, reason: Optional[str] = None) -> None:
        """Handle long poll connection closed"""
        logger.warning("HTTP long poll connection closed: %s", reason)
        self.is_connection_active = False
        self.stop_heartbeat()
        self.emit("close", {'type': 'close', 'reason': reason})

    def _on_lp_message(self, messages: List[Dict[str, Any]]) -> None:
        """Handle incoming long poll messages"""
        try:
            logger.debug("Received %d messages via HTTP long poll", len(messages))
            logger.debug("Long poll messages content: %s", messages)
            self.process_incoming_messages(messages)
        except Exception as e:
            logger.error("Error handling long poll messages: %s", e, exc_info=True)

    def _on_lp_error(self, error: Exception) -> None:
        """Handle long poll errors"""
        logger.error("HTTP long poll error: %s", error)
        self.emit("error", error)
        if "401" in str(error) or "Invalid token" in str(error):
            logger.warning("Token expired - forcing re-authentication")
            # Clear auth data to force refresh
            try:
                self.auth.auth_data = {"AccessToken": "", "RefreshToken": ""}
            except (AttributeError, TypeError):
                pass  # Auth not initialized or doesn't have auth_data 
            
    def remove_subscription(self, channel: str) -> None:
        """Remove a subscription from the subscriptions map."""
        if channel in self.subscriptions:
            del self.subscriptions[channel]
            logger.debug("Removed subscription for channel: %s", channel)
            
    def switch_to_http_poll(self) -> None:
        """Switch to HTTP polling when server requests it"""
        if self.pull_source == 'http':
            return  # Already polling

        logger.info('Shifting pullSource → http, pushSource → http')
        self.pull_source = 'http'
        self.push_source = 'http'
        # Start long-poller (it will reuse connection_id you already have)
        if self.lp_client and self.connection:
            self.lp_client.start(self.connection.get('ConnectionId'))       
      
    async def connect_websocket(self, ready_event: asyncio.Event) -> None:
        try:
            self.ready_event = ready_event
            logger.info('Attempting WebSocket connection...')

            if self.is_connecting:
                logger.debug("Already connecting, skipping")
                return
            self.is_connecting = True
            
            if not self.auth:
                logger.error("Auth instance not initialized")
                raise AuthenticationError("Auth instance not initialized")

            try:
                auth_data = await self.auth.authenticate(self.is_reconnecting)
                logger.info("Authenticated")
            except Exception as e:
                logger.error("Failed to authenticate: %s", e)
                self.is_connection_active = False
                self.ready_event.clear()
                self.emit('close', {'type': 'error', 'reason': 'auth_failed'})
                return  # Let reconnection logic handle it, don't trigger fallback
            ws_url = (
                f"{Constant.WS_URL}?"
                f"Org-Title={urllib.parse.quote(self.credentials.get('OrgTitle', ''))}"
                f"&token={urllib.parse.quote(auth_data.get('AccessToken', ''))}"
                f"&environment={urllib.parse.quote(self.credentials.get('Environment', ''))}"
                f"&project-key={urllib.parse.quote(self.credentials.get('ProjectKey', ''))}"
            )
            connection_id = self.connection.get('ConnectionId', '') if self.connection else ''
            ws_url += f"&connection_id={urllib.parse.quote(connection_id)}"
            logger.info("Connecting with connection_id: '%s' (reconnection: %s)", connection_id, self.connection is not None)
            try:
                self.websocket = await asyncio.wait_for(websockets.connect(ws_url, ping_interval=None), timeout=5.0)
                self.is_connection_active = True
                logger.info("WebSocket connected successfully")
            except asyncio.TimeoutError:
                logger.error("WebSocket handshake timeout")
                self.is_connection_active = False
                self.ready_event.clear()
                self.emit('close', {'type': 'error', 'reason': 'timeout'})
                raise
            except Exception as e:
                logger.error("WebSocket connection failed: %s", e)
                self.is_connection_active = False
                self.ready_event.clear()
                self.emit('close', {'type': 'error', 'reason': str(e)})
                raise
            # Start receive loop
            asyncio.create_task(self._websocket_receive_loop())
        except Exception as e:
            logger.error("Failed to connect WebSocket: %s", e)
            self.is_connection_active = False
            self.ready_event.clear()
            raise
        finally:
            self.is_connecting = False  
        
    async def _websocket_receive_loop(self) -> None:
        # Simulate onopen event.
        logger.info("Live connection opened")
        self.emit("open", None)  # Passing None as no event object is defined.
        self.listen_configuration()
        try:
            async for message in self.websocket:
                self.parse_incoming_message(message)
        except websockets.exceptions.ConnectionClosed as e:
            logger.warning("Live connection closed: %s", e)
            self.emit("close", e)
        except Exception as e:
            logger.error("Live error: %s", e)
            self.emit("error", e)
        finally:
            self.is_connecting = False
            self.is_connection_active = False
            self.ready_event.clear()
            self.stop_heartbeat()

    def parse_incoming_message(self, message: str) -> None:
        logger.debug("="*80)
        try:
            parsed = json.loads(message)
            logger.debug("[SOCKET] From: %s, To: %s", parsed.get('from_username'), parsed.get('to_username'))
            logger.debug("[SOCKET] Return flag: %s", parsed.get('return_flag'))
            if isinstance(parsed, list):  # Array check
                logger.debug("Array parsed, length: %d", len(parsed))
                self.process_incoming_messages(parsed)
                return
            else:
                self.handle_incoming_message(parsed)
        except Exception as error:
            logger.error('Failed to parse incoming message: %s', error)

    def process_incoming_messages(self, messages: List[Dict[str, Any]]) -> None:
        for msg in messages:
            self.handle_incoming_message(msg)
            
    def handle_incoming_message(self, parsed_message: Dict[str, Any]) -> None:  
        try:
            channel = parsed_message.get("channel")
            event = parsed_message.get("event")
            name_space = parsed_message.get("namespace")
            if channel == "art_ready" and event == "ready":
                data = parsed_message.get("content")
                if isinstance(data, str):
                    connection_data = json.loads(data)
                else:
                    connection_data = data
                self.connection = {
                    "ConnectionId": connection_data.get("connection_id"),
                    "InstanceId": connection_data.get("instance_id"),
                    "TenantName": self.credentials.get("OrgTitle"),
                    "Environment": self.credentials.get("Environment"),
                    "ProjectKey": self.credentials.get("ProjectKey"),
                }
                logger.info("Connection established via art_ready - ConnectionID: %s", self.connection.get('ConnectionId'))
                self.ready_event.set()
                self.emit("connection", self.connection)
                self.start_heartbeat()
                if self.auto_reconnect:
                    for subscription in self.subscriptions.values():
                        subscription.reconnect()
                    for interceptor in self.interceptors.values():
                        interceptor.reconnect()
                self.listen_configuration()
                return
            elif channel == "art_secure":
                ref_id = parsed_message.get("ref_id")
                key = f"secure-{ref_id}"
                
                if key in self.secure_callbacks:
                    data = parsed_message.get("content")
                    # Parse the data
                    try:
                        parsed_data = json.loads(data) if isinstance(data, str) else data
                    except:
                        parsed_data = data
                    
                    # Create response
                    parsed_response = {
                        "channel": channel,
                        "namespace": name_space,
                        "data": parsed_data,
                        "ref_id": ref_id,
                        "event": event
                    }
                    # Resolve the callback
                    callback = self.secure_callbacks[key]
                    callback(parsed_response)
                    del self.secure_callbacks[key]
                    logger.debug("Resolved secure callback for: %s", key)
                return
            # switch to http poll
            if event == 'shift_to_http':
                self.switch_to_http_poll()
                return
            interceptor_name = parsed_message.get("interceptor_name")
            data = parsed_message.get("content")
            return_flag = parsed_message.get("return_flag")
            if not channel or (not event and return_flag != "SA"):
                logger.warning("Received message without channel or event: %s", parsed_message)
                return
            if interceptor_name:
                interception = self.interceptors.get(interceptor_name)
                if interception:
                    if "content" in parsed_message:
                        del parsed_message["content"]
                    parsed_message["data"] = data
                    asyncio.create_task(interception.handle_message(channel, parsed_message))
                else:
                    logger.debug("No interceptors registered")
            else:
                subscription_key = channel
                if name_space:
                    subscription_key = subscription_key + ':' + name_space
                if channel not in ["art_ready", "art_secure"]:
                    subscription = self.subscriptions.get(subscription_key)
                    if subscription:
                        if "content" in parsed_message:
                            del parsed_message["content"]
                        parsed_message["data"] = data
                        asyncio.create_task(subscription.handle_message(event, parsed_message))
                    else:
                        logger.warning("No subscription found for channel: %s", subscription_key)
                        
        except Exception as e:
            logger.error("Failed to handle incoming message: %s", e, exc_info=True)

    async def subscribe(self, channel: str) -> Subscription:
        """
        Subscribe to a specific channel returns subscription instance.
        """
        return await self.handle_subscription(channel, "subscribe")

    async def handle_subscription(self, channel: str, process: str) -> Subscription:
        """Handle subscription"""
        
        await self.wait()
        # Check if subscription already exists
        if channel in self.subscriptions:
            sub = self.subscriptions[channel]
            if process == "subscribe":  
                await sub.subscribe() 
            return sub
        channel_config = await self.validate_subscription(channel, process)
        if not channel_config:
            raise ChannelError(f"Channel {channel} not found")
        # Create error handler
        def onerror(error: str):
            logger.error("Error in %s for channel '%s': %s", process, channel, error)
            if channel in self.subscriptions:
                del self.subscriptions[channel]
        # Create subscription with validated config
        subscription = Subscription(channel, self, onerror, self.loop, process)
        subscription.channel_config = channel_config
        subscription.subscription_id = channel_config.get('subscriptionID')
        if channel_config.get('presenceUsers'):
            subscription.presence_users = channel_config.get('presenceUsers', [])
        # Store subscription
        self.subscriptions[channel] = subscription
        # Process buffered messages
        if channel in self.pending_incoming_messages:
            buffered = self.pending_incoming_messages[channel]
            for msg in buffered:
                await subscription.handle_message(msg['event'], msg['payload'])
            del self.pending_incoming_messages[channel]
        
        return subscription
    
    async def validate_subscription(self, channelName: str, process: str) -> Optional[Dict[str, Any]]:
        """Validate subscription and return channel config"""
        
        if channelName in ["art_config", "art_secure"]:
            return {
                "channelName": channelName,
                "channelNamespace": "",
                "channelType": "default",
                "snapshot": None,
                "subscriptionID": ""
            }
        try:
            config = await subscribe_to_channel(
                channelName, 
                process, 
                self,
                lambda err: logger.error("Subscription validation error: %s", err)
            )
            # Check for shared-object channel type
            if process == "subscribe" and config.get("channelType") == "shared-object":
                raise ChannelError("Python ADK does not support live object channel features")
            return config
            
        except Exception as error:
            logger.error("Error validating subscription: %s", error, exc_info=True)
            raise

    async def send_message(self, message: str) -> bool:
        """Send message via appropriate transport"""
        if self.push_source == 'socket':
            if self.websocket and hasattr(self.websocket, "state") and self.websocket.state == State.OPEN:
                await self.websocket.send(message)
                return True
            else:
                return False
        elif self.push_source == 'http':   
            await self._send_via_http(message)
            return True
        return False
    
    async def _send_via_http(self, message: str) -> bool:
        """Send message via HTTP API when WebSocket is not available"""
        try:
            # Parse the message to get channel and other details
            msg_data = json.loads(message)
            logger.debug("Sending message via HTTP: %s", msg_data)
            msg_data["connection_id"] = msg_data['from']
            # Build HTTP endpoint
            url = f"{Constant.BASE_URL}/v1/push-message"
            logger.debug("HTTP send URL: %s", url)
            # Get auth headers
            headers = await self._get_auth_headers()
            headers['Content-Type'] = 'application/json'
            # Send request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=headers,
                    json=msg_data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_text = await response.text()
                    if response.status == 200:
                        logger.debug("Message sent successfully via HTTP")
                        return True
                    else:
                        logger.error("HTTP send failed: HTTP %d - %s", response.status, response_text)
                        return False
                        
        except Exception as e:
            logger.error("Error sending via HTTP: %s", e, exc_info=True)
            return False
        
    def listen_configuration(self) -> None:
        self.auto_reconnect = True
        self.is_connection_active = True
        logger.debug("Pushing connection-config to trigger server response")

    def get_connection(self) -> Optional[Dict[str, Any]]:
        return self.connection

    async def wait(self) -> None:
        """Wait until the connection is ready"""
        await self.ready_event.wait()

    async def push_for_secure_line(self, event: str, data: Any, listen: bool = False) -> Optional[Dict[str, Any]]:
        """
        Push a message through the secure channel with optional response listening.
        """
        ref_id = f"{self.connection.get('ConnectionId', '')}_secure_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
        
        message = {
            "from": self.connection.get('ConnectionId', ''),
            "channel": "art_secure",
            "event": event,
            "content": json.dumps(data if data else {}),
            "ref_id": ref_id
        }
        
        if listen:
            # Create a future to wait for response
            future = self.loop.create_future()
            # Store callback that will resolve the future
            def resolve_callback(result):
                if not future.done():
                    future.set_result(result)

            self.secure_callbacks[f"secure-{ref_id}"] = resolve_callback

            await self.send_message(json.dumps(message))

            # Wait for response with timeout (auto-cancels when done)
            try:
                return await asyncio.wait_for(future, timeout=20)
            except asyncio.TimeoutError:
                # Clean up callback on timeout
                if f"secure-{ref_id}" in self.secure_callbacks:
                    del self.secure_callbacks[f"secure-{ref_id}"]
                raise TimeoutError(f"Secure line response timeout for {event}")
        else:
            # Just send without waiting
            await self.send_message(json.dumps(message))
            return None
            
    async def close_websocket(self, clear_connection: bool = False) -> None:
        """
        Close all connections and clean up resources.
        """
        # Close WebSocket
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.error("Error closing websocket: %s", e, exc_info=True)
            finally:
                self.websocket = None
        # Close SSE client
        if self.sse_client:
            try:
                await self.sse_client.close()
            except Exception as e:
                logger.error("Error closing SSE client: %s", e, exc_info=True)
            finally:
                self.sse_client = None
        # Stop HTTP polling
        if self.lp_client:
            try:
                self.lp_client.stop()
            except Exception as e:
                logger.error("Error stopping long poll client: %s", e, exc_info=True)
            finally:
                self.lp_client = None
        self.is_connection_active = False
        self.connection = None
        self.is_connecting = False
        self.ready_event.clear()

        if clear_connection:
            self.pending_incoming_messages.clear()
            self.pending_send_messages = []
            self.subscriptions.clear()
            self.interceptors.clear()

        self.stop_heartbeat()
  
    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for HTTP requests"""
        await self.auth.authenticate()
        auth_data = self.auth.get_auth_data()
        credentials = self.auth.get_credentials()
        
        return {
            'Authorization': f'Bearer {auth_data.get("AccessToken")}',
            'X-Org': credentials.get("OrgTitle"),
            'Environment': credentials.get("Environment"),
            'ProjectKey': credentials.get("ProjectKey"),
        }
    async def _get_auth_params(self) -> Dict[str, str]:
            """Get authentication params for HTTP requests"""
            await self.auth.authenticate()
            auth_data = self.auth.get_auth_data()
            credentials = self.auth.get_credentials()
            
            return {
                'token': f'{auth_data.get("AccessToken")}',
                'Org-Title': credentials.get("OrgTitle"),
                'environment': credentials.get("Environment"),
                'project-key': credentials.get("ProjectKey"),
            }
    def _on_sse_open(self) -> None:
        """Handle SSE connection open"""
        logger.info("SSE connection opened")
        self.emit("open", None)
        self.is_connection_active = True
        self.listen_configuration()
        self.start_heartbeat()
    def _on_sse_close(self, message: str) -> None:
        """Handle SSE close event"""
        logger.info("SSE server requested close: %s", message)
        self.is_connection_active = False
        self.stop_heartbeat()
        if self.sse_client:
            asyncio.create_task(self.sse_client.close())
        self.emit("close", {'type': 'close', 'reason': message})

    def _on_sse_message(self, event: Dict[str, Any]) -> None:
        """Handle SSE message event"""
        try:
            data = event.get('data')
            #treat data as string and parse it
            if isinstance(data, str):
                logger.debug("Raw SSE data (string): %s", data)
                self.parse_incoming_message(data)
            elif isinstance(data, dict):
                logger.debug("Raw SSE data (dict): %s", data)
                # Convert back to string and parse
                data_str = json.dumps(data)
                self.parse_incoming_message(data_str)
            else:
                logger.warning("Unknown SSE data type: %s", type(data))
        except Exception as e:
            logger.error("Error handling SSE message: %s", e, exc_info=True)

    def _on_sse_error(self, error: Exception) -> None:
        """Handle SSE error event"""
        logger.error("SSE error: %s", error)
        self.emit("error", error)

    # Connect via Server-Sent Events
    async def connect_sse(self) -> None:
        """Connect via Server-Sent Events"""
        try:
            auth_data = await self.auth.authenticate()
        except Exception as e:
            logger.error("Authentication failed: %s", e, exc_info=True)
            self.emit('close', {'type': 'error'})
            raise
        
        params = {
            "Org-Title": self.credentials.get('OrgTitle'),
            "token": auth_data.get('AccessToken'),
            "environment": self.credentials.get('Environment'),
            "project-key": self.credentials.get('ProjectKey'),
        }
        
        if self.connection:
            params["connection_id"] = self.connection.get('ConnectionId', '')
        # Create SSE client
        self.sse_client = SSEClient({
            'url': Constant.SSE_URL,
            'params': params,
            'headers': {},
            'on_message': self._on_sse_message,
            'on_open': self._on_sse_open,
            'on_error': self._on_sse_error,
            'on_close': self._on_sse_close,
        })
        

        
        await self.sse_client.connect()
    def intercept(self, interceptor: str, fn: Callable) -> Interception:
        """Register an interceptor"""
        if interceptor in self.interceptors:
            return self.interceptors[interceptor]
        
        def onerror(error: str):
            logger.error("Authentication failed: %s", exc_info=True)
            if interceptor in self.interceptors:
                del self.interceptors[interceptor]
        interception = Interception(interceptor, fn, self, onerror, self.loop)
        self.interceptors[interceptor] = interception
        return interception
    
    def set_autoconnect(self, auto_connect: bool) -> None:
        self.auto_connect = auto_connect
        
    def _run_heartbeat_payload(self) -> Dict[str, Any]:
        """
        Build heartbeat payload containing connection ID, timestamp, and subscription list.

        Returns:
            Dictionary with connectionId, timestamp, and subscriptions array
        """
        subs = []
        for key, sub in self.subscriptions.items():
            presence = getattr(sub, "is_listening", False)
            subs.append({
                "name": key,                   # channel or channel:namespace
                "presenceTracking": presence
            })
        return {
            "connectionId": self.connection.get("ConnectionId") if self.connection else None,
            "timestamp": int(time.time() * 1000),
            "subscriptions": subs
        }

    async def _heartbeat_loop(self, interval_sec: int = 30) -> None:
        """
        Periodically send heartbeat messages while connection is active.

        Args:
            interval_sec: Interval between heartbeats in seconds (default: 30)
        """
        try:
            while self.is_connection_active:
                payload = self._run_heartbeat_payload()
                try:
                    # fire n forget
                    await self.push_for_secure_line("heartbeat", payload, listen=False)
                except Exception as e:
                    logger.debug("Heartbeat push failed (will retry): %s", e)
                await asyncio.sleep(interval_sec)
        except asyncio.CancelledError:
            return

    def start_heartbeat(self, interval_sec: int = 30) -> None:
        """
        Start periodic heartbeat (idempotent).

        Args:
            interval_sec: Interval between heartbeats in seconds (default: 30)
        """
        if self.heartbeat_interval and not self.heartbeat_interval.done():
            return
        if not self.is_connection_active:
            return
        self.heartbeat_interval = asyncio.create_task(self._heartbeat_loop(interval_sec))

    def stop_heartbeat(self) -> None:
        """
        Stop the periodic heartbeat (idempotent).
        """
        if self.heartbeat_interval and not self.heartbeat_interval.done():
            self.heartbeat_interval.cancel()
        self.heartbeat_interval = None
