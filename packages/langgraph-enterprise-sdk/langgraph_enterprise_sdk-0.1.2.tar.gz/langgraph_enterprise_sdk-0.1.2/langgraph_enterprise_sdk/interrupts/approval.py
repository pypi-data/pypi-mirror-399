from dataclasses import dataclass

from .interrupt import Interrupt


@dataclass(frozen=True)
class ApprovalInterrupt(Interrupt):
    """
    Raised when an action requires human approval.
    """

    approver_role: str | None = None

    def __init__(
        self,
        *,
        reason: str,
        node: str,
        approver_role: str | None = None,
    ):
        super().__init__(
            reason=reason,
            node=node,
            requires_human=True,
        )
        object.__setattr__(self, "approver_role", approver_role)
