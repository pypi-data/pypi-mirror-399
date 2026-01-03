import logging
from typing import Dict, Any, Callable, Optional
from ..exceptions import ChannelError

logger = logging.getLogger(__name__)

async def subscribe_to_channel(channel: str, process: str, websocket_handler: Any, error_callback: Callable) -> Optional[Dict[str, Any]]:
    """Subscribe to channel"""
    await websocket_handler.wait()
    try:
        channel_subscribe_process = "channel-subscribe" if process == "subscribe" else "channel-presence"
        response = await websocket_handler.push_for_secure_line(
            channel_subscribe_process,
            {"channel": channel},
            listen=True
        )
        logger.debug("Subscription response: %s", response)
        # Extract data from response
        if response and 'data' in response:
            result = response['data']
            # Check for errors
            if result.get('status') == 'not-OK':
                error_msg = f"Error in channel subscription: {channel}, {result.get('error')}"
                logger.error(error_msg)
                error_callback(error_msg)
                raise ChannelError(error_msg)
            # Extract fields
            raw_data = result.get('channelConfig')
            snapshot = result.get('snapshot')
            presence_users = result.get('presenceUsers', [])
            channel_name = result.get('channel')
            channel_namespace = result.get('channelNamespace', '')
            subscription_id = result.get('subscriptionID')

            if raw_data:
                channel_config = {
                    "channelName": channel_name or channel,
                    "channelNamespace": channel_namespace,
                    "channelType": raw_data.get('TypeofChannel'),
                    "snapshot": snapshot,
                    "presenceUsers": presence_users,
                    "subscriptionID": subscription_id
                }
                return channel_config

        raise ChannelError("Invalid response format")

    except Exception as error:
        logger.error("Error in subscribe_to_channel: %s", error)
        error_callback("Failed to subscribe")
        raise error

async def unsubscribe_from_channel(channel: str, subscription_id: str, process: str, websocket_handler: Any, error_callback: Callable) -> bool:
    """Unsubscribe from a channel."""
    await websocket_handler.wait()
    try:
        unsubscribe_channel = "channel-unsubscribe" if process == "subscribe" else "presence-unsubscribe"
        # Use push_for_secure_line with listen=True
        response = await websocket_handler.push_for_secure_line(
            unsubscribe_channel,
            {
                "channel": channel,
                "subscriptionID": subscription_id
            },
            listen=True
        )
        # Check response
        if response and 'data' in response:
            result = response['data']
            if result.get('status') == 'not-OK':
                error_msg = f"Failed to unsubscribe: {result.get('error')}"
                error_callback(error_msg)
                return False
            return True
        
        return False
    except Exception as error:
        error_callback(f"Failed to unsubscribe: {error}")
        return False

async def get_interceptor_config(interceptor: str, websocket_handler: Any, error_callback: Callable) -> Dict[str, Any]:
    await websocket_handler.ready_event.wait()
    try:
        # Use push_for_secure_line with listen=True
        response = await websocket_handler.push_for_secure_line("interceptor-subscribe", {"interceptor": interceptor}, listen=True)
        logger.debug("Interceptor response: %s", response)
        if response and 'data' in response:
            result = response['data']
            if result.get("status") == "not-OK":
                raise ChannelError(result.get("error"))
            raw_data = result.get("interceptorConfig", {})
            return raw_data
        raise ChannelError("Invalid response format")
    except Exception as error:
        error_callback("Failed to subscribe to interceptor")
        raise error