from fastapi import Header

from langgraph_enterprise_sdk.security.isolation import IsolationContext


def get_tenant_context(
    tenant_id: str | None = Header(default=None),
) -> IsolationContext:
    """
    Resolve tenant isolation context.
    """
    if not tenant_id:
        raise RuntimeError("Missing tenant header")

    return IsolationContext(
        tenant_id=tenant_id,
        execution_id="N/A",
    )
