from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LLMConfig:
    """
    Configuration for an LLM invocation.
    """
    model: str
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    timeout_seconds: Optional[int] = None
