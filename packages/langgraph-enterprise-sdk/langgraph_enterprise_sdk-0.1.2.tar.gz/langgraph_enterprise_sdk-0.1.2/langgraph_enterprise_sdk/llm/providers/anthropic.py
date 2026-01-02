from anthropic import Anthropic

from ..base import LLM
from ..config import LLMConfig


class AnthropicLLM(LLM):
    def __init__(self, api_key: str):
        self._client = Anthropic(api_key=api_key)

    def invoke(self, prompt: str, config: LLMConfig) -> dict:
        msg = self._client.messages.create(
            model=config.model,
            max_tokens=config.max_tokens or 1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return {"text": msg.content[0].text}
