"""
Version Command - Handles version information display
"""

from .base_command import BaseCommand
from ..interfaces import DisplayServiceInterface


class VersionCommand(BaseCommand):
    """
    Single Responsibility: Handle version information display
    Open/Closed: Easy to extend with additional version info
    Interface Segregation: Only depends on display service
    """
    
    def __init__(self, display_service: DisplayServiceInterface):
        super().__init__(display_service)
    
    def execute(self) -> None:
        """Execute the version command"""
        operation = "version display"
        self._log_execution_start(operation)
        
        try:
            self._display_service.display_header()
            self._display_version_info()
            self._log_execution_end(operation)
            
        except Exception as e:
            self._handle_error(e, operation)
    
    def _display_version_info(self) -> None:
        """Display version and system information"""
        version_info = self._get_version_info()
        
        for info, status_type in version_info:
            self._display_service.display_status(info, status_type)
    
    def _get_version_info(self) -> list:
        """Get version information to display"""
        return [
            ("Gnosari Engine CLI", "info"),
            ("Version: 1.0.0", "success"),
            ("Python: 3.9+", "info"),
            ("License: MIT", "warning")
        ]