"""
Tool streaming mixins for adding streaming capabilities to existing tools.

Provides composable streaming functionality following SOLID principles.
"""

import functools
import logging
from typing import Any, Callable, TypeVar, Union

from .interfaces import BaseStreamableTool, IStreamableTool, IToolStreamContext
from .registry import StreamContextRegistry

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


class StreamableToolMixin(BaseStreamableTool):
    """
    Mixin that adds streaming capabilities to existing tools.
    
    Follows Open/Closed Principle: Extends tools without modifying them.
    Follows Composition over Inheritance: Can be mixed with any tool class.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__()
        # Allow for multiple inheritance by calling super()
        if hasattr(super(), '__init__'):
            super().__init__(*args, **kwargs)  # type: ignore
    
    def _get_tool_name(self) -> str:
        """Get tool name from various possible sources."""
        # Try different common attributes for tool name
        for attr in ['name', 'tool_name', '__class__.__name__']:
            if hasattr(self, attr):
                value = getattr(self, attr)
                if isinstance(value, str) and value:
                    return value
        
        # Fallback to class name
        return self.__class__.__name__
    
    async def execute_with_streaming(self, method_name: str = 'execute_core_logic', **kwargs) -> Any:
        """
        Execute a method with automatic streaming events.
        
        Args:
            method_name: Name of the method to execute with streaming
            **kwargs: Arguments to pass to the method
            
        Returns:
            Result from the executed method
        """
        tool_name = self._get_tool_name()
        
        # Emit start event
        await self._emit_start({
            "method": method_name,
            "args": {k: str(v)[:100] for k, v in kwargs.items()}  # Truncate for logging
        })
        
        try:
            # Get the method to execute
            method = getattr(self, method_name)
            if not callable(method):
                raise AttributeError(f"Method {method_name} is not callable")
            
            # Execute the method
            result = await method(**kwargs) if asyncio.iscoroutinefunction(method) else method(**kwargs)
            
            # Emit completion event
            await self._emit_complete({
                "method": method_name,
                "result_type": type(result).__name__,
                "result_size": len(str(result)) if result else 0
            })
            
            return result
            
        except Exception as e:
            # Emit error event
            await self._emit_error(e)
            logger.error(f"Error in {tool_name}.{method_name}: {e}")
            raise


def with_streaming_events(
    start_data: dict[str, Any] | None = None,
    progress_callback: Callable[[Any], dict[str, Any]] | None = None,
    complete_data: dict[str, Any] | None = None
) -> Callable[[F], F]:
    """
    Decorator that adds streaming events to any method.
    
    Follows Decorator Pattern: Adds behavior without changing the original method.
    
    Args:
        start_data: Data to include in start event
        progress_callback: Function to generate progress data from method arguments
        complete_data: Data to include in completion event
        
    Returns:
        Decorated method with streaming events
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            # Check if the instance supports streaming
            if not isinstance(self, IStreamableTool) or not self.has_stream_context:
                # No streaming support, execute normally
                return await func(self, *args, **kwargs)
            
            tool_name = self._get_tool_name()
            
            # Emit start event
            start_event_data = start_data or {}
            if progress_callback:
                try:
                    callback_data = progress_callback({'args': args, 'kwargs': kwargs})
                    start_event_data.update(callback_data)
                except Exception as e:
                    logger.warning(f"Progress callback failed for {tool_name}: {e}")
            
            await self._emit_start(start_event_data)
            
            try:
                # Execute the original method
                result = await func(self, *args, **kwargs)
                
                # Emit completion event
                complete_event_data = complete_data or {}
                complete_event_data.update({
                    "result_type": type(result).__name__,
                    "success": True
                })
                await self._emit_complete(complete_event_data)
                
                return result
                
            except Exception as e:
                # Emit error event
                await self._emit_error(e)
                raise
        
        @functools.wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            # For sync methods, we can't emit events directly
            # This is a limitation - sync methods can't stream
            logger.debug(f"Sync method {func.__name__} cannot emit streaming events")
            return func(self, *args, **kwargs)
        
        # Return appropriate wrapper based on whether function is async
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper  # type: ignore
    
    return decorator


class ProgressTracker:
    """
    Helper class for tracking and emitting progress events.
    
    Follows Single Responsibility Principle: Only tracks progress.
    """
    
    def __init__(self, tool: BaseStreamableTool, total_steps: int, operation_name: str = ""):
        self._tool = tool
        self._total_steps = total_steps
        self._current_step = 0
        self._operation_name = operation_name
    
    async def step(self, step_name: str = "", step_data: dict[str, Any] | None = None) -> None:
        """Advance progress by one step and emit event."""
        self._current_step += 1
        progress_percent = (self._current_step / self._total_steps) * 100
        
        progress_data = {
            "operation": self._operation_name,
            "step": self._current_step,
            "total_steps": self._total_steps,
            "progress_percent": round(progress_percent, 2),
            "step_name": step_name
        }
        
        if step_data:
            progress_data.update(step_data)
        
        await self._tool._emit_progress(progress_data)
    
    async def complete(self, completion_data: dict[str, Any] | None = None) -> None:
        """Mark operation as complete."""
        complete_data = {
            "operation": self._operation_name,
            "total_steps": self._total_steps,
            "completed": True
        }
        
        if completion_data:
            complete_data.update(completion_data)
        
        await self._tool._emit_complete(complete_data)
    
    @property
    def progress_percent(self) -> float:
        """Get current progress percentage."""
        return (self._current_step / self._total_steps) * 100


# Import asyncio for decorator functionality
import asyncio