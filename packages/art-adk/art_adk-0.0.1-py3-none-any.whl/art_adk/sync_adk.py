"""
Synchronous ADK client implementation.
Wraps AsyncAdk to provide blocking API for non-async contexts.
"""
import asyncio
import threading
import time
from typing import Optional, Dict, Any, Callable
import logging
from .async_adk import AsyncAdk
from .sync_wrapper import SyncWrapper
from .exceptions import NotConnectedError
logger = logging.getLogger(__name__)

class Adk:
    """
    Synchronous ADK client.
    This is a thread-safe wrapper around AsyncAdk that manages its own
    event loop in a dedicated background thread. All async operations
    are automatically converted to synchronous blocking calls.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the synchronous ADK client.
        
        Args:
            config: Configuration dictionary with keys like ROOT, Uri, AuthToken
        """
        self._config = config
        self._async_adk: Optional[AsyncAdk] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._is_connected = False
        self._lock = threading.Lock()  # Thread safety for connect/disconnect
        self._loop_ready = threading.Event()  # Signal when loop is ready
        
    def connect(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Connect to the server (synchronous).
        
        Args:
            config: Optional config to override instance config
            
        Returns:
            Connection details dictionary
            
        Raises:
            ConnectionError: If connection fails
            TimeoutError: If connection times out (30s timeout)
        """
        with self._lock:
            if self._is_connected:
                return self._async_adk.socket.get_connection() if self._async_adk else {}
            
            # Setup event loop if not already done
            if not self._loop:
                self._setup_event_loop()
            
            # Wait for loop to be ready
            if not self._loop_ready.wait(timeout=5):
                raise RuntimeError("Event loop failed to start")
            
            try:
                # Run async connect in the background loop
                future = asyncio.run_coroutine_threadsafe(
                    self._async_connect(config or self._config),
                    self._loop
                )
                result = future.result(timeout=30)
                self._is_connected = True
                logger.info("Successfully connected to ADK server")
                return result
            except Exception as e:
                logger.error(f"Failed to connect: {e}")
                raise ConnectionError(f"Failed to connect: {e}") from e
    
    def _setup_event_loop(self) -> None:
        """Setup dedicated event loop in background thread."""
        self._loop = asyncio.new_event_loop()
        
        def run_loop():
            """Run event loop in thread."""
            asyncio.set_event_loop(self._loop)
            self._loop_ready.set()  # Signal that loop is ready
            try:
                self._loop.run_forever()
            finally:
                self._loop.close()
        
        self._thread = threading.Thread(
            target=run_loop,
            name="ADK-EventLoop",
            daemon=False  # Don't use daemon to ensure proper cleanup
        )
        self._thread.start()
        
        # Wait a moment for thread to start
        time.sleep(0.05)
    
    async def _async_connect(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Internal async helper for connection."""
        self._async_adk = AsyncAdk(config)
        await self._async_adk.connect()
        return self._async_adk.socket.get_connection() if self._async_adk.socket else {}
    
    def subscribe(self, channel: str) -> SyncWrapper:
        """
        Subscribe to a channel (synchronous).
        
        Args:
            channel: Channel name to subscribe to
            
        Returns:
            SyncWrapper wrapping the subscription object
            
        Raises:
            RuntimeError: If not connected
            TimeoutError: If subscription times out (10s timeout)
        """
        if not self._is_connected:
            raise NotConnectedError("Not connected. Call connect() first")
        
        future = asyncio.run_coroutine_threadsafe(
            self._async_adk.subscribe(channel),
            self._loop
        )
        async_sub = future.result(timeout=10)
        
        # Return wrapped subscription that converts all methods to sync
        return SyncWrapper(async_sub, self._loop, "subscription")
    
    def intercept(self, interceptor: str, fn: Callable) -> SyncWrapper:
        """
        Register an interceptor (synchronous).
        
        Args:
            interceptor: Interceptor name
            fn: Callback function(payload, resolve, reject)
            
        Returns:
            SyncWrapper wrapping the interception object
            
        Raises:
            RuntimeError: If not connected
        """
        if not self._is_connected:
            raise NotConnectedError("Not connected. Call connect() first")
        
        # The callback might be called from async context, so wrap it
        def wrapped_fn(payload, resolve, reject):
            """Wrapper to handle sync callback in async context."""
            try:
                # Call the user's sync function
                result = fn(payload, resolve, reject)
                # If it returns a value, resolve with it
                if result is not None and not asyncio.iscoroutine(result):
                    resolve(result)
            except Exception as e:
                reject(str(e))
        
        # Get the async interception
        interception_result = self._async_adk.intercept(interceptor, wrapped_fn)
        
        # Return wrapped interception
        return SyncWrapper(interception_result, self._loop, "interception")
    
    def generate_key_pair(self) -> Dict[str, str]:
        """
        Generate encryption key pair (synchronous).
        
        Returns:
            Dictionary with 'publicKey' and 'privateKey'
            
        Raises:
            RuntimeError: If not connected
        """
        if not self._is_connected:
            raise NotConnectedError("Not connected. Call connect() first")
        
        future = asyncio.run_coroutine_threadsafe(
            self._async_adk.generate_key_pair(),
            self._loop
        )
        return future.result(timeout=10)
    
    def set_key_pair(self, key_pair: Dict[str, str]) -> None:
        """
        Set an existing key pair (synchronous).
        
        Args:
            key_pair: Dictionary with 'publicKey' and 'privateKey'
            
        Raises:
            RuntimeError: If not connected
        """
        if not self._is_connected:
            raise NotConnectedError("Not connected. Call connect() first")
        
        future = asyncio.run_coroutine_threadsafe(
            self._async_adk.set_key_pair(key_pair),
            self._loop
        )
        future.result(timeout=10)
    
    def call(self, endpoint: str, options: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make an API call (synchronous).
        
        Args:
            endpoint: API endpoint path
            options: Request options (method, payload, headers, etc.)
            
        Returns:
            API response data
            
        Raises:
            RuntimeError: If not connected
            TimeoutError: If request times out (30s timeout)
        """
        if not self._is_connected:
            raise NotConnectedError("Not connected. Call connect() first")
        
        future = asyncio.run_coroutine_threadsafe(
            self._async_adk.call(endpoint, options or {}),
            self._loop
        )
        return future.result(timeout=30)
    
    def fetch_presence(self, channel: str, callback: Callable) -> Dict:
        """
        Fetch presence for a channel (synchronous).
        
        Args:
            channel: Channel name
            callback: Function to call with presence updates
            
        Returns:
            Dictionary with unsubscribe function
            
        Raises:
            RuntimeError: If not connected
        """
        if not self._is_connected:
            raise NotConnectedError("Not connected. Call connect() first")
        
        future = asyncio.run_coroutine_threadsafe(
            self._async_adk.fetch_presence(channel, callback),
            self._loop
        )
        result = future.result(timeout=10)
        
        # Wrap the async unsubscribe function if present
        if result and 'unsubscribe' in result:
            async_unsub = result['unsubscribe']
            
            def sync_unsub():
                """Synchronous unsubscribe."""
                unsub_future = asyncio.run_coroutine_threadsafe(
                    async_unsub(),
                    self._loop
                )
                return unsub_future.result(timeout=10)
            
            result['unsubscribe'] = sync_unsub
        
        return result
    
    def pause(self) -> None:
        """
        Pause the connection.
        
        This stops reconnection attempts and closes the socket.
        The connection can be resumed later with resume().
        """
        if not self._async_adk:
            raise RuntimeError("Not connected. Call connect() first")
        
        self._async_adk.pause()
        logger.info("Connection paused")
    
    def resume(self) -> None:
        """
        Resume a paused connection.
        
        Raises:
            RuntimeError: If not connected initially
            TimeoutError: If resume times out (30s timeout)
        """
        if not self._async_adk:
            raise RuntimeError("Not connected. Call connect() first")
        
        future = asyncio.run_coroutine_threadsafe(  
            self._async_adk.resume(),
            self._loop
        )
        future.result(timeout=30)
        logger.info("Connection resumed")
    
    def disconnect(self) -> None:
        """
        Disconnect from server and cleanup all resources.
        
        This method is safe to call multiple times.
        """
        with self._lock:
            if not self._is_connected and not self._async_adk:
                return  # Already disconnected
            
            logger.info("Disconnecting from ADK server...")
            
            # Disconnect the async ADK
            if self._async_adk and self._loop:
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        self._async_adk.disconnect(),
                        self._loop
                    )
                    future.result(timeout=10)
                except Exception as e:
                    logger.warning(f"Error during disconnect: {e}")
            
            # Stop the event loop
            if self._loop and self._loop.is_running():
                self._loop.call_soon_threadsafe(self._loop.stop)
            
            # Wait for thread to finish
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=5)
                if self._thread.is_alive():
                    logger.warning("Event loop thread did not stop cleanly")
            
            # Reset state
            self._is_connected = False
            self._async_adk = None
            self._loop = None
            self._thread = None
            self._loop_ready.clear()
            
            logger.info("Disconnected successfully")
    
    def get_state(self) -> str:
        """
        Get current connection state.
        
        Returns:
            One of: 'not_initialized', 'paused', 'connected', 'retrying', 'stopped'
        """
        if not self._async_adk:
            return "not_initialized"
        return self._async_adk.get_state()
    
    def get_security_code(self, user_payload: dict) -> str:
        """
        Get security passcode through WebSocket secure line (sync version).
        
        Args:
            user_payload: Dict with keys 'Username', 'FirstName', 'LastName'
        
        Returns:
            The passcode string
            
        Raises:
            RuntimeError: If not connected
            TimeoutError: If request times out (20s timeout)
        """
        if not self._is_connected:
            raise NotConnectedError("Not connected. Call connect() first")
        
        future = asyncio.run_coroutine_threadsafe(
            self._async_adk.get_security_code(user_payload),
            self._loop
        )
        return future.result(timeout=20)
    
    # Context manager support
    def __enter__(self):
        """Enter context manager - connects automatically."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager - ensures cleanup."""
        self.disconnect()
        return False  # Don't suppress exceptions
    
    def __del__(self):
        """Destructor - ensure cleanup if not done explicitly."""
        try:
            self.disconnect()
        except Exception:
            pass
    
    def __repr__(self):
        """String representation for debugging."""
        state = self.get_state()
        return f"<Adk(state={state}, connected={self._is_connected})>"