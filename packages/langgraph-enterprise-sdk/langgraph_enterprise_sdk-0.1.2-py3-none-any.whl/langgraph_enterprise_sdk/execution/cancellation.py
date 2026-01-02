import threading


class CancellationToken:
    """
    Cooperative cancellation token.

    ZAD:
    - No forceful termination
    - Checked explicitly by executor
    """

    def __init__(self):
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    def is_cancelled(self) -> bool:
        return self._event.is_set()

    def raise_if_cancelled(self) -> None:
        if self.is_cancelled():
            raise RuntimeError("Execution cancelled")
