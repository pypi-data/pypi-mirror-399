from abc import ABC, abstractmethod
from typing import Any, Dict

from .config import LLMConfig


class LLM(ABC):
    """
    Abstract LLM interface.

    TOON:
    - LLMs execute inference only
    ZAD:
    - No side effects
    """

    @abstractmethod
    def invoke(self, prompt: str, config: LLMConfig) -> Dict[str, Any]:
        """
        Execute an LLM call and return structured output.
        """
        raise NotImplementedError
