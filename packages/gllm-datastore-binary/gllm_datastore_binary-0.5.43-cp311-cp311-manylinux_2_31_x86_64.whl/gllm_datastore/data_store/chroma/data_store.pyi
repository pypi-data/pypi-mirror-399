from _typeshed import Incomplete
from enum import StrEnum
from gllm_datastore.core.filters.schema import FilterClause as FilterClause, QueryFilter as QueryFilter
from gllm_datastore.data_store.base import BaseDataStore as BaseDataStore, CapabilityType as CapabilityType
from gllm_datastore.data_store.chroma._chroma_import import safe_import_chromadb as safe_import_chromadb
from gllm_datastore.data_store.chroma.fulltext import ChromaFulltextCapability as ChromaFulltextCapability
from gllm_datastore.data_store.chroma.query import extract_chroma_query_components as extract_chroma_query_components
from gllm_datastore.data_store.chroma.vector import ChromaVectorCapability as ChromaVectorCapability
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from typing import Any

chromadb: Incomplete
DEFAULT_NUM_CANDIDATES: int

class ChromaClientType(StrEnum):
    """Enum for different types of ChromaDB clients."""
    MEMORY: str
    PERSISTENT: str
    HTTP: str

class ChromaDataStore(BaseDataStore):
    """ChromaDB data store with multiple capability support.

    Attributes:
        collection_name (str): The name of the ChromaDB collection.
        client (chromadb.ClientAPI): The ChromaDB client instance.
    """
    collection_name: Incomplete
    client: Incomplete
    def __init__(self, collection_name: str, client_type: ChromaClientType = ..., persist_directory: str | None = None, host: str | None = None, port: int | None = None, headers: dict | None = None, client_settings: dict | None = None) -> None:
        """Initialize the ChromaDB data store.

        Args:
            collection_name (str): The name of the ChromaDB collection.
            client_type (ChromaClientType, optional): Type of ChromaDB client to use.
                Defaults to ChromaClientType.MEMORY.
            persist_directory (str | None, optional): Directory to persist vector store data.
                Required for PERSISTENT client type. Defaults to None.
            host (str | None, optional): Host address for ChromaDB server.
                Required for HTTP client type. Defaults to None.
            port (int | None, optional): Port for ChromaDB server.
                Required for HTTP client type. Defaults to None.
            headers (dict | None, optional): A dictionary of headers to send to the Chroma server.
                Used for authentication with the Chroma server for HTTP client type. Defaults to None.
            client_settings (dict | None, optional): A dictionary of additional settings for the Chroma client.
                Defaults to None.
        """
    @property
    def supported_capabilities(self) -> list[str]:
        """Return list of currently supported capabilities.

        Returns:
            list[str]: List of capability names that are supported.
        """
    @property
    def fulltext(self) -> ChromaFulltextCapability:
        """Access fulltext capability if supported.

        This method uses the logic of its parent class to return the fulltext capability handler.
        This method overrides the parent class to return the ChromaFulltextCapability handler for better
        type hinting.

        Returns:
            ChromaFulltextCapability: Fulltext capability handler.

        Raises:
            NotSupportedException: If fulltext capability is not supported.
        """
    @property
    def vector(self) -> ChromaVectorCapability:
        """Access vector capability if supported.

        This method uses the logic of its parent class to return the vector capability handler.
        This method overrides the parent class to return the ChromaVectorCapability handler for better
        type hinting.

        Returns:
            ChromaVectorCapability: Vector capability handler.

        Raises:
            NotSupportedException: If vector capability is not supported.
        """
    def with_fulltext(self, collection_name: str | None = None, num_candidates: int = ...) -> ChromaDataStore:
        """Configure fulltext capability and return datastore instance.

        This method uses the logic of its parent class to configure the fulltext capability.
        This method overrides the parent class for better type hinting.

        Args:
            collection_name (str | None, optional): Name of the collection to use in ChromaDB. Defaults to None,
                in which case the default class attribute will be utilized.
            num_candidates (int, optional): Maximum number of candidates to consider during search.
                Defaults to DEFAULT_NUM_CANDIDATES.

        Returns:
            Self: Self for method chaining.
        """
    def with_vector(self, em_invoker: BaseEMInvoker, collection_name: str | None = None, num_candidates: int = ...) -> ChromaDataStore:
        """Configure vector capability and return datastore instance.

        This method uses the logic of its parent class to configure the vector capability.
        This method overrides the parent class for better type hinting.

        Args:
            em_invoker (BaseEMInvoker): The embedding model to perform vectorization.
            collection_name (str | None, optional): Name of the collection to use in ChromaDB. Defaults to None,
                in which case the default class attribute will be utilized.
            num_candidates (int, optional): Maximum number of candidates to consider during search.
                Defaults to DEFAULT_NUM_CANDIDATES.

        Returns:
            Self: Self for method chaining.
        """
    @classmethod
    def translate_query_filter(cls, query_filter: FilterClause | QueryFilter | None) -> dict[str, Any] | None:
        """Translate QueryFilter or FilterClause to ChromaDB native filter syntax.

        This method delegates to the existing extract_chroma_query_components function
        in the chroma.query module and returns the result as a dictionary.

        Args:
            query_filter (FilterClause | QueryFilter | None): The filter to translate.
                Can be a single FilterClause, a QueryFilter with multiple clauses,
                or None for empty filters.

        Returns:
            dict[str, Any] | None: The translated filter as a ChromaDB query dict.
                Returns None for empty filters.
        """
