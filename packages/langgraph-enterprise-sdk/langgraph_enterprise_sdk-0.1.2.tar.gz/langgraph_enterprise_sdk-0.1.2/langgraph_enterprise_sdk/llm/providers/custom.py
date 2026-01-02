from ..base import LLM
from ..config import LLMConfig


class CustomLLM(LLM):
    """
    Example custom / on-prem LLM.
    """

    def invoke(self, prompt: str, config: LLMConfig) -> dict:
        return {"text": f"[CUSTOM MODEL] {prompt}"}
