from abc import ABC, abstractmethod
from typing import Any, Dict, List


class KnowledgeGraph(ABC):
    """
    Abstract Knowledge Graph interface.

    TOON:
    - Used by nodes, not controlling them
    """

    @abstractmethod
    def query(self, query: Any) -> List[Dict[str, Any]]:
        """Execute a knowledge query"""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Verify graph availability"""
        raise NotImplementedError
