"""
Azure AI Search Vector Store Module.

This module provides a concrete implementation of the VectorStore abstract base class,
using Azure AI Search for managing collections of vectors and their associated metadata.
"""

# pylint: disable=line-too-long, duplicate-code, too-many-instance-attributes, arguments-differ

from __future__ import annotations

from functools import lru_cache
import uuid
from enum import Enum
from typing import Any, Dict, List, Literal, override
import time
import asyncio
import random

from tenacity import retry, wait_exponential_jitter, stop_after_attempt, retry_if_exception_type

from autorag.types.vector_stores.search import AdvancedQueryVectorDetails, SearchType


try:
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import (HttpResponseError, ResourceNotFoundError,
                                       ServiceRequestError, ServiceResponseError,
                                       ServiceRequestTimeoutError, AzureError)
    from azure.identity import DefaultAzureCredential
    from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
    from azure.search.documents import SearchClient, SearchIndexingBufferedSender
    from azure.search.documents.aio import SearchClient as AsyncSearchClient
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.aio import (
        SearchIndexClient as AsyncSearchIndexClient,
    )
    from azure.search.documents.indexes.models import (
        ComplexField,
        ExhaustiveKnnAlgorithmConfiguration,
        ExhaustiveKnnParameters,
        HnswAlgorithmConfiguration,
        HnswParameters,
        SearchField,
        SearchFieldDataType,
        SearchIndex,
        SimpleField,
        SearchableField,
        VectorSearch,
        VectorSearchAlgorithmKind,
        VectorSearchAlgorithmMetric,
        VectorSearchProfile,

    )
    from azure.search.documents.models import (VectorizedQuery, VectorQuery, QueryType)
except ImportError as err:  # pragma: no cover
    raise ImportError(
        "Unable to locate azure-search-documents package. "
        'Please install it with `pip install "autonomize-autorag[azure-ai-search]"`.'
    ) from err

from autorag.exceptions.vector_stores import (
    VectorStoreCollectionAlreadyExistsException,
    VectorStoreCollectionNotFoundException,
    VectorStoreDataMismatchException,
    VectorStoreNonTransientException,
    VectorStoreTransientException
)
from autorag.types.vector_stores import DistanceType, VectorStoreQueryResult
from autorag.vector_stores.base import VectorStore


