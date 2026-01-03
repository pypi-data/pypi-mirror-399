"""
Auto-discovery tool factory following Open/Closed Principle.

Open for extension: New tools and providers can be auto-discovered or registered.
Closed for modification: Core factory logic unchanged when adding new tools.
"""

import importlib
import logging
import pkgutil
from enum import Enum
from pathlib import Path
from typing import Any

from ...schemas.domain.tool import Tool
from ..interfaces import IToolProvider
from ..streaming.interfaces import IStreamableTool, IToolStreamContext
from .interfaces import IToolFactory


class SupportedProviders(Enum):
    """Supported tool providers for auto-discovery."""
    BUILTIN = "builtin"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class AutoDiscoveryToolFactory(IToolFactory):
    """
    Tool factory following Open/Closed Principle with auto-discovery.
    
    Open for extension: New tools and providers can be auto-discovered or registered.
    Closed for modification: Core factory logic unchanged when adding new tools.
    """

    def __init__(self):
        # Registry: tool_name -> provider_name -> provider_class
        self._registry: dict[str, dict[str, type[IToolProvider]]] = {}
        # Discovery paths for auto-loading
        self._discovery_paths: dict[str, Path] = {}
        self._supported_providers = SupportedProviders
        self._setup_discovery_paths()

    def _setup_discovery_paths(self) -> None:
        """Setup paths for auto-discovery."""
        base_path = Path(__file__).parent.parent
        self._discovery_paths = {
            SupportedProviders.BUILTIN.value: base_path / "builtin",
            SupportedProviders.OPENAI.value: base_path / "providers" / SupportedProviders.OPENAI.value,
            SupportedProviders.ANTHROPIC.value: base_path / "providers" / SupportedProviders.ANTHROPIC.value,
        }

    def create_tool_provider(
        self, 
        tool: Tool,
        provider_name: str,
        agent_run=None,
        stream_context: IToolStreamContext | None = None,
        **config
    ) -> IToolProvider:
        """Create tool provider instance with auto-discovery fallback."""
        tool_name = tool.id
        
        # 1. Check explicit registry first
        if self._is_registered(tool_name, provider_name):
            return self._create_from_registry(tool, provider_name, agent_run=agent_run, stream_context=stream_context, **config)

        # 2. Try auto-discovery
        provider_class = self._auto_discover_tool(tool, provider_name)
        if provider_class:
            # Register for future use
            self.register_tool_provider(tool_name, provider_name, provider_class)

            instance = provider_class(tool, agent_run=agent_run, **config)
            
            # Inject streaming context if tool supports it
            self._inject_streaming_context(instance, stream_context)
            
            return instance
        
        # 3. Fail with helpful error showing available tools
        available_tools = self._scan_available_tools(provider_name)
        raise ValueError(
            f"Tool '{tool_name}' not found for provider '{provider_name}'. "
            f"Available tools: {available_tools}"
        )

    def _is_registered(self, tool_name: str, provider_name: str) -> bool:
        """Check if tool is explicitly registered."""
        return (tool_name in self._registry and 
                provider_name in self._registry[tool_name])

    def _create_from_registry(
        self, 
        tool: Tool, 
        provider_name: str, 
        agent_run=None,
        stream_context: IToolStreamContext | None = None,
        **config
    ) -> IToolProvider:
        """Create tool from explicit registry."""
        tool_name = tool.id
        provider_class = self._registry[tool_name][provider_name]
        instance = provider_class(tool, agent_run=agent_run, **config)
        
        # Inject streaming context if tool supports it
        self._inject_streaming_context(instance, stream_context)
        
        return instance

    def _auto_discover_tool(
        self, 
        tool: Tool, 
        provider_name: str
    ) -> type[IToolProvider] | None:
        """
        Auto-discover tool provider using explicit config or conventional naming.
        
        Priority:
        1. Use explicit module/class_name from tool config if available
        2. Fall back to conventional naming for provider-specific tools
        3. Fall back to builtin tools with conventional naming
        """
        try:
            # 1. Try explicit module and class_name from config (highest priority)
            if tool.module and tool.class_name:
                try:
                    module = importlib.import_module(tool.module)
                    tool_class = getattr(module, tool.class_name, None)
                    if tool_class:
                        # Wrap the tool class with provider-specific adapter if needed
                        return self._wrap_tool_for_provider(tool_class, provider_name)
                except (ImportError, AttributeError):
                    pass
            
            # 2. Try conventional provider-specific naming
            tool_name = tool.id
            class_name = self._tool_name_to_class_name(tool_name, provider_name)
            
            # Try provider-specific path
            module_path = f".providers.{provider_name}.{tool_name}"
            try:
                module = importlib.import_module(module_path, __package__)
                return getattr(module, class_name, None)
            except (ImportError, AttributeError):
                pass
            
            # 3. Try builtin path with conventional naming
            module_path = f".builtin.{tool_name}"
            try:
                module = importlib.import_module(module_path, __package__)
                # Look for provider-specific class first
                provider_class = getattr(module, class_name, None)
                if provider_class:
                    return provider_class
                
                # Try base class as last resort
                base_class_name = self._tool_name_to_base_class_name(tool_name)
                base_class = getattr(module, base_class_name, None)
                if base_class:
                    return base_class
                
                # No suitable class found in module
                available_classes = [name for name in dir(module) 
                                   if isinstance(getattr(module, name), type)]
                raise AttributeError(
                    f"Module {module_path} does not contain expected tool classes. "
                    f"Expected: {class_name} or {base_class_name}. "
                    f"Available classes: {available_classes}"
                )
            except ImportError as e:
                # Module not found - this is expected for auto-discovery
                logging.debug(f"Builtin module not found for {tool_name}: {e}")
            except AttributeError as e:
                # Tool class not found in module - log for debugging
                logging.warning(f"Tool class not found in {module_path}: {e}")
                
        except Exception as e:
            # Log discovery failure for debugging but continue
            logging.debug(f"Tool auto-discovery failed for {tool.id}: {e}")
        
        return None

    def _wrap_tool_for_provider(
        self, 
        tool_class: type, 
        provider_name: str
    ) -> type[IToolProvider]:
        """
        Wrap a generic tool class with provider-specific adapter.
        
        This allows tools defined with explicit module/class_name to work
        with different providers by creating appropriate adapters.
        """
        # Check if tool class already implements IToolProvider protocol
        if isinstance(tool_class, type) and hasattr(tool_class, 'provider_name'):
            return tool_class
        
        # Check if instance would satisfy the protocol (duck typing)
        try:
            # Create a test instance to verify protocol compliance
            test_instance = tool_class.__new__(tool_class)
            if isinstance(test_instance, IToolProvider):
                return tool_class
        except Exception as e:
            # Log protocol checking failure for debugging
            logging.debug(f"Protocol checking failed for {tool_class}: {e}")
        
        # Create dynamic adapter for provider-agnostic tools
        return self._create_provider_adapter(tool_class, provider_name)

    def _create_provider_adapter(
        self, 
        base_tool_class: type, 
        provider_name: str
    ) -> type[IToolProvider]:
        """Create a dynamic adapter that wraps a base tool for a specific provider."""
        
        class ProviderToolAdapter(IToolProvider):
            """Dynamic adapter for provider-agnostic tools."""

            def __init__(self, tool: Tool, agent_run=None, **config):
                self.tool = tool
                self.agent_run = agent_run
                # Pass agent_run to base tool as keyword argument if provided
                if agent_run is not None:
                    self.base_tool_instance = base_tool_class(tool, agent_run=agent_run, **config)
                else:
                    self.base_tool_instance = base_tool_class(tool, **config)
                self._provider_name = provider_name
                self._is_initialized = False
            
            @property
            def provider_name(self) -> str:
                return self._provider_name
            
            @property
            def tool_name(self) -> str:
                return self.tool.id
            
            @property
            def is_initialized(self) -> bool:
                return self._is_initialized
            
            async def initialize(self, **config) -> None:
                """Initialize the wrapped tool."""
                try:
                    initialize_method = getattr(self.base_tool_instance, 'initialize', None)
                    if initialize_method and callable(initialize_method):
                        await initialize_method(**config)
                except Exception as e:
                    raise RuntimeError(f"Failed to initialize tool {self.tool.id}: {e}")
                self._is_initialized = True
            
            async def cleanup(self) -> None:
                """Cleanup the wrapped tool."""
                try:
                    cleanup_method = getattr(self.base_tool_instance, 'cleanup', None)
                    if cleanup_method and callable(cleanup_method):
                        await cleanup_method()
                except Exception as e:
                    # Log warning but don't fail cleanup
                    logging.warning(f"Failed to cleanup tool {self.tool.id}: {e}")
            
            def get_tool_implementation(self) -> Any:
                """Return provider-specific tool implementation."""
                return self._convert_to_provider_format()
            
            def _convert_to_provider_format(self) -> Any:
                """Convert base tool to provider-specific format."""
                if self._provider_name == SupportedProviders.OPENAI.value:
                    return self._create_openai_tool()
                elif self._provider_name == SupportedProviders.ANTHROPIC.value:
                    return self._create_anthropic_tool()
                else:
                    # Return base tool as fallback
                    return self.base_tool_instance
            
            def _create_openai_tool(self) -> Any:
                """Create OpenAI FunctionTool from base tool."""
                try:
                    from agents import FunctionTool
                    
                    return FunctionTool(
                        name=self.tool.id,
                        description=self.tool.description or self.tool.name,
                        params_json_schema=getattr(self.base_tool_instance, 'get_input_schema', lambda: {})(),
                        on_invoke_tool=self._execute_openai_tool
                    )
                except ImportError:
                    # Fallback if OpenAI agents not available
                    return self.base_tool_instance
            
            def _create_anthropic_tool(self) -> Any:
                """Create Anthropic tool from base tool."""
                # Implementation for Anthropic tool format
                # This would depend on Anthropic's tool interface
                return self.base_tool_instance
            
            async def _execute_openai_tool(self, ctx, args: str) -> str:
                """Execute tool within OpenAI context."""
                import json
                parsed_args = json.loads(args)
                
                # Execute the base tool using method resolution
                execute_method = getattr(self.base_tool_instance, 'execute', None)
                run_method = getattr(self.base_tool_instance, 'run', None)
                
                if execute_method and callable(execute_method):
                    result = await execute_method(**parsed_args)
                elif run_method and callable(run_method):
                    result = await run_method(**parsed_args)
                else:
                    available_methods = [name for name in dir(self.base_tool_instance) 
                                       if callable(getattr(self.base_tool_instance, name)) 
                                       and not name.startswith('_')]
                    raise NotImplementedError(
                        f"Tool {self.tool.id} does not implement execute() or run(). "
                        f"Available methods: {available_methods}"
                    )
                
                return str(result)
        
        return ProviderToolAdapter

    @staticmethod
    def _tool_name_to_class_name(tool_name: str, provider_name: str) -> str:
        """Convert tool_name to class name without provider prefix."""
        # knowledge_query -> KnowledgeQueryToolProvider
        words = tool_name.split('_')
        capitalized = ''.join(word.capitalize() for word in words)
        return f"{capitalized}ToolProvider"

    @staticmethod
    def _tool_name_to_base_class_name(tool_name: str) -> str:
        """Convert tool_name to base class name."""
        # knowledge_query -> KnowledgeQueryTool
        words = tool_name.split('_')
        capitalized = ''.join(word.capitalize() for word in words)
        return f"{capitalized}Tool"

    def _scan_available_tools(self, provider_name: str) -> list[str]:
        """Scan filesystem for available tools."""
        available_tools = []
        
        # Check registered tools
        for tool_name, providers in self._registry.items():
            if provider_name in providers:
                available_tools.append(tool_name)
        
        # Scan discovery paths
        if provider_name in self._discovery_paths:
            provider_path = self._discovery_paths[provider_name]
            if provider_path.exists():
                for module_info in pkgutil.iter_modules([str(provider_path)]):
                    if not module_info.name.startswith('_'):
                        available_tools.append(module_info.name)
        
        # Also check builtin tools
        builtin_path = self._discovery_paths.get("builtin")
        if builtin_path and builtin_path.exists():
            for module_info in pkgutil.iter_modules([str(builtin_path)]):
                if not module_info.name.startswith('_'):
                    available_tools.append(module_info.name)
        
        return sorted(list(set(available_tools)))

    def register_tool_provider(
        self, 
        tool_name: str,
        provider_name: str, 
        provider_class: type[IToolProvider]
    ) -> None:
        """Register tool provider class."""
        if tool_name not in self._registry:
            self._registry[tool_name] = {}
        
        self._registry[tool_name][provider_name] = provider_class

    def get_available_tools(self, provider_name: str) -> list[str]:
        """Get available tools for provider (includes auto-discoverable)."""
        return self._scan_available_tools(provider_name)
    
    def _inject_streaming_context(
        self, 
        tool_instance: IToolProvider, 
        stream_context: IToolStreamContext | None
    ) -> None:
        """
        Inject streaming context into tool if it supports streaming.
        
        Args:
            tool_instance: Tool instance to inject context into
            stream_context: Streaming context to inject
        """
        if not stream_context:
            return
        
        # Check if tool supports streaming
        if isinstance(tool_instance, IStreamableTool):
            if tool_instance.supports_streaming():
                tool_instance.set_stream_context(stream_context)
                logging.debug(f"Injected streaming context into tool: {tool_instance.tool_name}")
            else:
                logging.debug(f"Tool {tool_instance.tool_name} does not support streaming")
        else:
            # Check if the tool wraps a streamable tool (for dynamic adapters)
            base_tool = getattr(tool_instance, 'base_tool_instance', None)
            if base_tool and isinstance(base_tool, IStreamableTool):
                if base_tool.supports_streaming():
                    base_tool.set_stream_context(stream_context)
                    logging.debug(f"Injected streaming context into wrapped tool: {tool_instance.tool_name}")
    
    def is_tool_streamable(self, tool_name: str, provider_name: str) -> bool:
        """
        Check if a tool supports streaming for a given provider.
        
        Args:
            tool_name: Name of the tool
            provider_name: Provider name
            
        Returns:
            True if tool supports streaming
        """
        # Check if registered
        if self._is_registered(tool_name, provider_name):
            provider_class = self._registry[tool_name][provider_name]
            return issubclass(provider_class, IStreamableTool)
        
        # Try auto-discovery to check
        try:
            from ...schemas.domain.tool import Tool
            dummy_tool = Tool(id=tool_name, name=tool_name)
            provider_class = self._auto_discover_tool(dummy_tool, provider_name)
            if provider_class:
                return issubclass(provider_class, IStreamableTool)
        except Exception:
            pass
        
        return False