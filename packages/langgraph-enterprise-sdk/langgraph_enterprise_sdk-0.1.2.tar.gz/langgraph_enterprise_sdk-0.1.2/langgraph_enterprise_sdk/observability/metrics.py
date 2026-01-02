from typing import Optional

from prometheus_client import Counter, Histogram


class MetricsRegistry:
    """
    Central metrics registry.

    Metrics are passive and side-effect free.
    """

    def __init__(self, namespace: str = "langgraph_sdk"):
        self.execution_count = Counter(
            f"{namespace}_executions_total",
            "Total number of graph executions",
        )

        self.execution_errors = Counter(
            f"{namespace}_execution_errors_total",
            "Total number of execution errors",
        )

        self.node_latency = Histogram(
            f"{namespace}_node_latency_seconds",
            "Latency per node execution",
        )

    def inc_execution(self) -> None:
        self.execution_count.inc()

    def inc_error(self) -> None:
        self.execution_errors.inc()

    def observe_node_latency(self, seconds: float) -> None:
        self.node_latency.observe(seconds)
