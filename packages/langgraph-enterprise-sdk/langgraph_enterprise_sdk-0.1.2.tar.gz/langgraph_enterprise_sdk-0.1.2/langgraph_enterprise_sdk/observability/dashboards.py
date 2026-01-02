from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class DashboardLink:
    """
    Represents a dashboard reference.

    Used by operators, not runtime logic.
    """
    name: str
    url: str
    description: str | None = None


class DashboardRegistry:
    """
    Registry of observability dashboards.
    """

    def __init__(self):
        self._dashboards: Dict[str, DashboardLink] = {}

    def register(self, dashboard: DashboardLink) -> None:
        self._dashboards[dashboard.name] = dashboard

    def get(self, name: str) -> DashboardLink:
        if name not in self._dashboards:
            raise KeyError(f"Dashboard '{name}' not found")
        return self._dashboards[name]

    def list_all(self) -> Dict[str, DashboardLink]:
        return dict(self._dashboards)
