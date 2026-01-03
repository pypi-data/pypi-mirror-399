import asyncio
from typing import Any, List
from functools import wraps


class SyncWrapper:
    """
    Wraps any async object and makes its methods synchronous.
    Handles nested async objects automatically.
    """
    METHOD_TIMEOUTS = {
        'push': 10,
        'fetch_presence': 30,
        'unsubscribe': 10,
        'subscribe': 10,
        'presence': 10,
        'bind': 5,
        'listen': 5,
        'remove': 5,
        'check': 10,
    }
    
    def __init__(self, async_obj: Any, loop: asyncio.AbstractEventLoop, obj_type: str = "object") -> None:
        """
        Initialize the sync wrapper.

        Args:
            async_obj: The async object to wrap
            loop: Event loop to run async methods in
            obj_type: Type name for better error messages (e.g., "subscription", "interception")
        """
        self._async_obj = async_obj
        self._loop = loop
        self._obj_type = obj_type
    
    def __getattr__(self, name: str) -> Any:
        """
        Dynamically wrap async methods to be sync.
        Pass through non-async attributes as-is.
        """
        # Get the attribute from the wrapped object
        attr = getattr(self._async_obj, name)
        
        # If it's not a coroutine function, return as-is
        if not asyncio.iscoroutinefunction(attr):
            return attr
        
        # Get custom timeout for this method (default to 10 seconds)
        timeout = self.METHOD_TIMEOUTS.get(name, 10)
        
        @wraps(attr)
        def sync_method(*args, **kwargs):
            """Synchronous wrapper for async method."""
            # Run the async method in the event loop
            future = asyncio.run_coroutine_threadsafe(
                attr(*args, **kwargs),
                self._loop
            )
            
            try:
                # Wait for result with timeout
                result = future.result(timeout=timeout)
                # If result is another async object that might need wrapping
                if result and hasattr(result, '__class__'):
                    # Check if it's a subscription or other known async object
                    class_name = result.__class__.__name__
                    if class_name in ['Subscription', 'LiveObjSubscription', 'Interception']:
                        # Wrap nested async object
                        return SyncWrapper(result, self._loop, class_name.lower())
                
                return result
                
            except asyncio.TimeoutError:
                raise TimeoutError(
                    f"{self._obj_type}.{name}() timed out after {timeout} seconds. "
                    f"The operation may still be running in the background."
                )
            except Exception as e:
                # Provide better error context
                error_msg = f"Error in {self._obj_type}.{name}(): {str(e)}"
                # Re-raise the same exception type with more context
                raise type(e)(error_msg) from e
        
        # Set a helpful name for debugging
        sync_method.__name__ = f"sync_{name}"
        sync_method.__doc__ = f"Synchronous wrapper for {name}(). Timeout: {timeout}s"
        
        return sync_method
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<SyncWrapper({self._obj_type}) wrapping {self._async_obj}>"

    def __dir__(self) -> List[str]:
        """Make auto-completion work better in IDEs."""
        return dir(self._async_obj)