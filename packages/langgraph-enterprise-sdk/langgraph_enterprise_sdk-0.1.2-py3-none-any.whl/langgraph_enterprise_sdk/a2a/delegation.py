from typing import Any, Dict, Optional

from a2a.client import agent_client
from a2a.schema import message

from .security import A2ASecurityContext


class A2ADelegator:
    """
    Delegates a task to a remote A2A agent.

    This class:
    - Sends a structured A2A message
    - Returns the raw agent response
    """

    def __init__(self, agent_endpoint: str):
        self._client = agent_client(base_url=agent_endpoint)

    def send(
        self,
        message: message,
        security: Optional[A2ASecurityContext] = None,
        timeout: int = 60,
    ) -> Dict[str, Any]:
        return self._client.send_message(
            message=message,
            headers=security.to_headers() if security else None,
            timeout=timeout,
        )
