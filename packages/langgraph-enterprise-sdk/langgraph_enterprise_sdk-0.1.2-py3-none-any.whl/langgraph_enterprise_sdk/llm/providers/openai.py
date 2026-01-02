import openai

from ..base import LLM
from ..config import LLMConfig


class OpenAILLM(LLM):
    def __init__(self, api_key: str):
        openai.api_key = api_key

    def invoke(self, prompt: str, config: LLMConfig) -> dict:
        response = openai.ChatCompletion.create(
            model=config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
        return {
            "text": response.choices[0].message["content"],
            "usage": response.usage,
        }
