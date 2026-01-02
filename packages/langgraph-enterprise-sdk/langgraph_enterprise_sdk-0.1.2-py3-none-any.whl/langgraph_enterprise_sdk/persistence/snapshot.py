from dataclasses import dataclass
from datetime import datetime

from langgraph_enterprise_sdk.api.state import State


@dataclass(frozen=True)
class Snapshot:
    """
    Immutable snapshot of execution.

    Used for:
    - Time travel
    - Debugging
    - Audit
    """
    execution_id: str
    step: int
    state: State
    timestamp: datetime


class SnapshotStore:
    """
    Snapshot persistence interface.
    """

    def save(self, snapshot: Snapshot) -> None:
        raise NotImplementedError

    def load(self, execution_id: str, step: int) -> Snapshot:
        raise NotImplementedError
