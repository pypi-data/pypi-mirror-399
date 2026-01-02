from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


class PostgresConnector:
    """
    PostgreSQL connector.

    ZAD:
    - No implicit transactions
    - No global engine
    - Caller controls lifecycle
    """

    def __init__(
        self,
        dsn: str,
        pool_size: int = 5,
        max_overflow: int = 10,
        echo: bool = False,
    ):
        self._dsn = dsn
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._echo = echo
        self._engine: Optional[Engine] = None

    def connect(self) -> Engine:
        if self._engine is None:
            self._engine = create_engine(
                self._dsn,
                pool_size=self._pool_size,
                max_overflow=self._max_overflow,
                echo=self._echo,
                future=True,
            )
        return self._engine

    def health_check(self) -> bool:
        try:
            engine = self.connect()
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:
            return False
