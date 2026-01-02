from typing import Any, Dict, List

from neo4j import Driver

from .base import KnowledgeGraph


class Neo4jKnowledgeGraph(KnowledgeGraph):
    """
    Neo4j-backed Knowledge Graph.

    ZAD:
    - Read-only by default
    - No mutation helpers here
    """

    def __init__(self, driver: Driver):
        self._driver = driver

    def query(self, query: str, params: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        with self._driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]

    def health_check(self) -> bool:
        try:
            with self._driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception:
            return False
