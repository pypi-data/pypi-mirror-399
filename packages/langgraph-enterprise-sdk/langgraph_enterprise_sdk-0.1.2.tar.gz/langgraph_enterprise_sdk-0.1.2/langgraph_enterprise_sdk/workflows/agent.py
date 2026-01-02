from typing import Callable

from langgraph_enterprise_sdk.api.state import State
from .base import AgentWorkflow


class Agent(AgentWorkflow):
    """
    Single agent workflow.

    Wraps a reasoning/orchestration function.
    """

    def __init__(self, name: str, handler: Callable[[State], State]):
        self.name = name
        self._handler = handler

    def run(self, state: State) -> State:
        return self._handler(state)
