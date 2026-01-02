from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Interrupt:
    """
    Represents an execution interrupt.

    ZAD:
    - Immutable
    - Serializable
    - Replay-safe
    """
    reason: str
    node: Optional[str] = None
    requires_human: bool = False
