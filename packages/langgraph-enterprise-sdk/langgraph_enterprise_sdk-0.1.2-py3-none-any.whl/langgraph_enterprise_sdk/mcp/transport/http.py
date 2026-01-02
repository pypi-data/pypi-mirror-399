import httpx

from ..schemas import MCPToolRequest, MCPToolResponse
from ..security import MCPSecurityContext


class HTTPTransport:
    """
    HTTP-based MCP transport.
    """

    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/")

    def send(
        self,
        request: MCPToolRequest,
        security: MCPSecurityContext | None = None,
        timeout: int = 30,
    ) -> MCPToolResponse:
        headers = security.to_headers() if security else {}

        response = httpx.post(
            f"{self._base_url}/tools/{request.tool_name}",
            json={
                "arguments": request.arguments,
                "request_id": request.request_id,
            },
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()

        data = response.json()
        return MCPToolResponse(
            tool_name=request.tool_name,
            result=data.get("result", {}),
            success=data.get("success", True),
            error=data.get("error"),
        )
