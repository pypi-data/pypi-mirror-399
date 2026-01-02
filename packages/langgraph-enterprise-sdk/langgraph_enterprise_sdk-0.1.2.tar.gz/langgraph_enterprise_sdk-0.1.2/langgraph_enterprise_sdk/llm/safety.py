class SafetyViolation(RuntimeError):
    pass


class SafetyPolicy:
    """
    Applies safety checks to prompts and responses.
    """

    def validate_prompt(self, prompt: str) -> None:
        if not prompt.strip():
            raise SafetyViolation("Prompt must not be empty")

    def validate_response(self, response: str) -> None:
        if not response.strip():
            raise SafetyViolation("Empty LLM response")
