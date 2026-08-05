from typing import Callable, List

class EventDispatcher:
    def __init__(self):
        self._listeners: dict[str, List[Callable]] = {}

    def add_listener(self, event_name: str, callback: Callable):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def dispatch(self, event_name: str, *args, **kwargs):
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                callback(*args, **kwargs)
