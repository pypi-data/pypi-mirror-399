from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from langgraph_enterprise_sdk.api.state import State
from .serializers import StateSerializer


@dataclass(frozen=True)
class Checkpoint:
    """
    Immutable execution checkpoint.
    """
    execution_id: str
    node: str
    state: State
    timestamp: datetime


class CheckpointStore:
    """
    Abstract checkpoint store.

    Implementations:
    - Postgres
    - S3
    - Blob storage
    """

    def save(self, checkpoint: Checkpoint) -> None:
        raise NotImplementedError

    def load_latest(self, execution_id: str) -> Optional[Checkpoint]:
        raise NotImplementedError
