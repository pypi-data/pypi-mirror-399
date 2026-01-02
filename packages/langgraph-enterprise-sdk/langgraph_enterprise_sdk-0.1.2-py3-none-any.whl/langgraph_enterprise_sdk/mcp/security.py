from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class MCPSecurityContext:
    """
    Security metadata propagated to MCP servers.
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
