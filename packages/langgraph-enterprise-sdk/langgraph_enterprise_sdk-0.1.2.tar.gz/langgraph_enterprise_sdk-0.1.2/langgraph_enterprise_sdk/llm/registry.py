from typing import Dict

from .base import LLM
from .cache import LLMCache
from .config import LLMConfig
from .routing import LLMRouter
from .safety import SafetyPolicy


class LLMRegistry:
    """
    Central LLM registry.

    This is what orchestration nodes should use.
    """

    def __init__(self):
        self._providers: Dict[str, LLM] = {}
        self._cache = LLMCache()
        self._safety = SafetyPolicy()

    def register(self, prefix: str, llm: LLM) -> None:
        self._providers[prefix] = llm

    def invoke(self, prompt: str, config: LLMConfig) -> Dict:
        self._safety.validate_prompt(prompt)

        cached = self._cache.get(prompt, config)
        if cached:
            return cached

        router = LLMRouter(self._providers)
        provider = router.route(config)

        response = provider.invoke(prompt, config)

        self._safety.validate_response(response.get("text", ""))

        self._cache.set(prompt, config, response)
        return response
