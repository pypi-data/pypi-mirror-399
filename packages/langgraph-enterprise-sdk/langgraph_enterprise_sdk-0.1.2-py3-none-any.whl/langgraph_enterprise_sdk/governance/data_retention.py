from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class RetentionPolicy:
    """
    Defines how long data may be retained.
    """
    category: str
    retention_period: timedelta


class RetentionEvaluator:
    """
    Evaluates retention policies.

    ZAD:
    - Pure evaluation
    """

    def is_expired(self, age: timedelta, policy: RetentionPolicy) -> bool:
        return age > policy.retention_period