class AsyncKeyCredential:
    "Wraper Around Key Credential to make it usable with async with"

    def __init__(self, sync_obj: AzureKeyCredential):
        self._sync_obj = sync_obj

    async def __aenter__(self):
        """Async enter - returns the wrapped object"""
        return self._sync_obj

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Async exit - clean up if needed"""

    async def aclose(self):
        pass

class VectorIndexAlgorithm(str, Enum):
    HNSW = "HNSW"
    KNN = "KNN"
    BOTH = "BOTH"


class FieldDataType(str, Enum):
    """
    Enum class for valid data types for vector indexes.
    """

    # We don't have `single` or `single_list` here because
    # Azure doesn't support single precision outside vectors.
    # Please use `double` or `double_list` in its place.

    STRING = "string"
    INT32 = "int32"
    INT64 = "int64"
    DOUBLE = "double"
    BOOLEAN = "boolean"

    STRING_LIST = "string_list"
    INT32_LIST = "int32_list"
    INT64_LIST = "int64_list"
    DOUBLE_LIST = "double_list"
    BOOLEAN_LIST = "boolean_list"

    @classmethod
    def from_str(cls, value: str) -> FieldDataType:
        """
        Converts a string to FieldDataType
        Args:
            value (str): raw string value

        Returns:
            FieldDataType: FieldDataType object corresponding to the string
        """

        try:
            return cls(value)
        except ValueError:
            return cls.STRING

    def get_azure_data_type(self) -> str:
        """
        Convert FieldDataType to the corresponding Azure datatype string.

        Returns:
            str : Coresponding Azure Search Field data type for FieldDataType
        """

        mapping = {
            FieldDataType.STRING: SearchFieldDataType.String,
            FieldDataType.INT32: SearchFieldDataType.Int32,
            FieldDataType.INT64: SearchFieldDataType.Int64,
            FieldDataType.DOUBLE: SearchFieldDataType.Double,
            FieldDataType.BOOLEAN: SearchFieldDataType.Boolean,
            FieldDataType.STRING_LIST: SearchFieldDataType.Collection(
                SearchFieldDataType.String
            ),
            FieldDataType.INT32_LIST: SearchFieldDataType.Collection(
                SearchFieldDataType.Int32
            ),
            FieldDataType.INT64_LIST: SearchFieldDataType.Collection(
                SearchFieldDataType.Int64
            ),
            FieldDataType.DOUBLE_LIST: SearchFieldDataType.Collection(
                SearchFieldDataType.Double
            ),
            FieldDataType.BOOLEAN_LIST: SearchFieldDataType.Collection(
                SearchFieldDataType.Boolean
            ),
        }
        return mapping.get(self, SearchFieldDataType.String)


class AzureAISearchVectorStore(VectorStore):
    """
    Azure AI Search vector store implementation.

    This class provides an interface for interacting with an Azure AI Search vector database,
    utilizing the Azure SDK for Python for different operations.

    Args:
        endpoint (str): The endpoint of your Azure AI Search service.
        api_key (str): The API key for your Azure AI Search service.
        use_managed_identity (bool): If True, uses the managed identity for authentication. Default is False.

    Attributes:
        _m (int): Number of edges per node in the HNSW index graph.
                  Larger values lead to more accurate searches but require more space.
                  Default is 10.
        _ef_construct (int): Number of neighbors considered during the index building process.
                             Larger values improve accuracy but increase indexing time.
                             Default is 512.
        _ef_search (int): Size of the beam during a beam-search operation.
                          Larger values lead to more accurate search results but require more time.
                          Recommended to be the same as `_ef_construct`. Default is 512.

    Example:

    .. code-block:: python

        from autorag.vector_stores import AzureAISearchVectorStore
        from autorag.types.vector_stores import DistanceType

        client = AzureAISearchVectorStore(
            endpoint='https://<your-service-name>.search.windows.net',
            api_key='<your-api-key>'
        )

        client.create_collection(
            collection_name="test_collection",
            embedding_dimensions=768,
            distance=DistanceType.COSINE,
            metadata_fields=["content"]
        )
    """

    TRANSIENT_STATUS_CODES: set[int] = {408, 429, 500, 502, 503, 504}
    MAX_RETRIES : int = 5
    RETRY_BACKOFF_BASE : float = 1.5
    BATCH_SIZE : int = 50

    MAX_CUNCURRENT_BATCHES : int = 10

    def __init__(
        self, endpoint: str, api_key: str | None, use_managed_identity: bool = False, enable_logging : bool = False
    ) -> None:

        self._credential = self._get_sync_credential(
            api_key=api_key, use_managed_identity=use_managed_identity
        )
        self._enable_logging : bool = enable_logging
        self._api_key = api_key
        self._endpoint = endpoint
        self._use_managed_identity = use_managed_identity

        self._async_credential = self._get_async_credential(api_key=self._api_key, use_managed_identity=self._use_managed_identity)

        self._index_client = SearchIndexClient(
            endpoint=self._endpoint, credential=self._credential
        )

        self._async_index_client = AsyncSearchIndexClient(endpoint=self._endpoint, credential=self._async_credential)

        # Initialize collection parameters for HNSW
        self._m = (
            10  # Max allowed value is 10 for some reason, I wanted to set it to 16.
        )
        self._ef_construct = 512
        self._ef_search = self._ef_construct

        # Embedding field name
        # Fixed name for the field in the vector db to store embeddings.
        self._embedding_field_name = "embedding"

        self._async_client_cache: dict[str, AsyncSearchClient] = {}
        self._async_client_lock = asyncio.Lock()

    async def _get_reusable_async_client(self, index_name: str) -> AsyncSearchClient:
        """
        Returns a cached AsyncSearchClient instance for the index.
        Ensures only one client is created per index (thread-safe).
        """

        ## Clients are threadsafe/ async safe as per https://github.com/Azure/azure-sdk-for-python/issues/28665

        # Fast path: already cached
        if index_name in self._async_client_cache:
            return self._async_client_cache[index_name]

        async with self._async_client_lock:
            # Double-check inside lock
            if index_name not in self._async_client_cache:
                self._async_client_cache[index_name] = AsyncSearchClient(
                    endpoint=self._endpoint,
                    index_name=index_name,
                    credential=self._async_credential, # type: ignore
                    logging_enable=self._enable_logging,
                )

            return self._async_client_cache[index_name]


    async def _invalidate_async_client(self, index_name: str):
        client = self._async_client_cache.get(index_name)
        if client:
            try:
                await client.close()
            except:
                pass
        self._async_client_cache.pop(index_name, None)



    def _get_sync_credential(
        self, api_key: str | None, use_managed_identity: bool
    ) -> AzureKeyCredential | DefaultAzureCredential:

        if use_managed_identity:
            return DefaultAzureCredential()
        if api_key:
            return AzureKeyCredential(key=api_key)

        raise ValueError(
            "No authentication method was provided. "
            "Pass an `api_key` (str) or set `use_managed_identity=True` "
            "to authenticate using the managed identity."
        )

    def _get_async_credential(
        self, api_key: str | None, use_managed_identity: bool
    ) -> AsyncDefaultAzureCredential | AzureKeyCredential:
        if use_managed_identity:
            return AsyncDefaultAzureCredential()
        if api_key:
            return AzureKeyCredential(key=api_key)

        raise ValueError(
            "No authentication method was provided. "
            "Pass an `api_key` (str) or set `use_managed_identity=True` "
            "to authenticate using the managed identity."
        )

    def _schema_to_field(self, name: str, spec: Any) -> SearchField:
        """
        Turn a user schema spec into an Azure Search field, recursively.

        Args:
            name (str): The name of the field.
            spec (Any): The schema specification for the field.

        Supported:
            - "string", "int32", "double_list", ... (primitive or *_list)
            - {"type": "complex", "field": { ... }}
            - {"type": "complex_list", "field": { ... }}
            - Arbitrary nesting via the same pattern.

        Also accepts (optional) synonyms for flexibility:
            - "fields" instead of "field"
            - "object" instead of "complex"

        Args:
            name (str): The name of the field.
            spec (Any): The schema specification for the field.

        Returns:
            SearchField: The corresponding Azure Search field.

        """
        # 1) Primitive
        if isinstance(spec, str):
            # Uses your FieldDataType to map primitives and *_list to Azure types
            t_enum = FieldDataType.from_str(spec)
            return SimpleField(
                name=name,
                type=t_enum.get_azure_data_type(),
                filterable=True,
            )

        # 2) Complex / Complex list
        if isinstance(spec, dict):
            t = (spec.get("type") or "").lower()

            # Allow synonyms
            if t == "object":
                t = "complex"

            # pull child map from "field", falling back to "fields" for convenience
            child_map = spec.get("field", spec.get("fields"))
            if t in {"complex", "complex_list"}:
                if not isinstance(child_map, dict):
                    raise VectorStoreDataMismatchException(
                        f"Complex field '{name}' must have a dict under 'field'."
                    )

                child_fields: List[SearchField] = [
                    self._schema_to_field(child_name, child_spec)
                    for child_name, child_spec in child_map.items()
                ]

                return ComplexField(
                    name=name,
                    fields=child_fields,
                    collection=(t == "complex_list"),
                )

        raise VectorStoreDataMismatchException(
            f"Unsupported schema spec for field '{name}': {spec!r}"
        )

    def _create_fields(
        self,
        embedding_dimensions: int,
        metadata_fields: List[str],
        metadata_field_to_type_mapping: Dict[str, str],
        searchable_fields : list[str],
        analyzer_name : str | None
    ) -> List[SearchField]:  # SimpleField instantiates SearchField class
        """
        Creates a list of fields for the collection, including metadata and embedding fields.

        Args:
            embedding_dimensions (int): Number of dimensions for the embeddings.
            metadata_fields (List[str]): List of metadata field names.

        Returns:
            List[SearchField]: List of SearchFields for the collection schema.
        """

        fields = [
            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
            )  # Default id field as key
        ]

        for metadata_field in metadata_fields:
            field_type_string = metadata_field_to_type_mapping.get(
                metadata_field, "string"
            )
      
            field_type_enum = FieldDataType.from_str(field_type_string)
            azure_data_type_for_field = field_type_enum.get_azure_data_type()

            is_searchable : bool = False

            if metadata_field in searchable_fields:
                is_searchable = True


            if is_searchable:

                fields.append(
                    SearchField
                        (
                        name=metadata_field,
                        type = azure_data_type_for_field,
                        filterable = False,
                        searchable=True,
                        analyzer_name = analyzer_name if analyzer_name else "en.lucene",
                        sortable = False,
                        facetable = False
                            )
                    )


            else:

                spec = metadata_field_to_type_mapping.get(metadata_field, "string")
                fields.append(self._schema_to_field(metadata_field, spec))


        fields.append(
            SearchField(
                name=self._embedding_field_name,
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=embedding_dimensions,
                vector_search_profile_name="myHnswProfile",
            )
        )

        return fields

    def _create_vector_search_config(
        self, vector_distance: VectorSearchAlgorithmMetric, index_algorithm : VectorIndexAlgorithm = VectorIndexAlgorithm.HNSW
    ) -> VectorSearch:
        """
        Creates vector search configurations using HNSW and KNN algorithms.

        Args:
            vector_distance (VectorSearchAlgorithmMetric): The distance metric to use.

        Returns:
            VectorSearch: The vector search configuration for the collection.
        """

        if index_algorithm == VectorIndexAlgorithm.BOTH:
            return VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(
                        name="myHnsw",
                        kind=VectorSearchAlgorithmKind.HNSW,
                        parameters=HnswParameters(
                            m=self._m,
                            ef_construction=self._ef_construct,
                            ef_search=self._ef_search,
                            metric=vector_distance,
                        ),
                    ),
                    ExhaustiveKnnAlgorithmConfiguration(
                        name="myExhaustiveKnn",
                        kind=VectorSearchAlgorithmKind.EXHAUSTIVE_KNN,
                        parameters=ExhaustiveKnnParameters(metric=vector_distance),
                    ),
                ],
                profiles=[
                    VectorSearchProfile(
                        name="myHnswProfile",
                        algorithm_configuration_name="myHnsw",
                    ),
                    VectorSearchProfile(
                        name="myExhaustiveKnnProfile",
                        algorithm_configuration_name="myExhaustiveKnn",
                    ),
                ],
            )
        elif index_algorithm == VectorIndexAlgorithm.HNSW:
            return VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(
                        name="myHnsw",
                        kind=VectorSearchAlgorithmKind.HNSW,
                        parameters=HnswParameters(
                            m=self._m,
                            ef_construction=self._ef_construct,
                            ef_search=self._ef_search,
                            metric=vector_distance,
                        ),
                    )
                ],
                profiles=[
                    VectorSearchProfile(
                        name="myHnswProfile",
                        algorithm_configuration_name="myHnsw",
                    )
                ],
            )
        else:
                        return VectorSearch(
                algorithms=[
                    ExhaustiveKnnAlgorithmConfiguration(
                        name="myExhaustiveKnn",
                        kind=VectorSearchAlgorithmKind.EXHAUSTIVE_KNN,
                        parameters=ExhaustiveKnnParameters(metric=vector_distance),
                    ),
                ],
                profiles=[
                    VectorSearchProfile(
                        name="myExhaustiveKnnProfile",
                        algorithm_configuration_name="myExhaustiveKnn",
                    ),
                ],
            )

    def _get_distance_metric(
        self, distance: DistanceType
    ) -> VectorSearchAlgorithmMetric:
        """
        Converts DistanceType to the corresponding `VectorSearchAlgorithmMetric`
        metric as per the configurations required by the Azure AI Search Vector Store.

        Args:
            distance (DistanceType): The type of distance metric to use.

        Returns:
            str: The matching distance metric for the Qdrant configuration.
        """
        if distance == DistanceType.EUCLIDEAN:
            return VectorSearchAlgorithmMetric.EUCLIDEAN
        if distance == DistanceType.COSINE:
            return VectorSearchAlgorithmMetric.COSINE
        return VectorSearchAlgorithmMetric.DOT_PRODUCT

    def _create_collection(  # type: ignore[override]
        self,
        collection_name: str,
        embedding_dimensions: int,
        distance: DistanceType,
        metadata_fields: List[str],
        **kwargs: Any,
    ) -> None:
        """
        Creates a new collection (index) in Azure AI Search.

        Args:
            collection_name (str): The name of the index to be created.
            embedding_dimensions (int): The number of dimensions for the embeddings.
            distance (DistanceType): The type of distance metric to use.
            metadata_fields (List[str]): A list of fields to define the schema of the collection.
            kwargs (Any): Any additional arguments to be used.
        """

        if "id" in metadata_fields:
            raise VectorStoreDataMismatchException(
                "Field `id` is a reserved keyword. Please use a different identifier in metadata_fields."
            )

        vector_distance = self._get_distance_metric(distance=distance)

        metadata_field_to_type_mapping: Dict[str, str] = kwargs.pop(
            "metadata_field_to_type_mapping", {}
        )

        searchable_fields : list [str] = kwargs.pop("searchable_fields", [])

        analyzer_name = kwargs.pop("analyzer_name", None)

        fields = self._create_fields(
            embedding_dimensions=embedding_dimensions,
            metadata_fields=metadata_fields,
            metadata_field_to_type_mapping=metadata_field_to_type_mapping,
            searchable_fields=searchable_fields,
            analyzer_name=analyzer_name
        )

        vector_search = self._create_vector_search_config(
            vector_distance=vector_distance
        )

        index = SearchIndex(
            name=collection_name,
            fields=fields,
            vector_search=vector_search,
        )

        self._index_client.create_index(index, **kwargs)

    def _delete_collection(self, collection_name: str, **kwargs: Any) -> None:
        """
        Deletes an existing collection (index) in Azure AI Search.

        Args:
            collection_name (str): The name of the collection to be deleted.
            kwargs (Any): Any additional arguments to be used.
        """
        self._index_client.delete_index(collection_name, **kwargs)




    def _is_transient_error(self, error : Exception) -> bool:
        # Azure Search uses HTTP status codes and service errors for transient failures
        if isinstance(error, HttpResponseError):
            if error.status_code in self.TRANSIENT_STATUS_CODES:
                return True
        if isinstance(error, (ServiceRequestError, ServiceResponseError)):
            return True

        if "Flush returned failure" in str(error):
            return True
        return False



    def _upload_with_retries(self, endpoint, index_name, credential, documents, **kwargs):
        """
        Production-grade batching with retrying both upload and flush.
        Recreates the batch client on repeated failures.
        """

        retry_count = 0

        while True:
            try:
                # Create batch client fresh for every retry attempt (Azure recommended)
                with SearchIndexingBufferedSender(
                    endpoint=endpoint,
                    index_name=index_name,
                    credential=credential,
                ) as batch:

                    # Upload documents
                    batch.upload_documents(documents=documents, **kwargs)

                    # Try flushing
                    flush_errors = batch.flush()

                    if flush_errors:
                        # flush() returns a list of DocumentIndexingResult for failed docs
                        raise HttpResponseError(
                            message=f"Flush returned failure",
                            response=None
                        )

                    # Success!
                    return

            except Exception as e:
                if not self._is_transient_error(e) or retry_count >= self.MAX_RETRIES:
                    # Non-transient, or max attempts reached → fail permanently
                    raise

                # Log or print warning
                (f"[WARN] Batch upload failed with transient error: {e}. Retrying {retry_count+1}/{self.MAX_RETRIES}...")

                # Apply exponential backoff
                delay = (self.RETRY_BACKOFF_BASE ** retry_count) + (0.3 * retry_count)
                time.sleep(delay)

                retry_count += 1

    async def _async_upload_batch(
        self,
        client: AsyncSearchClient,
        batch: list[dict],
        *,
        max_attempts: int | None = None,
    ) -> dict:
        """
        Uploads a batch of documents to Azure Search with:
        - Retry of ONLY failed docs
        - Exponential backoff + jitter
        - Structured results
        - No recursion
        """

        if max_attempts is None:
            max_attempts = self.MAX_RETRIES

        docs_remaining = batch[:]     # copy
        attempt = 1
        start_time = time.time()
        total_sent = len(batch)

        while docs_remaining and attempt <= max_attempts:

            try:
                result = await client.upload_documents(documents=docs_remaining)

                # Identify failed ones
                failed_docs = [
                    docs_remaining[i]
                    for i, r in enumerate(result)
                    if not r.succeeded
                ]

                if not failed_docs:
                    # All uploaded successfully
                    return {
                        "succeeded": total_sent,
                        "failed": 0,
                        "failed_docs": [],
                        "attempts": attempt,
                        "duration": time.time() - start_time,
                    }

                # Prepare for retry
                docs_remaining = failed_docs

                # Construct artificial transient error so we enter retry logic
                raise HttpResponseError(
                    message=f"{len(docs_remaining)} failed documents",
                    response=None
                )

            except Exception as e:
                # Identify transient error


                is_transient = (
                    isinstance(e, HttpResponseError)
                    and getattr(e, "status_code", None) in self.TRANSIENT_STATUS_CODES
                ) or isinstance(e, (ServiceRequestError, ServiceResponseError))


                if isinstance( e, HttpResponseError):
                    if e.status_code in (401, 403):
                        index_name : str = client._index_name  # token bad/expired
                        await self._invalidate_async_client(index_name)
                        client = await self._get_reusable_async_client(index_name)
                        is_transient = True


                # HttpResponseError raised artificially has no status_code → treat as transient
                if isinstance(e, HttpResponseError) and getattr(e, "status_code", None) is None:
                    is_transient = True

                if not is_transient:
                    # Non-transient; fail immediately
                    raise

                if attempt >= max_attempts:
                    # Out of retry attempts
                    return {
                        "succeeded": total_sent - len(docs_remaining),
                        "failed": len(docs_remaining),
                        "failed_docs": docs_remaining,
                        "attempts": attempt,
                        "duration": time.time() - start_time,
                    }

                # Exponential backoff with jitter
                base = 2 ** attempt
                jitter = random.uniform(0.2, 1.2)
                delay = base * jitter + (attempt * 0.1)

                await asyncio.sleep(delay)
                attempt += 1

        # If we exit loop: some docs remain and retries exhausted
        return {
            "succeeded": total_sent - len(docs_remaining),
            "failed": len(docs_remaining),
            "failed_docs": docs_remaining,
            "attempts": attempt,
            "duration": time.time() - start_time,
        }

    async def aupsert(self,collection_name: str,
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        **kwargs: Any):




        use_client_provided_id = kwargs.pop("use_client_provided_id", False)
        documents = []

        for embedding, metadata in zip(embeddings, metadatas):
            doc = metadata.copy()
            if not (use_client_provided_id and "id" in metadata):
                doc["id"] = str(uuid.uuid4())

            doc[self._embedding_field_name] = embedding
            documents.append(doc)

        # --- Chunk into batches ---
        batches = [
            documents[i:i + self.BATCH_SIZE]
            for i in range(0, len(documents), self.BATCH_SIZE)
        ]

        tasks = []

        sem = asyncio.Semaphore(self.MAX_CUNCURRENT_BATCHES)


        client : AsyncSearchClient = await self._get_reusable_async_client(index_name=collection_name)

        async def process_batch(batch):

            async with sem:
                return await self._async_upload_batch(client, batch)

        # Launch ingestion concurrently
        for batch in batches:
            tasks.append(asyncio.create_task(process_batch(batch)))

        results = await asyncio.gather(*tasks)

        # Optionally: raise error if any failures remain
        total_failed = sum(r["failed"] for r in results)
        if total_failed > 0:
            raise ValueError(
                f"{total_failed} documents failed after retries. "
                f"Failed examples: {results[0]['failed_docs'][:3]}"
            )

        print(f"Results from upload: {results}")



    @retry(wait=wait_exponential_jitter(max=120, jitter=3),
           stop=stop_after_attempt(5),
           retry=retry_if_exception_type(VectorStoreTransientException))
    def _upsert(
        self,
        collection_name: str,
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> None:
        """
        Upserts embeddings and metadata into the collection (index).

        Args:
            collection_name (str): The name of the collection to upsert into.
            embeddings (List[List[float]]): A list of vectors to be upserted.
            metadatas (List[Dict[str, Any]]): A list of metadata dictionaries corresponding to the embeddings.
            kwargs (Any): Any additional arguments to be used.
        """



        use_client_provided_id: bool = False

        if "use_client_provided_id" in kwargs:
            # for idempotency when ExactlyOnceProcessing cannot be guaranteed
            use_client_provided_id_value_in_kwargs: bool = kwargs[
                "use_client_provided_id"
            ]
            kwargs.pop("use_client_provided_id")
            if "id" in metadatas[0] and use_client_provided_id_value_in_kwargs:
                use_client_provided_id = True

        if not use_client_provided_id and "id" in metadatas[0]:
            raise VectorStoreDataMismatchException(
                "Field `id` is a reserved keyword. Please use a different identifier in metadata."
            )

        documents = []
        for embedding, metadata in zip(embeddings, metadatas):
            if use_client_provided_id:
                doc = {
                    self._embedding_field_name: embedding,
                    **metadata,
                }
            else:
                doc = {
                    "id": str(uuid.uuid4()),
                    self._embedding_field_name: embedding,
                    **metadata,
                }

            documents.append(doc)

        try:
            # `SearchIndexingBufferedSender` is preferred when batching uploading requests

            self._upload_with_retries(endpoint=self._endpoint,
                                      index_name=collection_name, credential=self._credential,
                                      documents=documents)

            # with SearchIndexingBufferedSender(
            #     endpoint=self._endpoint,
            #     index_name=collection_name,
            #     credential=self._credential,
            # ) as batch_client:
            #     batch_client.upload_documents(documents=documents, **kwargs)

            #     # Manually flushing any remaining documents
            #     error_in_flush = batch_client.flush()
            #     if error_in_flush:
            #         raise HttpResponseError(f"Error in Flushing Documents in upsert of {metadatas}")
        except HttpResponseError as e:  # pragma: no cover
            raise ValueError(f"Error occurred when uploading documents: {e}") from e

    def _delete_by_metadata_field(
        self,
        collection_name: str,
        field_name: str,
        field_values: List[str | int],
        **kwargs: Any
    ) -> None:
        search_client = SearchClient(
            endpoint=self._endpoint,
            index_name=collection_name,
            credential=self._credential,
        )

        # Build filter to find all documents matching the field values
        filter_conditions = self._build_query_filter({field_name: field_values})

        # Search for all matching documents
        results = search_client.search(
            search_text="",
            filter=filter_conditions,
            select=["id"],  # Only retrieve the ID field
            **kwargs,
        )

        ids_to_delete = [result["id"] for result in results]

        if not ids_to_delete:
            return None

        # Delete documents by their IDs
        documents = [{"id": doc_id} for doc_id in ids_to_delete]

        try:
            with SearchIndexingBufferedSender(
                endpoint=self._endpoint,
                index_name=collection_name,
                credential=self._credential,
            ) as batch_client:
                batch_client.delete_documents(documents=documents)

                # Manually flushing
                error_in_flush = batch_client.flush()
                if error_in_flush:
                    raise HttpResponseError(
                        f"Error in flushing documents during deletion. Field: {field_name}, Values: {field_values}"
                    )
        except HttpResponseError as e:
            raise ValueError(f"Error occurred when deleting documents: {e}") from e

        return None

    def _query(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int,
        metadata_filter: Dict[str, Any],
        metadata_fields: List[str],
        **kwargs: Any,
    ) -> List[VectorStoreQueryResult]:
        """
        Queries the vector store to find the top_k most similar vectors to the given query embedding.

        Args:
            collection_name (str): The name of the collection to query.
            query_embedding (List[float]): The vector to query for.
            top_k (int): The number of top similar vectors to retrieve.
            metadata_filter (Dict[str, Any]): A dictionary to filter the results based on metadata.
            metadata_fields (List[str]): A list of fields to retrieve in the results.
            kwargs (Any): Any additional arguments to be used.

        Returns:
            List[VectorStoreQueryResult]: A list of type VectorStoreQueryResult containing the search results.
        """

        filter_string = kwargs.pop("filter_string", None)

        if filter_string:
            filter_conditions = filter_string

        else:
            filter_conditions = self._build_query_filter(metadata_filter=metadata_filter)

        search_client = SearchClient(
            endpoint=self._endpoint,
            index_name=collection_name,
            credential=self._credential,
        )  # type: ignore





        vector = VectorizedQuery(
            vector=query_embedding,
            k_nearest_neighbors=top_k,
            fields=self._embedding_field_name,
        )


        results = search_client.search(
            search_text="",
            vector_queries=[vector], # type: ignore
            filter=filter_conditions,
            select=metadata_fields,
            top=top_k,
            **kwargs,
        )
        result_list = list(results)

        return self._convert_to_model(results=result_list)

    def _convert_to_model(
        self, results: List[Dict[str, Any]]
    ) -> List[VectorStoreQueryResult]:
        """
        Converts a list of the search results to VectorStoreQueryResult models.

        Args:
            results (List[Dict[str, Any]]): A list of search results from Azure AI Search.

        Returns:
            List[VectorStoreQueryResult]: A list of converted VectorStoreQueryResult models.
        """
        return [
            VectorStoreQueryResult(
                score=result.get("@search.score", 0.0),
                metadata={
                    k: v for k, v in result.items() if k not in {"@search.score"}
                },
            )
            for result in results
        ]

    def _build_query_filter(self, metadata_filter: Dict[str, Any]) -> str:
        """
        Constructs a query filter for the Azure AI Search vector store based on the provided metadata.

        The function translates a dictionary of metadata filters into a string format suitable for querying
        the vector store. Each key-value pair in the metadata_filter dictionary is converted
        into a corresponding OData filter condition needed for Azure AI Search.

        Supported filter conditions:
        - Equality
        - IN (as in checking all values in a list)

        Note:
            Additional filter conditions to be added later.

        Args:
            metadata_filter (Dict[str, Any]): A dictionary to filter the results based on metadata.

        Returns:
            str: A filter string formatted for Azure AI Search's API.
        """

        field_conditions = []

        for key, value in metadata_filter.items():
            if isinstance(value, list):
                if all(isinstance(item, str) for item in value):
                    # List of strings
                    or_conditions = " or ".join(
                        [f"{key} eq '{item}'" for item in value]
                    )
                elif all(isinstance(item, bool) for item in value):
                    # List of booleans
                    or_conditions = " or ".join(
                        [f"{key} eq {str(item).lower()}" for item in value]
                    )
                elif all(isinstance(item, (int, float)) for item in value):
                    # List of numbers (int, float)
                    or_conditions = " or ".join([f"{key} eq {item}" for item in value])
                else:
                    raise VectorStoreDataMismatchException(
                        f"Unsupported list type for key for filtering: {key}"
                    )

                or_conditions = f"({or_conditions})"
                field_conditions.append(or_conditions)

            # Non-list elements
            elif isinstance(value, str):
                condition = f"{key} eq '{value}'"
                field_conditions.append(condition)
            elif isinstance(value, bool):
                condition = f"{key} eq {str(value).lower()}"
                field_conditions.append(condition)
            elif isinstance(value, (int, float)):
                condition = f"{key} eq {value}"
                field_conditions.append(condition)
            else:
                raise VectorStoreDataMismatchException(
                    f"Unsupported data type for key for filtering: {key}"
                )

        return " and ".join(field_conditions)

    def _delete_by_metadata(
        self,
        collection_name: str,
        metadata_filter: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """
        Deletes items from a collection (index) that match the given metadata filter.

        Args:
            collection_name (str): The name of the collection (index) to delete from.
            metadata_filter (Dict[str, Any]): A dictionary describing which items to delete.
            kwargs (Any): Any additional arguments to be used.
        """

        filter_conditions = self._build_query_filter(metadata_filter=metadata_filter)

        search_client = SearchClient(
            endpoint=self._endpoint,
            index_name=collection_name,
            credential=self._credential,
        )  # type: ignore

        # Collect all matching ids
        results = search_client.search(
            search_text="",
            filter=filter_conditions,
            select=["id"],
            **kwargs,
        )

        ids_to_delete: List[str] = [doc["id"] for doc in results]  # type: ignore[index]

        documents = [{"id": _id} for _id in ids_to_delete]

        try:
            # Buffered sender handles batching and retries.
            with SearchIndexingBufferedSender(
                endpoint=self._endpoint,
                index_name=collection_name,
                credential=self._credential,
            ) as batch_client:
                batch_client.delete_documents(documents=documents, **kwargs)
                batch_client.flush()
        except HttpResponseError as e:  # pragma: no cover
            raise ValueError(f"Error occurred when deleting documents: {e}") from e

    def _collection_exists(self, collection_name: str, **kwargs: Any) -> bool:
        """
        Checks if a collection (index) exists in Azure AI Search.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        try:
            self._index_client.get_index(collection_name)
            return True
        except ResourceNotFoundError:
            return False

    async def acreate_collection(  # type: ignore[override]
        self,
        collection_name: str,
        embedding_dimensions: int,
        distance: DistanceType,
        metadata_fields: List[str],
        **kwargs: Any,
    ) -> None:
        """
        Asynchronously creates a new collection (index) in Azure AI Search.

        Args:
            collection_name (str): The name of the index to be created.
            embedding_dimensions (int): The number of dimensions for the embeddings.
            distance (DistanceType): The type of distance metric to use.
            metadata_fields (List[str]): A list of fields to define the schema of the collection.
            kwargs (Any): Any additional arguments to be used.
        """

        if "id" in metadata_fields:
            raise VectorStoreDataMismatchException(
                "Field `id` is a reserved keyword. Please use a different identifier in metadata_fields."
            )

        if await self._acollection_exists(collection_name):
            raise VectorStoreCollectionAlreadyExistsException(
                f"Collection '{collection_name}' already exists."
            )

        vector_distance = self._get_distance_metric(distance=distance)

        metadata_field_to_type_mapping: Dict[str, str] = kwargs.pop(
            "metadata_field_to_type_mapping", {}
        )

        searchable_fields : List[str] = kwargs.pop("searchable_fields", [])

        analyzer_name : str | None = kwargs.pop("analyzer_name", None)


        fields = self._create_fields(
            embedding_dimensions=embedding_dimensions,
            metadata_fields=metadata_fields,
            metadata_field_to_type_mapping=metadata_field_to_type_mapping,
            searchable_fields=searchable_fields,
            analyzer_name=analyzer_name
        )

        vector_search = self._create_vector_search_config(
            vector_distance=vector_distance
        )

        index = SearchIndex(
            name=collection_name,
            fields=fields,
            vector_search=vector_search,
        )



        async_index_client = self._async_index_client
        await async_index_client.create_index(index, **kwargs)

    async def adelete_collection(self, collection_name: str, **kwargs: Any) -> None:
        """
        Asynchronously deletes an existing collection in the vector store.

        Args:
            collection_name (str): The name of the collection to be deleted.
            kwargs (Any): Any additional arguments to be used.

        Raises:
            VectorStoreCollectionNotFoundException: If the collection does not exist.
        """
        if not await self._acollection_exists(collection_name):
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )


        async_index_client = self._async_index_client

        await async_index_client.delete_index(collection_name, **kwargs)


    @retry(wait=wait_exponential_jitter(max=120, jitter=3),
           stop=stop_after_attempt(5),
           retry=retry_if_exception_type(VectorStoreTransientException))
    async def adelete_by_metadata_field(
        self,
        collection_name: str,
        field_name: str,
        field_values: List[str | int],
        **kwargs: Any,
    ) -> None:
        if not await self._acollection_exists(collection_name):
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        try:

            search_client : AsyncSearchClient = await self._get_reusable_async_client(index_name=collection_name)
            # Build filter to find all documents matching the field values
            filter_conditions = self._build_query_filter({field_name: field_values})

            # Search for all matching documents
            results = await search_client.search(
                search_text="",
                filter=filter_conditions,
                select=["id"],  # Only retrieve the ID field
                **kwargs,
            )

            ids = [r["id"] async for r in results]

            # Delete in batches of 1000
            batch_size = 1000
            for i in range(0, len(ids), batch_size):
                batch = [{"id": x} for x in ids[i:i+batch_size]]
                await search_client.delete_documents(documents=batch)

        except HttpResponseError as error:

            if error.status_code in (401, 403):   # token bad/expired
                await self._invalidate_async_client(collection_name)
                search_client = await self._get_reusable_async_client(collection_name)
                raise VectorStoreTransientException(exception=str(error), status_code=error.status_code) from error

            elif error.status_code in [500, 503, 429, 428, 409]:
                if error.status_code == 429:
                    raise VectorStoreTransientException(exception=str(error), status_code=error.status_code) from error
                raise VectorStoreNonTransientException(exception=str(error), status_code=error.status_code) from error
            else:
                raise error
        except (ServiceRequestError, ServiceRequestTimeoutError, ServiceResponseError) as error:
            raise VectorStoreTransientException(exception=str(error), status_code=500) from error
        except AzureError as error:
            raise VectorStoreNonTransientException(exception=str(error), status_code=500) from error
        except Exception as error:
            raise  VectorStoreNonTransientException(exception=str(error), status_code=500) from error

    @retry(wait=wait_exponential_jitter(max=120, jitter=3),
           stop=stop_after_attempt(5),
           retry=retry_if_exception_type(VectorStoreTransientException))
    async def aquery(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int,
        metadata_filter: Dict[str, Any],
        metadata_fields: List[str],
        **kwargs: Any,
    ) -> List[VectorStoreQueryResult]:
        """
        Asynchronously queries the vector store to find the top_k most similar vectors to the given query embedding.

        Args:
            collection_name (str): The name of the collection to query.
            query_embedding (List[float]): The vector to query for.
            top_k (int): The number of top similar vectors to retrieve.
            metadata_filter (Dict[str, Any]): A dictionary to filter the results based on metadata.
            metadata_fields (List[str]): A list of fields to retrieve in the results.
            kwargs (Any): Any additional arguments to be used.

        Returns:
            List[VectorStoreQueryResult]: A list of type VectorStoreQueryResult containing the embeddings and their corresponding metadatas.
        """
        if not await self._acollection_exists(collection_name):
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        filter_string = kwargs.pop("filter_string", None)

        if filter_string:
            filter_conditions = filter_string

        else:
            filter_conditions = self._build_query_filter(metadata_filter=metadata_filter)

        try:


                search_client : AsyncSearchClient = await self._get_reusable_async_client(index_name=collection_name)
                vectors : List[VectorizedQuery] = []

                vector = VectorizedQuery(
                    vector=query_embedding,
                    k_nearest_neighbors=top_k,
                    fields=self._embedding_field_name,
                )


                results = await search_client.search(
                    search_text="",
                    vector_queries=[vector], # type: ignore
                    filter=filter_conditions,
                    select=metadata_fields,
                    top=top_k,
                    **kwargs,
                )
                result_list = [result async for result in results]

                return self._convert_to_model(results=result_list)

        except HttpResponseError as error:

            if error.status_code in (401, 403):   # token bad/expired
                await self._invalidate_async_client(collection_name)
                search_client = await self._get_reusable_async_client(collection_name)
                raise VectorStoreTransientException(exception=str(error), status_code=error.status_code) from error

            elif error.status_code in [500, 503, 429, 428, 409]:
                if error.status_code == 429:
                    raise VectorStoreTransientException(exception=str(error), status_code=error.status_code) from error
                raise VectorStoreNonTransientException(exception=str(error), status_code=error.status_code) from error
            else:
                raise error
        except (ServiceRequestError, ServiceRequestTimeoutError, ServiceResponseError) as error:
            raise VectorStoreTransientException(exception=str(error), status_code=500) from error
        except AzureError as error:
            raise VectorStoreNonTransientException(exception=str(error), status_code=500) from error
        except Exception as error:
            raise  VectorStoreNonTransientException(exception=str(error), status_code=500) from error

    async def _acollection_exists(self, collection_name: str) -> bool:
        """
        Asynchronously checks if a collection (index) exists in Azure AI Search.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        try:

            async_index_client = self._async_index_client

            await async_index_client.get_index(collection_name)

            return True
        except ResourceNotFoundError:
            return False


    @retry(wait=wait_exponential_jitter(max=120, jitter=3),
           stop=stop_after_attempt(5),
           retry=retry_if_exception_type(VectorStoreTransientException))
    async def a_advanced_query(
        self,
        collection_name: str,
        query_vectors: List[AdvancedQueryVectorDetails],
        search_string : str,
        search_fields : list[str],
        keyword_search_query_type : Literal["simple", "full", "semantic"],
        search_type : SearchType,
        top_k: int,
        metadata_filter: Dict[str, Any],
        metadata_fields: List[str],
        **kwargs: Any,
    ) -> List[VectorStoreQueryResult]:
        """
        Asyncronously queries the vector store to find the top_k most similar vectors to the given query embedding.

        Args:
            collection_name (str): The name of the collection to query.
            query_embedding (List[float]): The vector to query for.
            top_k (int): The number of top similar vectors to retrieve.
            metadata_filter (Dict[str, Any]): A dictionary to filter the results based on metadata.
            metadata_fields (List[str]): A list of fields to retrieve in the results.
            kwargs (Any): Any additional arguments to be used.

        Returns:
            List[VectorStoreQueryResult]: A list of dictionaries containing the embeddings and their corresponding metadatas.

        Raises:
            VectorStoreCollectionNotFoundException: If the collection does not exist.
        """


        if not await self._acollection_exists(collection_name):
            raise VectorStoreCollectionNotFoundException(
                f"Collection '{collection_name}' does not exist."
            )

        filter_string = kwargs.pop("filter_string", None)

        if filter_string:
            filter_conditions = filter_string

        else:
            filter_conditions = self._build_query_filter(metadata_filter=metadata_filter)

        query_type : QueryType | None = None

        if keyword_search_query_type == "full":
            query_type = QueryType.FULL
        elif keyword_search_query_type == "semantic":
            query_type = QueryType.SEMANTIC
        elif keyword_search_query_type == "simple":
            query_type = QueryType.SIMPLE

        try:


                search_client : AsyncSearchClient = await self._get_reusable_async_client(index_name=collection_name)
                vectors : List[VectorizedQuery] = []

                for current_query_vector in query_vectors:
                    current_query_vector_fields = [self._embedding_field_name]
                    current_query_vector_fields.extend(current_query_vector.fields)
                    current_query_vector_fields = list(set(current_query_vector_fields))
                    current_query_vector_fields_string = ",".join(current_query_vector_fields)
                    vector = VectorizedQuery(
                        vector=current_query_vector.vector,
                        k_nearest_neighbors=current_query_vector.top_k,
                        exhaustive=current_query_vector.exhaustive,
                        fields=current_query_vector_fields_string,
                        # weight = current_query_vector.weight
                    )
                    vectors.append(vector)


                search_text= ""

                if search_type in [SearchType.FULL_TEXT]:
                    vectors = []
                    search_text = search_string
                elif search_type in [SearchType.VECTOR]:
                    search_text = ""
                    query_type = None
                    search_fields = []

                elif search_type in [SearchType.HYBRID]:
                    search_text = search_string



                results = await search_client.search(
                    search_text=search_text,
                    vector_queries=vectors, # type: ignore
                    filter=filter_conditions,
                    select=metadata_fields,
                    top=top_k,
                    search_fields= search_fields,
                    query_type = query_type,
                    **kwargs,
                )
                result_list = [result async for result in results]

                return self._convert_to_model(results=result_list)

        except HttpResponseError as error:

            if error.status_code in (401, 403):   # token bad/expired
                await self._invalidate_async_client(collection_name)
                search_client = await self._get_reusable_async_client(collection_name)
                raise VectorStoreTransientException(exception=str(error), status_code=error.status_code) from error

            elif error.status_code in [500, 503, 429, 428, 409]:
                if error.status_code == 429:
                    raise VectorStoreTransientException(exception=str(error), status_code=error.status_code) from error
                raise VectorStoreNonTransientException(exception=str(error), status_code=error.status_code) from error
            else:
                raise error
        except (ServiceRequestError, ServiceRequestTimeoutError, ServiceResponseError) as error:
            raise VectorStoreTransientException(exception=str(error), status_code=500) from error
        except AzureError as error:
            raise VectorStoreNonTransientException(exception=str(error), status_code=500) from error
        except Exception as error:
            raise  VectorStoreNonTransientException(exception=str(error), status_code=500) from error



    async def aclose(self):


        for index_name, client in self._async_client_cache.items():
            await client.close()

        if isinstance(self._async_credential, AsyncKeyCredential):
            await self._async_credential.aclose()
        elif isinstance(self._async_credential, AsyncDefaultAzureCredential):
            await self._async_credential.close()




