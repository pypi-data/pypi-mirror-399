from typing import Dict, Any

from .base import Tool, ToolContext


class SandboxViolation(RuntimeError):
    pass


class ToolSandbox:
    """
    Enforces sandbox constraints around tool execution.

    Examples:
    - Disable filesystem
    - Block network access
    - Limit execution time
    """

    def __init__(
        self,
        *,
        allow_network: bool = False,
        allow_filesystem: bool = False,
    ):
        self._allow_network = allow_network
        self._allow_filesystem = allow_filesystem

    def run(
        self,
        tool: Tool,
        inputs: Dict[str, Any],
        context: ToolContext,
    ) -> Dict[str, Any]:
        # Placeholder enforcement hooks
        if not self._allow_network and inputs.get("uses_network"):
            raise SandboxViolation("Network access is not allowed")

        if not self._allow_filesystem and inputs.get("uses_filesystem"):
            raise SandboxViolation("Filesystem access is not allowed")

        return tool.execute(inputs, context)
