from dataclasses import dataclass

from .interrupt import Interrupt


@dataclass(frozen=True)
class EscalationInterrupt(Interrupt):
    """
    Raised when execution must be escalated
    to a higher authority or system.
    """

    severity: str = "high"

    def __init__(
        self,
        *,
        reason: str,
        node: str,
        severity: str = "high",
    ):
        super().__init__(
            reason=reason,
            node=node,
            requires_human=True,
        )
        object.__setattr__(self, "severity", severity)
