from typing import Dict

from langgraph_enterprise_sdk.api.state import State
from .agent import Agent
from .planner import Planner
from .delegation import Delegator
from .supervisor import Supervisor
from .base import AgentWorkflow


class MultiAgentWorkflow(AgentWorkflow):
    """
    Multi-agent workflow.

    Planner + Supervisor + Agents.
    """

    def __init__(
        self,
        name: str,
        planner: Planner,
        agents: Dict[str, Agent],
    ):
        self.name = name
        self._supervisor = Supervisor(
            planner=planner,
            delegator=Delegator(agents),
        )

    def run(self, state: State) -> State:
        return self._supervisor.run(state)
