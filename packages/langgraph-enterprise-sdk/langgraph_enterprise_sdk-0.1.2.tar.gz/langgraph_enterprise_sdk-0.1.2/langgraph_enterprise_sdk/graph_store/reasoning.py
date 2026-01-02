from typing import Dict, Any, List

from .base import KnowledgeGraph
from .cypher import CypherBuilder


class KnowledgeReasoner:
    """
    Performs deterministic reasoning over the knowledge graph.

    Examples:
    - Find root cause
    - Identify remediation steps
    - Trace dependencies

    TOON:
    - Used by orchestration nodes
    - Does not decide actions
    """

    def __init__(self, graph: KnowledgeGraph):
        self._graph = graph

    def find_related(
        self,
        node_label: str,
        relation: str,
        target_label: str,
    ) -> List[Dict[str, Any]]:
        query = CypherBuilder.match_relation(
            source_label=node_label,
            relation=relation,
            target_label=target_label,
        )
        return self._graph.query(query)

    def lookup(
        self,
        label: str,
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        query = CypherBuilder.match_node(label, filters)
        return self._graph.query(query, filters)
