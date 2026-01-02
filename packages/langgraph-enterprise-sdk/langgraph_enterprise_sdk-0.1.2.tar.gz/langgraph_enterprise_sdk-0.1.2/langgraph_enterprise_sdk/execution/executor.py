from typing import Optional

from langgraph_enterprise_sdk.api.config import RunnableConfig
from langgraph_enterprise_sdk.api.graph import Graph
from langgraph_enterprise_sdk.api.state import State
from langgraph_enterprise_sdk.errors import (
    ExecutionError,
    MaxStepsExceededError,
)

from .cancellation import CancellationToken
from .lifecycle import ExecutionLifecycle
from .retries import RetryPolicy
from .scheduler import DeterministicScheduler


class GraphExecutor:
    """
    Core execution engine.

    Guarantees:
    - TOON-compliant orchestration
    - ZAD-compliant state transitions
    - Deterministic execution
    """

    def __init__(
        self,
        graph: Graph,
        *,
        retry_policy: Optional[RetryPolicy] = None,
        lifecycle: Optional[ExecutionLifecycle] = None,
        scheduler: Optional[DeterministicScheduler] = None,
    ):
        self._graph = graph
        self._retry_policy = retry_policy
        self._lifecycle = lifecycle or ExecutionLifecycle()
        self._scheduler = scheduler or DeterministicScheduler()

    def execute(
        self,
        initial_state: State,
        *,
        config: Optional[RunnableConfig] = None,
        cancellation_token: Optional[CancellationToken] = None,
    ) -> State:
        if not isinstance(initial_state, State):
            raise TypeError("Initial input must be a State")

        cancellation_token = cancellation_token or CancellationToken()
        max_steps = config.max_steps if config else None

        current_node = self._graph.entrypoint()
        current_state = initial_state
        steps = 0

        if self._lifecycle.on_start:
            self._lifecycle.on_start(current_state)

        try:
            while True:
                cancellation_token.raise_if_cancelled()

                if max_steps is not None and steps >= max_steps:
                    raise MaxStepsExceededError(max_steps)

                node = self._graph.get_node(current_node)

                def run_node():
                    return node.run(current_state)

                if self._retry_policy:
                    run_node = self._retry_policy.decorator()(run_node)

                next_state = run_node()

                if self._lifecycle.on_step:
                    self._lifecycle.on_step(current_node, next_state)

                steps += 1
                current_state = next_state

                next_nodes = self._graph.get_next_nodes(
                    current_node, current_state
                )

                if not next_nodes:
                    if self._lifecycle.on_complete:
                        self._lifecycle.on_complete(current_state)
                    return current_state

                ordered = self._scheduler.select_next(next_nodes)
                current_node = ordered[0]

        except Exception as exc:
            if self._lifecycle.on_error:
                self._lifecycle.on_error(exc)

            if isinstance(exc, ExecutionError):
                raise

            raise ExecutionError(
                f"Execution failed at node '{current_node}'",
                node=current_node,
            ) from exc
