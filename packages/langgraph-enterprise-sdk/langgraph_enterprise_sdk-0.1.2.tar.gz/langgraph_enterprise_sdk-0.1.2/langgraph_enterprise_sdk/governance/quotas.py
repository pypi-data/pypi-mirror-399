from dataclasses import dataclass


@dataclass(frozen=True)
class Quota:
    """
    Usage quota definition.
    """
    name: str
    limit: int


class QuotaPolicy:
    """
    Enforces usage quotas.

    Used for:
    - Agent executions
    - Tool calls
    - LLM invocations
    """

    def check(self, used: int, quota: Quota) -> None:
        if used >= quota.limit:
            raise RuntimeError(
                f"Quota exceeded for '{quota.name}': {quota.limit}"
            )
