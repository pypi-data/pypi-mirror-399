from typing import Any, Dict, List, Optional

from a2a.client.discovery import discover_agent


from .security import A2ASecurityContext


class A2AAgentDiscovery:
    """
    Thin wrapper around a2a-python-sdk discovery client.

    Responsibility:
    - Discover agents by capability
    - Return raw agent metadata
    """

    def __init__(self, registry_url: str):
        self._client = discover_agent(base_url=registry_url)

    def discover(
        self,
        capability: str,
        security: Optional[A2ASecurityContext] = None,
    ) -> List[Dict[str, Any]]:
        return self._client.find_agents(
            capability=capability,
            headers=security.to_headers() if security else None,
        )
