"""
Logging Service - SOLID implementation for enterprise-grade logging configuration
"""

import logging
import sys
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any
from pathlib import Path

from rich.logging import RichHandler
from rich.console import Console


class LogLevel(Enum):
    """Enumeration of available log levels"""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    TRACE = "TRACE"  # Custom level for ultra-verbose debugging


class LoggerServiceInterface(ABC):
    """
    Single Responsibility: Define logging service contract
    Interface Segregation: Clean interface for logging configuration
    """
    
    @abstractmethod
    def configure_logging(
        self, 
        level: LogLevel = LogLevel.INFO,
        debug_mode: bool = False,
        verbose: bool = False,
        log_file: Optional[Path] = None,
        structured: bool = False
    ) -> None:
        """Configure the logging system"""
        pass
    
    @abstractmethod
    def get_logger(self, name: str) -> logging.Logger:
        """Get a configured logger instance"""
        pass
    
    @abstractmethod
    def set_debug_mode(self, enabled: bool) -> None:
        """Enable/disable debug mode"""
        pass
    
    @abstractmethod
    def add_structured_context(self, context: Dict[str, Any]) -> None:
        """Add structured context to all log messages"""
        pass


class CLILoggerService(LoggerServiceInterface):
    """
    Single Responsibility: Manage CLI logging configuration
    Open/Closed: Extensible for different output formats
    Dependency Inversion: Depends on abstractions (Console, Logger)
    """
    
    def __init__(self, console: Optional[Console] = None):
        self._console = console or Console(stderr=True)
        self._configured = False
        self._debug_mode = False
        self._structured_context: Dict[str, Any] = {}
        self._trace_level = 5  # Custom TRACE level below DEBUG
        
        # Add custom TRACE level
        logging.addLevelName(self._trace_level, "TRACE")
        
    def configure_logging(
        self, 
        level: LogLevel = LogLevel.INFO,
        debug_mode: bool = False,
        verbose: bool = False,
        log_file: Optional[Path] = None,
        structured: bool = False
    ) -> None:
        """Configure the logging system with enterprise-grade options"""
        
        # Determine effective log level
        effective_level = self._determine_effective_level(level, debug_mode, verbose)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(effective_level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Configure console handler
        self._configure_console_handler(root_logger, effective_level, structured)
        
        # Configure file handler if specified
        if log_file:
            self._configure_file_handler(root_logger, log_file, effective_level, structured)
        
        # Store configuration state
        self._debug_mode = debug_mode
        self._configured = True
        
        # Log configuration summary
        logger = self.get_logger("cli.logging")
        logger.info(f"Logging configured: level={effective_level}, debug={debug_mode}")
        
    def get_logger(self, name: str) -> logging.Logger:
        """Get a configured logger instance with custom methods"""
        logger = logging.getLogger(name)
        
        # Add custom trace method
        def trace(message, *args, **kwargs):
            if logger.isEnabledFor(self._trace_level):
                logger._log(self._trace_level, message, args, **kwargs)
        
        logger.trace = trace
        return logger
    
    def set_debug_mode(self, enabled: bool) -> None:
        """Enable/disable debug mode dynamically"""
        self._debug_mode = enabled
        
        if enabled:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.INFO)
        
        logger = self.get_logger("cli.logging")
        logger.info(f"Debug mode {'enabled' if enabled else 'disabled'}")
    
    def add_structured_context(self, context: Dict[str, Any]) -> None:
        """Add structured context to all log messages"""
        self._structured_context.update(context)
        
        logger = self.get_logger("cli.logging")
        logger.debug(f"Added structured context: {context}")
    
    def _determine_effective_level(
        self, 
        level: LogLevel, 
        debug_mode: bool, 
        verbose: bool
    ) -> int:
        """Determine the effective logging level based on options"""
        
        if debug_mode:
            return logging.DEBUG
        elif verbose:
            return logging.INFO if level == LogLevel.WARNING else getattr(logging, level.value)
        else:
            return getattr(logging, level.value)
    
    def _configure_console_handler(
        self, 
        logger: logging.Logger, 
        level: int, 
        structured: bool
    ) -> None:
        """Configure console output handler"""
        
        if structured:
            # Use standard formatter for structured output
            handler = logging.StreamHandler(sys.stderr)
            formatter = self._create_structured_formatter()
        else:
            # Use Rich handler for beautiful console output
            handler = RichHandler(
                console=self._console,
                show_time=True,
                show_path=level <= logging.DEBUG,
                show_level=True,
                markup=True,
                rich_tracebacks=True,
                tracebacks_show_locals=level <= logging.DEBUG
            )
            formatter = logging.Formatter(
                fmt="%(message)s",
                datefmt="[%X]"
            )
        
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    def _configure_file_handler(
        self, 
        logger: logging.Logger, 
        log_file: Path, 
        level: int, 
        structured: bool
    ) -> None:
        """Configure file output handler"""
        
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.FileHandler(log_file)
        handler.setLevel(level)
        
        if structured:
            formatter = self._create_structured_formatter()
        else:
            formatter = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    def _create_structured_formatter(self) -> logging.Formatter:
        """Create a structured JSON formatter"""
        import json
        import datetime
        
        class StructuredFormatter(logging.Formatter):
            def format(self, record):
                # Build structured log entry
                log_entry = {
                    'timestamp': datetime.datetime.fromtimestamp(record.created).isoformat(),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno
                }
                
                # Add structured context
                if self._structured_context:
                    log_entry['context'] = self._structured_context.copy()
                
                # Add exception info if present
                if record.exc_info:
                    log_entry['exception'] = self.formatException(record.exc_info)
                
                return json.dumps(log_entry, default=str)
        
        return StructuredFormatter()


class LoggingConfigurationFactory:
    """
    Single Responsibility: Create logging service instances
    Factory Pattern: Encapsulates logging service creation logic
    """
    
    @staticmethod
    def create_cli_logger(console: Optional[Console] = None) -> LoggerServiceInterface:
        """Create a CLI logger service instance"""
        return CLILoggerService(console)
    
    @staticmethod
    def create_test_logger() -> LoggerServiceInterface:
        """Create a logger service for testing (no console output)"""
        return CLILoggerService(Console(file=open('/dev/null', 'w')))