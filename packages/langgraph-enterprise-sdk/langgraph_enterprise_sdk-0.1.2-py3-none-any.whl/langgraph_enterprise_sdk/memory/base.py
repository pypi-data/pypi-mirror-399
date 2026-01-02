from abc import ABC, abstractmethod
from typing import Any, Dict, List


class MemoryStore(ABC):
    """
    Abstract memory store interface.

    ZAD:
    - Explicit reads and writes only
    """

    @abstractmethod
    def write(self, key: str, value: Dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def read(self, key: str) -> Dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> None:
        raise NotImplementedError


class VectorMemoryStore(ABC):
    """
    Abstract vector memory interface (RAG).
    """

    @abstractmethod
    def upsert(self, id: str, embedding: List[float], metadata: Dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(self, embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        raise NotImplementedError
