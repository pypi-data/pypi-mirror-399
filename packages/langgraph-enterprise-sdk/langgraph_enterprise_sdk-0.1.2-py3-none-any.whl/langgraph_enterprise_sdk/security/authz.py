from dataclasses import dataclass

from .authn import Identity


@dataclass(frozen=True)
class AuthorizationRequest:
    """
    Authorization request.
    """
    identity: Identity
    action: str
    resource: str


class Authorizer:
    """
    Authorization evaluator.

    AuthZ answers:
    - Is this identity allowed?
    """

    def authorize(self, request: AuthorizationRequest) -> None:
        if "admin" in request.identity.roles:
            return

        if request.action.lower().startswith("read"):
            return

        raise RuntimeError(
            f"Unauthorized action '{request.action}' on '{request.resource}'"
        )
