from dataclasses import dataclass
from typing import Type, Tuple

from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type


@dataclass(frozen=True)
class RetryPolicy:
    """
    Retry policy.

    ZAD:
    - Retries must be safe
    - Nodes must be idempotent
    """

    max_attempts: int = 3
    wait_seconds: float = 0.5
    retry_on: Tuple[Type[Exception], ...] = (Exception,)

    def decorator(self):
        return retry(
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_fixed(self.wait_seconds),
            retry=retry_if_exception_type(self.retry_on),
            reraise=True,
        )
