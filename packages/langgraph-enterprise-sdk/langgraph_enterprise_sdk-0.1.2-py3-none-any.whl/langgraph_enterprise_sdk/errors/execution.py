class ExecutionError(RuntimeError):
    """
    Raised when a graph execution fails.

    Characteristics:
    - Deterministic
    - Retry-safe
    - Serializable
    """

    def __init__(self, message: str, *, node: str | None = None):
        self.node = node
        super().__init__(message)


class MaxStepsExceededError(ExecutionError):
    """
    Raised when graph execution exceeds max allowed steps.
    """

    def __init__(self, max_steps: int):
        super().__init__(
            f"Maximum execution steps exceeded ({max_steps})"
        )
