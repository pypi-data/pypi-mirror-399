from fastapi import Depends, Header

from langgraph_enterprise_sdk.security.authn import Authenticator, Identity


authenticator = Authenticator()


def get_identity(
    authorization: str | None = Header(default=None),
) -> Identity:
    """
    Resolve identity from Authorization header.
    """
    if not authorization:
        raise RuntimeError("Missing Authorization header")

    token = authorization.replace("Bearer ", "")
    return authenticator.authenticate(token)
