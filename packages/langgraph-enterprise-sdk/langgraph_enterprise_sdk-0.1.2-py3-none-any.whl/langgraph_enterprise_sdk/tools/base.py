from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class ToolContext:
    """
    Context provided to tools at execution time.

    Includes:
    - Actor identity
    - Tenant
    - Execution metadata
    """
    actor: str
    tenant_id: str
    execution_id: str


class Tool(ABC):
    """
    Abstract Tool interface.

    TOON:
    - Tools execute actions
    - Nodes decide WHEN to call tools
    """

    name: str
    description: str

    @abstractmethod
    def execute(
        self,
        inputs: Dict[str, Any],
        context: ToolContext,
    ) -> Dict[str, Any]:
        """
        Execute the tool.

        Side effects are allowed here.
        """
        raise NotImplementedError
