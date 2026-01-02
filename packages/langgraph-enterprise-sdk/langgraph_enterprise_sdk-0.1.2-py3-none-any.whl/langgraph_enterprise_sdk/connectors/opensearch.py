from typing import Optional

from opensearchpy import OpenSearch


class OpenSearchConnector:
    """
    OpenSearch connector.

    Used by:
    - Vector search
    - Hybrid semantic search
    """

    def __init__(
        self,
        hosts: list[str],
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_ssl: bool = True,
        verify_certs: bool = True,
    ):
        self._hosts = hosts
        self._username = username
        self._password = password
        self._use_ssl = use_ssl
        self._verify_certs = verify_certs
        self._client: Optional[OpenSearch] = None

    def connect(self) -> OpenSearch:
        if self._client is None:
            self._client = OpenSearch(
                hosts=self._hosts,
                http_auth=(self._username, self._password)
                if self._username
                else None,
                use_ssl=self._use_ssl,
                verify_certs=self._verify_certs,
            )
        return self._client

    def health_check(self) -> bool:
        try:
            client = self.connect()
            return client.ping()
        except Exception:
            return False
