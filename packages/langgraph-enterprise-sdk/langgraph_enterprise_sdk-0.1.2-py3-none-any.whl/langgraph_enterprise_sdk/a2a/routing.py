from typing import Any, Dict, List


class A2ARoutingStrategy:
    """
    Agent selection strategy.

    This is intentionally simple and deterministic.
    Advanced strategies (latency, region, load)
    can be added later without changing adapters.
    """

    def select(self, agents: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not agents:
            raise RuntimeError("No A2A agents available for routing")

        # Default: first healthy agent
        return agents[0]
