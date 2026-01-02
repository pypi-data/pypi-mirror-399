from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class ResumeCommand:
    """
    Represents a command to resume execution
    after an interrupt.

    ZAD:
    - No execution logic
    - Only declarative intent
    """
    approved: bool
    metadata: Dict[str, Any] | None = None
