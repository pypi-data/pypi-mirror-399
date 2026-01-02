class SecurityError(RuntimeError):
    """
    Base error for all security-related failures.

    Includes:
    - Authentication
    - Authorization
    - Policy enforcement
    """

    def __init__(self, message: str):
        super().__init__(message)


class AuthorizationError(SecurityError):
    """
    Raised when access is denied due to insufficient permissions.
    """

    def __init__(self, actor: str | None = None):
        msg = "Authorization failed"
        if actor:
            msg = f"Authorization failed for actor '{actor}'"
        super().__init__(msg)
