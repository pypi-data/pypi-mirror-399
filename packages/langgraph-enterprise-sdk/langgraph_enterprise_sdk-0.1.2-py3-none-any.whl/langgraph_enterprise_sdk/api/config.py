from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RunnableConfig:
    """
    Runtime execution configuration.

    ZAD:
    - Configuration does not affect state directly
    - Used only by executor/runtime
    """
    max_steps: Optional[int] = None
    timeout_seconds: Optional[int] = None
    trace_id: Optional[str] = None
