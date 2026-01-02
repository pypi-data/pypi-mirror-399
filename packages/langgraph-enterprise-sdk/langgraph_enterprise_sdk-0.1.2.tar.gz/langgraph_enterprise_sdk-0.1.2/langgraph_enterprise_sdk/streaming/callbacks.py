from typing import Protocol

from .events import StreamEvent


class StreamCallback(Protocol):
    """
    Streaming callback interface.

    Implementations:
    - UI push
    - Logging
    - Metrics
    """

    def on_event(self, event: StreamEvent) -> None:
        ...
