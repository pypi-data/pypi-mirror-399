from llama_cpp import Llama

from ..base import LLM
from ..config import LLMConfig


class LlamaCppLLM(LLM):
    def __init__(self, model_path: str):
        self._llm = Llama(model_path=model_path)

    def invoke(self, prompt: str, config: LLMConfig) -> dict:
        output = self._llm(prompt, max_tokens=config.max_tokens)
        return {"text": output["choices"][0]["text"]}
