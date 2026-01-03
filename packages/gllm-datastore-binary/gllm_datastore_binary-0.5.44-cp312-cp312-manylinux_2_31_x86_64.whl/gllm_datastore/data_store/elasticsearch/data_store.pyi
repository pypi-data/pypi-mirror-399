from _typeshed import Incomplete
from elasticsearch import AsyncElasticsearch
from gllm_datastore.constants import DEFAULT_REQUEST_TIMEOUT as DEFAULT_REQUEST_TIMEOUT
from gllm_datastore.core.filters.schema import FilterClause as FilterClause, QueryFilter as QueryFilter
from gllm_datastore.data_store.base import BaseDataStore as BaseDataStore, CapabilityType as CapabilityType
from gllm_datastore.data_store.elasticsearch.fulltext import ElasticsearchFulltextCapability as ElasticsearchFulltextCapability
from gllm_datastore.data_store.elasticsearch.query import translate_filter as translate_filter
from gllm_datastore.data_store.elasticsearch.vector import ElasticsearchVectorCapability as ElasticsearchVectorCapability
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from langchain_elasticsearch.vectorstores import AsyncRetrievalStrategy
from typing import Any

class ElasticsearchDataStore(BaseDataStore):
    """Elasticsearch data store with multiple capability support.

    Attributes:
        index_name (str): The name of the Elasticsearch index.
        client (AsyncElasticsearch): AsyncElasticsearch client.
    """
    client: Incomplete
    index_name: Incomplete
    def __init__(self, index_name: str, client: AsyncElasticsearch | None = None, url: str | None = None, cloud_id: str | None = None, api_key: str | None = None, username: str | None = None, password: str | None = None, request_timeout: int = ...) -> None:
        """Initialize the Elasticsearch fulltext capability.

        Args:
            index_name (str): The name of the Elasticsearch index.
            client (AsyncElasticsearch | None, optional): The Elasticsearch client. Defaults to None.
                If provided, it will be used instead of the url and cloud_id.
            url (str | None, optional): The URL of the Elasticsearch server. Defaults to None.
            cloud_id (str | None, optional): The cloud ID of the Elasticsearch cluster. Defaults to None.
            api_key (str | None, optional): The API key for authentication. Defaults to None.
            username (str | None, optional): The username for authentication. Defaults to None.
            password (str | None, optional): The password for authentication. Defaults to None.
            request_timeout (int, optional): The request timeout. Defaults to DEFAULT_REQUEST_TIMEOUT.
        """
    @property
    def supported_capabilities(self) -> list[str]:
        """Return list of currently supported capabilities.

        Returns:
            list[str]: List of capability names that are supported.
        """
    @property
    def fulltext(self) -> ElasticsearchFulltextCapability:
        """Access fulltext capability if supported.

        This method uses the logic of its parent class to return the fulltext capability handler.
        This method overrides the parent class to return the ElasticsearchFulltextCapability handler for better
        type hinting.

        Returns:
            ElasticsearchFulltextCapability: Fulltext capability handler.

        Raises:
            NotSupportedException: If fulltext capability is not supported.
        """
    @property
    def vector(self) -> ElasticsearchVectorCapability:
        """Access vector capability if supported.

        This method uses the logic of its parent class to return the vector capability handler.
        This method overrides the parent class to return the ElasticsearchVectorCapability handler for better
        type hinting.

        Returns:
            ElasticsearchVectorCapability: Vector capability handler.

        Raises:
            NotSupportedException: If vector capability is not supported.
        """
    def with_fulltext(self, index_name: str | None = None, query_field: str = 'text') -> ElasticsearchDataStore:
        '''Configure fulltext capability and return datastore instance.

        This method uses the logic of its parent class to configure the fulltext capability.
        This method overrides the parent class for better type hinting.

        Args:
            index_name (str | None, optional): The name of the Elasticsearch index. Defaults to None,
                in which case the default class attribute will be utilized.
            query_field (str, optional): The field name to use for text content. Defaults to "text".

        Returns:
            Self: Self for method chaining.
        '''
    def with_vector(self, em_invoker: BaseEMInvoker, index_name: str | None = None, query_field: str = 'text', vector_query_field: str = 'vector', retrieval_strategy: AsyncRetrievalStrategy | None = None, distance_strategy: str | None = None) -> ElasticsearchDataStore:
        '''Configure vector capability and return datastore instance.

        This method uses the logic of its parent class to configure the vector capability.
        This method overrides the parent class for better type hinting.

        Args:
            em_invoker (BaseEMInvoker): The embedding model to perform vectorization.
            index_name (str | None, optional): The name of the Elasticsearch index. Defaults to None,
                in which case the default class attribute will be utilized.
            query_field (str, optional): The field name for text queries. Defaults to "text".
            vector_query_field (str, optional): The field name for vector queries. Defaults to "vector".
            retrieval_strategy (AsyncRetrievalStrategy | None, optional): The retrieval strategy for retrieval.
                Defaults to None, in which case DenseVectorStrategy() is used.
            distance_strategy (str | None, optional): The distance strategy for retrieval. Defaults to None.

        Returns:
            Self: Self for method chaining.
        '''
    @classmethod
    def translate_query_filter(cls, query_filter: FilterClause | QueryFilter | None) -> dict[str, Any] | None:
        """Translate QueryFilter or FilterClause to Elasticsearch native filter syntax.

        This method delegates to the existing translate_filter function in the
        elasticsearch.query module and returns the result as a dictionary.

        Args:
            query_filter (FilterClause | QueryFilter | None): The filter to translate.
                Can be a single FilterClause, a QueryFilter with multiple clauses,
                or None for empty filters.

        Returns:
            dict[str, Any] | None: The translated filter as an Elasticsearch DSL dict.
                Returns None for empty filters.
        """
