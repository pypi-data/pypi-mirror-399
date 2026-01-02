from fastapi import APIRouter, Depends, FastAPI

from .auth import get_identity
from .tenancy import get_tenant_context
from langgraph_enterprise_sdk.security.authn import Identity
from langgraph_enterprise_sdk.security.isolation import IsolationContext


router = APIRouter()


@router.get("/health")
def health():
    """
    Health check endpoint.
    """
    return {"status": "ok"}


@router.get("/whoami")
def whoami(
    identity: Identity = Depends(get_identity),
    tenancy: IsolationContext = Depends(get_tenant_context),
):
    """
    Debug endpoint for identity & tenancy.
    """
    return {
        "subject": identity.subject,
        "roles": identity.roles,
        "tenant": tenancy.tenant_id,
    }


def register_routes(app: FastAPI) -> None:
    app.include_router(router)
