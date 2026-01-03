"""
Coding Agent Tool with streaming support.

Executes coding tasks using external coding agents like cursor-agent with real-time streaming.
"""

import asyncio
import json
import logging
import os
import shutil
import subprocess
from typing import Any

from ...schemas.domain.execution import AgentRun
from ...schemas.domain.tool import Tool
from ...tools.streaming.interfaces import IStreamableTool, IToolStreamContext
from ...tools.streaming.mixins import StreamableToolMixin, ProgressTracker
from .base import BaseProviderAgnosticTool

logger = logging.getLogger(__name__)


class CodingAgentTool(StreamableToolMixin, BaseProviderAgnosticTool, IStreamableTool):
    """
    Coding Agent Tool with streaming support.
    
    Executes coding tasks using external coding agents with real-time output streaming.
    Follows Open/Closed Principle: Extended with streaming without modification.
    """

    def __init__(self, tool_config: Tool, agent_run: AgentRun):
        # Initialize BaseProviderAgnosticTool first
        BaseProviderAgnosticTool.__init__(self, tool_config)
        # Initialize streaming components
        StreamableToolMixin.__init__(self)
        self.agent_run = agent_run
        self._stream_context: IToolStreamContext | None = None
        
        # Debug: Log the tool configuration being used
        logger.info(f"🔧 [DEBUG] Initializing CodingAgentTool:")
        logger.info(f"  - tool_config.id: {tool_config.id}")
        logger.info(f"  - tool_config.name: {tool_config.name}")
        logger.info(f"  - tool_config.module: {tool_config.module}")
        logger.info(f"  - tool_config.class_name: {tool_config.class_name}")
        logger.info(f"  - tool_config.args: {tool_config.args}")
        logger.info(f"  - self.args: {self.args}")
        
        # Configuration from tool args
        self.agent_name = self.args.get("agent_name", "cursor").lower()
        self.timeout = int(self.args.get("timeout", 300))  # 5 minutes default
        
        logger.info(f"🔧 [DEBUG] Configured values:")
        logger.info(f"  - agent_name: {self.agent_name}")
        logger.info(f"  - timeout: {self.timeout}")
        logger.info(f"  - working_directory: {self.args.get('working_directory')}")
        
        # Validate agent name
        if self.agent_name not in ["cursor"]:
            raise ValueError(f"Unsupported agent: {self.agent_name}. Supported agents: cursor")

    async def execute_core_logic(self, message: str, working_directory: str = None) -> str:
        """
        Execute coding agent with streaming support.
        
        Args:
            message: The message/prompt to send to the coding agent
            working_directory: Optional working directory override
            
        Returns:
            Formatted coding agent results or error message
        """
        logger.info(f"🚀 [DEBUG] execute_core_logic called with:")
        logger.info(f"  - message: '{message[:100]}...'")
        logger.info(f"  - working_directory parameter: {working_directory}")
        logger.info(f"  - self.args: {self.args}")
        logger.info(f"  - current os.getcwd(): {os.getcwd()}")
        
        # Emit start event if streaming is available
        await self._emit_start({
            "message": message[:200],  # Truncate for logging
            "agent_name": self.agent_name,
            "operation": "coding_task"
        })
        
        # Create progress tracker
        progress = ProgressTracker(self, total_steps=3, operation_name="coding_agent")
        
        try:
            # Step 1: Prepare command and environment
            await progress.step("preparing_command", {"agent_name": self.agent_name})
            
            # Determine working directory with debug logging
            logger.info(f"🔍 [DEBUG] Working directory resolution:")
            logger.info(f"  - working_directory param: {working_directory}")
            logger.info(f"  - self.args['working_directory']: {self.args.get('working_directory')}")
            logger.info(f"  - os.getcwd(): {os.getcwd()}")
            
            # Use self.args['working_directory'] as the primary source
            # Only fall back to parameter if args doesn't have working_directory
            args_working_dir = self.args.get('working_directory')
            if args_working_dir:
                cwd = args_working_dir
                logger.info(f"  - using args working_directory: {cwd}")
            elif working_directory and working_directory not in [".", "./"]:
                cwd = working_directory
                logger.info(f"  - using explicit parameter: {cwd}")
            else:
                cwd = os.getcwd()
                logger.info(f"  - using current working directory: {cwd}")
            
            logger.info(f"  - resolved cwd: {cwd}")
            
            # Convert to absolute path for consistency
            cwd = os.path.abspath(cwd)
            logger.info(f"  - absolute cwd: {cwd}")
            
            command = self._get_agent_command(message)
            logger.info(f"🎯 [DEBUG] Final execution details:")
            logger.info(f"  - command: {command}")
            logger.info(f"  - will execute in: {cwd}")
            
            # Step 2: Execute agent command with streaming
            await progress.step("executing_agent", {
                "command": " ".join(command),
                "working_directory": cwd
            })
            
            exit_code, stdout, stderr, final_result = await self._execute_agent_command(command, cwd)
            
            # Step 3: Process results
            await progress.step("processing_results", {
                "exit_code": exit_code,
                "has_stdout": bool(stdout),
                "has_stderr": bool(stderr)
            })
            
            # Emit intermediate result
            await self._emit_result({
                "exit_code": exit_code,
                "agent_name": self.agent_name,
                "message_length": len(message),
                "result_length": len(final_result) if final_result else 0
            })
            
            # Complete progress tracking
            await progress.complete({
                "exit_code": exit_code,
                "agent_name": self.agent_name,
                "success": exit_code == 0
            })
            
            if exit_code == 0:
                return f"Coding agent completed successfully.\n\nFinal result:\n{final_result}"
            else:
                error_msg = stderr if stderr else "Unknown error"
                return f"Coding agent failed with exit code {exit_code}.\n\nError details:\n{error_msg}"
            
        except Exception as e:
            logger.error(f"Error executing coding agent: {e}", exc_info=True)
            await self._emit_error(e)
            return f"Error executing coding agent: {str(e)}"

    def _get_agent_command(self, message: str) -> list[str]:
        """
        Get the command to execute for the specific agent.
        
        Args:
            message: The message to send to the agent
            
        Returns:
            List of command parts
        """
        if self.agent_name == "cursor":
            return [
                "cursor-agent", 
                "--force", 
                "--stream-partial-output",
                "--output-format", "stream-json",
                "-p", 
                message
            ]
        else:
            raise ValueError(f"Unsupported agent: {self.agent_name}")

    async def _execute_agent_command(self, command: list[str], cwd: str) -> tuple[int, str, str, str]:
        """
        Execute the coding agent command with real-time streaming.
        
        Args:
            command: Command to execute
            cwd: Working directory
            
        Returns:
            Tuple of (exit_code, stdout, stderr, final_result)
        """
        logger.info(f"🔧 Executing coding agent: {' '.join(command)}")
        logger.info(f"📁 Working directory: {cwd}")
        
        # Debug: Show current user and environment info
        import getpass
        import pwd
        try:
            current_user = getpass.getuser()
            logger.info(f"👤 Current user (getpass): {current_user}")
            
            # Get more detailed user info
            user_info = pwd.getpwuid(os.getuid())
            logger.info(f"👤 User info (pwd):")
            logger.info(f"  - Username: {user_info.pw_name}")
            logger.info(f"  - UID: {user_info.pw_uid}")
            logger.info(f"  - GID: {user_info.pw_gid}")
            logger.info(f"  - Home directory: {user_info.pw_dir}")
            logger.info(f"  - Shell: {user_info.pw_shell}")
            
            # Show environment variables
            logger.info(f"🌍 Environment info:")
            logger.info(f"  - USER: {os.environ.get('USER', 'not set')}")
            logger.info(f"  - HOME: {os.environ.get('HOME', 'not set')}")
            logger.info(f"  - PATH: {os.environ.get('PATH', 'not set')[:200]}...")
            logger.info(f"  - SHELL: {os.environ.get('SHELL', 'not set')}")
            
            # Show current working directory and permissions
            current_cwd = os.getcwd()
            logger.info(f"📂 Directory info:")
            logger.info(f"  - Current directory: {current_cwd}")
            logger.info(f"  - Target directory: {cwd}")
            logger.info(f"  - Target exists: {os.path.exists(cwd)}")
            if os.path.exists(cwd):
                stat_info = os.stat(cwd)
                logger.info(f"  - Target permissions: {oct(stat_info.st_mode)}")
                logger.info(f"  - Target owner UID: {stat_info.st_uid}")
                logger.info(f"  - Target group GID: {stat_info.st_gid}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get user/environment info: {e}")
        
        # Check if cursor-agent is available and install if needed
        if self.agent_name == "cursor" and not shutil.which("cursor-agent"):
            logger.info("📦 cursor-agent not found, installing...")
            await self._emit_progress({
                "event": "installing_cursor_agent",
                "type": "setup"
            })
            
            try:
                await self._install_cursor_agent()
                logger.info("✅ cursor-agent installed successfully")
                await self._emit_progress({
                    "event": "cursor_agent_installed",
                    "type": "setup"
                })
            except Exception as e:
                error_msg = f"Failed to install cursor-agent: {str(e)}"
                logger.error(f"❌ {error_msg}")
                await self._emit_error(RuntimeError(error_msg))
                raise RuntimeError(error_msg)
        
        # Ensure working directory exists
        try:
            if not os.path.exists(cwd):
                os.makedirs(cwd, exist_ok=True)
                logger.info(f"✅ Created working directory: {cwd}")
                # Emit progress for directory creation
                await self._emit_progress({
                    "event": "directory_created",
                    "directory": cwd,
                    "type": "setup"
                })
            else:
                logger.info(f"✅ Working directory exists: {cwd}")
        except OSError as e:
            logger.error(f"❌ Failed to create working directory {cwd}: {e}")
            await self._emit_error(RuntimeError(f"Failed to create working directory {cwd}: {e}"))
            raise RuntimeError(f"Failed to create working directory {cwd}: {e}")
        
        # Save current directory and change to target directory
        original_cwd = os.getcwd()
        try:
            os.chdir(cwd)
            logger.info(f"🔄 Changed to working directory: {cwd}")
            await self._emit_progress({
                "event": "directory_changed",
                "from_directory": original_cwd,
                "to_directory": cwd,
                "type": "setup"
            })
            
            # Start the process (no need for cwd parameter since we changed directory)
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except Exception as e:
            # Make sure we restore original directory on any error
            os.chdir(original_cwd)
            raise
        
        # Monitor output in real-time
        stdout_lines = []
        stderr_lines = []
        current_content = ""
        final_result = ""
        
        async def read_stream(stream, lines_list, stream_name):
            """Read from a stream line by line and stream agent messages."""
            nonlocal current_content, final_result
            
            while True:
                line = await stream.readline()
                if not line:
                    break
                
                line_text = line.decode('utf-8', errors='replace').rstrip()
                lines_list.append(line_text)
                
                # Try to parse as JSON and handle agent messages
                if line_text.strip():
                    try:
                        json_data = json.loads(line_text)
                        await self._handle_agent_message(json_data)
                        
                        # Extract final result for return
                        if (json_data.get("type") == "result" and 
                            json_data.get("subtype") == "success" and 
                            "result" in json_data):
                            final_result = json_data["result"]
                            
                    except json.JSONDecodeError:
                        # Not JSON, might be plain text output
                        if stream_name == "STDOUT" and line_text:
                            await self._emit_progress({
                                "stream": "stdout",
                                "content": line_text,
                                "type": "plain_text"
                            })
                        elif stream_name == "STDERR" and line_text:
                            await self._emit_progress({
                                "stream": "stderr", 
                                "content": line_text,
                                "type": "error_text"
                            })
        
        # Create tasks for reading both streams
        stdout_task = asyncio.create_task(
            read_stream(process.stdout, stdout_lines, "STDOUT")
        )
        stderr_task = asyncio.create_task(
            read_stream(process.stderr, stderr_lines, "STDERR")
        )
        
        # Wait for process completion or timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(stdout_task, stderr_task, process.wait()),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"❌ Coding agent timeout after {self.timeout} seconds")
            await self._emit_error(TimeoutError(f"Process exceeded {self.timeout} seconds"))
            process.kill()
            await process.wait()
            # Restore directory even on timeout
            try:
                os.chdir(original_cwd)
                logger.info(f"🔄 Restored original directory after timeout: {original_cwd}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to restore directory after timeout: {e}")
            return -1, "", f"Process timed out after {self.timeout} seconds", ""
        
        # Get final output
        stdout_text = "\n".join(stdout_lines)
        stderr_text = "\n".join(stderr_lines)
        
        # If no final result was extracted, use the full stdout
        if not final_result:
            final_result = self._extract_result_from_output(stdout_text)
        
        # Restore original directory
        try:
            os.chdir(original_cwd)
            logger.info(f"🔄 Restored original directory: {original_cwd}")
            await self._emit_progress({
                "event": "directory_restored",
                "directory": original_cwd,
                "type": "cleanup"
            })
        except Exception as e:
            logger.warning(f"⚠️ Failed to restore original directory: {e}")
        
        return process.returncode, stdout_text, stderr_text, final_result

    async def _install_cursor_agent(self) -> None:
        """
        Install cursor-agent using the official installer.
        
        Raises:
            RuntimeError: If installation fails
        """
        logger.info("🔧 Installing cursor-agent...")
        
        try:
            # Download and run the installer
            install_cmd = [
                "bash", "-c",
                "curl https://cursor.com/install -fsS | bash"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *install_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_output = stderr.decode('utf-8', errors='replace') if stderr else "Unknown error"
                raise RuntimeError(f"Installation failed with exit code {process.returncode}: {error_output}")
            
            logger.info("📦 cursor-agent downloaded successfully")
            
            # Add ~/.local/bin to PATH in ~/.bashrc if not already present
            bashrc_path = os.path.expanduser("~/.bashrc")
            path_export = 'export PATH="$HOME/.local/bin:$PATH"'
            
            try:
                # Check if PATH export already exists
                if os.path.exists(bashrc_path):
                    with open(bashrc_path, 'r') as f:
                        bashrc_content = f.read()
                    
                    if path_export not in bashrc_content:
                        with open(bashrc_path, 'a') as f:
                            f.write(f"\n{path_export}\n")
                        logger.info("📝 Added ~/.local/bin to PATH in ~/.bashrc")
                else:
                    # Create ~/.bashrc with PATH export
                    with open(bashrc_path, 'w') as f:
                        f.write(f"{path_export}\n")
                    logger.info("📝 Created ~/.bashrc with PATH export")
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to update ~/.bashrc: {e}")
            
            # Update current process PATH
            local_bin_path = os.path.expanduser("~/.local/bin")
            if local_bin_path not in os.environ.get("PATH", ""):
                os.environ["PATH"] = f"{local_bin_path}:{os.environ.get('PATH', '')}"
                logger.info(f"🔄 Updated current process PATH to include {local_bin_path}")
            
            # Verify installation
            if not shutil.which("cursor-agent"):
                raise RuntimeError("cursor-agent not found in PATH after installation")
                
            logger.info("✅ cursor-agent installation completed and verified")
            
        except Exception as e:
            logger.error(f"❌ Failed to install cursor-agent: {e}")
            raise RuntimeError(f"cursor-agent installation failed: {str(e)}")

    async def _handle_agent_message(self, json_data: dict[str, Any]) -> None:
        """Handle structured agent messages and emit appropriate streaming events."""
        message_type = json_data.get("type")
        
        if message_type == "system":
            subtype = json_data.get("subtype")
            if subtype == "init":
                session_id = json_data.get("session_id", "unknown")
                model = json_data.get("model", "unknown")
                await self._emit_progress({
                    "event": "agent_initialized",
                    "session_id": session_id[-8:] if len(session_id) > 8 else session_id,
                    "model": model,
                    "type": "system"
                })
                
        elif message_type == "user":
            user_msg = json_data.get("message", {})
            content = user_msg.get("content", [])
            if content and isinstance(content, list):
                text = content[0].get("text", "") if content[0].get("type") == "text" else ""
                if text:
                    await self._emit_progress({
                        "event": "user_message",
                        "content": text[:200],  # Truncate for logging
                        "type": "user"
                    })
                    
        elif message_type == "assistant":
            assistant_msg = json_data.get("message", {})
            content = assistant_msg.get("content", [])
            if content and isinstance(content, list):
                text = content[0].get("text", "") if content[0].get("type") == "text" else ""
                if text:
                    await self._emit_progress({
                        "event": "assistant_response",
                        "content": text,
                        "type": "assistant"
                    })
                    
        elif message_type == "result":
            subtype = json_data.get("subtype")
            if subtype == "success":
                await self._emit_progress({
                    "event": "task_completed",
                    "type": "result",
                    "success": True
                })

    def _extract_result_from_output(self, stdout: str) -> str:
        """
        Extract the final result from the coding agent output.
        
        Args:
            stdout: Standard output from the coding agent
            
        Returns:
            Extracted result or full output if no result found
        """
        try:
            # Look for the last result message in JSON format
            lines = stdout.strip().split('\n')
            for line in reversed(lines):
                line = line.strip()
                if line:
                    try:
                        json_data = json.loads(line)
                        if (json_data.get("type") == "result" and 
                            json_data.get("subtype") == "success" and 
                            "result" in json_data):
                            return json_data["result"]
                    except json.JSONDecodeError:
                        continue
            
            # If no result found, return the full output
            return stdout
            
        except Exception as e:
            logger.warning(f"Failed to extract result: {str(e)}")
            return stdout

    def get_input_schema(self) -> dict[str, Any]:
        """Get input schema for coding agent."""
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message/prompt to send to the coding agent"
                },
                "working_directory": {
                    "type": "string",
                    "description": "Optional working directory for agent execution"
                }
            },
            "required": ["message"]
        }

    def get_output_schema(self) -> dict[str, Any]:
        """Get output schema for coding agent."""
        return {
            "type": "string",
            "description": "Results from coding agent execution"
        }
    
    # IStreamableTool interface methods
    def supports_streaming(self) -> bool:
        """Coding agent tool supports streaming."""
        return True
    
    def set_stream_context(self, context: IToolStreamContext) -> None:
        """Set streaming context for this tool."""
        self._stream_context = context
        # Also set in the mixin
        super().set_stream_context(context)
    
    def _get_tool_name(self) -> str:
        """Get tool name for streaming events."""
        return self.name or "coding_agent"