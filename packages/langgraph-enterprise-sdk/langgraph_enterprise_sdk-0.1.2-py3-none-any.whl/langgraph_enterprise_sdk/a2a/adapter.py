from typing import Any, Callable, Dict, Optional

from a2a.schema import message

from .delegation import A2ADelegator
from .discovery import A2AAgentDiscovery
from .routing import A2ARoutingStrategy
from .security import A2ASecurityContext


class A2AAdapter:
    """
    LangGraph → A2A adapter.

    Designed to be:
    - Stateless
    - Deterministic
    - Safe for retries
    """

    def __init__(
        self,
        registry_url: str,
        routing_strategy: Optional[A2ARoutingStrategy] = None,
    ):
        self._discovery = A2AAgentDiscovery(registry_url)
        self._routing = routing_strategy or A2ARoutingStrategy()

    def invoke(
        self,
        *,
        capability: str,
        state: Dict[str, Any],
        build_message: Callable[[Dict[str, Any]], message],
        parse_response: Callable[[Dict[str, Any]], Dict[str, Any]],
        security: Optional[A2ASecurityContext] = None,
    ) -> Dict[str, Any]:
        """
        Invoke a remote A2A agent from a LangGraph node.

        Flow:
        1. Discover agents
        2. Select agent
        3. Build A2A message
        4. Delegate
        5. Parse response
        """

        agents = self._discovery.discover(capability, security)
        agent = self._routing.select(agents)

        delegator = A2ADelegator(agent["endpoint"])

        message = build_message(state)
        response = delegator.send(message, security=security)

        return parse_response(response)
