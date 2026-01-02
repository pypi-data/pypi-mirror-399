from abc import ABC, abstractmethod
from typing import Any, Dict

from langgraph_enterprise_sdk.api.state import State


class AgentWorkflow(ABC):
    """
    Base workflow interface.

    TOON:
    - Workflow orchestrates agents
    - Execution happens elsewhere
    """

    name: str

    @abstractmethod
    def run(self, state: State) -> State:
        """
        Orchestrate agent execution.
        """
        raise NotImplementedError
