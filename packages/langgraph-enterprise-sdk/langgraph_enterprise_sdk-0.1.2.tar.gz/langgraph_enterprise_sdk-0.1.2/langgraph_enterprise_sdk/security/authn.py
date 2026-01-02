from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Identity:
    """
    Authenticated identity.
    """
    subject: str
    issuer: str
    tenant_id: Optional[str]
    roles: tuple[str, ...]


class Authenticator:
    """
    Authentication interface.

    Converts credentials → Identity
    """

    def authenticate(self, token: str) -> Identity:
        """
        Validate token and extract identity.

        Token validation MUST be done here.
        """
        # Example stub (JWT / OAuth handled externally)
        if not token:
            raise RuntimeError("Missing authentication token")

        return Identity(
            subject="user-123",
            issuer="auth-provider",
            tenant_id="default",
            roles=("user",),
        )
