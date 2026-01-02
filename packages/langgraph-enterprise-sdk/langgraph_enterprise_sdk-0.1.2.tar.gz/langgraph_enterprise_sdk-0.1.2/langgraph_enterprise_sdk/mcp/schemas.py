from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class MCPToolRequest:
    """
    MCP tool invocation request.
    """
    tool_name: str
    arguments: Dict[str, Any]
    request_id: Optional[str] = None


@dataclass(frozen=True)
class MCPToolResponse:
    """
    MCP tool invocation response.
    """
    tool_name: str
    result: Dict[str, Any]
    success: bool
    error: Optional[str] = None
