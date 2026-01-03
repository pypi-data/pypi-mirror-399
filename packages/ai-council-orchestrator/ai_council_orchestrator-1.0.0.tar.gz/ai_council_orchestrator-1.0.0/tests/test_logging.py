"""Tests for logging utilities."""

import pytest
from ai_council.utils.logging import configure_logging, get_logger, LoggerMixin


class TestLoggingConfiguration:
    """Test logging configuration."""
    
    def test_configure_logging_basic(self):
        """Test basic logging configuration."""
        # Should not raise any exceptions
        configure_logging()
        configure_logging(level="DEBUG")
        configure_logging(format_json=True)
        configure_logging(include_timestamp=False)
        configure_logging(include_caller=True)
    
    def test_get_logger(self):
        """Test getting logger instance."""
        configure_logging()
        logger = get_logger("test_module")
        
        assert logger is not None
        # Logger should have basic methods
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')


class TestLoggerMixin:
    """Test LoggerMixin functionality."""
    
    def test_logger_mixin(self):
        """Test LoggerMixin provides logger property."""
        configure_logging()
        
        class TestClass(LoggerMixin):
            pass
        
        instance = TestClass()
        logger = instance.logger
        
        assert logger is not None
        assert hasattr(logger, 'info')
    
    def test_log_operation(self):
        """Test log_operation method."""
        configure_logging()
        
        class TestClass(LoggerMixin):
            def test_method(self):
                self.log_operation("test_operation", level="info", extra_data="test")
        
        instance = TestClass()
        # Should not raise any exceptions
        instance.test_method()
    
    def test_log_error(self):
        """Test log_error method."""
        configure_logging()
        
        class TestClass(LoggerMixin):
            def test_method(self):
                try:
                    raise ValueError("Test error")
                except Exception as e:
                    self.log_error(e, operation="test_operation")
        
        instance = TestClass()
        # Should not raise any exceptions
        instance.test_method()
    
    def test_log_performance(self):
        """Test log_performance method."""
        configure_logging()
        
        class TestClass(LoggerMixin):
            def test_method(self):
                self.log_performance("test_operation", 1.5, requests=100)
        
        instance = TestClass()
        # Should not raise any exceptions
        instance.test_method()