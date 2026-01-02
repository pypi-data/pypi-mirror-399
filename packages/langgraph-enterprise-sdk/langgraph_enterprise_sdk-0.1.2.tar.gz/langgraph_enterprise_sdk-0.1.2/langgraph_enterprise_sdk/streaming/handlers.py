from typing import List

from .callbacks import StreamCallback
from .events import StreamEvent


class StreamHandler:
    """
    Dispatches streaming events to registered callbacks.

    TOON:
    - Passive observer
    """

    def __init__(self):
        self._callbacks: List[StreamCallback] = []

    def register(self, callback: StreamCallback) -> None:
        self._callbacks.append(callback)

    def emit(self, event: StreamEvent) -> None:
        for callback in self._callbacks:
            try:
                callback.on_event(event)
            except Exception:
                # Streaming must never break execution
                pass
