from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class NodeType:
    """
    Defines a node type in the knowledge graph.
    """
    label: str
    properties: Dict[str, type]


@dataclass(frozen=True)
class RelationType:
    """
    Defines a relationship between node types.
    """
    name: str
    from_type: str
    to_type: str
    properties: Dict[str, type] | None = None
