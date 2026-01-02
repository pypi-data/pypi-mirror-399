from typing import Protocol

from .state import State


class OrchestrationFn(Protocol):
    """
    TOON contract.

    Rules:
    - No side effects
    - No I/O
    - Delegates to tools / agents
    - Returns a NEW State
    """
    def __call__(self, state: State) -> State: ...


class Node:
    """
    Tool-Oriented Orchestration Node (TOON).

    A node:
    - Orchestrates tools/agents
    - Does NOT execute business logic
    - Does NOT perform I/O
    """

    def __init__(self, name: str, orchestrator: OrchestrationFn):
        if not callable(orchestrator):
            raise TypeError("Node orchestrator must be callable")

        self.name = name
        self._orchestrator = orchestrator

    def run(self, state: State) -> State:
        next_state = self._orchestrator(state)

        if not isinstance(next_state, State):
            raise TypeError(
                f"Node '{self.name}' must return a State instance (ZAD violation)"
            )

        return next_state

    def __repr__(self) -> str:
        return f"Node(name={self.name})"
