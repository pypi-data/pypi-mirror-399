from typing import Dict, Any

from .registry import ToolRegistry
from .sandbox import ToolSandbox
from .base import ToolContext


class ToolAdapter:
    """
    Adapter used by orchestration nodes.

    This is the ONLY approved way for nodes to invoke tools.
    """

    def __init__(
        self,
        registry: ToolRegistry,
        sandbox: ToolSandbox,
        context: ToolContext,
    ):
        self._registry = registry
        self._sandbox = sandbox
        self._context = context

    def call(self, tool_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        tool = self._registry.get(tool_name)
        return self._sandbox.run(tool, inputs, self._context)
