import logging
import asyncio
import json
import aiohttp
from typing import Dict, Any, Optional
from .constant import Constant
from .exceptions import AuthenticationError
logger = logging.getLogger(__name__)

class LongPollClient:
    """HTTP long polling client"""

    def __init__(self, options: Dict[str, Any]) -> None:
        self.endpoint = options.get('endpoint', Constant.LPOLL)
        self.connection_id = options.get('initial_connection_id')
        self.get_auth_params = options.get('get_auth_params')
        self.on_message = options.get('on_message')
        self.on_open = options.get('on_open')
        self.on_error = options.get('on_error')
        self.on_close = options.get('on_close')
        self.retry_delay_ms = options.get('retry_delay_ms', 1000)
        self.is_running = False
        self._task = None
        self._abort_event = asyncio.Event()
        self.server_timeout = 30
        self.client_timeout = self.server_timeout + 10
        self.empty_poll_delay_ms = options.get('empty_poll_delay_ms', 500)
        self.max_empty_poll_delay_ms = options.get('max_empty_poll_delay_ms', 5000)
        logger.debug("LongPollClient initialized with endpoint: %s", self.endpoint)

    def start(self, connection_id: Optional[str] = None) -> None:
        """Start the long polling loop"""
        if self.is_running:
            return
            
        if connection_id:
            self.connection_id = connection_id
            
        self.is_running = True
        self._abort_event.clear()
        self._task = asyncio.create_task(self._poll_loop())
        # Trigger open event
        if self.on_open:
            self.on_open()
        logger.info("HTTP long polling started with connection_id: %s", self.connection_id)

    def stop(self) -> None:
        """Stop the long polling loop"""
        if not self.is_running:
            return
        logger.info("Stopping HTTP long polling")
        self.is_running = False
        self._abort_event.set()
        
        if self._task:
            self._task.cancel()

        if self.on_close:
            self.on_close("Client stopped")

    async def _poll_loop(self) -> None:
        """Main polling loop"""
        consecutive_errors = 0
        backoff_empty = self.empty_poll_delay_ms / 1000
        while self.is_running:
            try:
                url = self.endpoint
                params = await self.get_auth_params()
                
                if self.connection_id:
                    params["connection_id"] = self.connection_id
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get(
                            url, 
                            params=params, 
                            timeout=aiohttp.ClientTimeout(total=self.client_timeout)
                        ) as resp:
                            logger.debug("Long poll request URL: %s", str(resp.url))
                            
                            consecutive_errors = 0
                            if resp.status == 204:
                                await asyncio.sleep(backoff_empty)
                                backoff_empty = min(backoff_empty * 2, self.max_empty_poll_delay_ms / 1000)
                                continue
                                
                            elif resp.status == 401:
                                error_text = await resp.text()
                                error_msg = f"Authentication failed: {error_text}"
                                if self.on_error:
                                    self.on_error(AuthenticationError(error_msg))
                                await asyncio.sleep(1)
                                continue
                                
                            elif not resp.ok:
                                error_text = await resp.text()
                                error_msg = f"HTTP error {resp.status}: {error_text}"
                                if self.on_error:
                                    self.on_error(Exception(error_msg))
                                await asyncio.sleep(self.retry_delay_ms / 1000)
                                continue
                            try:
                                data = await resp.json()
                                logger.debug("Long poll response received: %d messages", len(data) if isinstance(data, list) else 1)
                            except json.JSONDecodeError as e:
                                if self.on_error:
                                    self.on_error(e)
                                continue
                    except asyncio.TimeoutError:
                        consecutive_errors += 1
                        if consecutive_errors > 5:
                            if self.on_error:
                                self.on_error(Exception("Too many consecutive timeouts"))
                            await asyncio.sleep(self.retry_delay_ms / 1000)
                        continue
                    except Exception as e:
                        consecutive_errors += 1
                        if self.on_error:
                            self.on_error(e)
                        await asyncio.sleep(self.retry_delay_ms / 1000)
                        continue
                if not self.connection_id and "connection_id" in data:
                    self.connection_id = data["connection_id"]
                    logger.debug("Received connection_id: %s", self.connection_id)
                
                if "messages" in data and data["messages"]:
                    if self.on_message:
                        self.on_message(data["messages"])
                
            except asyncio.TimeoutError:
                consecutive_errors += 1
                if consecutive_errors > 5:
                    if self.on_error:
                        self.on_error(Exception("Too many consecutive timeouts"))
                    await asyncio.sleep(self.retry_delay_ms / 1000)
                continue
                
            except Exception as e:
                # Other errors
                consecutive_errors += 1
                if self.on_error:
                    self.on_error(e)
                await asyncio.sleep(self.retry_delay_ms / 1000)
                continue
        
        # Trigger close event when loop ends
        if self.on_close:
            self.on_close("Poll loop ended")
