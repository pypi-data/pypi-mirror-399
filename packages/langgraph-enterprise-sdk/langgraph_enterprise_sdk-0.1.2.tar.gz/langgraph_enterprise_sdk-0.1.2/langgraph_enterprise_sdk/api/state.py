from typing import Any, Dict


class State:
    """
    Immutable-by-convention state container.

    ZAD rules:
    - No in-place mutation
    - Serializable
    - Deterministic updates only
    """

    def __init__(self, data: Dict[str, Any]):
        if not isinstance(data, dict):
            raise TypeError("State must be initialized with a dict")
        self._data = dict(data)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)

    def update(self, updates: Dict[str, Any]) -> "State":
        if not isinstance(updates, dict):
            raise TypeError("State updates must be a dict")

        new_data = {**self._data, **updates}
        return State(new_data)

    def __repr__(self) -> str:
        return f"State({self._data})"
