from typing import List

from langgraph_enterprise_sdk.api.state import State
from .planner import Planner
from .delegation import Delegator


class Supervisor:
    """
    Supervisor controls the workflow.

    Responsibilities:
    - Invoke planner
    - Delegate tasks
    - Enforce order
    """

    def __init__(self, planner: Planner, delegator: Delegator):
        self._planner = planner
        self._delegator = delegator

    def run(self, state: State) -> State:
        tasks: List[str] = self._planner.plan(state)

        current_state = state
        for task in tasks:
            current_state = self._delegator.delegate(task, current_state)

        return current_state
