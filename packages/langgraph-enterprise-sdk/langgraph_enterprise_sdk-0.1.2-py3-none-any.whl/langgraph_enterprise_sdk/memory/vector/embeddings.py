from typing import List

from langgraph_enterprise_sdk.llm.registry import LLMRegistry
from langgraph_enterprise_sdk.llm.config import LLMConfig

from .base import EmbeddingProvider


class LLMEmbeddingProvider(EmbeddingProvider):
    """
    Generates embeddings using an LLM.
    """

    def __init__(self, registry: LLMRegistry, model: str):
        self._registry = registry
        self._model = model

    def embed(self, text: str) -> List[float]:
        response = self._registry.invoke(
            prompt=text,
            config=LLMConfig(model=self._model),
        )
        return response.get("embedding", [])
