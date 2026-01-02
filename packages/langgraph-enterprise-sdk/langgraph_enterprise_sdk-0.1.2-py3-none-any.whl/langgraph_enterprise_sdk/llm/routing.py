from typing import Dict

from .base import LLM
from .config import LLMConfig


class LLMRouter:
    """
    Routes requests to a registered LLM.

    Example:
    - model prefix based routing
    - fallback routing
    """

    def __init__(self, providers: Dict[str, LLM]):
        self._providers = providers

    def route(self, config: LLMConfig) -> LLM:
        for prefix, provider in self._providers.items():
            if config.model.startswith(prefix):
                return provider
        raise RuntimeError(f"No LLM provider for model '{config.model}'")
