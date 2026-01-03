import logging
from typing import Dict, List, Callable, Any, Optional

logger = logging.getLogger(__name__)


class EventEmitter:
    def __init__(self) -> None:
        self._events: Dict[str, List[Callable]] = {}

    def on(self, event: str, listener: Callable) -> "EventEmitter":
        if event not in self._events:
            self._events[event] = []
        self._events[event].append(listener)
        return self

    def off(self, event: str, listener: Callable) -> "EventEmitter":
        """Remove a specific listener for an event"""
        if event in self._events:
            try:
                self._events[event].remove(listener)
                # Clean up empty event arrays
                if not self._events[event]:
                    del self._events[event]
            except ValueError:
                pass
        return self

    def emit(self, event: str, *args: Any, **kwargs: Any) -> bool:
        """Emit an event to all listeners"""
        if event not in self._events:
            return False

        listeners = self._events[event][:]
        for listener in listeners:
            try:
                listener(*args, **kwargs)
            except Exception as e:
                logger.error("[EventEmitter] Error in listener for event '%s': %s", event, e)

        return True

    def listeners(self, event: str) -> List[Callable]:
        """Get all listeners for an event"""
        return self._events.get(event, []).copy()

    def has_listeners(self, event: str) -> bool:
        """Check if an event has any listeners"""
        return event in self._events and len(self._events[event]) > 0

    def listener_count(self, event: str) -> int:
        """Get the number of listeners for an event"""
        return len(self._events.get(event, []))

    def remove_all_listeners(self, event: Optional[str] = None) -> "EventEmitter":
        """Remove all listeners for a specific event, or all events if no event specified"""
        if event is None:
            self._events.clear()
        else:
            if event in self._events:
                del self._events[event]
        return self
                
    def once(self, event: str, listener: Callable) -> None:
        """Add a one-time listener for an event"""
        def once_wrapper(*args: Any, **kwargs: Any) -> None:
            self.off(event, once_wrapper)
            listener(*args, **kwargs)
        self.on(event, once_wrapper)

    def prepend_listener(self, event: str, listener: Callable) -> None:
        """Add a listener to the beginning of the listeners array"""
        if event not in self._events:
            self._events[event] = []
        self._events[event].insert(0, listener)

    def prepend_once_listener(self, event: str, listener: Callable) -> None:
        """Add a one-time listener to the beginning of the listeners array"""
        def once_wrapper(*args: Any, **kwargs: Any) -> None:
            self.off(event, once_wrapper)
            listener(*args, **kwargs)

        self.prepend_listener(event, once_wrapper)

    def event_names(self) -> List[str]:
        """Get a list of all event names that have listeners"""
        return list(self._events.keys())
