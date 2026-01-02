from typing import Optional

from opentelemetry import trace
from opentelemetry.trace import Tracer


class TracingProvider:
    """
    OpenTelemetry tracing provider.

    Tracing is optional and non-intrusive.
    """

    def __init__(self, service_name: str = "langgraph-sdk"):
        self._tracer: Tracer = trace.get_tracer(service_name)

    def start_span(self, name: str):
        """
        Start a new tracing span.
        """
        return self._tracer.start_as_current_span(name)
