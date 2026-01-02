import json
import subprocess

from ..schemas import MCPToolRequest, MCPToolResponse


class StdioTransport:
    """
    stdio-based MCP transport.

    Used for:
    - Local tools
    - Air-gapped environments
    """

    def __init__(self, command: list[str]):
        self._command = command

    def send(self, request: MCPToolRequest) -> MCPToolResponse:
        process = subprocess.Popen(
            self._command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        payload = json.dumps({
            "tool": request.tool_name,
            "arguments": request.arguments,
            "request_id": request.request_id,
        })

        stdout, stderr = process.communicate(payload)

        if process.returncode != 0:
            return MCPToolResponse(
                tool_name=request.tool_name,
                result={},
                success=False,
                error=stderr,
            )

        data = json.loads(stdout)
        return MCPToolResponse(
            tool_name=request.tool_name,
            result=data.get("result", {}),
            success=data.get("success", True),
            error=data.get("error"),
        )
