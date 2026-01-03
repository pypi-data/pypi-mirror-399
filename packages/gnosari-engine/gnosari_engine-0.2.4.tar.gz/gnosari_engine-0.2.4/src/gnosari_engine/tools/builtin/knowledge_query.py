"""
Simple knowledge query tool that directly uses OpenSearch.

Queries knowledge bases using OpenSearchKnowledgeBase with streaming support.
"""

import logging
import os
from typing import Any

from opensearchpy import OpenSearch, RequestsHttpConnection

from ...knowledge.components import KnowledgeQueryResult
from ...knowledge.providers.opensearch import OpenSearchKnowledgeBase
from ...schemas.domain.execution import AgentRun
from ...schemas.domain.tool import Tool
from ...tools.streaming.interfaces import IStreamableTool, IToolStreamContext
from ...tools.streaming.mixins import StreamableToolMixin, ProgressTracker
from .base import BaseProviderAgnosticTool

logger = logging.getLogger(__name__)


class KnowledgeQueryTool(StreamableToolMixin, BaseProviderAgnosticTool, IStreamableTool):
    """
    Simple knowledge query tool with streaming support.
    
    Queries knowledge bases using OpenSearchKnowledgeBase directly.
    Follows Open/Closed Principle: Extended with streaming without modification.
    """

    def __init__(self, tool_config: Tool, agent_run: AgentRun):
        # Initialize BaseProviderAgnosticTool first
        BaseProviderAgnosticTool.__init__(self, tool_config)
        # Initialize streaming components
        StreamableToolMixin.__init__(self)
        self.agent_run = agent_run

        # ULTRA-CLEAN: Set session ID for registry lookup
        if agent_run and agent_run.metadata and agent_run.metadata.session_id:
            self.set_session_id(agent_run.metadata.session_id)
            logger.debug(f"Set session_id on tool: {agent_run.metadata.session_id}")
        else:
            logger.warning(f"No session_id available during tool initialization")

    async def execute_core_logic(self, query: str, knowledge_name: str) -> str:
        """
        Query knowledge base directly with streaming support.
        
        Args:
            query: Search query for knowledge base
            knowledge_name: Name of knowledge base to query
            
        Returns:
            Formatted search results or error message
        """
        logger.info(f"Querying knowledge base '{knowledge_name}' with query: '{query}'")
        
        # Emit start event if streaming is available
        await self._emit_start({
            "query": query,
            "knowledge_base": knowledge_name,
            "operation": "knowledge_search"
        })
        
        # Create progress tracker
        progress = ProgressTracker(self, total_steps=4, operation_name="knowledge_search")
        
        try:
            # Step 1: Find knowledge base configuration
            await progress.step("finding_knowledge_config", {"knowledge_name": knowledge_name})
            knowledge = self._find_knowledge_config(knowledge_name)
            if not knowledge:
                error_msg = f"Knowledge base '{knowledge_name}' not found in team configuration"
                await self._emit_error(ValueError(error_msg))
                return error_msg
            
            # Step 2: Initialize OpenSearch client
            # Extract OpenSearch connection details with environment variable fallbacks
            host = os.getenv("OPENSEARCH_HOST", "localhost")
            port = int(os.getenv("OPENSEARCH_PORT", "9200"))
            use_ssl = os.getenv("OPENSEARCH_USE_SSL", "false").lower() == "true"
            verify_certs = os.getenv("OPENSEARCH_VERIFY_CERTS", "false").lower() == "true"
            
            # Handle authentication from environment
            http_auth = None
            if os.getenv("OPENSEARCH_USERNAME") and os.getenv("OPENSEARCH_PASSWORD"):
                http_auth = (os.getenv("OPENSEARCH_USERNAME"), os.getenv("OPENSEARCH_PASSWORD"))
            
            await progress.step("initializing_client", {"host": host, "port": port})

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
            
            client = OpenSearch(**client_config)
            
            # Step 3: Create and initialize knowledge base
            await progress.step("creating_knowledge_base", {"knowledge_id": knowledge.id})
            knowledge_base = OpenSearchKnowledgeBase(
                knowledge=knowledge,
                client=client,
                config=knowledge.config or {}
            )
            
            await knowledge_base.initialize()
            
            # Step 4: Execute query
            await progress.step("executing_query", {"query": query})
            result: KnowledgeQueryResult = await knowledge_base.query(query)
            
            # Emit intermediate result
            await self._emit_result({
                "query": query,
                "knowledge_base": knowledge_name,
                "result_count": len(result.results),
                "has_results": len(result.results) > 0
            })
            
            formatted_result = self._format_results(result)
            
            # Complete progress tracking
            await progress.complete({
                "query": query,
                "knowledge_base": knowledge_name,
                "result_count": len(result.results),
                "result_size": len(formatted_result)
            })
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}", exc_info=True)
            await self._emit_error(e)
            return f"Error querying knowledge base: {str(e)}"

    def _find_knowledge_config(self, knowledge_name: str):
        """Find knowledge base configuration from team."""
        if not (self.agent_run and self.agent_run.team and self.agent_run.team.knowledge):
            return None
            
        for kb in self.agent_run.team.knowledge:
            if kb.id == knowledge_name:
                return kb
        return None
    
    @staticmethod
    def _format_results(result: KnowledgeQueryResult) -> str:
        """Format query results for LLM consumption."""
        if not result.results:
            return "No relevant information found."
        
        formatted_results = []
        for doc in result.results:
            formatted_results.append(f"Source: {doc.source}\nContent: {doc.content}")
        
        return "\n\n".join(formatted_results)

    def get_input_schema(self) -> dict[str, Any]:
        """Get input schema for knowledge query."""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for knowledge base"
                },
                "knowledge_name": {
                    "type": "string", 
                    "description": "Name of knowledge base to query"
                }
            },
            "required": ["query", "knowledge_name"]
        }

    def get_output_schema(self) -> dict[str, Any]:
        """Get output schema for knowledge query."""
        return {
            "type": "string",
            "description": "Formatted search results from knowledge base"
        }
    
    # IStreamableTool interface methods
    def supports_streaming(self) -> bool:
        """Knowledge query tool supports streaming."""
        return True

    def _get_tool_name(self) -> str:
        """Get tool name for streaming events."""
        return self.name or "knowledge_query"