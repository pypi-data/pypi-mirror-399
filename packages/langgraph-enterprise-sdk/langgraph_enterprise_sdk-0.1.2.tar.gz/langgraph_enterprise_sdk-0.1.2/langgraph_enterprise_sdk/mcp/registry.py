from typing import Dict

from .client import MCPClient


class MCPRegistry:
    """
    Registry for MCP clients.

    Allows:
    - Multiple MCP servers
    - Tool-to-server mapping
    """

    def __init__(self):
        self._clients: Dict[str, MCPClient] = {}

    def register(self, tool_name: str, client: MCPClient) -> None:
        self._clients[tool_name] = client

    def get(self, tool_name: str) -> MCPClient:
        if tool_name not in self._clients:
            raise KeyError(f"No MCP client registered for '{tool_name}'")
        return self._clients[tool_name]
