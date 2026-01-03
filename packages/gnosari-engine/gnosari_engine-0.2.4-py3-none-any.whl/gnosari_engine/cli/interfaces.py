"""
CLI Interfaces - Following SOLID principles with clean abstractions
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Any, Dict, Callable, Protocol

from ..schemas.domain import Team, AgentRun, Task, TaskRun
from .logger_service import LoggerServiceInterface


class ConfigurationLoaderInterface(ABC):
    """Single Responsibility: Load team configurations"""
    
    @abstractmethod
    def load_team_configuration(self, config_path: Path) -> Team:
        """Load team configuration from file"""
        pass


class ExecutionServiceInterface(ABC):
    """Single Responsibility: Handle execution orchestration"""
    
    
    @abstractmethod
    async def execute_agent(
        self, 
        agent_run: AgentRun, 
        provider: str,
        database_url: Optional[str] = None,
        stream: bool = True,
        debug: bool = False,
        logger_service: Optional[LoggerServiceInterface] = None
    ) -> str:
        """Execute a single agent"""
        pass


class DisplayServiceInterface(ABC):
    """Single Responsibility: Handle all display and formatting"""
    
    @abstractmethod
    def display_header(self) -> None:
        """Display the CLI header"""
        pass
    
    @abstractmethod
    def display_execution_details(
        self, 
        team: Team, 
        provider: str, 
        execution_mode: str,
        session_id: Optional[str] = None
    ) -> None:
        """Display execution details panel"""
        pass
    
    @abstractmethod
    def display_status(self, message: str, status_type: str = "info") -> None:
        """Display status messages"""
        pass
    
    @abstractmethod
    def display_streaming_output(self, content: str) -> None:
        """Display streaming content"""
        pass
    
    @abstractmethod
    def display_final_result(self, result: str) -> None:
        """Display final execution result"""
        pass
    
    @abstractmethod
    def show_loading(self, message: str):
        """Create a loading context manager"""
        pass
    
    @abstractmethod
    def show_progress(self, description: str):
        """Create a progress context manager"""
        pass


class SessionManagerInterface(ABC):
    """Single Responsibility: Handle session management"""
    
    @abstractmethod
    def generate_session_id(self) -> str:
        """Generate a new session ID"""
        pass


class DomainFactoryInterface(ABC):
    """Single Responsibility: Create domain objects"""

    @abstractmethod
    def create_agent_run(
        self,
        team: Team,
        agent_id: str,
        message: str,
        stream: bool = True,
        debug: bool = False
    ) -> AgentRun:
        """Create agent execution context"""
        pass

    @abstractmethod
    def create_task_from_dict(self, task_data: Dict[str, Any]) -> Task:
        """Create Task domain object from dictionary"""
        pass

    @abstractmethod
    def create_task_run(
        self,
        task: Task,
        team: Team,
        prompt_builder: Any,
        stream: bool = True,
        debug: bool = False,
        tool_streaming: bool = True,
        stream_merger: str = "time_ordered",
        session_id: Optional[str] = None,
        account_id: Optional[int] = None
    ) -> TaskRun:
        """Create TaskRun execution context"""
        pass


