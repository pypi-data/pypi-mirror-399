from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class A2ASecurityContext:
    """
    Security context passed through to a2a-python-sdk.

    This class only carries metadata.
    Authentication, signing, and validation
    are handled entirely by the A2A SDK.
    """
    access_token: Optional[str] = None
    tenant_id: Optional[str] = None
    actor: Optional[str] = None

    def to_headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}

        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        if self.tenant_id:
            headers["X-Tenant-ID"] = self.tenant_id
        if self.actor:
            headers["X-Actor"] = self.actor

        return headers
