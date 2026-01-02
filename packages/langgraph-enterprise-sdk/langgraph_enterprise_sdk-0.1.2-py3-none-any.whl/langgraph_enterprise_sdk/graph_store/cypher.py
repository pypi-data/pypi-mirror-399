from typing import Dict, Any


class CypherBuilder:
    """
    Builds safe Cypher queries.

    ZAD:
    - No execution
    - No driver dependency
    """

    @staticmethod
    def match_node(label: str, filters: Dict[str, Any] | None = None) -> str:
        if not filters:
            return f"MATCH (n:{label}) RETURN n"

        conditions = " AND ".join(
            [f"n.{k} = ${k}" for k in filters.keys()]
        )
        return f"MATCH (n:{label}) WHERE {conditions} RETURN n"

    @staticmethod
    def match_relation(
        source_label: str,
        relation: str,
        target_label: str,
    ) -> str:
        return (
            f"MATCH (a:{source_label})"
            f"-[r:{relation}]->"
            f"(b:{target_label}) "
            f"RETURN a, r, b"
        )
