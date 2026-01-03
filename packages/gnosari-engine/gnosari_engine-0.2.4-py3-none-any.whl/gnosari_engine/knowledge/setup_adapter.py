"""
OpenSearch Setup Adapter for initializing semantic search infrastructure.
Provides the advanced setup operations needed for the CLI setup command.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict

import boto3
import requests
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.exceptions import OpenSearchException


class OpenSearchSetupAdapter:
    """
    Adapter for setting up OpenSearch semantic search infrastructure.
    
    This class handles the complex setup operations required for:
    - OpenAI embedding model connector
    - Model group and deployment
    - Ingest pipeline for automatic text embedding
    - Search pipeline for hybrid search
    - Vector index creation
    - Sample data ingestion
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the setup adapter with configuration."""
        self._config = config
        self._logger = logging.getLogger(__name__)
        
        # Extract OpenSearch connection details with environment variable fallbacks
        opensearch_config = config.get("opensearch", {})
        host = opensearch_config.get("host", os.getenv("OPENSEARCH_HOST", "localhost"))
        port = int(opensearch_config.get("port", os.getenv("OPENSEARCH_PORT", "9200")))
        use_ssl = opensearch_config.get("use_ssl", os.getenv("OPENSEARCH_USE_SSL", "false").lower() == "true")
        verify_certs = opensearch_config.get("verify_certs", os.getenv("OPENSEARCH_VERIFY_CERTS", "false").lower() == "true")
        
        # Check for AWS credentials for OpenAI connector
        aws_secret_arn = os.getenv("AWS_OPENAI_CREDENTIALS_SECRET_ARN")
        aws_role_arn = os.getenv("AWS_OPENAI_CREDENTIALS_ROLE_ARN")
        aws_region = os.getenv("AWS_REGION")
        
        # Store AWS credentials for connector operations only
        self._aws_secret_arn = aws_secret_arn
        self._aws_role_arn = aws_role_arn
        self._aws_region = aws_region
        self._awsauth = None
        
        if aws_secret_arn and aws_role_arn:
            # Setup AWS authentication for connector operations only
            self._use_aws_auth = True
            self._host = host
            self._port = port
            self._use_ssl = use_ssl
            
            if not aws_region:
                raise ValueError("AWS_REGION environment variable is required when using AWS credentials")
            
            # Get AWS credentials - handle both local development and EKS/IRSA scenarios
            aws_profile = os.getenv("AWS_PROFILE")
            force_profile = os.getenv("FORCE_AWS_PROFILE", "false").lower() == "true"
            
            if aws_profile:
                session = boto3.Session(profile_name=aws_profile)
            else:
                session = boto3.Session()
            
            sts_client = session.client('sts', region_name=aws_region)
            
            try:
                # Check current AWS identity
                identity = sts_client.get_caller_identity()
                current_arn = identity.get('Arn', '')
                
                # Check if we're already using the target role (EKS/IRSA scenario)
                # OR if we're using any AWS role that might have cross-account permissions
                if aws_role_arn in current_arn:
                    self._logger.info(f"Already using target role via IRSA/EKS: {current_arn}")
                    # Use current session credentials directly
                    credentials = session.get_credentials()
                    access_key = credentials.access_key
                    secret_key = credentials.secret_key
                    session_token = credentials.token
                    
                elif aws_profile or force_profile:
                    # AWS profile specified or forced - always prefer role assumption for consistency
                    if force_profile:
                        self._logger.info(f"FORCE_AWS_PROFILE enabled, assuming role: {aws_role_arn}")
                    else:
                        self._logger.info(f"AWS_PROFILE specified, assuming role for consistency: {aws_role_arn}")
                    
                    response = sts_client.assume_role(
                        RoleArn=aws_role_arn,
                        RoleSessionName='gnosari-setup'
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
                
                # Create AWS4Auth for connector operations only
                self._awsauth = AWS4Auth(
                    access_key, 
                    secret_key, 
                    aws_region,
                    'es',
                    session_token=session_token
                )
                
                self._logger.info("AWS authentication configured for connector operations")
                
            except Exception as e:
                error_msg = f"Failed to configure AWS authentication: {str(e)}"
                if not aws_profile:
                    error_msg += ". Consider setting AWS_PROFILE for local development"
                raise ValueError(error_msg)
            
            self._logger.info(f"AWS authentication available for connector operations")
        else:
            self._use_aws_auth = False
        
        # Always create OpenSearch client for regular operations (pipelines, indexes, etc.)
        # Handle authentication from config or environment
        http_auth = opensearch_config.get("http_auth")
        if not http_auth and os.getenv("OPENSEARCH_USERNAME") and os.getenv("OPENSEARCH_PASSWORD"):
            http_auth = (os.getenv("OPENSEARCH_USERNAME"), os.getenv("OPENSEARCH_PASSWORD"))
        
        # Create OpenSearch client with timeout and retry configuration from environment
        timeout = int(os.getenv("OPENSEARCH_TIMEOUT", "30"))
        client_config = {
            "hosts": [{"host": host, "port": port}],
            "http_compress": True,
            "use_ssl": use_ssl,
            "verify_certs": verify_certs,
            "ssl_assert_hostname": False,
            "ssl_show_warn": False,
            "connection_class": RequestsHttpConnection,
            "timeout": timeout,
            "max_retries": 3,
            "retry_on_timeout": True,
        }
        
        if http_auth:
            client_config["http_auth"] = http_auth
        
        # Add CA certs if specified in environment
        ca_certs = os.getenv("OPENSEARCH_CA_CERTS")
        if ca_certs:
            client_config["ca_certs"] = ca_certs
        
        self._client = OpenSearch(**client_config)
        self._logger.info(f"Using username/password authentication for OpenSearch operations at {host}:{port}")
        
        if self._use_aws_auth:
            self._logger.info(f"Using AWS authentication for connector operations")
        
        # Setup constants from environment variables with fallbacks
        self._connector_name = os.getenv("OPENSEARCH_CONNECTOR_NAME", "gnosari-openai-connector")
        self._model_group_name = os.getenv("OPENSEARCH_MODEL_GROUP_NAME", "gnosari-model-group")
        self._model_name = os.getenv("OPENSEARCH_MODEL_NAME", "gnosari-embedding-model")
        self._ingest_pipeline_name = os.getenv("OPENSEARCH_PIPELINE_NAME", "gnosari-ingest-pipeline")
        self._search_pipeline_name = os.getenv("OPENSEARCH_SEARCH_PIPELINE_NAME", "gnosari-search-pipeline")
        self._index_name = os.getenv("OPENSEARCH_INDEX_NAME", "gnosari-sample-index")
        
        # OpenAI configuration from environment
        self._openai_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
        self._embedding_dimension = int(os.getenv("OPENAI_EMBEDDING_DIMENSION", "1536"))
        
        # Vector search configuration from environment
        self._vector_space_type = os.getenv("VECTOR_SPACE_TYPE", "cosinesimil")
        self._vector_method = os.getenv("VECTOR_METHOD", "hnsw")
        
        # Initialize instance variables to avoid setting them outside __init__
        self._connector_id: str = ""
        self._model_group_id: str = ""
        
        # Will be set during deployment
        self.model_id = None
    
    async def _make_aws_request(self, method: str, path: str, data: dict = None) -> dict:
        """Helper method to make AWS authenticated requests to OpenSearch."""
        protocol = "https" if self._use_ssl else "http"
        url = f"{protocol}://{self._host}:{self._port}{path}"
        headers = {"Content-Type": "application/json"}
        
        def make_request():
            if method == "GET":
                return requests.get(url, auth=self._awsauth, headers=headers, timeout=30)
            elif method == "POST":
                return requests.post(url, auth=self._awsauth, json=data, headers=headers, timeout=30)
            elif method == "PUT":
                return requests.put(url, auth=self._awsauth, json=data, headers=headers, timeout=30)
            elif method == "DELETE":
                return requests.delete(url, auth=self._awsauth, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        
        response = await asyncio.get_event_loop().run_in_executor(None, make_request)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
    
    async def create_openai_connector(self) -> Dict[str, Any]:
        """Create OpenAI connector for embedding model."""
        self._logger.info("Creating OpenAI connector")
        
        try:
            # Check for AWS credentials first, fall back to direct API key
            aws_secret_arn = os.getenv("AWS_OPENAI_CREDENTIALS_SECRET_ARN")
            aws_role_arn = os.getenv("AWS_OPENAI_CREDENTIALS_ROLE_ARN")
            
            if aws_secret_arn and aws_role_arn:
                # Use AWS credentials
                credential_config = {
                    "secretArn": aws_secret_arn,
                    "roleArn": aws_role_arn
                }
                auth_header = "Bearer ${credential.secretArn.my_openai_key}"
                self._logger.info("Using AWS credentials for OpenAI connector")
            else:
                # Use direct API key
                openai_api_key = os.getenv("OPENAI_API_KEY")
                if not openai_api_key:
                    raise ValueError("Either OPENAI_API_KEY or both AWS_OPENAI_CREDENTIALS_SECRET_ARN and AWS_OPENAI_CREDENTIALS_ROLE_ARN environment variables are required")
                credential_config = {
                    "openAI_key": openai_api_key
                }
                auth_header = "Bearer ${credential.openAI_key}"
                self._logger.info("Using direct API key for OpenAI connector")
            
            connector_config = {
                "name": self._connector_name,
                "description": f"Connector for {self._openai_model} model",
                "version": "1.0",
                "protocol": "http",
                "credential": credential_config,
                "parameters": {
                    "model": self._openai_model
                },
                "actions": [
                    {
                        "action_type": "predict",
                        "method": "POST",
                        "url": os.getenv("OPENAI_EMBEDDINGS_API_URL", "https://api.openai.com/v1/embeddings"),
                        "headers": {
                            "Authorization": auth_header
                        },
                        "request_body": "{ \"input\": ${parameters.input}, \"model\": \"${parameters.model}\" }",
                        "pre_process_function": "connector.pre_process.openai.embedding",
                        "post_process_function": "connector.post_process.openai.embedding"
                    }
                ]
            }

            
            if self._use_aws_auth:
                # Use AWS4Auth
                result = await self._make_aws_request("POST", "/_plugins/_ml/connectors/_create", connector_config)
                self._connector_id = result["connector_id"]
                self._logger.info(f"Created OpenAI connector: {self._connector_id}")
                return {"success": True, "connector_id": self._connector_id}
            else:
                # Use opensearchpy client
                response = await asyncio.get_event_loop().run_in_executor(
                    None, self._client.transport.perform_request, 
                    "POST", "/_plugins/_ml/connectors/_create", {}, connector_config
                )
                
                self._connector_id = response["connector_id"]
                self._logger.info(f"Created OpenAI connector: {self._connector_id}")
                
                return {"success": True, "connector_id": self._connector_id}
            
        except Exception as e:
            self._logger.error(f"Failed to create OpenAI connector: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_model_group(self) -> Dict[str, Any]:
        """Create model group for organizing models."""
        self._logger.info("Creating model group")
        
        try:
            model_group_config = {
                "name": self._model_group_name,
                "description": f"Model group for {self._openai_model} models"
            }
            
            # Always use regular client for model group operations
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._client.transport.perform_request,
                "POST", "/_plugins/_ml/model_groups/_register", {}, model_group_config
            )
            self._model_group_id = response["model_group_id"]
            
            self._logger.info(f"Created model group: {self._model_group_id}")
            return {"success": True, "model_group_id": self._model_group_id}
            
        except Exception as e:
            self._logger.error(f"Failed to create model group: {e}")
            return {"success": False, "error": str(e)}
    
    async def deploy_embedding_model(self) -> Dict[str, Any]:
        """Deploy the embedding model."""
        self._logger.info("Deploying embedding model")
        
        try:
            if not hasattr(self, '_connector_id') or not hasattr(self, '_model_group_id'):
                raise ValueError("Connector and model group must be created first")
            
            model_config = {
                "name": self._model_name,
                "function_name": "remote",
                "description": f"OpenAI {self._openai_model} model",
                "model_group_id": self._model_group_id,
                "connector_id": self._connector_id
            }
            
            # Register the model - always use regular client
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._client.transport.perform_request,
                "POST", "/_plugins/_ml/models/_register", {}, model_config
            )
            
            task_id = response["task_id"]
            self._logger.info(f"Model registration task: {task_id}")
            
            # Wait for registration to complete
            await self._wait_for_task_completion(task_id)
            
            # Get the model ID - always use regular client
            task_response = await asyncio.get_event_loop().run_in_executor(
                None, self._client.transport.perform_request,
                "GET", f"/_plugins/_ml/tasks/{task_id}"
            )
            
            self.model_id = task_response["model_id"]
            self._logger.info(f"Model registered: {self.model_id}")
            
            # Deploy the model - always use regular client
            deploy_response = await asyncio.get_event_loop().run_in_executor(
                None, self._client.transport.perform_request,
                "POST", f"/_plugins/_ml/models/{self.model_id}/_deploy"
            )
            
            deploy_task_id = deploy_response["task_id"]
            await self._wait_for_task_completion(deploy_task_id)
            
            self._logger.info(f"Model deployed successfully: {self.model_id}")
            
            return {"success": True, "model_id": self.model_id}
            
        except Exception as e:
            self._logger.error(f"Failed to deploy embedding model: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_ingest_pipeline(self) -> Dict[str, Any]:
        """Create ingest pipeline for automatic text embedding."""
        self._logger.info("Creating ingest pipeline")
        
        try:
            if not self.model_id:
                raise ValueError("Model must be deployed first")
            
            # Check if pipeline already exists - always use regular client
            try:
                existing_pipeline = await asyncio.get_event_loop().run_in_executor(
                    None, self._client.ingest.get_pipeline, self._ingest_pipeline_name
                )
                
                if self._ingest_pipeline_name in existing_pipeline:
                    self._logger.info(f"Pipeline {self._ingest_pipeline_name} already exists, updating with new model ID")
                    # Delete existing pipeline first
                    await asyncio.get_event_loop().run_in_executor(
                        None, self._client.ingest.delete_pipeline, self._ingest_pipeline_name
                    )
                    self._logger.info(f"Deleted existing pipeline to update with new model ID")
            except Exception:
                # Pipeline doesn't exist, which is fine
                pass
            
            pipeline_config = {
                "description": "Gnosari ingest pipeline for text embedding",
                "processors": [
                    {
                        "text_embedding": {
                            "model_id": self.model_id,
                            "field_map": {
                                "text": "embedding"
                            }
                        }
                    }
                ]
            }
            
            # Always use regular client for pipeline operations
            await asyncio.get_event_loop().run_in_executor(
                None, self._client.ingest.put_pipeline,
                self._ingest_pipeline_name, pipeline_config
            )
            
            # Set environment variables for other components (only if not already set)
            if not os.getenv("OPENSEARCH_PIPELINE_NAME"):
                os.environ["OPENSEARCH_PIPELINE_NAME"] = self._ingest_pipeline_name
            if not os.getenv("OPENSEARCH_MODEL_ID"):
                os.environ["OPENSEARCH_MODEL_ID"] = self.model_id
            
            self._logger.info(f"Created ingest pipeline: {self._ingest_pipeline_name} with model ID: {self.model_id}")
            
            return {"success": True, "pipeline_name": self._ingest_pipeline_name}
            
        except Exception as e:
            self._logger.error(f"Failed to create ingest pipeline: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_search_pipeline(self) -> Dict[str, Any]:
        """Create search pipeline for hybrid search."""
        self._logger.info("Creating search pipeline")
        
        try:
            if not self.model_id:
                raise ValueError("Model must be deployed first")
            
            pipeline_config = {
                "description": "Gnosari search pipeline for hybrid search",
                "phase_results_processors": [
                    {
                        "normalization-processor": {
                            "normalization": {
                                "technique": "min_max"
                            },
                            "combination": {
                                "technique": "arithmetic_mean",
                                "parameters": {
                                    "weights": [0.3, 0.7]
                                }
                            }
                        }
                    }
                ]
            }
            
            await asyncio.get_event_loop().run_in_executor(
                None, self._client.transport.perform_request,
                "PUT", f"/_search/pipeline/{self._search_pipeline_name}", {}, pipeline_config
            )
            
            # Set environment variable (only if not already set)
            if not os.getenv("OPENSEARCH_SEARCH_PIPELINE_NAME"):
                os.environ["OPENSEARCH_SEARCH_PIPELINE_NAME"] = self._search_pipeline_name
            
            self._logger.info(f"Created search pipeline: {self._search_pipeline_name}")
            
            return {"success": True, "pipeline_name": self._search_pipeline_name}
            
        except Exception as e:
            self._logger.error(f"Failed to create search pipeline: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_vector_index(self) -> Dict[str, Any]:
        """Create vector index for semantic search."""
        self._logger.info("Creating vector index")
        
        try:
            index_mapping = {
                "settings": {
                    "index.knn": True,
                    "default_pipeline": self._ingest_pipeline_name
                },
                "mappings": {
                    "properties": {
                        "id": {
                            "type": "text"
                        },
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": self._embedding_dimension,
                            "space_type": self._vector_space_type
                        },
                        "text": {
                            "type": "text"
                        }
                    }
                }
            }
            
            # Always use regular client for index operations
            await asyncio.get_event_loop().run_in_executor(
                None, self._client.indices.create, self._index_name, index_mapping
            )
            
            self._logger.info(f"Created vector index: {self._index_name}")
            
            return {"success": True, "index_name": self._index_name}
            
        except Exception as e:
            self._logger.error(f"Failed to create vector index: {e}")
            return {"success": False, "error": str(e)}
    
    async def ingest_sample_data(self) -> Dict[str, Any]:
        """Ingest sample data for testing."""
        self._logger.info("Ingesting sample data")
        
        try:
            sample_documents = [
                {
                    "text": "Gnosari is an AI agent orchestration framework that enables teams of agents to collaborate on complex tasks.",
                    "metadata": {"type": "documentation", "category": "overview"},
                    "source": "sample_data",
                    "timestamp": "2024-01-01T00:00:00Z"
                },
                {
                    "text": "OpenSearch provides powerful vector search capabilities for semantic similarity matching.",
                    "metadata": {"type": "documentation", "category": "search"},
                    "source": "sample_data",
                    "timestamp": "2024-01-01T00:00:00Z"
                },
                {
                    "text": "The knowledge management system supports multiple data sources including websites, documents, and APIs.",
                    "metadata": {"type": "documentation", "category": "knowledge"},
                    "source": "sample_data",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            ]
            
            # Bulk index sample documents
            bulk_body = []
            for i, doc in enumerate(sample_documents):
                bulk_body.append({"index": {"_index": self._index_name, "_id": f"sample_{i}"}})
                bulk_body.append(doc)

            response = await asyncio.get_event_loop().run_in_executor(
                None, self._client.bulk, bulk_body
            )
            
            # Refresh index
            await asyncio.get_event_loop().run_in_executor(
                None, self._client.indices.refresh, self._index_name
            )
            
            indexed_count = len([item for item in response["items"] if not item.get("index", {}).get("error")])
            
            self._logger.info(f"Ingested {indexed_count} sample documents")
            return {"success": True, "indexed_count": indexed_count}
            
        except Exception as e:
            self._logger.error(f"Failed to ingest sample data: {e}")
            return {"success": False, "error": str(e)}
    
    async def verify_setup(self) -> Dict[str, Any]:
        """Verify that the setup was successful."""
        self._logger.info("Verifying setup")
        
        try:
            # Check if model is deployed and ready
            if not self.model_id:
                return {"success": False, "error": "No model ID available"}
            
            model_response = await asyncio.get_event_loop().run_in_executor(
                None, self._client.transport.perform_request,
                "GET", f"/_plugins/_ml/models/{self.model_id}"
            )
            
            model_state = model_response.get("model_state", "")
            if model_state != "DEPLOYED":
                return {"success": False, "error": f"Model not deployed, state: {model_state}"}
            
            # Check if index exists
            index_exists = await asyncio.get_event_loop().run_in_executor(
                None, self._client.indices.exists, self._index_name
            )
            
            if not index_exists:
                return {"success": False, "error": "Vector index not found"}
            
            # Check if pipeline exists
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, self._client.ingest.get_pipeline, self._ingest_pipeline_name
                )
            except Exception:
                return {"success": False, "error": "Ingest pipeline not found"}
            
            # Test a simple search to verify everything works (make this optional and more robust)
            try:
                # First try a simple match_all query to ensure basic search works
                basic_query = {
                    "size": 1,
                    "query": {"match_all": {}}
                }
                
                basic_response = await asyncio.get_event_loop().run_in_executor(
                    None, self._client.search, basic_query, self._index_name
                )
                
                basic_hits = len(basic_response.get("hits", {}).get("hits", []))
                
                # Try neural search if basic search works and we have documents
                neural_search_works = False
                if basic_hits > 0:
                    try:
                        test_query = {
                            "size": 1,
                            "query": {
                                "neural": {
                                    "embedding": {  # Standard vector field name
                                        "query_text": "test search",
                                        "model_id": self.model_id,
                                        "k": 1
                                    }
                                }
                            }
                        }
                        
                        search_response = await asyncio.get_event_loop().run_in_executor(
                            None, self._client.search, test_query, self._index_name
                        )
                        neural_search_works = True
                        neural_hits = len(search_response.get("hits", {}).get("hits", []))
                    except Exception as neural_error:
                        self._logger.warning(f"Neural search test failed (this may be normal if vectors aren't ready yet): {neural_error}")
                        neural_hits = 0
                else:
                    neural_hits = 0
                
                self._logger.info("Setup verification completed successfully")
                
                return {
                    "success": True,
                    "model_id": self.model_id,
                    "model_state": model_state,
                    "index_name": self._index_name,
                    "pipeline_name": self._ingest_pipeline_name,
                    "basic_search_hits": basic_hits,
                    "neural_search_works": neural_search_works,
                    "neural_search_hits": neural_hits
                }
                
            except Exception as search_error:
                # Even if search fails, setup might still be valid - just report the issue
                self._logger.warning(f"Search test failed, but setup components exist: {search_error}")
                return {
                    "success": True,
                    "model_id": self.model_id,
                    "model_state": model_state,
                    "index_name": self._index_name,
                    "pipeline_name": self._ingest_pipeline_name,
                    "search_test_error": str(search_error)
                }
            
        except Exception as e:
            self._logger.error(f"Setup verification failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _wait_for_task_completion(self, task_id: str, max_wait_time: int = 300) -> None:
        """Wait for an ML task to complete."""
        import time
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            try:
                # Always use regular client for task checking
                response = await asyncio.get_event_loop().run_in_executor(
                    None, self._client.transport.perform_request,
                    "GET", f"/_plugins/_ml/tasks/{task_id}"
                )
                
                state = response.get("state", "")
                if state == "COMPLETED":
                    return
                elif state == "FAILED":
                    error = response.get("error", "Unknown error")
                    raise Exception(f"Task failed: {error}")
                
                await asyncio.sleep(2)
                
            except Exception as e:
                if "404" in str(e):
                    await asyncio.sleep(2)
                    continue
                raise
        
        raise Exception(f"Task {task_id} did not complete within {max_wait_time} seconds")
    
    # Cleanup methods for force mode
    async def delete_openai_connector(self) -> Dict[str, Any]:
        """Delete OpenAI connector."""
        try:
            # If we don't have the ID, search for it by name
            connector_id = getattr(self, '_connector_id', None)
            if not connector_id:
                # Search for existing connector by name
                try:
                    search_body = {
                        "size": 100,
                        "query": {
                            "match_all": {}
                        }
                    }
                    if self._use_aws_auth:
                        # Use AWS4Auth
                        response = await self._make_aws_request("POST", "/_plugins/_ml/connectors/_search", search_body)
                    else:
                        # Use opensearchpy client
                        response = await asyncio.get_event_loop().run_in_executor(
                            None, self._client.transport.perform_request,
                            "GET", "/_plugins/_ml/connectors/_search", {}, search_body
                        )
                    for hit in response.get("hits", {}).get("hits", []):
                        if hit.get("_source", {}).get("name") == self._connector_name:
                            connector_id = hit["_id"]
                            break
                except Exception:
                    pass  # Search failed, continue
            
            if connector_id:
                if self._use_aws_auth:
                    # Use AWS4Auth
                    await self._make_aws_request("DELETE", f"/_plugins/_ml/connectors/{connector_id}")
                else:
                    # Use opensearchpy client
                    await asyncio.get_event_loop().run_in_executor(
                        None, self._client.transport.perform_request,
                        "DELETE", f"/_plugins/_ml/connectors/{connector_id}"
                    )
                self._logger.info(f"Deleted connector: {connector_id}")
            return {"success": True}
        except Exception as e:
            self._logger.warning(f"Failed to delete connector: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_model_group(self) -> Dict[str, Any]:
        """Delete model group."""
        try:
            # If we don't have the ID, search for it by name
            model_group_id = getattr(self, '_model_group_id', None)
            if not model_group_id:
                # Search for existing model group by name
                try:
                    search_body = {
                        "size": 100,
                        "query": {
                            "match_all": {}
                        }
                    }
                    if self._use_aws_auth:
                        # Use AWS4Auth
                        response = await self._make_aws_request("POST", "/_plugins/_ml/model_groups/_search", search_body)
                    else:
                        # Use opensearchpy client
                        response = await asyncio.get_event_loop().run_in_executor(
                            None, self._client.transport.perform_request,
                            "GET", "/_plugins/_ml/model_groups/_search", {}, search_body
                        )
                    for hit in response.get("hits", {}).get("hits", []):
                        if hit.get("_source", {}).get("name") == self._model_group_name:
                            model_group_id = hit["_id"]
                            break
                except Exception:
                    pass  # Search failed, continue
            
            if model_group_id:
                if self._use_aws_auth:
                    # Use AWS4Auth
                    await self._make_aws_request("DELETE", f"/_plugins/_ml/model_groups/{model_group_id}")
                else:
                    # Use opensearchpy client
                    await asyncio.get_event_loop().run_in_executor(
                        None, self._client.transport.perform_request,
                        "DELETE", f"/_plugins/_ml/model_groups/{model_group_id}"
                    )
                self._logger.info(f"Deleted model group: {model_group_id}")
            return {"success": True}
        except Exception as e:
            self._logger.warning(f"Failed to delete model group: {e}")
            return {"success": False, "error": str(e)}
    
    async def undeploy_embedding_model(self) -> Dict[str, Any]:
        """Undeploy and delete embedding model."""
        try:
            # If we don't have the model ID, search for it by name
            model_id = self.model_id
            if not model_id:
                # Search for existing model by name
                try:
                    search_body = {
                        "size": 100,
                        "query": {
                            "match_all": {}
                        }
                    }
                    response = await asyncio.get_event_loop().run_in_executor(
                        None, self._client.transport.perform_request,
                        "GET", "/_plugins/_ml/models/_search", {}, search_body
                    )
                    for hit in response.get("hits", {}).get("hits", []):
                        if hit.get("_source", {}).get("name") == self._model_name:
                            model_id = hit["_id"]
                            break
                except Exception:
                    pass  # Search failed, continue
            
            if model_id:
                # Undeploy first
                try:
                    await asyncio.get_event_loop().run_in_executor(
                        None, self._client.transport.perform_request,
                        "POST", f"/_plugins/_ml/models/{model_id}/_undeploy"
                    )
                    self._logger.info(f"Undeployed model: {model_id}")
                except Exception:
                    pass  # May already be undeployed
                
                # Delete model
                await asyncio.get_event_loop().run_in_executor(
                    None, self._client.transport.perform_request,
                    "DELETE", f"/_plugins/_ml/models/{model_id}"
                )
                self._logger.info(f"Deleted model: {model_id}")
                self.model_id = None
            return {"success": True}
        except Exception as e:
            self._logger.warning(f"Failed to undeploy/delete model: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_ingest_pipeline(self) -> Dict[str, Any]:
        """Delete ingest pipeline."""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, self._client.ingest.delete_pipeline, self._ingest_pipeline_name
            )
            self._logger.info(f"Deleted ingest pipeline: {self._ingest_pipeline_name}")
            return {"success": True}
        except Exception as e:
            self._logger.warning(f"Failed to delete ingest pipeline: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_search_pipeline(self) -> Dict[str, Any]:
        """Delete search pipeline."""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, self._client.transport.perform_request,
                "DELETE", f"/_search/pipeline/{self._search_pipeline_name}"
            )
            self._logger.info(f"Deleted search pipeline: {self._search_pipeline_name}")
            return {"success": True}
        except Exception as e:
            self._logger.warning(f"Failed to delete search pipeline: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_vector_index(self) -> Dict[str, Any]:
        """Delete vector index."""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, self._client.indices.delete, self._index_name
            )
            self._logger.info(f"Deleted vector index: {self._index_name}")
            return {"success": True}
        except Exception as e:
            self._logger.warning(f"Failed to delete vector index: {e}")
            return {"success": False, "error": str(e)}
    
    async def clear_sample_data(self) -> Dict[str, Any]:
        """Clear sample data."""
        try:
            # Delete all documents with source "sample_data"
            delete_query = {
                "query": {
                    "term": {
                        "source": "sample_data"
                    }
                }
            }
            
            await asyncio.get_event_loop().run_in_executor(
                None, self._client.delete_by_query, self._index_name, delete_query
            )
            self._logger.info("Cleared sample data")
            return {"success": True}
        except Exception as e:
            self._logger.warning(f"Failed to clear sample data: {e}")
            return {"success": False, "error": str(e)}


__all__ = ["OpenSearchSetupAdapter"]