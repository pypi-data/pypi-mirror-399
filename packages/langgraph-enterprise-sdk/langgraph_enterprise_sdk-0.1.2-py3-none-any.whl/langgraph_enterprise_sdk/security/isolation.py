from dataclasses import dataclass


@dataclass(frozen=True)
class IsolationContext:
    """
    Isolation boundaries.
    """
    tenant_id: str
    execution_id: str


class IsolationPolicy:
    """
    Enforces tenant & execution isolation.
    """

    def validate(self, context: IsolationContext, target_tenant: str) -> None:
        if context.tenant_id != target_tenant:
            raise RuntimeError("Cross-tenant access denied")
