from typing import Dict

from langgraph_enterprise_sdk.api.state import State
from .agent import Agent


class Delegator:
    """
    Delegates tasks to agents.

    Used by supervisors.
    """

    def __init__(self, agents: Dict[str, Agent]):
        self._agents = agents

    def delegate(self, task: str, state: State) -> State:
        if task not in self._agents:
            raise RuntimeError(f"No agent registered for task '{task}'")
        agent = self._agents[task]
        return agent.run(state)
