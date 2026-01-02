import json
from typing import Any, Dict, Optional

from sqlalchemy import Table, Column, String, JSON, MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.sql import select, insert, delete

from .base import MemoryStore


class PostgresMemoryStore(MemoryStore):
    """
    PostgreSQL-backed key-value memory store.

    Used for:
    - Agent memory
    - Execution checkpoints
    """

    def __init__(self, engine: Engine, table_name: str = "agent_memory"):
        self._engine = engine
        self._metadata = MetaData()

        self._table = Table(
            table_name,
            self._metadata,
            Column("key", String, primary_key=True),
            Column("value", JSON, nullable=False),
        )

        self._metadata.create_all(self._engine)

    def write(self, key: str, value: Dict[str, Any]) -> None:
        with self._engine.begin() as conn:
            conn.execute(
                insert(self._table)
                .values(key=key, value=value)
                .on_conflict_do_update(
                    index_elements=["key"],
                    set_={"value": value},
                )
            )

    def read(self, key: str) -> Optional[Dict[str, Any]]:
        with self._engine.connect() as conn:
            result = conn.execute(
                select(self._table.c.value).where(self._table.c.key == key)
            ).fetchone()
            return result[0] if result else None

    def delete(self, key: str) -> None:
        with self._engine.begin() as conn:
            conn.execute(
                delete(self._table).where(self._table.c.key == key)
            )
