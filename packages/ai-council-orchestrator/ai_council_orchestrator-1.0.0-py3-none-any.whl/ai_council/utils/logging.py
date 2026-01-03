"""Logging configuration and utilities for AI Council."""

import logging
import sys
from typing import Optional, Dict, Any
import structlog
from structlog.types import FilteringBoundLogger


def configure_logging(
    level: str = "INFO",
    format_json: bool = False,
    include_timestamp: bool = True,
    include_caller: bool = False,
) -> None:
    """
    Configure structured logging for the AI Council system.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_json: Whether to output logs in JSON format
        include_timestamp: Whether to include timestamps in logs
        include_caller: Whether to include caller information in logs
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )
    
    # Configure structlog processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
    ]
    
    if include_caller:
        processors.append(structlog.processors.CallsiteParameterAdder())
    
    if include_timestamp:
        processors.append(structlog.processors.TimeStamper(fmt="iso"))
    
    if format_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True),
        ])
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper())
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> FilteringBoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name, typically __name__
        
    Returns:
        Configured structlog logger instance
    """
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to other classes."""
    
    @property
    def logger(self) -> FilteringBoundLogger:
        """Get a logger instance for this class."""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__module__)
        return self._logger
    
    def log_operation(
        self,
        operation: str,
        level: str = "info",
        **kwargs: Any
    ) -> None:
        """
        Log an operation with structured data.
        
        Args:
            operation: Name of the operation being performed
            level: Log level (debug, info, warning, error, critical)
            **kwargs: Additional structured data to include in the log
        """
        log_method = getattr(self.logger, level.lower())
        log_method(f"Operation: {operation}", **kwargs)
    
    def log_error(
        self,
        error: Exception,
        operation: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        Log an error with structured data.
        
        Args:
            error: The exception that occurred
            operation: Optional operation name where error occurred
            **kwargs: Additional structured data to include in the log
        """
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            **kwargs
        }
        
        if operation:
            error_data["operation"] = operation
            
        self.logger.error("Error occurred", **error_data)
    
    def log_performance(
        self,
        operation: str,
        duration: float,
        **kwargs: Any
    ) -> None:
        """
        Log performance metrics for an operation.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            **kwargs: Additional performance metrics
        """
        self.logger.info(
            f"Performance: {operation}",
            duration_seconds=duration,
            **kwargs
        )