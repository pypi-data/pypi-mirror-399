import logging
import json
import asyncio
from typing import Dict, Any, Callable
from .utils.event_emitter import EventEmitter
from .utils.server_data_utils import get_interceptor_config
logger = logging.getLogger(__name__)

class Interception(EventEmitter):
    def __init__(self, interceptor: str, fn: Callable, websocket_handler: Any, error_callback: Callable, loop: asyncio.AbstractEventLoop) -> None:
        super().__init__()
        self.interceptor = interceptor
        self.fn = fn  # Now expects (payload, resolve, reject) signature
        self.websocket_handler = websocket_handler
        self.error_callback = error_callback
        self.state = False
        self.loop = loop
        try:
            self.loop.call_soon_threadsafe(lambda: asyncio.create_task(self.validate_interception()))
        except RuntimeError:
            asyncio.run(self.validate_interception())

    async def validate_interception(self) -> None:
        await self.websocket_handler.ready_event.wait()
        await get_interceptor_config(self.interceptor, self.websocket_handler, self.error_callback)

    def reconnect(self) -> None:
        asyncio.create_task(self.validate_interception())

    def execute(self, request: Dict[str, Any]) -> None:
        """Execute interceptor with resolve/reject pattern"""
        self.acknowledge(request)
        
        # Extract request details
        id_ = request.get("id")
        channel = request.get("channel")
        namespace = request.get("namespace")
        from_ = request.get("from")
        to = request.get("to")
        event = request.get("event")
        interceptor_name = request.get("interceptor_name")
        pipeline_position = request.get("pipeline_position")
        interceptor_id = request.get("interceptor_id")
        attempt_id = request.get("attempt_id")
        ref_id = request.get("ref_id")
        data = request.get("data")
        
        # Config for interceptor
        config = {
            "channel": channel,
            "namespace": namespace,
            "event": event,
            "interceptor_id": interceptor_id,
            "interceptor_name": interceptor_name,
            "from": from_,
            "to": to
        }
        
        # Resolve callback
        def resolve(result_data):
            """Send success response back through pipeline"""
            if result_data is None or not isinstance(result_data, (dict, list)):
                result_data = {}
            
            # Clean up nested data structure if present
            if isinstance(result_data, dict):
                if result_data.get("attempt_id") or result_data.get("pipeline_id"):
                    result_data = result_data.get("data", {})
            
            response = self._create_response(
                config, id_, ref_id, channel, namespace, event,
                pipeline_position, interceptor_name, attempt_id, 
                "resolve", result_data
            )
            self.loop.call_soon_threadsafe(
                lambda: self.loop.create_task(
                    self.websocket_handler.send_message(json.dumps(response))
                )
            )
        
        # Reject callback
        def reject(error_msg: str):
            """Send error response back through pipeline"""
            if not isinstance(error_msg, str):
                error_msg = str(error_msg)
            
            error_response = {
                "original_data": data,
                "error": error_msg
            }
            
            response = self._create_response(
                config, id_, ref_id, channel, namespace, event,
                pipeline_position, interceptor_name, attempt_id,
                "reject", error_response
            )
            self.loop.call_soon_threadsafe(
                lambda: self.loop.create_task(
                    self.websocket_handler.send_message(json.dumps(response))
                )
            )
        
        payload = {
            **request,
            "config": config,
            "data": data
        }
        try:
            # Support both sync and async interceptor functions
            result = self.fn(payload, resolve, reject)
            # If function returns a coroutine, await it
            if asyncio.iscoroutine(result):
                asyncio.create_task(result)
        except Exception as e:
            logger.error("Error in interceptor execution: %s", e, exc_info=True)
            reject(str(e))

    def _create_response(self, config: Dict[str, Any], id_: str, ref_id: str, channel: str, namespace: str, event: str, pipeline_position: str, interceptor_name: str, attempt_id: str, return_type: str, content: Any) -> Dict[str, Any]:
        """Create standardized response message"""
        return {
            **config,
            "channel": channel,
            "namespace": namespace,
            "event": event,
            "id": id_,
            "ref_id": ref_id,
            "return_flag": return_type,
            "pipeline_position": pipeline_position,
            "interceptor_name": interceptor_name,
            "attempt_id": attempt_id,
            "content": json.dumps(content)
        }

    def acknowledge(self, request: Dict[str, Any]) -> None:
        """Send acknowledgment that interceptor received the message"""
        id_ = request.get("id")
        from_ = request.get("from")
        to = request.get("to")
        channel = request.get("channel")
        namespace = request.get("namespace")
        pipeline_position = request.get("pipeline_position")
        interceptor_id = request.get("interceptor_id")
        interceptor_name = request.get("interceptor_name")
        attempt_id = request.get("attempt_id")
        ref_id = request.get("ref_id")
        data = request.get("data")
        
        response = {
            "channel": channel,
            "namespace": namespace,
            "id": id_,
            "ref_id": ref_id,
            "from": from_,
            "to": to,
            "return_flag": "IA",
            "pipeline_position": pipeline_position,
            "interceptor_id": interceptor_id,
            "interceptor_name": interceptor_name,
            "attempt_id": attempt_id,
            "content": json.dumps(data)
        }
        
        self.loop.call_soon_threadsafe(
            lambda: self.loop.create_task(
                self.websocket_handler.send_message(json.dumps(response))
            )
        )

    async def handle_message(self, channel: str, data: Dict[str, Any]) -> None:
        """Handle incoming message for this interceptor"""
        try:
            if "data" in data:
                data["data"] = json.loads(data["data"])
            else:
                data = json.loads(data) 
            self.execute(data)
        except Exception as err:
            raise err