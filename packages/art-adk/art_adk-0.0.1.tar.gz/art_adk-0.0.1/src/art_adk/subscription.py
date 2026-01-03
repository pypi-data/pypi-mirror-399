import logging
import json
import asyncio
from typing import Optional, Dict, Any, Callable
from .utils.event_emitter import EventEmitter
from .utils.server_data_utils import subscribe_to_channel
from .utils.server_data_utils import unsubscribe_from_channel
from .exceptions import ChannelError
logger = logging.getLogger(__name__)

class Subscription(EventEmitter):
    def __init__(self, channel: str, websocket_handler: Any, error_callback: Callable, loop: asyncio.AbstractEventLoop, process: str = "subscribe") -> None:
        super().__init__()
        self.websocket_handler = websocket_handler
        self.error_callback = error_callback
        self.subscription_id = None
        self.loop = loop
        self.is_subscribed = False
        self.is_listening = False
        self.message_buffer = {}
        self.pending_acks = {}
        self.message_count = 0
        self.ACK_TIMEOUT = 50
        self.presence_users = []
        self.channel_config = {
            "channelName": channel,
            "channelType": ""
        }
        # Set flags based on process type
        if process == "subscribe":
            self.is_subscribed = True
        elif process == "presence":
            self.is_listening = True
        if channel in ("art_config", "art_secure"):
            self.is_subscribed = True

    async def validate_subscription(self, channel: str, process: str = "subscribe") -> Optional[Dict[str, Any]]:
        if channel in ("art_config", "art_secure"):
            return None
        try:
            self.channel_config = await subscribe_to_channel(
                channel,
                process,
                self.websocket_handler,
                self.error_callback
            )
            if self.channel_config:
                self.subscription_id = self.channel_config.get('subscriptionID')
            if process == "presence":
                self.is_listening = True
            return self.channel_config
        except Exception as error:
            logger.error("Subscription validation failed for channel '%s': %s", channel, error, exc_info=True)
            raise

    def listen(self, callback: Callable) -> None:
        """Listen to all events on the channel."""
        # Process any buffered messages first
        for event, messages in list(self.message_buffer.items()):
            for req_data in messages:
                content = req_data.get('content')
                callback({"event": event, "content": content})
                self.acknowledge(req_data, "CA")
        self.message_buffer.clear()
        self.on("all", callback)

    def bind(self, event: str, callback: Callable) -> None:
        """Bind a callback to a specific event on the channel."""
        # Process any buffered messages for this event
        if event in self.message_buffer:
            for req_data in self.message_buffer[event]:
                content = req_data.get('content')
                callback(content)
                self.acknowledge(req_data, "CA")
            del self.message_buffer[event]
        self.on(event, callback)

    def remove(self, event: str, callback: Optional[Callable] = None) -> None:
        """Remove event listeners."""
        if callback:
            self.off(event, callback)
        else:
            self.remove_all_listeners(event)
        if event in self.message_buffer:
            del self.message_buffer[event]

    async def check(self, callback: Callable) -> None:
        """Check for presence on the channel."""
        if not self.is_listening:
            await self.presence()
        previous_presence_data = None
        def on_art_presence(data):
            nonlocal previous_presence_data
            usernames = data.get('usernames')
            error = data.get('error')
            if not error:
                previous_presence_data = usernames
                callback(usernames)
        self.on('art_presence', on_art_presence)
        if previous_presence_data is not None:
            callback(previous_presence_data)

    async def fetch_presence(self, callback: Callable) -> Dict[str, Any]:
        """
        Enable presence for this subscription.
        Called on an existing subscription instance.
        """
        previous_presence_data = self.presence_users if self.presence_users else []
        if len(previous_presence_data) > 0:
            callback(previous_presence_data)

        await self.validate_subscription(self.channel_config['channelName'], "presence")

        if not self.is_listening:
            raise ChannelError("Not subscribed for presence")

        def on_art_presence(data):
            usernames = data.get('usernames')
            error = data.get('error')

            if not error:
                self.presence_users = usernames
                callback(usernames)
            else:
                logger.error("Presence error: %s", error)
        
        # Register the presence listener
        self.on('art_presence', on_art_presence)
        
        try:
            result = await self.push('art_presence', {})
            logger.debug("Presence push completed for channel: %s", self.channel_config['channelName'])
        except Exception as e:
            logger.error("Presence push failed for channel %s: %s", self.channel_config['channelName'], e, exc_info=True)
            self.off('art_presence', on_art_presence)
            raise
        
        async def unsubscribe_presence():
            self.off('art_presence', on_art_presence)
            
            if self.subscription_id:
                success = await unsubscribe_from_channel(
                    self.channel_config['channelName'],
                    self.subscription_id,
                    "presence",
                    self.websocket_handler,
                    lambda err: logger.error("Presence unsubscribe error: %s", err)
                )
                if success:
                    self.is_listening = False
                return success
            return False
        
        return {"unsubscribe": unsubscribe_presence}
    
    async def push(self, event: str, data: Any, options: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Push a message to the channel with full functionality"""
        logger.debug("Pushing event '%s' to channel '%s' (type: %s)", event, self.channel_config.get('channelName'), self.channel_config.get('channelType'))
        if self.channel_config.get('channelName') not in ["art_config", "art_secure", "art_presence"]:
            await self.websocket_handler.wait()
            logger.debug("Push awaited, connection ready")
        connection = self.websocket_handler.get_connection()
        logger.debug("Push using connection: %s", connection.get('ConnectionId'))
        if not connection:
            if self.channel_config.get('channelName') in ["art_config", "art_secure", "art_presence"]:
                connection = {"ConnectionId": ""}
            else:
                raise ChannelError("No connection available")
        # Extract options
        to = options.get('to', []) if options else []
        message_str = json.dumps(data)
        # Validate for secure/targeted channels
        if self.channel_config.get('channelType') in ["secure", "targeted"]:
            if (not to or len(to) != 1) and event != 'art_presence':
                raise ChannelError("Exactly one user must be specified for sending message.")
        if self.channel_config.get('channelType') == "secure" and event != 'art_presence':
            response = await self.websocket_handler.push_for_secure_line(
                "secured_public_key",
                {"username": to[0]},
                listen=True
            )
            if response and 'data' in response:
                result = response['data']
                if result.get("status") == "unsuccessful":
                    raise ChannelError(result.get("error"))
                public_key = result.get("public_key")
                if not public_key:
                    raise ChannelError(f"No public key received for user {to[0]}")
                message_str = await self.websocket_handler.encrypt(message_str, public_key)
            else:
                raise ChannelError("Failed to get public key for encryption")
        # Handle ACK for non-system channels
        ref_id = None
        ack_future = None
        if self.channel_config['channelName'] not in ("art_config", "art_secure", "art_presence"):
            self.message_count += 1
            ref_id = f"{connection['ConnectionId']}_{self.channel_config['channelName']}_{self.message_count}"
            if (self.channel_config.get('channelType') in ('targeted', 'secure') and event != 'art_presence'):
                ack_future = self.loop.create_future()
                # Store future for ACK handling (no timer needed with wait_for)
                self.pending_acks[ref_id] = ack_future
            else:
                # For broadcast channels, resolve immediately
                ack_future = self.loop.create_future()
                ack_future.set_result(ref_id)

        # Build the message
        channel_with_ns = self.channel_config['channelName']
        if self.channel_config.get('channelNamespace'):
            channel_with_ns += f":{self.channel_config['channelNamespace']}"
        message = {
            "from": connection['ConnectionId'],
            "to": to,
            "channel": channel_with_ns,
            "event": event,
            "content": message_str,
        }
        # Only add ref_id if it exists (not None)
        if ref_id:
            message["ref_id"] = ref_id

        await self.websocket_handler.send_message(json.dumps(message))

        if ack_future:
            # Wait for ACK with timeout (auto-cancels when done)
            try:
                return await asyncio.wait_for(ack_future, timeout=self.ACK_TIMEOUT)
            except asyncio.TimeoutError:
                # Clean up on timeout
                if ref_id and ref_id in self.pending_acks:
                    del self.pending_acks[ref_id]
                raise ChannelError(f'ACK timeout for ref_id: {ref_id}')
        return None

    async def handle_message_acks(self, event: str, return_flag: str, data: Dict[str, Any]) -> None:
        """
        Handle server acknowledgments.
        """
        if return_flag == 'SA' and data.get('ref_id'):
            ref_id = data['ref_id']
            if ref_id in self.pending_acks:
                ack_future = self.pending_acks[ref_id]
                if not ack_future.done():
                    ack_future.set_result(ref_id)
                del self.pending_acks[ref_id]
                return
        return

    def acknowledge(self, request: Dict[str, Any], res: str) -> None:
        """Send acknowledgment for received message."""
        if self.channel_config.get('channelType') not in ("targeted", "secure"):
            return
        channel = request.get('channel')
        if channel in ("art_config", "art_secure", "art_presence"):
            return     
        response = {
            "channel": channel,
            "id": request.get('id'),
            "namespace": request.get('namespace'),
            "ref_id": request.get('ref_id'),
            "from": request.get('from'),
            "to_username": request.get('to_username'),
            "to": request.get('to'),
            "return_flag": res,
            "pipeline_id": request.get('pipeline_id'),
            "interceptor_name": request.get('interceptor_name'),
            "attempt_id": request.get('attempt_id'),
        }
        logger.debug("Sending %s acknowledgment for message: %s", res, request.get('id'))
        asyncio.create_task(self.websocket_handler.send_message(json.dumps(response)))
    
    async def handle_message(self, event: str, payload: Any) -> None:
        """Handle incoming messages"""
        return_flag = payload.get('return_flag')
        if return_flag == "SA":
            asyncio.create_task(self.handle_message_acks(event, return_flag, payload))
            return
        self.acknowledge(payload, "MA")
        if self.channel_config.get("channelType") == "secure":
            from_username = payload.get("from_username")
            if from_username:
                response = await self.websocket_handler.push_for_secure_line(
                    "secured_public_key",
                    {"username": from_username},
                    listen=True
                )
                if response and 'data' in response:
                    result = response['data']
                    if result.get("status") == "unsuccessful":
                        raise ChannelError(result.get("error"))
                    
                    sender_key = result.get("public_key")
                    if sender_key:
                        payload['data'] = await self.websocket_handler.decrypt(
                            payload['data'], 
                            sender_key
                        )    
        content = {}
        if 'data' in payload:
            try:
                data_str = payload['data']
                if data_str == "":
                    content = {}
                else:
                    content = json.loads(data_str)
            except json.JSONDecodeError:
                content = payload['data']
        else:
            content = json.loads(payload) if isinstance(payload, str) else payload
        
        if event == 'art_presence':
            self.emit('art_presence', content)
            return
        if self.is_subscribed and event != 'art_presence':
            has_specific = len(self.listeners(event)) > 0
            has_all = len(self.listeners("all")) > 0
            
            if has_specific or has_all:
                if has_specific:
                    self.emit(event, content)
                if has_all:
                    self.emit("all", {"event": event, "content": content})
                self.acknowledge(payload, "CA")
            else:
                if event not in self.message_buffer:
                    self.message_buffer[event] = []
                buffered_message = {
                    'id': payload.get('id'),
                    'from': payload.get('from'),
                    'channel': payload.get('channel'),
                    'to': payload.get('to'),
                    'pipeline_id': payload.get('pipeline_id'),
                    'attempt_id': payload.get('attempt_id'),
                    'interceptor_name': payload.get('interceptor_name'),
                    'to_username': payload.get('to_username'),
                    'ref_id': payload.get('ref_id'),
                    'content': content
                }
                self.message_buffer[event].append(buffered_message)

    async def subscribe(self) -> None:
        """Subscribe to the channel."""
        if self.channel_config['channelName'] in ("art_config", "art_secure"):
            return
            
        self.is_subscribed = True
        self.channel_config = await subscribe_to_channel(self.channel_config['channelName'], "subscribe", self.websocket_handler, lambda error: self._handle_subscription_error(error))
       
    async def unsubscribe(self) -> bool:
        """Unsubscribe from the channel."""
        if self.channel_config['channelName'] in ("art_config", "art_secure"):
            return True
            
        if not self.subscription_id:
            logger.warning("No subscription ID for channel: %s", self.channel_config['channelName'])
            return False    
        try:
            success = await unsubscribe_from_channel(self.channel_config['channelName'], self.subscription_id, "subscribe", self.websocket_handler, self.error_callback)         
            if success:
                self.is_subscribed = False
                self.remove_all_listeners()
                self.message_buffer.clear()
                self.cleanup_pending_acks()
                self.websocket_handler.remove_subscription(self.channel_config['channelName'])   
            return success            
        except Exception as e:
            logger.error("Error unsubscribing from channel %s: %s", self.channel_config['channelName'], e, exc_info=True)
            return False
        
    def _handle_subscription_error(self, error: Exception) -> None:
        logger.error("Error in subscription for channel '%s': %s", self.channel_config['channelName'], error, exc_info=True)
        self.is_subscribed = False

    async def presence(self) -> None:
        """Enable presence for the channel."""
        if self.channel_config['channelName'] in ("art_config", "art_secure"):
            return
        self.is_listening = True
        self.is_subscribed = True 
        await subscribe_to_channel(self.channel_config['channelName'], "presence", self.websocket_handler, lambda error: self._handle_presence_error(error))

    def _handle_presence_error(self, error: Exception) -> None:
        self.is_listening = False
        raise ChannelError(f"Error in subscription for presence channel '{self.channel_config['channelName']}': {error}")

    def reconnect(self) -> None:
        """
        Reconnect the subscription after connection loss.

        Re-validates presence tracking and resubscribes to the channel.
        """
        if self.channel_config['channelName'] not in ("art_config", "art_secure"):
            if self.is_listening:
                asyncio.create_task(self.validate_subscription(self.channel_config['channelName'], "presence"))
            # Always re-subscribe after reconnection
            asyncio.create_task(self.subscribe())

    def cleanup_pending_acks(self) -> None:
        """Clean up any pending acknowledgments (call on disconnect)."""
        for ref_id, ack_future in list(self.pending_acks.items()):
            if not ack_future.done():
                ack_future.set_exception(Exception("Connection closed"))
        self.pending_acks.clear()