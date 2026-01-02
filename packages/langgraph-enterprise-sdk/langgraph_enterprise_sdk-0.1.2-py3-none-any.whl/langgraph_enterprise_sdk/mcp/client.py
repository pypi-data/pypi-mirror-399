from typing import Optional

from .schemas import MCPToolRequest, MCPToolResponse
from .security import MCPSecurityContext


class MCPClient:
    """
    MCP client abstraction.

    Wraps a transport and exposes tool invocation.
    """

    def __init__(self, transport):
        self._transport = transport

    def invoke(
        self,
        tool_name: str,
        arguments: dict,
        *,
        request_id: Optional[str] = None,
        security: Optional[MCPSecurityContext] = None,
    ) -> MCPToolResponse:
        request = MCPToolRequest(
            tool_name=tool_name,
            arguments=arguments,
            request_id=request_id,
        )

        # Transport may be sync or async
        if hasattr(self._transport, "send"):
            return self._transport.send(request, security)

        raise RuntimeError("Unsupported MCP transport")
