from typing import Dict, Any

from .client import MCPClient
from .registry import MCPRegistry
from .security import MCPSecurityContext


class MCPAdapter:
    """
    Adapter for TOON orchestration nodes.

    Used inside Node orchestration logic.
    """

    def __init__(
        self,
        registry: MCPRegistry,
        security: MCPSecurityContext | None = None,
    ):
        self._registry = registry
        self._security = security

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        client = self._registry.get(tool_name)
        response = client.invoke(
            tool_name=tool_name,
            arguments=arguments,
            security=self._security,
        )

        if not response.success:
            raise RuntimeError(response.error)

        return response.result
