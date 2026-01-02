class PersistenceError(RuntimeError):
    """
    Raised when persistence or durability fails.

    Used by:
    - Checkpointing
    - Snapshotting
    - Recovery / replay
    """

    def __init__(self, message: str):
        super().__init__(message)


class CheckpointError(PersistenceError):
    """
    Raised when checkpoint save/load fails.
    """

    def __init__(self, operation: str, reason: str):
        super().__init__(
            f"Checkpoint {operation} failed: {reason}"
        )
