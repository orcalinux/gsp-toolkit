# desktop/gsp_core/events.py

from typing import Callable, Any, List

# Internal list of subscriber callables
_subscribers: List[Callable[[str, Any], None]] = []

def subscribe(fn: Callable[[str, Any], None]) -> None:
    """
    Subscribe to GSP events.
    'fn' will be called as fn(event_name: str, payload: Any).
    """
    if fn not in _subscribers:
        _subscribers.append(fn)

def publish(event: str, payload: Any) -> None:
    """
    Publish an event to all subscribers.
    Exceptions in subscribers are caught and ignored.
    """
    for fn in list(_subscribers):
        try:
            fn(event, payload)
        except Exception:
            pass

def clear_subscribers() -> None:
    """
    Clear all subscribers (for testing or reinitialization).
    """
    _subscribers.clear()
