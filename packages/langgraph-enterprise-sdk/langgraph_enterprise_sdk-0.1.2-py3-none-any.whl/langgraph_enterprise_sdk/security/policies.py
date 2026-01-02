from dataclasses import dataclass
from typing import Any, Dict

from .authn import Identity


@dataclass(frozen=True)
class PolicyContext:
    """
    Context used for policy evaluation.
    """
    identity: Identity
    metadata: Dict[str, Any]


class Policy:
    """
    Base policy interface.
    """

    def evaluate(self, context: PolicyContext, action: str) -> None:
        """
        Raise exception if policy violated.
        """
        pass
