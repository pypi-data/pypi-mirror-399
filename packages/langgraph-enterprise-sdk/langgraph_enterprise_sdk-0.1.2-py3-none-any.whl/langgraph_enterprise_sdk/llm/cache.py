from typing import Dict, Optional, Tuple

from .config import LLMConfig


class LLMCache:
    """
    Simple in-memory cache.

    ZAD:
    - Cache is optional
    - Cache miss must not change behavior
    """

    def __init__(self):
        self._store: Dict[Tuple[str, str], Dict] = {}

    def get(self, prompt: str, config: LLMConfig) -> Optional[Dict]:
        key = (prompt, config.model)
        return self._store.get(key)

    def set(self, prompt: str, config: LLMConfig, response: Dict) -> None:
        key = (prompt, config.model)
        self._store[key] = response
