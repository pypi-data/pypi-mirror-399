from typing import Optional

from langgraph_enterprise_sdk.api.state import State
from .checkpoint import CheckpointStore
from .serializers import StateSerializer


class RecoveryManager:
    """
    Restores execution state after failure.

    Used by:
    - Executor
    - Resume flows
    """

    def __init__(self, store: CheckpointStore):
        self._store = store

    def recover(self, execution_id: str) -> Optional[State]:
        checkpoint = self._store.load_latest(execution_id)
        if not checkpoint:
            return None
        return checkpoint.state
