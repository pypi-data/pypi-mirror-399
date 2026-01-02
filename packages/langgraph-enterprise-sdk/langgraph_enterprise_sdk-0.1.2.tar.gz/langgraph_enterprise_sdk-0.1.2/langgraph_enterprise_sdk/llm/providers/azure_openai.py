from openai import AzureOpenAI

from ..base import LLM
from ..config import LLMConfig


class AzureOpenAILLM(LLM):
    def __init__(self, client: AzureOpenAI):
        self._client = client

    def invoke(self, prompt: str, config: LLMConfig) -> dict:
        response = self._client.chat.completions.create(
            model=config.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return {"text": response.choices[0].message.content}
