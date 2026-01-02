from dataclasses import dataclass
from typing import Dict, Set


@dataclass(frozen=True)
class Role:
    name: str
    permissions: Set[str]


class RBACRegistry:
    """
    Role → Permission mapping.
    """

    def __init__(self):
        self._roles: Dict[str, Role] = {}

    def register_role(self, role: Role) -> None:
        self._roles[role.name] = role

    def check(self, role_name: str, permission: str) -> bool:
        role = self._roles.get(role_name)
        if not role:
            return False
        return permission in role.permissions
