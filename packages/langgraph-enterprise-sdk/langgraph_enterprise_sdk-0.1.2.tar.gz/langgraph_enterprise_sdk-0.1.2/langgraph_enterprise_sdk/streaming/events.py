from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class StreamEvent:
    """
    Immutable streaming event.

    ZAD:
    - Serializable
    - Deterministic
    """
    type: str
    timestamp: datetime
    execution_id: str
    node: Optional[str]
    payload: Dict[str, Any]
