from typing import Dict, List

from .edges import Edge
from .node import Node
from .state import State


class Graph:
    """
    Directed graph definition.

    Responsibilities:
    - Node registration
    - Edge definition
    - No execution logic
    """

    def __init__(self):
        self._nodes: Dict[str, Node] = {}
        self._edges: List[Edge] = []

    def add_node(self, node: Node) -> None:
        if node.name in self._nodes:
            raise ValueError(f"Node '{node.name}' already exists")
        self._nodes[node.name] = node

    def add_edge(self, edge: Edge) -> None:
        if edge.source not in self._nodes:
            raise ValueError(f"Unknown source node '{edge.source}'")
        if edge.target not in self._nodes:
            raise ValueError(f"Unknown target node '{edge.target}'")
        self._edges.append(edge)

    def get_node(self, name: str) -> Node:
        return self._nodes[name]

    def get_next_nodes(self, current: str, state: State) -> List[str]:
        return [
            edge.target
            for edge in self._edges
            if edge.source == current and edge.is_active(state)
        ]

    def entrypoint(self) -> str:
        if not self._nodes:
            raise RuntimeError("Graph has no nodes")
        return next(iter(self._nodes))
