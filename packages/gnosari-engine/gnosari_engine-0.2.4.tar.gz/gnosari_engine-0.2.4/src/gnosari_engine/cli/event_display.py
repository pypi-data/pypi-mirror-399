"""
CLI Event Display Service - Advanced streaming event visualization following SOLID principles
"""

import time
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from contextlib import contextmanager

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.status import Status
from rich.spinner import Spinner
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.layout import Layout
from rich.align import Align

from ..runners.events import StreamEvent, EventType


@dataclass
class EventDisplayState:
    """State tracking for event display"""
    current_agent: Optional[str] = None
    current_tool: Optional[str] = None
    tool_call_id: Optional[str] = None
    response_buffer: str = ""
    tool_arguments_buffer: str = ""
    events_count: int = 0
    start_time: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    tool_calls_active: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    completed_tools: list = field(default_factory=list)
    execution_completed: bool = False


class EventDisplayService:
    """
    Enterprise-grade event display service following SOLID principles.
    
    Single Responsibility: Handles only event visualization and CLI formatting
    Open/Closed: Easy to extend with new event types without modification
    Liskov Substitution: Can be replaced with other display implementations
    Interface Segregation: Focused interface for event display
    Dependency Inversion: Depends on abstractions (Rich Console)
    """
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.state = EventDisplayState()
        self._live_display: Optional[Live] = None
        self._status_display: Optional[Status] = None
        
        # Event handlers mapping (Open/Closed Principle)
        self._event_handlers = {
            EventType.AGENT_STARTED: self._handle_agent_started,
            EventType.AGENT_COMPLETED: self._handle_agent_completed,
            EventType.AGENT_ERROR: self._handle_agent_error,
            EventType.AGENT_UPDATED: self._handle_agent_updated,
            
            EventType.TEXT_DELTA: self._handle_text_delta,
            EventType.TEXT_COMPLETE: self._handle_text_complete,
            
            EventType.TOOL_CALL: self._handle_tool_call,
            EventType.TOOL_CALL_DELTA: self._handle_tool_call_delta,
            EventType.TOOL_RESULT: self._handle_tool_result,
            EventType.TOOL_ERROR: self._handle_tool_error,
            
            EventType.MESSAGE_OUTPUT: self._handle_message_output,
            EventType.MESSAGE_COMPLETE: self._handle_message_complete,
            
            EventType.RESPONSE_CREATED: self._handle_response_created,
            EventType.RESPONSE_IN_PROGRESS: self._handle_response_in_progress,
            EventType.RESPONSE_COMPLETE: self._handle_response_complete,
            
            EventType.DEBUG_INFO: self._handle_debug_info,
            EventType.EVENT_ERROR: self._handle_event_error,
            EventType.UNKNOWN_EVENT: self._handle_unknown_event,
            
            # Tool streaming event handlers
            EventType.TOOL_STREAM_START: self._handle_tool_streaming_start,
            EventType.TOOL_STREAM_PROGRESS: self._handle_tool_streaming_progress,
            EventType.TOOL_STREAM_RESULT: self._handle_tool_streaming_result,
            EventType.TOOL_STREAM_COMPLETE: self._handle_tool_streaming_complete,
            EventType.TOOL_STREAM_ERROR: self._handle_tool_streaming_error,
            
            # String fallbacks for tool streaming events
            "tool_start": self._handle_tool_streaming_start,
            "tool_progress": self._handle_tool_streaming_progress,
            "tool_stream_result": self._handle_tool_streaming_result,
            "tool_complete": self._handle_tool_streaming_complete,
            "tool_stream_error": self._handle_tool_streaming_error,
        }
    
    @contextmanager
    def live_event_display(self, debug: bool = False):
        """Context manager for event display - simplified to show streaming updates"""
        try:
            # Simple streaming mode - just show events as they come
            self.console.print("\n🎬 [bold cyan]Starting event stream...[/bold cyan]")
            yield self
        finally:
            self.console.print("\n🏁 [bold green]Event stream completed[/bold green]")
    
    def handle_event(self, event: StreamEvent, debug: bool = False) -> None:
        """
        Main event handler that delegates to specific handlers.
        Follows Single Responsibility and Open/Closed principles.
        """
        self.state.events_count += 1
        self.state.last_activity = time.time()

        if debug:
            self._display_debug_event(event)
            return
        
        # Get event type (handle both enum and string)
        event_type = event.event_type
        if isinstance(event_type, str):
            # Try to convert string to EventType enum
            try:
                event_type = EventType(event_type)
            except ValueError:
                # If it's a tool event string, try direct lookup
                if event_type in self._event_handlers:
                    handler = self._event_handlers[event_type]
                    handler(event)
                    return
                else:
                    event_type = EventType.UNKNOWN_EVENT
        
        # Delegate to specific handler
        handler = self._event_handlers.get(event_type, self._handle_unknown_event)
        handler(event)
        
        # Live display removed - events are shown directly via handlers
    
    def _normalize_event_data(self, data) -> dict:
        """Normalize event data to a consistent dictionary format"""
        if hasattr(data, 'to_dict'):
            return data.to_dict()
        elif isinstance(data, dict):
            return data
        else:
            return {"value": str(data)}
    
    def _create_live_layout(self) -> Layout:
        """Create live display layout"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="response", ratio=2),
            Layout(name="tools", ratio=1)
        )
        
        return layout
    
    def _update_live_display(self) -> None:
        """Update the live display with current state"""
        if not self._live_display or self.state.execution_completed:
            return
        
        layout = self._live_display.renderable
        
        # Header
        header_text = Text("🤖 Gnosari Agent Execution", style="bold cyan")
        if self.state.current_agent:
            header_text.append(f" - {self.state.current_agent}", style="bold yellow")
        layout["header"].update(Align.center(header_text))
        
        # Response area
        response_panel = Panel(
            Text(self.state.response_buffer or "Waiting for response...", style="white"),
            title="Agent Response",
            border_style="cyan"
        )
        layout["response"].update(response_panel)
        
        # Tools area
        tools_content = self._create_tools_display()
        layout["tools"].update(tools_content)
        
        # Footer
        elapsed = time.time() - self.state.start_time
        footer_text = Text(f"Events: {self.state.events_count} | Time: {elapsed:.1f}s", style="dim")
        layout["footer"].update(Align.center(footer_text))
    
    def _create_tools_display(self) -> Panel:
        """Create tools status display"""
        if not self.state.tool_calls_active and not self.state.completed_tools:
            return Panel("No tool activity", title="🛠️ Tools", border_style="dim")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Tool", style="cyan")
        table.add_column("Status", style="yellow")
        
        # Active tool calls
        for call_id, tool_info in self.state.tool_calls_active.items():
            status = "🔄 Running"
            if tool_info.get("arguments_complete"):
                status = "⚙️ Executing"
            table.add_row(tool_info["name"], status)
        
        # Completed tools (last 3)
        for tool_info in self.state.completed_tools[-3:]:
            status = "✅ Complete" if tool_info["status"] == "success" else "❌ Error"
            table.add_row(tool_info["name"], status)
        
        return Panel(table, title="🛠️ Tools", border_style="green")
    
    def _display_debug_event(self, event: StreamEvent) -> None:
        """Display event in debug mode with full details"""
        timestamp = time.strftime("%H:%M:%S", time.localtime(event.timestamp))
        
        # Create debug panel
        event_data = event.to_dict()
        
        # Format event data nicely
        data_text = ""
        for key, value in event_data.get("data", {}).items():
            if key == "original_event":
                continue  # Skip original_event to reduce noise
            data_text += f"  {key}: {value}\n"
        
        debug_content = f"[bold cyan]Type:[/bold cyan] {event.event_type}\n"
        debug_content += f"[bold cyan]Time:[/bold cyan] {timestamp}\n"
        if event.session_id:
            debug_content += f"[bold cyan]Session:[/bold cyan] {event.session_id}\n"
        if event.agent_id:
            debug_content += f"[bold cyan]Agent:[/bold cyan] {event.agent_id}\n"
        debug_content += f"[bold cyan]Data:[/bold cyan]\n{data_text}"
        
        panel = Panel(
            debug_content,
            title=f"🐛 DEBUG EVENT #{self.state.events_count}",
            border_style="red",
            expand=False
        )
        
        self.console.print(panel)
    
    # Event-specific handlers (Single Responsibility)
    
    def _handle_agent_started(self, event: StreamEvent) -> None:
        """Handle agent started events"""
        data = self._normalize_event_data(event.data)
        
        # Get agent name from the event, not the message
        agent_name = data.get("agent_name", event.agent_id or "Unknown Agent")
        self.state.current_agent = agent_name
        
        self.console.print(f"🤖 [bold cyan]{agent_name}[/bold cyan] started", style="bold")
        self.console.file.flush()  # Prepare for streaming text
    
    def _handle_agent_completed(self, event: StreamEvent) -> None:
        """Handle agent completed events"""
        data = event.data
        if hasattr(data, 'to_dict'):
            data = data.to_dict()
        
        status = data.get("status", "completed")
        self.state.execution_completed = True
        
        self.console.print(f"\n✅ Agent [bold green]{status}[/bold green]")
    
    def _handle_agent_error(self, event: StreamEvent) -> None:
        """Handle agent error events"""
        data = event.data
        if hasattr(data, 'to_dict'):
            data = data.to_dict()
        
        error = data.get("error", "Unknown error")
        self.state.execution_completed = True
        
        self.console.print(f"\n❌ [bold red]Agent Error:[/bold red] {error}")
    
    def _handle_agent_updated(self, event: StreamEvent) -> None:
        """Handle agent updated events"""
        # Usually not displayed in normal mode, only in debug
        pass
    
    def _handle_text_delta(self, event: StreamEvent) -> None:
        """Handle text delta events (streaming response)"""
        data = self._normalize_event_data(event.data)
        
        delta = data.get("delta", data.get("value", ""))
        if delta:
            self.state.response_buffer += delta
            
            # Stream directly to console
            self.console.print(delta, end="", style="white")
    
    def _handle_text_complete(self, event: StreamEvent) -> None:
        """Handle text completion events"""
        # Text streaming is complete, no action needed
        pass
    
    def _handle_tool_call(self, event: StreamEvent) -> None:
        """Handle tool call events"""
        data = event.data
        if hasattr(data, 'to_dict'):
            data = data.to_dict()
        
        tool_name = data.get("tool_name", "Unknown Tool")
        call_id = data.get("call_id", "unknown")
        arguments = data.get("arguments", {})
        
        # Store active tool call
        self.state.tool_calls_active[call_id] = {
            "name": tool_name,
            "arguments": arguments,
            "arguments_complete": False,
            "start_time": time.time()
        }
        
        self.console.print(f"\n🛠️ [bold yellow]Calling tool:[/bold yellow] [cyan]{tool_name}[/cyan]")
        if arguments and isinstance(arguments, dict):
                for key, value in arguments.items():
                    # Truncate long values
                    str_value = str(value)
                    if len(str_value) > 100:
                        str_value = str_value[:100] + "..."
                    self.console.print(f"  [dim]{key}:[/dim] {str_value}")
    
    def _handle_tool_call_delta(self, event: StreamEvent) -> None:
        """Handle tool call delta events (streaming arguments)"""
        data = event.data
        if hasattr(data, 'to_dict'):
            data = data.to_dict()
        
        delta = data.get("delta", "")
        call_id = data.get("call_id", "unknown")
        
        if call_id in self.state.tool_calls_active:
            self.state.tool_arguments_buffer += delta
    
    def _handle_tool_result(self, event: StreamEvent) -> None:
        """Handle tool result events"""
        data = event.data
        if hasattr(data, 'to_dict'):
            data = data.to_dict()

        content = data.get("content", "")
        call_id = data.get("call_id", "unknown")
        tool_name = data.get("tool_name", "Unknown Tool")
        
        # Move from active to completed
        if call_id in self.state.tool_calls_active:
            tool_info = self.state.tool_calls_active.pop(call_id)
            tool_info["status"] = "success"
            tool_info["result"] = content
            tool_name = tool_info["name"]
            self.state.completed_tools.append(tool_info)
        
        if not self._live_display:
            self.console.print(f"✅ [bold green]Tool completed:[/bold green] [cyan]{tool_name}[/cyan]")
            # Show truncated result
            if content:
                truncated_content = content[:200] + "..." if len(content) > 200 else content
                self.console.print(f"  [dim]Result:[/dim] {truncated_content}")
    
    def _handle_tool_error(self, event: StreamEvent) -> None:
        """Handle tool error events"""
        data = event.data
        if hasattr(data, 'to_dict'):
            data = data.to_dict()
        
        error = data.get("error", "Unknown error")
        call_id = data.get("call_id", "unknown")
        tool_name = data.get("tool_name", "Unknown Tool")
        
        # Move from active to completed with error
        if call_id in self.state.tool_calls_active:
            tool_info = self.state.tool_calls_active.pop(call_id)
            tool_info["status"] = "error"
            tool_info["error"] = error
            self.state.completed_tools.append(tool_info)
        
        if not self._live_display:
            self.console.print(f"❌ [bold red]Tool error:[/bold red] [cyan]{tool_name}[/cyan]")
            self.console.print(f"  [dim]Error:[/dim] {error}")
    
    def _handle_message_output(self, event: StreamEvent) -> None:
        """Handle message output events"""
        # Similar to text delta but for complete messages
        self._handle_text_delta(event)
    
    def _handle_message_complete(self, event: StreamEvent) -> None:
        """Handle message completion events"""
        # Message is complete
        pass
    
    def _handle_response_created(self, event: StreamEvent) -> None:
        """Handle response created events"""
        data = event.data
        if hasattr(data, 'to_dict'):
            data = data.to_dict()
        
        model = data.get("model", "Unknown")
        
        if not self._live_display:
            self.console.print(f"🔄 [dim]Starting response with model: {model}[/dim]")
    
    def _handle_response_in_progress(self, event: StreamEvent) -> None:
        """Handle response in progress events"""
        # Usually just updates status, no display needed
        pass
    
    def _handle_response_complete(self, event: StreamEvent) -> None:
        """Handle response complete events"""
        data = event.data
        if hasattr(data, 'to_dict'):
            data = data.to_dict()
        
        usage = data.get("usage", {})
        
        if not self._live_display and usage:
            tokens_used = usage.get("total_tokens", "Unknown")
            self.console.print(f"\n[dim]💰 Tokens used: {tokens_used}[/dim]")
    
    def _handle_debug_info(self, event: StreamEvent) -> None:
        """Handle debug info events"""
        data = event.data
        if hasattr(data, 'to_dict'):
            data = data.to_dict()
        
        message = data.get("message", "")
        context = data.get("context", {})
        
        if not self._live_display:
            self.console.print(f"[dim]🐛 Debug: {message}[/dim]")
            if context:
                for key, value in context.items():
                    self.console.print(f"[dim]  {key}: {value}[/dim]")
    
    def _handle_event_error(self, event: StreamEvent) -> None:
        """Handle event processing errors"""
        data = event.data
        if hasattr(data, 'to_dict'):
            data = data.to_dict()
        
        error = data.get("error", "Unknown error")
        
        if not self._live_display:
            self.console.print(f"⚠️ [bold yellow]Event Error:[/bold yellow] {error}")
    
    def _handle_unknown_event(self, event: StreamEvent) -> None:
        """Handle unknown event types"""
        if not self._live_display:
            self.console.print(f"❓ [dim]Unknown event: {event.event_type}[/dim]")
    
    # Tool streaming event handlers
    def _handle_tool_streaming_start(self, event: StreamEvent) -> None:
        """Handle tool streaming start events"""
        data = self._normalize_event_data(event.data)
        tool_name = data.get("tool_name", "Unknown Tool")
        operation = data.get("operation", "operation")
        
        if not self._live_display:
            self.console.print(f"🔧 [bold cyan]Tool Started:[/bold cyan] {tool_name} - {operation}")
    
    def _handle_tool_streaming_progress(self, event: StreamEvent) -> None:
        """Handle tool streaming progress events"""
        import logging
        logger = logging.getLogger(__name__)

        data = self._normalize_event_data(event.data)
        tool_name = data.get("tool_name", "Unknown Tool")

        logger.info(f"[EVENT DISPLAY] Handling tool_progress event. Data keys: {list(data.keys())}")
        logger.info(f"[EVENT DISPLAY] Tool: {tool_name}, step_name: {data.get('step_name')}, progress: {data.get('progress_percent')}")

        # Handle different types of progress events
        if "event" in data:
            event_type = data.get("event")
            logger.info(f"[EVENT DISPLAY] Has 'event' field: {event_type}")
            if event_type == "directory_created":
                directory = data.get("directory", "unknown")
                self.console.print(f"📁 [green]Created directory:[/green] {directory}")
            elif event_type == "directory_changed":
                to_dir = data.get("to_directory", "unknown")
                self.console.print(f"🔄 [blue]Changed to directory:[/blue] {to_dir}")
            elif event_type == "agent_initialized":
                model = data.get("model", "unknown")
                session_id = data.get("session_id", "unknown")
                self.console.print(f"🚀 [green]Agent initialized:[/green] {model} (session: {session_id})")
            elif event_type == "assistant_response":
                content = data.get("content", "")
                if content.strip():
                    # Show partial content for assistant responses
                    self.console.print(f"💬 [dim]{content}[/dim]", end="")
            elif event_type == "task_completed":
                self.console.print(f"✅ [green]Task completed successfully[/green]")
            else:
                # Generic progress event with "event" field
                step_name = data.get("step_name", "")
                progress_percent = data.get("progress_percent", "")
                if step_name:
                    progress_text = f" - {step_name}"
                    if progress_percent:
                        progress_text += f" ({progress_percent}%)"
                    logger.info(f"[EVENT DISPLAY] Printing progress (with event field): {tool_name}{progress_text}")
                    self.console.print(f"⏳ [yellow]Progress:[/yellow] {tool_name}{progress_text}")
        else:
            # Standard progress event without "event" field
            logger.info(f"[EVENT DISPLAY] No 'event' field, using standard progress display")
            step_name = data.get("step_name", "")
            progress_percent = data.get("progress_percent", "")
            logger.info(f"[EVENT DISPLAY] step_name={step_name}, progress_percent={progress_percent}")
            if step_name:
                progress_text = f" - {step_name}"
                if progress_percent:
                    progress_text += f" ({progress_percent}%)"
                logger.info(f"[EVENT DISPLAY] About to print: ⏳ Progress: {tool_name}{progress_text}")
                self.console.print(f"⏳ [yellow]Progress:[/yellow] {tool_name}{progress_text}")
                logger.info(f"[EVENT DISPLAY] Print completed")
            else:
                logger.warning(f"[EVENT DISPLAY] step_name is empty, skipping display")
    
    def _handle_tool_streaming_result(self, event: StreamEvent) -> None:
        """Handle tool streaming result events"""
        data = self._normalize_event_data(event.data)
        tool_name = data.get("tool_name", "Unknown Tool")
        result_count = data.get("result_count", "")
        
        if not self._live_display:
            result_info = f" ({result_count} results)" if result_count else ""
            self.console.print(f"📊 [blue]Tool Result:[/blue] {tool_name}{result_info}")
    
    def _handle_tool_streaming_complete(self, event: StreamEvent) -> None:
        """Handle tool streaming complete events"""
        data = self._normalize_event_data(event.data)
        tool_name = data.get("tool_name", "Unknown Tool")
        success = data.get("success", True)
        
        if not self._live_display:
            if success:
                self.console.print(f"✅ [bold green]Tool Completed:[/bold green] {tool_name}")
            else:
                self.console.print(f"⚠️ [bold yellow]Tool Finished:[/bold yellow] {tool_name}")
    
    def _handle_tool_streaming_error(self, event: StreamEvent) -> None:
        """Handle tool streaming error events"""
        data = self._normalize_event_data(event.data)
        tool_name = data.get("tool_name", "Unknown Tool")
        error = data.get("error", "Unknown error")
        
        if not self._live_display:
            self.console.print(f"❌ [bold red]Tool Error:[/bold red] {tool_name} - {error}")
    
    def display_summary(self) -> None:
        """Display execution summary"""
        elapsed = time.time() - self.state.start_time
        
        summary_table = Table(title="🎯 Execution Summary", show_header=True)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="yellow")
        
        summary_table.add_row("Total Events", str(self.state.events_count))
        summary_table.add_row("Execution Time", f"{elapsed:.2f}s")
        summary_table.add_row("Tools Used", str(len(self.state.completed_tools)))
        
        success_tools = sum(1 for t in self.state.completed_tools if t.get("status") == "success")
        error_tools = len(self.state.completed_tools) - success_tools
        
        if success_tools > 0:
            summary_table.add_row("Successful Tools", str(success_tools))
        if error_tools > 0:
            summary_table.add_row("Failed Tools", str(error_tools))
        
        self.console.print(summary_table)