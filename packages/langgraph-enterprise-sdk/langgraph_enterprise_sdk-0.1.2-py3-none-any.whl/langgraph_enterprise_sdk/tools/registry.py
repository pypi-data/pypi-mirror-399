from typing import Dict

from .base import Tool


class ToolRegistry:
    """
    Central tool registry.

    Ensures:
    - Explicit registration
    - No ad-hoc tool execution
    """

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise RuntimeError(f"Tool '{tool.name}' already registered")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found")
        return self._tools[name]

    def list(self) -> Dict[str, Tool]:
        return dict(self._tools)
