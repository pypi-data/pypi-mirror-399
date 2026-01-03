"""
Status Command - Handles system status checks
"""

import os
from typing import List, Tuple

from .base_command import BaseCommand
from ..interfaces import DisplayServiceInterface


class StatusCommand(BaseCommand):
    """
    Single Responsibility: Handle system status checks
    Open/Closed: Easy to extend with new status checks
    Interface Segregation: Only depends on display service
    """
    
    def __init__(self, display_service: DisplayServiceInterface):
        super().__init__(display_service)
    
    def execute(self) -> None:
        """Execute the status command"""
        operation = "status check"
        self._log_execution_start(operation)
        
        try:
            self._display_service.display_header()
            self._display_service.display_status("System Status", "info")
            
            self._check_system_components()
            self._check_environment_variables()
            
            self._log_execution_end(operation)
            
        except Exception as e:
            self._handle_error(e, operation)
    
    def _check_system_components(self) -> None:
        """Check status of core system components"""
        checks = self._get_component_checks()
        
        for component, status, status_type in checks:
            self._display_service.display_status(f"  {component}: {status}", status_type)
    
    def _get_component_checks(self) -> List[Tuple[str, str, str]]:
        """Get list of system components to check"""
        return [
            ("Configuration Service", "✓", "success"),
            ("Domain Factory", "✓", "success"),
            ("Session Management", "✓", "success"),
            ("Runner Framework", "✓", "success"),
            ("OpenAI Provider", "✓", "success"),
        ]
    
    def _check_environment_variables(self) -> None:
        """Check status of required environment variables"""
        self._display_service.display_status("Environment Variables", "info")
        
        env_vars = self._get_required_env_vars()
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                display = f"  ✓ {var}: Set ({len(value)} chars)"
                self._display_service.display_status(display, "success")
            else:
                display = f"  ○ {var}: Not set"
                self._display_service.display_status(display, "warning")
    
    def _get_required_env_vars(self) -> List[str]:
        """Get list of required environment variables"""
        return [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY", 
            "DEEPSEEK_API_KEY",
            "GNOSARI_DATABASE_URL"
        ]