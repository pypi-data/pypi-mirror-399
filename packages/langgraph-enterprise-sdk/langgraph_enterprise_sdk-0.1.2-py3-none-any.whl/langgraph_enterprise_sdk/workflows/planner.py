from typing import List

from langgraph_enterprise_sdk.api.state import State


class Planner:
    """
    Planner decides WHAT steps are required.

    Does NOT execute.
    """

    def plan(self, state: State) -> List[str]:
        """
        Return a list of task identifiers.
        """
        # Example deterministic plan
        if state.get("error"):
            return ["diagnose", "remediate", "validate"]
        return ["respond"]
