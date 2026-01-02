import ollama

from ..base import LLM
from ..config import LLMConfig


class OllamaLLM(LLM):
    def invoke(self, prompt: str, config: LLMConfig) -> dict:
        result = ollama.generate(
            model=config.model,
            prompt=prompt,
        )
        return {"text": result["response"]}
