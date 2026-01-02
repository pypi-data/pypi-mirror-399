from abc import ABC, abstractmethod
from typing import Dict, List


class EmbeddingProvider(ABC):
    """
    Abstract embedding provider.
    """

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        raise NotImplementedError
