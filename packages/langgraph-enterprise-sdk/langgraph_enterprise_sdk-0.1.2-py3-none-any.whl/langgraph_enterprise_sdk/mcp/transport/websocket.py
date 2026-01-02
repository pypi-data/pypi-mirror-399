import json
import websockets

from ..schemas import MCPToolRequest, MCPToolResponse
from ..security import MCPSecurityContext


class WebSocketTransport:
    """
    WebSocket-based MCP transport.
    """

    def __init__(self, url: str):
        self._url = url

    async def send(
        self,
        request: MCPToolRequest,
        security: MCPSecurityContext | None = None,
    ) -> MCPToolResponse:
        headers = security.to_headers() if security else {}

        async with websockets.connect(self._url, extra_headers=headers) as ws:
            await ws.send(json.dumps({
                "tool": request.tool_name,
                "arguments": request.arguments,
                "request_id": request.request_id,
            }))
            raw = await ws.recv()
            data = json.loads(raw)

            return MCPToolResponse(
                tool_name=request.tool_name,
                result=data.get("result", {}),
                success=data.get("success", True),
                error=data.get("error"),
            )
