from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.engine import Engine

from ..base import VectorMemoryStore


class PGVectorStore(VectorMemoryStore):
    """
    pgvector-backed vector store.
    """

    def __init__(self, engine: Engine, table_name: str = "vector_memory"):
        self._engine = engine
        self._table = table_name

    def upsert(self, id: str, embedding: List[float], metadata: Dict[str, Any]) -> None:
        with self._engine.begin() as conn:
            conn.execute(
                text(f"""
                INSERT INTO {self._table} (id, embedding, metadata)
                VALUES (:id, :embedding, :metadata)
                ON CONFLICT (id)
                DO UPDATE SET embedding = :embedding, metadata = :metadata
                """),
                {
                    "id": id,
                    "embedding": embedding,
                    "metadata": metadata,
                },
            )

    def search(self, embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        with self._engine.connect() as conn:
            result = conn.execute(
                text(f"""
                SELECT id, metadata
                FROM {self._table}
                ORDER BY embedding <-> :embedding
                LIMIT :k
                """),
                {
                    "embedding": embedding,
                    "k": top_k,
                },
            )
            return [dict(row) for row in result]
