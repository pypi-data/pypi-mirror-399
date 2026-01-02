from typing import Any, Dict, List

from opensearchpy import OpenSearch

from ..base import VectorMemoryStore


class OpenSearchVectorStore(VectorMemoryStore):
    """
    OpenSearch-backed vector memory store.
    """

    def __init__(self, client: OpenSearch, index_name: str):
        self._client = client
        self._index = index_name

    def upsert(self, id: str, embedding: List[float], metadata: Dict[str, Any]) -> None:
        self._client.index(
            index=self._index,
            id=id,
            body={
                "embedding": embedding,
                "metadata": metadata,
            },
        )

    def search(self, embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        query = {
            "size": top_k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": embedding,
                        "k": top_k,
                    }
                }
            }
        }
        result = self._client.search(index=self._index, body=query)
        return [
            hit["_source"]["metadata"]
            for hit in result["hits"]["hits"]
        ]
