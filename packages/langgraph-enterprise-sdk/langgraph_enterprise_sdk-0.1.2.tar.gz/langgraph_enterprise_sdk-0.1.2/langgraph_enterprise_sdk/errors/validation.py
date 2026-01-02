class ValidationError(ValueError):
    """
    Raised when input or configuration validation fails.

    ZAD:
    - Validation errors must be raised BEFORE execution
    """

    def __init__(self, message: str, *, field: str | None = None):
        self.field = field
        super().__init__(message)
