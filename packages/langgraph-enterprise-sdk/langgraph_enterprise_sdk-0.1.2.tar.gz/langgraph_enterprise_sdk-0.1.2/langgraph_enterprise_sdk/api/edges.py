from typing import Callable, Optional

from .state import State


class Edge:
    """
    Directed edge between nodes.

    ZAD rules:
    - Condition must be a pure function of State
    - No side effects
    """

    def __init__(
        self,
        source: str,
        target: str,
        condition: Optional[Callable[[State], bool]] = None,
    ):
        self.source = source
        self.target = target
        self.condition = condition

    def is_active(self, state: State) -> bool:
        if self.condition is None:
            return True

        try:
            return bool(self.condition(state))
        except Exception as exc:
            raise RuntimeError(
                f"Edge condition must be pure and side-effect free: {exc}"
            )
