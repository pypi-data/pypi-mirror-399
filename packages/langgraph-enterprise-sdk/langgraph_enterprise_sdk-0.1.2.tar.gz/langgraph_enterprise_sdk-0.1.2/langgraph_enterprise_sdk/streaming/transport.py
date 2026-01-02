from abc import ABC, abstractmethod

from .events import StreamEvent


class StreamTransport(ABC):
    """
    Streaming transport abstraction.

    Examples:
    - Server-Sent Events (SSE)
    - WebSocket
    - Kafka
    """

    @abstractmethod
    def send(self, event: StreamEvent) -> None:
        raise NotImplementedError
