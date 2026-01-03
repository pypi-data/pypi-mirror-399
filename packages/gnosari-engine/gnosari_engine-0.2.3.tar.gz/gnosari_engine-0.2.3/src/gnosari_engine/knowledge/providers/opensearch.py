"""
OpenSearch provider implementation for knowledge management.
Implements IKnowledgeProvider and IKnowledgeBase interfaces following SOLID principles.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Optional, Callable

from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.exceptions import OpenSearchException

from dotenv import load_dotenv
load_dotenv()

# Import AWS dependencies for hybrid authentication
try:
    import boto3
    from requests_aws4auth import AWS4Auth
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

from ..interfaces import IKnowledgeProvider, IKnowledgeBase, IKnowledgeLoader
from ..components import Document, KnowledgeQueryResult, KnowledgeStatus
from ..loaders.loader_factory import LoaderFactory
from ..streaming import EventEmitter
from ...schemas.domain.knowledge import Knowledge


class OpenSearchKnowledgeProvider(IKnowledgeProvider):
    """OpenSearch implementation following Strategy pattern."""
    
    def __init__(self) -> None:
        """Initialize OpenSearch provider."""
        self._provider_name = "opensearch"
        self._is_initialized = False
        self._client: Optional[OpenSearch] = None
        self._knowledge_bases: dict[str, OpenSearchKnowledgeBase] = {}
        self._config: dict[str, Any] = {}
        self._logger = logging.getLogger(__name__)
    
    @property
    def provider_name(self) -> str:
        """Get the provider name identifier."""
        return self._provider_name
    
    @property
    def is_initialized(self) -> bool:
        """Check if the provider is initialized and ready to use."""
        return self._is_initialized and self._client is not None
    
    async def initialize(self, **config: Any) -> None:
        """Initialize the provider with configuration."""
        self._logger.debug(f"Initializing OpenSearch provider with config keys: {list(config.keys())}")
        self._config = config
        
        # Get OpenSearch configuration with defaults
        opensearch_config = config.get("opensearch", {})
        host = opensearch_config.get("host", os.getenv("OPENSEARCH_HOST", "localhost"))
        port = int(opensearch_config.get("port", os.getenv("OPENSEARCH_PORT", "9200")))
        
        # Handle boolean values that might come as bool or string
        use_ssl_value = opensearch_config.get("use_ssl", os.getenv("OPENSEARCH_USE_SSL", "false"))
        if isinstance(use_ssl_value, bool):
            use_ssl = use_ssl_value
        else:
            use_ssl = str(use_ssl_value).lower() == "true"
            
        verify_certs_value = opensearch_config.get("verify_certs", os.getenv("OPENSEARCH_VERIFY_CERTS", "false"))
        if isinstance(verify_certs_value, bool):
            verify_certs = verify_certs_value
        else:
            verify_certs = str(verify_certs_value).lower() == "true"
        
        # Check for AWS credentials to ensure connector operations work
        aws_secret_arn = os.getenv("AWS_OPENAI_CREDENTIALS_SECRET_ARN")
        aws_role_arn = os.getenv("AWS_OPENAI_CREDENTIALS_ROLE_ARN")
        aws_region = os.getenv("AWS_REGION")
        
        # If AWS credentials are configured, setup AWS authentication like setup adapter
        if aws_secret_arn and aws_role_arn and AWS_AVAILABLE:
            try:
                # Use same logic as setup adapter for consistency
                aws_profile = os.getenv("AWS_PROFILE")
                force_profile = os.getenv("FORCE_AWS_PROFILE", "false").lower() == "true"
                
                if aws_profile:
                    session = boto3.Session(profile_name=aws_profile)
                else:
                    session = boto3.Session()
                
                sts_client = session.client('sts', region_name=aws_region)
                
                # Check current AWS identity
                identity = sts_client.get_caller_identity()
                current_arn = identity.get('Arn', '')
                
                # Use same role assumption logic as setup adapter
                if aws_role_arn in current_arn:
                    self._logger.info(f"Already using target role via IRSA/EKS: {current_arn}")
                    # Use current session credentials directly
                    credentials = session.get_credentials()
                    access_key = credentials.access_key
                    secret_key = credentials.secret_key
                    session_token = credentials.token
                    
                elif aws_profile or force_profile:
                    # AWS profile specified or forced - assume the role for consistency
                    if force_profile:
                        self._logger.info(f"FORCE_AWS_PROFILE enabled, assuming role: {aws_role_arn}")
                    else:
                        self._logger.info(f"AWS_PROFILE specified, assuming role for data indexing: {aws_role_arn}")
                    
                    response = sts_client.assume_role(
                        RoleArn=aws_role_arn,
                        RoleSessionName='gnosari-provider'
                    )
                    
                    # Extract temporary credentials
                    temp_credentials = response['Credentials']
                    access_key = temp_credentials['AccessKeyId']
                    secret_key = temp_credentials['SecretAccessKey']
                    session_token = temp_credentials['SessionToken']
                    
                else:
                    # Default credentials or unrecognized role - try to use existing credentials
                    self._logger.info(f"Using default AWS credentials: {current_arn}")
                    credentials = session.get_credentials()
                    if not credentials:
                        raise ValueError("No AWS credentials available")
                    access_key = credentials.access_key
                    secret_key = credentials.secret_key
                    session_token = credentials.token
                
                # Store AWS credentials for potential connector operations during indexing
                self._aws_credentials = {
                    'access_key': access_key,
                    'secret_key': secret_key,
                    'session_token': session_token,
                    'region': aws_region
                }
                
                self._logger.info("AWS authentication configured for data indexing operations")
                
            except Exception as e:
                self._logger.warning(f"AWS credential setup failed: {e}")
                self._logger.warning("Data indexing may fail if OpenAI connector is used in ingest pipeline")
                if not aws_profile and not force_profile:
                    self._logger.warning("Consider setting AWS_PROFILE or FORCE_AWS_PROFILE=true for local development")
                self._aws_credentials = None
        else:
            self._aws_credentials = None
        
        # Authentication configuration for direct OpenSearch operations
        username = opensearch_config.get("username", os.getenv("OPENSEARCH_USERNAME"))
        password = opensearch_config.get("password", os.getenv("OPENSEARCH_PASSWORD"))
        
        self._logger.debug(f"OpenSearch connection config: host={host}, port={port}, use_ssl={use_ssl}, verify_certs={verify_certs}, auth={bool(username and password)}")
        
        # Create OpenSearch client
        try:
            self._logger.debug("Creating OpenSearch client instance")
            
            # Prepare client configuration
            client_config = {
                "hosts": [{"host": host, "port": port}],
                "http_compress": True,
                "use_ssl": use_ssl,
                "verify_certs": verify_certs,
                "ssl_assert_hostname": False,
                "ssl_show_warn": False,
                "connection_class": RequestsHttpConnection,
                "timeout": 30,
                "max_retries": 3,
                "retry_on_timeout": True,
            }
            
            # Add authentication if provided
            if username and password:
                client_config["http_auth"] = (username, password)
                self._logger.debug("OpenSearch authentication enabled")
            
            self._client = OpenSearch(**client_config)
            
            # Skip connection test during initialization - will be validated on first use
            self._is_initialized = True
            self._logger.info(f"OpenSearch provider initialized successfully at {host}:{port}")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize OpenSearch provider: {e}", exc_info=True)
            raise RuntimeError(f"OpenSearch initialization failed: {e}") from e
    
    async def cleanup(self) -> None:
        """Clean up provider resources."""
        if self._client:
            # Close client connection if needed
            # OpenSearch client doesn't require explicit cleanup
            pass
        
        self._knowledge_bases.clear()
        self._is_initialized = False
        self._logger.info("OpenSearch provider cleaned up")
    
    async def create_knowledge_base(self, knowledge: Knowledge) -> IKnowledgeBase:
        """Create a new knowledge base from Knowledge domain object."""
        self._logger.debug(f"Creating knowledge base for: {knowledge.id}")
        
        if not self.is_initialized:
            self._logger.error("Attempted to create knowledge base with uninitialized provider")
            raise RuntimeError("Provider not initialized")
        
        # Create knowledge base instance
        kb = OpenSearchKnowledgeBase(
            knowledge=knowledge,
            client=self._client,
            config=self._config
        )
        
        # Store reference
        self._knowledge_bases[knowledge.id] = kb
        
        self._logger.info(f"Created knowledge base: {knowledge.id}")
        return kb
    
    async def get_knowledge_base(self, knowledge_id: str) -> IKnowledgeBase | None:
        """Retrieve an existing knowledge base by ID."""
        self._logger.debug(f"Getting knowledge base: {knowledge_id}")
        kb = self._knowledge_bases.get(knowledge_id)
        if kb:
            self._logger.debug(f"Found knowledge base: {knowledge_id}")
        else:
            self._logger.debug(f"Knowledge base not found: {knowledge_id}")
        return kb
    
    async def delete_knowledge_base(self, knowledge_id: str) -> bool:
        """Delete a knowledge base by ID."""
        self._logger.debug(f"Deleting knowledge base: {knowledge_id}")
        
        if not self.is_initialized:
            self._logger.error("Attempted to delete knowledge base with uninitialized provider")
            raise RuntimeError("Provider not initialized")
        
        kb = self._knowledge_bases.get(knowledge_id)
        if not kb:
            self._logger.warning(f"Knowledge base not found for deletion: {knowledge_id}")
            return False
        
        try:
            # Delete the OpenSearch index
            index_name = f"kb_{knowledge_id}"
            self._logger.debug(f"Deleting OpenSearch index: {index_name}")
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._client.indices.delete(index=index_name)
            )
            
            # Remove from tracking
            del self._knowledge_bases[knowledge_id]
            
            self._logger.info(f"Deleted knowledge base: {knowledge_id}")
            return True
            
        except OpenSearchException as e:
            self._logger.error(f"Failed to delete knowledge base {knowledge_id}: {e}", exc_info=True)
            return False


class OpenSearchKnowledgeBase(IKnowledgeBase):
    """OpenSearch knowledge base implementation."""
    
    def __init__(
        self, 
        knowledge: Knowledge, 
        client: OpenSearch, 
        config: dict[str, Any]
    ) -> None:
        """Initialize OpenSearch knowledge base."""
        self._knowledge = knowledge
        self._client = client
        self._config = config
        self._is_initialized = False
        self._index_name = f"gnosari_{knowledge.id}"  # Match old adapter naming
        self._logger = logging.getLogger(__name__)
        
        # Get effective configuration from knowledge object
        self._effective_config = knowledge.get_effective_config()
        
        # Initialize loader factory for data loading
        self._loader_factory = LoaderFactory(self._effective_config.get("loader_config", {}))
        
        # Cache for tracking loaded data sources
        self._loaded_sources: set[str] = set()
        
        # Bulk processing configuration
        self._bulk_batch_size = self._effective_config.get("bulk_batch_size", 5)
        
        
        self._logger.debug(f"Created OpenSearchKnowledgeBase for {knowledge.id} with index {self._index_name}")
        self._logger.debug(f"Effective config keys: {list(self._effective_config.keys())}")
    
    @property
    def knowledge_id(self) -> str:
        """Get the knowledge base identifier."""
        return self._knowledge.id
    
    @property
    def is_initialized(self) -> bool:
        """Check if the knowledge base is initialized and ready."""
        return self._is_initialized
    
    async def initialize(self) -> None:
        """Initialize the knowledge base."""
        self._logger.debug(f"Initializing knowledge base {self.knowledge_id}")
        
        try:
            # Check if index exists
            self._logger.debug(f"Checking if index exists: {self._index_name}")
            index_exists = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._client.indices.exists(index=self._index_name)
            )
            self._logger.debug(f"Index {self._index_name} exists: {index_exists}")
            
            if not index_exists:
                # Create index with appropriate mapping
                self._logger.debug(f"Creating new index: {self._index_name}")
                await self._create_index()
            else:
                self._logger.debug(f"Using existing index: {self._index_name}")
            
            self._is_initialized = True
            self._logger.info(f"Knowledge base {self.knowledge_id} initialized")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize knowledge base {self.knowledge_id}: {e}", exc_info=True)
            raise RuntimeError(f"Knowledge base initialization failed: {e}") from e

    async def add_data_source(self, data_source: str, **options: Any) -> int:
        """Add a data source to the knowledge base with bulk indexing."""
        self._logger.info(f"Adding data source {data_source} to knowledge base {self.knowledge_id}")
        self._logger.debug(f"Options: {options}")
        
        if not self.is_initialized:
            self._logger.error(f"Attempted to add data source to uninitialized knowledge base {self.knowledge_id}")
            raise RuntimeError("Knowledge base not initialized")
        
        try:
            # Check if we need to force reload
            force_reload = options.get("force_reload", False)
            
            if not force_reload and data_source in self._loaded_sources:
                self._logger.info(f"Data source '{data_source}' already loaded in knowledge base {self.knowledge_id}")
                return 0
            
            if force_reload:
                await self._handle_force_reload()

            # Extract event emitter from options for progress tracking
            event_emitter = options.get("event_emitter", None)

            # Get the appropriate loader for the source type
            # Create a fresh loader instance with event_emitter for this specific load operation
            source_type = self._knowledge.source_type or self._detect_source_type(data_source)
            loader = self._create_loader_with_event_emitter(source_type, event_emitter)

            if not loader:
                raise ValueError(f"No loader available for source type: {source_type}")

            self._logger.info(f"Using {type(loader).__name__} for source type: {source_type}")
            
            # Verify pipeline on first data load (lazy verification)
            await self._verify_ingest_pipeline()
            
            # Use streaming loader for real-time bulk indexing
            total_indexed = 0
            total_failed = 0
            batch_counter = 0
            
            def bulk_index_callback(batch_documents: list[Document]) -> None:
                """Callback function to index documents as they're loaded."""
                nonlocal total_indexed, total_failed, batch_counter
                batch_counter += 1
                
                if not batch_documents:
                    return
                
                # Convert documents to OpenSearch bulk format
                bulk_body = []
                for j, doc in enumerate(batch_documents):
                    doc_id = f"{data_source}_{total_indexed + total_failed + j}"
                    
                    # Add index operation metadata
                    bulk_body.append({
                        "index": {
                            "_index": self._index_name,
                            "_id": doc_id
                        }
                    })
                    
                    # Add document body (embeddings generated by ingest pipeline if configured)
                    # Use "text" field to match standard pipeline field mapping from setup script
                    bulk_body.append({
                        "text": doc.content,  # Use "text" field (standard field name)
                        "metadata": doc.metadata,
                        "source": data_source,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Perform bulk indexing for this batch
                try:
                    response = self._client.bulk(body=bulk_body)
                    
                    # Check for bulk operation errors
                    failed_items = []
                    if response.get('errors'):
                        failed_items = [item for item in response['items'] 
                                      if 'error' in item.get('index', {})]
                        if failed_items:
                            total_failed += len(failed_items)
                            self._logger.warning(f"Batch {batch_counter}: {len(failed_items)} documents failed to index")
                            for item in failed_items[:2]:  # Log first 2 failures
                                error = item['index'].get('error', {})
                                self._logger.error(f"Index error: {error.get('reason', 'Unknown error')}")
                                self._logger.error(f"Full error details: {error}")
                    
                    # Log successful indexing and check if vectors were generated
                    successful_items = [item for item in response['items'] 
                                      if 'error' not in item.get('index', {})]
                    if successful_items:
                        # Sample first successful item to check if vector was generated
                        sample_id = successful_items[0]['index']['_id']
                        self._logger.debug(f"Checking if vector was generated for document: {sample_id}")
                        
                        # Get the document to verify vector field
                        try:
                            doc_response = self._client.get(index=self._index_name, id=sample_id)
                            doc_source = doc_response.get('_source', {})
                            has_vector = 'embedding' in doc_source
                            if has_vector:
                                vector_field = doc_source['embedding']
                                vector_size = len(vector_field) if isinstance(vector_field, list) else "unknown"
                                self._logger.info(f"✓ Vector field 'embedding' generated successfully for document {sample_id} (size: {vector_size})")
                            else:
                                self._logger.warning(f"⚠ Vector field 'embedding' NOT generated for document {sample_id}. Pipeline may not be working.")
                                self._logger.warning(f"Available fields: {list(doc_source.keys())}")
                                # Check if there are any vector-like fields
                                vector_fields = [k for k, v in doc_source.items() if isinstance(v, list) and len(v) > 100]
                                if vector_fields:
                                    self._logger.info(f"Found potential vector fields: {vector_fields}")
                        except Exception as check_error:
                            self._logger.warning(f"Could not verify vector generation: {check_error}")
                    
                    successful_in_batch = len(batch_documents) - len(failed_items)
                    total_indexed += successful_in_batch
                    
                    self._logger.debug(f"Batch {batch_counter}: indexed {successful_in_batch}/{len(batch_documents)} documents")
                    
                except Exception as e:
                    total_failed += len(batch_documents)
                    self._logger.error(f"Batch {batch_counter} indexing failed: {e}")
            
            # Load data with streaming callback for real-time indexing
            if hasattr(loader, 'load_data_streaming'):
                total_documents = await loader.load_data_streaming(
                    data_source,
                    bulk_index_callback,
                    self._bulk_batch_size,
                    **options
                )
            else:
                # Fallback to regular loading and manual batching
                documents = await loader.load_data(data_source, **options)
                total_documents = len(documents)
                
                # Process in batches
                for i in range(0, len(documents), self._bulk_batch_size):
                    batch = documents[i:i + self._bulk_batch_size]
                    bulk_index_callback(batch)
            
            # Refresh index to make documents searchable
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._client.indices.refresh(index=self._index_name)
            )
            
            # Mark as successfully loaded
            self._loaded_sources.add(data_source)
            
            # Log final summary
            if total_failed > 0:
                self._logger.warning(f"Indexing summary: {total_indexed} successful, {total_failed} failed out of {total_documents} documents")
            else:
                self._logger.info(f"Successfully indexed all {total_indexed} documents from {data_source}")
            
            return total_indexed
            
        except Exception as e:
            self._logger.error(f"Failed to add data source {data_source} to knowledge base {self.knowledge_id}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to add data source: {e}") from e
    
    async def query(self, query: str, **options: Any) -> KnowledgeQueryResult:
        """Query the knowledge base using vector search."""
        self._logger.debug(f"Querying knowledge base {self.knowledge_id} with query: {query[:100]}...")
        self._logger.debug(f"Query options: {options}")
        
        if not self.is_initialized:
            self._logger.error(f"Attempted to query uninitialized knowledge base {self.knowledge_id}")
            raise RuntimeError("Knowledge base not initialized")
        
        try:
            start_time = datetime.now()
            
            # Default search parameters
            size = options.get("size", 10)
            score_threshold = options.get("score_threshold", 0.7)
            
            self._logger.debug(f"Search parameters: size={size}, score_threshold={score_threshold}")
            
            # Construct OpenSearch query for vector search or fallback to text search
            opensearch_config = self._effective_config.get("opensearch", {})
            model_id = os.getenv("OPENSEARCH_MODEL_ID")
            
            self._logger.debug(f"OpenSearch config: {opensearch_config}")
            self._logger.debug(f"OPENSEARCH_MODEL_ID from env: {os.getenv('OPENSEARCH_MODEL_ID')}")
            self._logger.debug(f"Final model_id: {model_id}")
            
            if model_id:
                # Use semantic search with neural query (using standard field names)
                search_body = {
                    "size": size,
                    "query": {
                        "neural": {
                            "embedding": {  # Standard vector field name
                                "query_text": query,
                                "model_id": model_id,
                                "k": size * 2  # Get more candidates for better results
                            }
                        }
                    },
                    # "min_score": score_threshold,
                    "_source": ["text", "metadata", "source"]  # Standard field names
                }
            else:
                # Fallback to text search
                self._logger.warning("No model_id configured, falling back to text search")
                search_body = {
                    "size": size,
                    "query": {
                        "match": {
                            "text": query  # Use standard field name
                        }
                    },
                    "min_score": score_threshold,
                    "_source": ["text", "metadata", "source"]  # Standard field names
                }
            
            self._logger.debug(f"OpenSearch query body: {search_body}")
            
            # Execute search
            self._logger.info(f"Executing search on index: {self._index_name}")
            self._logger.info(f"Search body: {search_body}")
            try:
                self._logger.info("About to execute OpenSearch query...")
                response = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self._client.search(body=search_body, index=self._index_name)
                )
                self._logger.info(f"OpenSearch response received successfully!")
                self._logger.info(f"Response hits: {len(response.get('hits', {}).get('hits', []))} hits")
                self._logger.debug(f"Full response: {response}")
                
                # Check for search errors in response
                if response.get('timed_out'):
                    self._logger.warning(f"Search timed out for query: {query[:50]}...")
                
                shards = response.get('_shards', {})
                if shards.get('failed', 0) > 0:
                    self._logger.error(f"Search failed on {shards['failed']} shards. Failures: {shards.get('failures', [])}")
                    
            except Exception as search_error:
                self._logger.error(f"OpenSearch query execution failed: {search_error}", exc_info=True)
                self._logger.error(f"Failed query body: {search_body}")
                self._logger.error(f"Index: {self._index_name}")
                self._logger.error(f"Exception type: {type(search_error)}")
                raise
            
            # Convert results to Document objects
            documents = []
            hits = response.get("hits", {}).get("hits", [])
            
            for i, hit in enumerate(hits):
                source = hit["_source"]
                score = hit.get("_score", 0)
                doc = Document(
                    content=source.get("text", ""),  # Use standard field name
                    metadata=source.get("metadata", {}),
                    source=source.get("source", ""),
                    doc_id=hit["_id"]
                )
                documents.append(doc)
                self._logger.debug(f"Document {i}: score={score}, source={source.get('source', '')[:50]}...")
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            total_found = response.get("hits", {}).get("total", {}).get("value", 0)
            max_score = response.get("hits", {}).get("max_score")
            
            self._logger.debug(f"Query completed: {len(documents)} documents, {total_found} total, {execution_time:.2f}ms")
            
            return KnowledgeQueryResult(
                results=documents,
                query=query,
                total_found=total_found,
                execution_time_ms=execution_time,
                metadata={
                    "max_score": max_score,
                    "search_params": options
                }
            )
            
        except Exception as e:
            self._logger.error(f"Query failed for knowledge base {self.knowledge_id}: {e}", exc_info=True)
            raise RuntimeError(f"Query execution failed: {e}") from e
    
    async def get_status(self) -> KnowledgeStatus:
        """Get current status of the knowledge base."""
        self._logger.debug(f"Getting status for knowledge base {self.knowledge_id}")
        
        try:
            if not self._is_initialized:
                self._logger.debug(f"Knowledge base {self.knowledge_id} not initialized")
                return KnowledgeStatus(
                    knowledge_id=self.knowledge_id,
                    document_count=0,
                    status="empty",
                    provider="opensearch"
                )
            
            # Get index stats
            self._logger.debug(f"Getting stats for index: {self._index_name}")
            stats = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._client.indices.stats(index=self._index_name)
            )
            
            index_stats = stats.get("indices", {}).get(self._index_name, {})
            doc_count = index_stats.get("total", {}).get("docs", {}).get("count", 0)
            index_size = index_stats.get("total", {}).get("store", {}).get("size_in_bytes", 0)
            
            self._logger.debug(f"Index stats: doc_count={doc_count}, size={index_size} bytes")
            
            status = "ready" if doc_count > 0 else "empty"
            
            return KnowledgeStatus(
                knowledge_id=self.knowledge_id,
                document_count=doc_count,
                last_updated=datetime.now(),  # TODO: Track actual last update time
                status=status,
                provider="opensearch",
                metadata={
                    "index_name": self._index_name,
                    "index_size": index_size
                }
            )
            
        except Exception as e:
            self._logger.error(f"Failed to get status for knowledge base {self.knowledge_id}: {e}", exc_info=True)
            return KnowledgeStatus(
                knowledge_id=self.knowledge_id,
                document_count=0,
                status="error",
                provider="opensearch",
                metadata={"error": str(e)}
            )
    
    async def _create_index(self) -> None:
        """Create OpenSearch index with enhanced mapping and ingest pipeline support."""
        self._logger.debug(f"Creating OpenSearch index with mapping for {self._index_name}")
        
        opensearch_config = self._effective_config.get("opensearch", {})
        embedding_dimension = opensearch_config.get("embedding_dimension", 1536)
        model_id = os.getenv("OPENSEARCH_MODEL_ID")
        pipeline_name = os.getenv("OPENSEARCH_PIPELINE_NAME")
        
        self._logger.debug(f"Environment variables: MODEL_ID={os.getenv('OPENSEARCH_MODEL_ID')}, PIPELINE_NAME={os.getenv('OPENSEARCH_PIPELINE_NAME')}")
        self._logger.debug(f"OpenSearch config from knowledge: {opensearch_config}")
        self._logger.debug(f"Final values: model_id={model_id}, pipeline_name={pipeline_name}")
        
        self._logger.debug(f"Index configuration: embedding_dimension={embedding_dimension}, model_id={model_id}, pipeline_name={pipeline_name}")
        
        # Enhanced mapping with ingest pipeline support
        mapping = {
            "settings": {
                "index": {
                    "knn": True,
                    "number_of_shards": opensearch_config.get("number_of_shards", 1),
                    "number_of_replicas": opensearch_config.get("number_of_replicas", 1)
                }
            },
            "mappings": {
                "properties": {
                    "text": {"type": "text"},  # Standard text field name
                    "embedding": {  # Standard vector field name
                        "type": "knn_vector",
                        "dimension": embedding_dimension,
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosinesimil",
                            "engine": "lucene",
                            "parameters": {
                                "ef_construction": 512,
                                "m": 16
                            }
                        }
                    },
                    "metadata": {"type": "object"},
                    "source": {"type": "keyword"},
                    "timestamp": {"type": "date"}
                }
            }
        }

        self._logger.debug(f"Pipeline Name: {pipeline_name} -  Model ID: {model_id}")
        # Add ingest pipeline to index settings if available
        if pipeline_name and model_id:
            mapping["settings"]["index"]["default_pipeline"] = pipeline_name
            self._logger.info(f"Configured index to use ingest pipeline: {pipeline_name}")
        elif model_id:
            self._logger.warning(f"Model ID available ({model_id}) but no pipeline_name configured. Embeddings will not be generated automatically.")
        
        self._logger.debug(f"Index mapping: {mapping}")
        
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: self._client.indices.create(index=self._index_name, body=mapping)
        )
        
        self._logger.info(f"Created OpenSearch index: {self._index_name}")
    
    async def _handle_force_reload(self) -> None:
        """Handle force reload by recreating index."""
        self._logger.info(f"Force reload requested for index {self._index_name}")
        
        try:
            # Delete existing index if it exists
            index_exists = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._client.indices.exists(index=self._index_name)
            )
            
            if index_exists:
                await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self._client.indices.delete(index=self._index_name)
                )
                self._logger.info(f"Deleted existing index: {self._index_name}")
            
            # Recreate the index
            await self._create_index()
            
            # Clear loaded sources cache
            self._loaded_sources.clear()
            
            self._logger.info(f"Index {self._index_name} recreated for force reload")
            
        except Exception as e:
            raise RuntimeError(f"Failed to handle force reload for index '{self._index_name}': {e}") from e
    
    async def _verify_ingest_pipeline(self) -> None:
        """Verify that the ingest pipeline exists and is properly configured."""
        pipeline_name = os.getenv("OPENSEARCH_PIPELINE_NAME")
        model_id = os.getenv("OPENSEARCH_MODEL_ID")
        
        if not pipeline_name:
            self._logger.warning("No OPENSEARCH_PIPELINE_NAME configured. Vector generation will not work.")
            return
        
        if not model_id:
            self._logger.warning("No OPENSEARCH_MODEL_ID configured. Vector generation will not work.")
            return
        
        try:
            # Check if pipeline exists
            pipeline_response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._client.ingest.get_pipeline(id=pipeline_name)
            )
            
            if pipeline_name in pipeline_response:
                self._logger.info(f"✓ Ingest pipeline '{pipeline_name}' exists and is configured")
                pipeline_config = pipeline_response[pipeline_name]
                self._logger.debug(f"Pipeline configuration: {pipeline_config}")
                
                # Check if the pipeline has the expected model_id and field mapping
                processors = pipeline_config.get('processors', [])
                text_embedding_processors = [p for p in processors if 'text_embedding' in p]
                
                if text_embedding_processors:
                    for processor in text_embedding_processors:
                        text_embedding_config = processor.get('text_embedding', {})
                        processor_model_id = text_embedding_config.get('model_id')
                        field_map = text_embedding_config.get('field_map', {})
                        
                        if processor_model_id == model_id:
                            self._logger.info(f"✓ Pipeline uses correct model_id: {model_id}")
                        else:
                            self._logger.warning(f"⚠ Pipeline model_id ({processor_model_id}) differs from env model_id ({model_id})")
                        
                        # Check field mapping (using standard field names)
                        self._logger.info(f"Pipeline field mapping: {field_map}")
                        if 'text' in field_map:
                            target_field = field_map['text']
                            if target_field == 'embedding':
                                self._logger.info(f"✓ Pipeline correctly maps 'text' → 'embedding'")
                            else:
                                self._logger.warning(f"⚠ Pipeline maps 'text' → '{target_field}' (expected 'embedding')")
                        else:
                            self._logger.warning(f"⚠ Pipeline doesn't map 'text' field. Available mappings: {field_map}")
                            if field_map:
                                input_field = list(field_map.keys())[0]
                                output_field = field_map[input_field]
                                self._logger.warning(f"💡 Pipeline maps '{input_field}' → '{output_field}'. Expected 'text' → 'embedding'.")
                else:
                    self._logger.warning(f"⚠ Pipeline '{pipeline_name}' has no text_embedding processors")
            else:
                self._logger.error(f"❌ Ingest pipeline '{pipeline_name}' not found!")
                
        except Exception as e:
            self._logger.error(f"Failed to verify ingest pipeline '{pipeline_name}': {e}")
            self._logger.warning("Vector generation may not work properly")

    def _create_loader_with_event_emitter(self, source_type: str, event_emitter) -> IKnowledgeLoader | None:
        """
        Create a fresh loader instance with event emitter for this specific load operation.

        Args:
            source_type: Type of source (sitemap, website, etc.)
            event_emitter: EventEmitter instance for progress tracking

        Returns:
            Fresh loader instance configured with event emitter, or None if not supported
        """
        from ..loaders.sitemap import SitemapLoader
        from ..loaders.website import WebsiteLoader
        from ..loaders.file import FileLoader

        # Get loader config for this source type
        loader_config = self._effective_config.get("loader_config", {}).get(source_type, {})

        # Create appropriate loader with event emitter
        if source_type == "sitemap":
            return SitemapLoader(loader_config, event_emitter=event_emitter)
        elif source_type == "website":
            return WebsiteLoader(loader_config, event_emitter=event_emitter)
        elif source_type == "file":
            return FileLoader(loader_config, event_emitter=event_emitter)
        else:
            # Fall back to factory's shared loader if source type not recognized
            self._logger.warning(f"Unknown source type '{source_type}', using factory loader")
            return self._loader_factory.get_loader(source_type)

    def _detect_source_type(self, source: str) -> str:
        """Detect source type from source string."""
        source_lower = source.lower()

        # URL detection
        if source_lower.startswith(('http://', 'https://')):
            if 'sitemap' in source_lower or source_lower.endswith('.xml'):
                return "sitemap"
            else:
                return "website"

        # File detection
        if source_lower.endswith('.xml') and ('sitemap' in source_lower or 'site-map' in source_lower):
            return "sitemap"

        # Default to website
        return "website"


__all__ = [
    "OpenSearchKnowledgeProvider",
    "OpenSearchKnowledgeBase",
]