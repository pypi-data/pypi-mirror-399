"""
MCP server factory for creating OpenAI MCP servers.
Follows SOLID principles for clean, maintainable, and extensible code.
"""

import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class MCPServerCreationError(Exception):
    """MCP server creation specific errors."""
    pass


class IMCPServerFactory(ABC):
    """Interface for MCP server factory following Interface Segregation Principle."""

    @abstractmethod
    async def create_mcp_servers(self, mcp_tools: List[Any]) -> List[Any]:
        """Create MCP servers from tool configurations."""
        pass

    @abstractmethod
    async def create_single_mcp_server(self, tool_config: Any) -> Optional[Any]:
        """Create a single MCP server from tool configuration."""
        pass


class MCPServerFactory(IMCPServerFactory):
    """
    Factory for creating OpenAI MCP servers from tool configurations.
    
    Follows SOLID Principles:
    - Single Responsibility: Only responsible for creating MCP servers
    - Open/Closed: Extensible for new MCP server types, closed for modification
    - Liskov Substitution: Implements IMCPServerFactory interface correctly
    - Interface Segregation: Focused interface for MCP server creation
    - Dependency Inversion: Depends on abstractions (Tool configurations)
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._failed_connections: List[Dict[str, str]] = []

    @property
    def failed_connections(self) -> List[Dict[str, str]]:
        """Get list of failed MCP server connections."""
        return self._failed_connections.copy()

    async def create_mcp_servers(self, mcp_tools: List[Any]) -> List[Any]:
        """
        Create MCP servers from tool configurations without connecting them.
        Connection will be handled via async context management.
        
        Args:
            mcp_tools: List of MCP tool configurations
            
        Returns:
            List of successfully created MCP servers (not connected)
        """
        mcp_servers = []
        self._failed_connections = []

        for tool_config in mcp_tools:
            try:
                mcp_server = await self.create_single_mcp_server(tool_config)
                if mcp_server:
                    mcp_servers.append(mcp_server)
                    self.logger.info(f"✅ Created MCP server for '{tool_config.name}' (connection deferred)")
                else:
                    self.logger.warning(f"⚠️  Failed to create MCP server for '{tool_config.name}'")
            except Exception as e:
                error_msg = f"Failed to create MCP server for '{tool_config.name}': {e}"
                self.logger.error(error_msg)
                self._record_failed_connection(tool_config.name, str(tool_config.url or tool_config.command), str(e))

        if mcp_servers:
            self.logger.info(f"Created {len(mcp_servers)} MCP servers successfully")
        
        if self._failed_connections:
            self.logger.warning(f"Failed to create {len(self._failed_connections)} MCP servers")

        return mcp_servers

    async def create_single_mcp_server(self, tool_config: Any) -> Optional[Any]:
        """
        Create a single MCP server from tool configuration.
        
        Args:
            tool_config: Tool configuration with MCP server details
            
        Returns:
            MCP server instance or None if creation fails
        """
        if not tool_config.is_mcp_tool():
            return None

        tool_name = tool_config.name or tool_config.id
        tool_url = tool_config.url
        tool_command = tool_config.command

        if not (tool_url or tool_command):
            self.logger.warning(f"MCP tool '{tool_name}' has no URL or command")
            return None

        connection_type = tool_config.connection_type or 'sse'

        try:
            if connection_type == 'sse':
                return await self._create_sse_server(tool_config, tool_name, tool_url)
            elif connection_type == 'streamable_http':
                return await self._create_streamable_http_server(tool_config, tool_name, tool_url)
            elif connection_type == 'stdio':
                return await self._create_stdio_server(tool_config, tool_name, tool_command)
            else:
                raise MCPServerCreationError(f"Unsupported connection_type: {connection_type}")

        except Exception as e:
            self.logger.error(f"Failed to create MCP server '{tool_name}': {e}")
            self._record_failed_connection(tool_name, tool_url or tool_command or '', str(e))
            return None

    async def _create_sse_server(self, tool_config: Any, tool_name: str, tool_url: str) -> Any:
        """Create SSE MCP server using OpenAI agents SDK."""
        try:
            from agents.mcp import MCPServerSse, MCPServerSseParams
        except ImportError as e:
            raise MCPServerCreationError(f"OpenAI agents MCP package not available: {e}") from e

        params = MCPServerSseParams(
            url=tool_url,
            headers=tool_config.headers or {},
            timeout=tool_config.timeout or 30,
            sse_read_timeout=getattr(tool_config, 'sse_read_timeout', 30),
        )

        server = MCPServerSse(
            params=params,
            name=tool_name,
            cache_tools_list=True,
            client_session_timeout_seconds=getattr(tool_config, 'client_session_timeout_seconds', 30),
        )

        self.logger.debug(f"Created SSE MCP server '{tool_name}' with params: {params}")
        return server

    async def _create_streamable_http_server(self, tool_config: Any, tool_name: str, tool_url: str) -> Any:
        """Create Streamable HTTP MCP server using OpenAI agents SDK."""
        try:
            from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams
        except ImportError as e:
            raise MCPServerCreationError(f"OpenAI agents MCP package not available: {e}") from e

        params = MCPServerStreamableHttpParams(
            url=tool_url,
            headers=tool_config.headers or {},
            timeout=tool_config.timeout or 30,
            sse_read_timeout=getattr(tool_config, 'sse_read_timeout', 30),
            terminate_on_close=getattr(tool_config, 'terminate_on_close', True)
        )

        server = MCPServerStreamableHttp(
            params=params,
            name=tool_name,
            client_session_timeout_seconds=getattr(tool_config, 'client_session_timeout_seconds', 30),
            cache_tools_list=True,
        )

        self.logger.debug(f"Created Streamable HTTP MCP server '{tool_name}' with params: {params}")
        return server

    async def _create_stdio_server(self, tool_config: Any, tool_name: str, tool_command: str) -> Any:
        """Create Stdio MCP server using OpenAI agents SDK."""
        try:
            from agents.mcp import MCPServerStdio, MCPServerStdioParams
        except ImportError as e:
            raise MCPServerCreationError(f"OpenAI agents MCP package not available: {e}") from e

        # Handle args - could be dict or list
        args = tool_config.args if tool_config.args else []
        if isinstance(args, dict):
            # Convert dict to list of arguments
            args = []
            for key, value in tool_config.args.items():
                args.extend([f"--{key}", str(value)])

        params = MCPServerStdioParams(
            command=tool_command,
            args=args,
        )

        server = MCPServerStdio(
            params=params,
            name=tool_name,
            client_session_timeout_seconds=getattr(tool_config, 'client_session_timeout_seconds', 30),
        )

        self.logger.debug(f"Created Stdio MCP server '{tool_name}' with params: {params}")
        return server

    def _record_failed_connection(self, name: str, url: str, error: str) -> None:
        """Record a failed connection for reporting."""
        self._failed_connections.append({
            'name': name,
            'url': url,
            'error': error
        })