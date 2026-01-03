"""
Logging Configuration - Enterprise-grade logging setup and utilities
"""

import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

from .logger_service import LogLevel, LoggerServiceInterface, LoggingConfigurationFactory


@dataclass
class LoggingConfiguration:
    """
    Value Object: Represents logging configuration settings
    Immutable configuration for logging setup
    """
    level: LogLevel = LogLevel.INFO
    debug_mode: bool = False
    verbose: bool = False
    log_file: Optional[Path] = None
    structured: bool = False
    context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.context is None:
            self.context = {}
        
        # Ensure log file path is absolute if provided
        if self.log_file and not self.log_file.is_absolute():
            self.log_file = Path.cwd() / self.log_file


class LoggingConfigurator:
    """
    Single Responsibility: Configure logging based on CLI arguments and environment
    """
    
    def __init__(self, logger_service: LoggerServiceInterface):
        self._logger_service = logger_service
        self._is_configured = False
    
    def configure_from_cli_args(
        self,
        log_level: Optional[str] = None,
        debug: bool = False,
        verbose: bool = False,
        log_file: Optional[str] = None,
        structured_logs: bool = False,
        session_id: Optional[str] = None,
        team_name: Optional[str] = None
    ) -> LoggingConfiguration:
        """
        Configure logging from CLI arguments
        
        Args:
            log_level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            debug: Enable debug mode
            verbose: Enable verbose output
            log_file: Path to log file
            structured_logs: Enable structured JSON logging
            session_id: Session ID for context
            team_name: Team name for context
            
        Returns:
            LoggingConfiguration instance
        """
        
        # Determine log level
        effective_level = self._determine_log_level(log_level, debug, verbose)
        
        # Build context
        context = self._build_logging_context(session_id, team_name)
        
        # Create configuration
        config = LoggingConfiguration(
            level=effective_level,
            debug_mode=debug,
            verbose=verbose,
            log_file=Path(log_file) if log_file else None,
            structured=structured_logs,
            context=context
        )
        
        # Apply configuration
        self._apply_configuration(config)
        
        return config
    
    def configure_from_environment(self) -> LoggingConfiguration:
        """
        Configure logging from environment variables
        
        Environment variables:
        - GNOSARI_LOG_LEVEL: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - GNOSARI_DEBUG: Enable debug mode (true/false)
        - GNOSARI_VERBOSE: Enable verbose mode (true/false)
        - GNOSARI_LOG_FILE: Path to log file
        - GNOSARI_STRUCTURED_LOGS: Enable structured logging (true/false)
        """
        
        log_level = os.getenv('GNOSARI_LOG_LEVEL')
        debug = os.getenv('GNOSARI_DEBUG', '').lower() in ('true', '1', 'yes')
        verbose = os.getenv('GNOSARI_VERBOSE', '').lower() in ('true', '1', 'yes')
        log_file = os.getenv('GNOSARI_LOG_FILE')
        structured = os.getenv('GNOSARI_STRUCTURED_LOGS', '').lower() in ('true', '1', 'yes')
        
        return self.configure_from_cli_args(
            log_level=log_level,
            debug=debug,
            verbose=verbose,
            log_file=log_file,
            structured_logs=structured
        )
    
    def add_execution_context(
        self,
        provider: str,
        execution_mode: str,
        team_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> None:
        """Add execution-specific context to logging"""
        
        context = {
            'provider': provider,
            'execution_mode': execution_mode
        }
        
        if team_id:
            context['team_id'] = team_id
        
        if agent_id:
            context['agent_id'] = agent_id
        
        self._logger_service.add_structured_context(context)
    
    def _determine_log_level(
        self,
        log_level: Optional[str],
        debug: bool,
        verbose: bool
    ) -> LogLevel:
        """Determine effective log level from various inputs"""
        
        if debug:
            return LogLevel.DEBUG
        
        if log_level:
            try:
                return LogLevel(log_level.upper())
            except ValueError:
                # Invalid log level, fall back to INFO with warning
                logger = logging.getLogger(__name__)
                logger.warning(f"Invalid log level '{log_level}', using INFO")
                return LogLevel.INFO
        
        if verbose:
            return LogLevel.INFO
        
        return LogLevel.WARNING  # Default to WARNING for production use
    
    def _build_logging_context(
        self,
        session_id: Optional[str],
        team_name: Optional[str]
    ) -> Dict[str, Any]:
        """Build structured logging context"""
        
        context = {
            'component': 'gnosari-cli',
            'version': '1.0.0'  # Should be imported from version module
        }
        
        if session_id:
            context['session_id'] = session_id
        
        if team_name:
            context['team_name'] = team_name
        
        return context
    
    def _apply_configuration(self, config: LoggingConfiguration) -> None:
        """Apply the logging configuration"""
        
        self._logger_service.configure_logging(
            level=config.level,
            debug_mode=config.debug_mode,
            verbose=config.verbose,
            log_file=config.log_file,
            structured=config.structured
        )
        
        if config.context:
            self._logger_service.add_structured_context(config.context)
        
        self._is_configured = True


def create_default_logging_configurator() -> LoggingConfigurator:
    """Factory function to create default logging configurator"""
    logger_service = LoggingConfigurationFactory.create_cli_logger()
    return LoggingConfigurator(logger_service)


def setup_default_logging(
    debug: bool = False,
    verbose: bool = False,
    log_file: Optional[str] = None
) -> LoggingConfigurator:
    """
    Convenience function to setup default logging configuration
    
    Args:
        debug: Enable debug mode
        verbose: Enable verbose output
        log_file: Optional log file path
        
    Returns:
        Configured LoggingConfigurator instance
    """
    configurator = create_default_logging_configurator()
    configurator.configure_from_cli_args(
        debug=debug,
        verbose=verbose,
        log_file=log_file
    )
    return configurator