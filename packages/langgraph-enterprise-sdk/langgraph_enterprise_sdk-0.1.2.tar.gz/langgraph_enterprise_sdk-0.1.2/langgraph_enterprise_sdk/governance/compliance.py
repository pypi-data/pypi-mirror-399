from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class ComplianceContext:
    """
    Context used for compliance checks.
    """
    jurisdiction: str
    data_classification: str
    actor_role: str


class CompliancePolicy:
    """
    Validates actions against regulatory rules.

    Examples:
    - GDPR
    - SOC2
    - HIPAA
    """

    def validate(self, context: ComplianceContext, action: str) -> None:
        # Example rule:
        if context.jurisdiction == "EU" and action == "export_data":
            raise RuntimeError("Data export restricted under GDPR")
