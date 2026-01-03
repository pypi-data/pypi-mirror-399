"""
Knowledge Setup Command - Handles OpenSearch knowledge base setup
"""

import os
import sys
from typing import Optional, List, Tuple, Callable, Any

from dotenv import load_dotenv

from .base_command import BaseCommand
from ..interfaces import DisplayServiceInterface


class KnowledgeSetupCommand(BaseCommand):
    """
    Single Responsibility: Handle OpenSearch knowledge base setup
    Open/Closed: Easy to extend with new setup operations
    Interface Segregation: Only depends on display service
    """
    
    def __init__(self, display_service: DisplayServiceInterface):
        super().__init__(display_service)
    
    async def execute(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_ssl: Optional[bool] = None,
        verify_certs: Optional[bool] = None,
        force: bool = False,
        no_sample_data: bool = False,
        no_hybrid: bool = False
    ) -> None:
        """Execute the knowledge setup command"""
        operation = "OpenSearch knowledge base setup"
        self._log_execution_start(operation)
        
        # Load environment variables from .env file
        load_dotenv()
        
        # Apply environment variable defaults
        host = host or os.getenv("OPENSEARCH_HOST", "localhost")
        port = port or int(os.getenv("OPENSEARCH_PORT", "9200"))
        username = username or os.getenv("OPENSEARCH_USERNAME")
        password = password or os.getenv("OPENSEARCH_PASSWORD")
        use_ssl = use_ssl if use_ssl is not None else os.getenv("OPENSEARCH_USE_SSL", "false").lower() == "true"
        verify_certs = verify_certs if verify_certs is not None else os.getenv("OPENSEARCH_VERIFY_CERTS", "false").lower() == "true"
        
        try:
            self._display_service.display_header()
            self._display_service.display_status("Setting up OpenSearch for Gnosari Knowledge Base", "info")
            
            # Log the configuration being used
            self._display_service.display_status(f"Connecting to: {host}:{port} (SSL: {use_ssl}, Auth: {'Yes' if username else 'No'})", "info")
            
            result = await self._execute_setup(
                host=host,
                port=port,
                username=username,
                password=password,
                use_ssl=use_ssl,
                verify_certs=verify_certs,
                force=force,
                no_sample_data=no_sample_data,
                no_hybrid=no_hybrid
            )
            
            self._handle_setup_result(result)
            self._log_execution_end(operation)
            
        except Exception as e:
            self._handle_error(e, operation)
            sys.exit(1)
    
    def _handle_setup_result(self, result: dict) -> None:
        """Handle the setup result and display appropriate messages"""
        if result['success']:
            self._display_service.display_status(
                result.get('message', 'OpenSearch setup completed'), 
                "success"
            )
            
            model_id = result.get('model_id')
            if model_id:
                self._display_setup_success_info(model_id)
        else:
            self._display_service.display_status(
                result.get('message', 'OpenSearch setup failed'), 
                "error"
            )
            sys.exit(1)
    
    def _display_setup_success_info(self, model_id: str) -> None:
        """Display success information and environment variable instructions"""
        self._display_service.display_status("Setup completed successfully!", "success")
        self._display_service.display_status("IMPORTANT: Please set the following environment variable:", "warning")
        self._display_service.display_status(f"OPENSEARCH_MODEL_ID={model_id}", "info")
        self._display_service.display_status("Add this to your .env file or export it in your shell:", "info")
        self._display_service.display_status(f"echo 'OPENSEARCH_MODEL_ID={model_id}' >> .env", "info")
    
    async def _execute_setup(
        self,
        host: str,
        port: int,
        username: Optional[str],
        password: Optional[str],
        use_ssl: bool,
        verify_certs: bool,
        force: bool,
        no_sample_data: bool,
        no_hybrid: bool
    ) -> dict:
        """Execute the OpenSearch setup operation using the new provider"""
        
        try:
            self._display_service.display_status(f"Starting OpenSearch setup on {host}:{port}", "info")
            
            # Validate environment
            if not self._validate_environment():
                return {
                    'success': False,
                    'message': 'OPENAI_API_KEY environment variable is required'
                }
            
            # Initialize provider and connection
            provider = await self._initialize_provider(host, port, username, password, use_ssl, verify_certs)
            if not provider:
                return {
                    'success': False,
                    'message': f'Failed to connect to OpenSearch at {host}:{port}'
                }
            
            # Execute setup with adapter
            return await self._execute_setup_steps(
                host, port, use_ssl, verify_certs, username, password,
                force, no_sample_data, no_hybrid
            )
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Setup failed: {e}'
            }
    
    def _validate_environment(self) -> bool:
        """Validate required environment variables"""
        openai_api_key = os.getenv('OPENAI_API_KEY')
        return bool(openai_api_key)
    
    async def _initialize_provider(
        self,
        host: str,
        port: int,
        username: Optional[str],
        password: Optional[str],
        use_ssl: bool,
        verify_certs: bool
    ):
        """Initialize the OpenSearch knowledge provider"""
        # Import the new OpenSearch adapter from the knowledge system
        from ...knowledge.providers.opensearch import OpenSearchKnowledgeProvider
        
        # Create connection config
        connection_config = {
            'opensearch': {
                'host': host,
                'port': port,
                'use_ssl': use_ssl,
                'verify_certs': verify_certs
            }
        }
        
        if username and password:
            connection_config['opensearch']['username'] = username
            connection_config['opensearch']['password'] = password
        
        # Initialize provider
        provider = OpenSearchKnowledgeProvider()
        await provider.initialize(**connection_config)
        
        # Test connection
        self._display_service.display_status("Testing OpenSearch connection...", "info")
        if not provider.is_initialized:
            return None
        
        self._display_service.display_status("✓ Connected to OpenSearch", "success")
        return provider
    
    async def _execute_setup_steps(
        self,
        host: str,
        port: int,
        use_ssl: bool,
        verify_certs: bool,
        username: Optional[str],
        password: Optional[str],
        force: bool,
        no_sample_data: bool,
        no_hybrid: bool
    ) -> dict:
        """Execute the setup steps using the setup adapter"""
        # Import the setup adapter class for advanced setup operations
        from ...knowledge.setup_adapter import OpenSearchSetupAdapter
        
        # Create connection config
        connection_config = {
            'opensearch': {
                'host': host,
                'port': port,
                'use_ssl': use_ssl,
                'verify_certs': verify_certs
            }
        }
        
        if username and password:
            connection_config['opensearch']['http_auth'] = (username, password)
        
        # Create setup adapter instance
        setup_adapter = OpenSearchSetupAdapter(connection_config)
        
        # Handle force cleanup if requested
        if force:
            await self._execute_cleanup_steps(setup_adapter)
        
        # Execute main setup steps
        success = await self._execute_main_setup_steps(setup_adapter, no_hybrid, no_sample_data)
        if not success:
            return {'success': False, 'message': 'Setup failed during main steps'}
        
        # Verify and return result
        return await self._verify_and_return_result(setup_adapter, host, port, use_ssl, no_hybrid, no_sample_data)
    
    async def _execute_cleanup_steps(self, setup_adapter) -> None:
        """Execute cleanup steps in force mode"""
        self._display_service.display_status("Force mode: cleaning up existing resources...", "info")
        cleanup_steps = [
            ("Clearing sample data", setup_adapter.clear_sample_data),
            ("Deleting vector index", setup_adapter.delete_vector_index),
            ("Deleting search pipeline", setup_adapter.delete_search_pipeline),
            ("Deleting ingest pipeline", setup_adapter.delete_ingest_pipeline),
            ("Undeploying embedding model", setup_adapter.undeploy_embedding_model),
            ("Deleting model group", setup_adapter.delete_model_group),
            ("Deleting OpenAI connector", setup_adapter.delete_openai_connector),
        ]
        
        for cleanup_name, cleanup_func in cleanup_steps:
            try:
                self._display_service.display_status(f"  {cleanup_name}...", "info")
                await cleanup_func()
            except Exception:
                # Cleanup failures are expected - resources might not exist
                self._display_service.display_status(f"  {cleanup_name} (not found - OK)", "warning")
        
        self._display_service.display_status("Cleanup completed, starting fresh setup...", "info")
    
    async def _execute_main_setup_steps(self, setup_adapter, no_hybrid: bool, no_sample_data: bool) -> bool:
        """Execute the main setup steps"""
        setup_steps = self._get_setup_steps(setup_adapter, no_hybrid, no_sample_data)
        
        for step_name, step_func in setup_steps:
            try:
                self._display_service.display_status(f"{step_name}...", "info")
                
                result = await step_func()
                
                if result.get('success', True):
                    self._display_service.display_status(f"✓ {step_name}", "success")
                else:
                    error_msg = result.get('error', 'Unknown error')
                    self._display_service.display_status(f"✗ {step_name}: {error_msg}", "error")
                    return False
                        
            except Exception as e:
                self._display_service.display_status(f"✗ {step_name}: {e}", "error")
                return False
        
        return True
    
    def _get_setup_steps(self, setup_adapter, no_hybrid: bool, no_sample_data: bool) -> List[Tuple[str, Callable]]:
        """Get the list of setup steps to execute"""
        setup_steps = [
            ("Creating OpenAI connector", setup_adapter.create_openai_connector),
            ("Setting up model group", setup_adapter.create_model_group),
            ("Deploying embedding model", setup_adapter.deploy_embedding_model),
            ("Creating ingest pipeline", setup_adapter.create_ingest_pipeline),
        ]
        
        if not no_hybrid:
            setup_steps.append(("Creating search pipeline", setup_adapter.create_search_pipeline))
        
        setup_steps.append(("Creating vector index", setup_adapter.create_vector_index))
        
        if not no_sample_data:
            setup_steps.append(("Ingesting sample data", setup_adapter.ingest_sample_data))
        
        return setup_steps
    
    async def _verify_and_return_result(
        self,
        setup_adapter,
        host: str,
        port: int,
        use_ssl: bool,
        no_hybrid: bool,
        no_sample_data: bool
    ) -> dict:
        """Verify setup and return final result"""
        # Verify setup
        self._display_service.display_status("Verifying setup...", "info")
        verification_result = await setup_adapter.verify_setup()
        
        if verification_result.get('success', False):
            self._display_service.display_status("✓ OpenSearch semantic search setup verified", "success")
            
            # Show setup summary
            self._display_setup_summary(host, port, use_ssl, no_hybrid, no_sample_data)
            
            # Get model ID from adapter
            model_id = getattr(setup_adapter, 'model_id', None)
            
            return {
                'success': True,
                'message': 'OpenSearch semantic search setup completed successfully',
                'model_id': model_id
            }
        else:
            error_msg = verification_result.get('error', 'Verification failed')
            return {
                'success': False,
                'message': f'Setup completed but verification failed: {error_msg}'
            }
    
    def _display_setup_summary(self, host: str, port: int, use_ssl: bool, no_hybrid: bool, no_sample_data: bool) -> None:
        """Display setup summary information"""
        self._display_service.display_status("Setup Summary:", "info")
        self._display_service.display_status(f"  • Host: {host}:{port}", "info")
        self._display_service.display_status(f"  • SSL: {'Enabled' if use_ssl else 'Disabled'}", "info")
        self._display_service.display_status(f"  • Hybrid search: {'Enabled' if not no_hybrid else 'Disabled'}", "info")
        self._display_service.display_status(f"  • Sample data: {'Loaded' if not no_sample_data else 'Skipped'}", "info")