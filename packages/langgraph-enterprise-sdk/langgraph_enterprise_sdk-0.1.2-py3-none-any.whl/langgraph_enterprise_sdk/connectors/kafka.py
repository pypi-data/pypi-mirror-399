from typing import Optional

from kafka import KafkaProducer, KafkaConsumer


class KafkaConnector:
    """
    Kafka connector.

    Used by:
    - Event streaming
    - Async tool invocation
    - Audit pipelines

    ZAD:
    - Produces / consumes only when explicitly called
    """

    def __init__(self, bootstrap_servers: list[str]):
        self._bootstrap_servers = bootstrap_servers
        self._producer: Optional[KafkaProducer] = None

    def producer(self) -> KafkaProducer:
        if self._producer is None:
            self._producer = KafkaProducer(
                bootstrap_servers=self._bootstrap_servers
            )
        return self._producer

    def consumer(
        self,
        topic: str,
        group_id: str,
        auto_offset_reset: str = "latest",
    ) -> KafkaConsumer:
        return KafkaConsumer(
            topic,
            bootstrap_servers=self._bootstrap_servers,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
        )

    def health_check(self) -> bool:
        try:
            producer = self.producer()
            return producer.bootstrap_connected()
        except Exception:
            return False
