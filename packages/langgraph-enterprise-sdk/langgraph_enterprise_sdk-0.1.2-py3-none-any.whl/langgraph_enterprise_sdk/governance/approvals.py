from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ApprovalRequest:
    """
    Represents an approval requirement.

    Used for:
    - High-risk agent actions
    - Production changes
    - Human-in-the-loop (HITL)
    """
    action: str
    actor: str
    reason: Optional[str] = None


class ApprovalPolicy:
    """
    Determines whether an action requires approval.

    ZAD:
    - Pure decision logic
    """

    def requires_approval(self, request: ApprovalRequest) -> bool:
        # Default enterprise-safe behavior:
        # Require approval for all non-read actions
        return not request.action.lower().startswith("read")
