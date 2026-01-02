import json
from typing import Any

from langgraph_enterprise_sdk.api.state import State


class StateSerializer:
    """
    Serializes and deserializes State objects.

    ZAD:
    - Deterministic
    - Lossless
    """

    @staticmethod
    def serialize(state: State) -> str:
        return json.dumps(state.to_dict(), sort_keys=True)

    @staticmethod
    def deserialize(payload: str) -> State:
        data = json.loads(payload)
        return State(data)
