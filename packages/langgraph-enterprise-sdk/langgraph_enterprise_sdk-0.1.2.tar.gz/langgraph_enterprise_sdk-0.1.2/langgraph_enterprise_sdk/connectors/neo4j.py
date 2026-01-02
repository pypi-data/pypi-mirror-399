from typing import Optional

from neo4j import GraphDatabase, Driver


class Neo4jConnector:
    """
    Neo4j connector.

    Used by:
    - Knowledge Graph
    - SOP / Runbook reasoning

    TOON:
    - No traversal logic here
    """

    def __init__(
        self,
        uri: str,
        username: str,
        password: str,
    ):
        self._uri = uri
        self._username = username
        self._password = password
        self._driver: Optional[Driver] = None

    def connect(self) -> Driver:
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self._uri,
                auth=(self._username, self._password),
            )
        return self._driver

    def close(self) -> None:
        if self._driver:
            self._driver.close()
            self._driver = None

    def health_check(self) -> bool:
        try:
            driver = self.connect()
            with driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception:
            return False
