import logging
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from .exceptions import AuthenticationError
logger = logging.getLogger(__name__)


class SSEClient:
    """Server-Sent Events client implementation."""

    def __init__(self, options: Dict[str, Any]) -> None:
        """
        Initialize the SSE client.

        Args:
            options: Configuration options dictionary
                url: SSE endpoint URL
                params: URL query parameters
                headers: HTTP headers for request
                on_message: Callback for message events
                on_open: Callback when connection opens
                on_error: Callback for error events
                on_close: Callback when server requests close
        """
        self.url = options.get('url')
        self.params = options.get('params', {})
        self.headers = options.get('headers', {})
        self.on_message = options.get('on_message')
        self.on_open = options.get('on_open')
        self.on_error = options.get('on_error')
        self.on_close = options.get('on_close')
        
        self._session = None
        self._response = None
        self._task: Optional[asyncio.Task] = None
        self._is_running = False
        self._abort_event = asyncio.Event()

    async def connect(self) -> None:
        """Establish SSE connection and start processing events."""
        if self._is_running:
            return
        
        self._is_running = True
        self._abort_event.clear()
        
        try:
            self._session = aiohttp.ClientSession()
            self._response = await self._session.get(
                self.url,
                params=self.params,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=None)  # No timeout for SSE
            )
            
            if not self._response.ok:
                if self._response.status == 401:
                    raise AuthenticationError(f"SSE connection failed: HTTP {self._response.status}")
                raise ConnectionError(f"SSE connection failed: HTTP {self._response.status}")
            logger.debug("SSE connection established")
            # Call the onopen callback
            if self.on_open:
                self.on_open()
            
            # Start processing the event stream
            self._task = asyncio.create_task(self._process_events())
            
        except Exception as e:
            if self.on_error:
                self.on_error(e)
            await self.close()
            raise  # Re-raise to allow fallback logic to work
    
    async def _process_events(self) -> None:
        """Process the SSE event stream."""
        try:
            # SSE event parsing state
            current_event = "message"  # Default event type
            data_buffer = []
            last_event_id = None
            
            # Read the response line by line
            async for line_bytes in self._response.content:
                # Check if we should stop
                if not self._is_running:
                    break
                    
                line = line_bytes.decode('utf-8').rstrip()
                
                # Empty line marks the end of an event
                if not line:
                    if data_buffer:
                        data = '\n'.join(data_buffer)
                        
                        # Handle special "close" event from server
                        if current_event == "close":
                            if self.on_close:
                                self.on_close(data)
                            await self.close()
                            break
                        
                        # Dispatch regular event
                        if self.on_message:
                            try:
                                # Try to parse as JSON array or object
                                parsed_data = json.loads(data)
                                
                                # If it's an array, process each message
                                if isinstance(parsed_data, list):
                                    for msg in parsed_data:
                                        self.on_message({
                                            'type': current_event,
                                            'data': msg,
                                            'lastEventId': last_event_id
                                        })
                                else:
                                    self.on_message({
                                        'type': current_event,
                                        'data': parsed_data,
                                        'lastEventId': last_event_id
                                    })
                            except json.JSONDecodeError:
                                # If not JSON, pass raw data
                                self.on_message({
                                    'type': current_event,
                                    'data': data,
                                    'lastEventId': last_event_id
                                })
                        
                        # Reset for next event
                        data_buffer = []
                        current_event = "message"
                    continue
                
                if line.startswith(':'):
                    # Comment line, ignore
                    continue
                    
                if ':' in line:
                    field, value = line.split(':', 1)
                    value = value.lstrip() 
                    
                    if field == 'event':
                        current_event = value
                    elif field == 'data':
                        data_buffer.append(value)
                    elif field == 'id':
                        last_event_id = value
                    elif field == 'retry':
                        pass
                else:
                    if line == 'data':
                        data_buffer.append('')
        
        except asyncio.CancelledError:
      
            return
        except Exception as e:
            if self.on_error:
                self.on_error(e)
        finally:
            await self.close()
    
    async def close(self) -> None:
        """Close the SSE connection."""
        self._is_running = False
        self._abort_event.set()
        
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):
                pass
            self._task = None
        
        if self._response:
            self._response.close()
            self._response = None
        
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None