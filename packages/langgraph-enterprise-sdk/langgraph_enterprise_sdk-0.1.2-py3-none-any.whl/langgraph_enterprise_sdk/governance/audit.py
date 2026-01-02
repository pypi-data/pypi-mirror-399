from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass(frozen=True)
class AuditEvent:
    """
    Immutable audit event.

    Safe for:
    - Storage
    - Streaming
    - Compliance review
    """
    event_type: str
    actor: str
    resource: str
    timestamp: datetime
    metadata: Dict[str, Any]


class AuditLogger:
    """
    Audit logger interface.

    Implementations may:
    - Send to Kafka
    - Store in DB
    - Write to SIEM
    """

    def log(self, event: AuditEvent) -> None:
        # Intentionally no-op.
        # Concrete implementations live in infra layer.
        pass
