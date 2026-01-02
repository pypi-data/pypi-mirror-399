from abc import ABC
from gllm_datastore.graph_data_store.graph_rag_data_store import BaseGraphRAGDataStore as BaseGraphRAGDataStore
from llama_index.core.graph_stores.types import PropertyGraphStore
from typing import Any

class LlamaIndexGraphRAGDataStore(PropertyGraphStore, BaseGraphRAGDataStore, ABC):
    """Abstract base class for a LlamaIndex graph RAG data store."""
    async def query(self, query: str, **kwargs: Any) -> Any:
        """Query the graph RAG data store.

        Args:
            query (str): The query to be executed.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            Any: The result of the query.
        """
