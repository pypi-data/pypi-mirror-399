"""Tests for comprehensive failure handling system."""

import pytest
import time
from unittest.mock import Mock, patch

from ai_council.core.failure_handling import (
    FailureType, RiskLevel, FailureEvent, RetryConfig, RetryStrategy,
    CircuitBreakerConfig, CircuitBreaker, CircuitBreakerState,
    APIFailureHandler, RateLimitHandler, ResilienceManager,
    create_failure_event, resilience_manager
)
from ai_council.core.timeout_handler import (
    TimeoutHandler, AdaptiveTimeoutManager, RateLimitManager,
    timeout_handler, adaptive_timeout_manager, rate_limit_manager
)


class TestFailureHandling:
    """Test failure handling components."""
    
    def test_create_failure_event(self):
        """Test failure event creation."""
        failure = create_failure_event(
            FailureType.API_FAILURE,
            "test_component",
            "Test error message",
            subtask_id="test_subtask",
            model_id="test_model",
            severity=RiskLevel.MEDIUM
        )
        
        assert failure.failure_type == FailureType.API_FAILURE
        assert failure.component == "test_component"
        assert failure.error_message == "Test error message"
        assert failure.subtask_id == "test_subtask"
        assert failure.model_id == "test_model"
        assert failure.severity == RiskLevel.MEDIUM
        assert not failure.resolved
    
    def test_api_failure_handler(self):
        """Test API failure handler."""
        retry_config = RetryConfig(
            max_attempts=3,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            base_delay=1.0
        )
        handler = APIFailureHandler(retry_config)
        
        # Test can handle API failures
        failure = create_failure_event(
            FailureType.API_FAILURE,
            "test_component",
            "API error"
        )
        assert handler.can_handle(failure)
        
        # Test recovery action
        recovery = handler.handle(failure)
        assert recovery.should_retry
        assert recovery.action_type == "retry_with_backoff"
        assert recovery.retry_delay > 0
    
    def test_rate_limit_handler(self):
        """Test rate limit handler."""
        handler = RateLimitHandler()
        
        # Test can handle rate limit failures
        failure = create_failure_event(
            FailureType.RATE_LIMIT,
            "test_component",
            "Rate limit exceeded",
            model_id="test_model"
        )
        assert handler.can_handle(failure)
        
        # Test recovery action
        recovery = handler.handle(failure)
        assert recovery.should_retry
        assert recovery.action_type == "rate_limit_backoff"
        assert recovery.retry_delay > 0
    
    def test_circuit_breaker(self):
        """Test circuit breaker functionality."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=1.0,
            success_threshold=1
        )
        cb = CircuitBreaker("test_cb", config)
        
        # Initially closed
        assert cb.state == CircuitBreakerState.CLOSED
        
        # Successful calls
        result = cb.call(lambda: "success")
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED
        
        # Simulate failures
        with pytest.raises(ValueError):
            cb.call(lambda: exec('raise ValueError("test error")'))
        
        with pytest.raises(ValueError):
            cb.call(lambda: exec('raise ValueError("test error")'))
        
        # Should be open now
        assert cb.state == CircuitBreakerState.OPEN
        
        # Should reject calls when open
        from ai_council.core.failure_handling import CircuitBreakerOpenError
        with pytest.raises(CircuitBreakerOpenError):
            cb.call(lambda: "should fail")
    
    def test_resilience_manager(self):
        """Test resilience manager."""
        manager = ResilienceManager()
        
        # Test failure handling
        failure = create_failure_event(
            FailureType.API_FAILURE,
            "test_component",
            "Test error"
        )
        
        recovery = manager.handle_failure(failure)
        assert recovery.action_type in ["retry_with_backoff", "unhandled_failure"]
        
        # Test statistics
        stats = manager.get_failure_statistics()
        assert "total_failures" in stats
        assert stats["total_failures"] >= 1
        
        # Test health check
        health = manager.health_check()
        assert "overall_health" in health
        assert health["overall_health"] in ["healthy", "degraded"]


class TestTimeoutHandling:
    """Test timeout handling components."""
    
    def test_timeout_handler_sync(self):
        """Test timeout handler with synchronous functions."""
        handler = TimeoutHandler()
        
        # Test successful execution
        def quick_function():
            return "success"
        
        result = handler.execute_with_timeout(
            quick_function, 5.0, "test_op", "test_component"
        )
        assert result == "success"
        
        # Test timeout
        def slow_function():
            time.sleep(2.0)
            return "too slow"
        
        from ai_council.core.timeout_handler import TimeoutError
        with pytest.raises(TimeoutError):
            handler.execute_with_timeout(
                slow_function, 0.1, "slow_op", "test_component"
            )
    
    def test_adaptive_timeout_manager(self):
        """Test adaptive timeout manager."""
        manager = AdaptiveTimeoutManager()
        
        # Test default timeout
        timeout = manager.get_adaptive_timeout("new_operation")
        assert timeout == 30.0  # Default
        
        # Record some execution times
        manager.record_execution_time("test_op", 1.0)
        manager.record_execution_time("test_op", 2.0)
        manager.record_execution_time("test_op", 1.5)
        
        # Get adaptive timeout
        adaptive_timeout = manager.get_adaptive_timeout("test_op")
        assert adaptive_timeout > 0
        assert adaptive_timeout != 30.0  # Should be different from default
        
        # Test performance stats
        stats = manager.get_performance_stats("test_op")
        assert stats["count"] == 3
        assert stats["mean"] == 1.5
    
    def test_rate_limit_manager(self):
        """Test rate limit manager."""
        manager = RateLimitManager()
        
        # Set rate limit
        manager.set_rate_limit("test_resource", 2)  # 2 requests per minute
        
        # First request should be allowed
        allowed, wait_time = manager.check_rate_limit("test_resource")
        assert allowed
        assert wait_time == 0.0
        
        # Second request should be allowed
        allowed, wait_time = manager.check_rate_limit("test_resource")
        assert allowed
        assert wait_time == 0.0
        
        # Third request should be rate limited
        allowed, wait_time = manager.check_rate_limit("test_resource")
        assert not allowed
        assert wait_time > 0
        
        # Test status
        status = manager.get_rate_limit_status("test_resource")
        assert status["configured"]
        assert status["requests_per_minute"] == 2


class TestIntegration:
    """Test integration between failure handling components."""
    
    def test_global_resilience_manager(self):
        """Test global resilience manager instance."""
        # Test that global instance is available
        assert resilience_manager is not None
        
        # Test failure handling
        failure = create_failure_event(
            FailureType.NETWORK_ERROR,
            "integration_test",
            "Network connection failed"
        )
        
        recovery = resilience_manager.handle_failure(failure)
        assert recovery is not None
        assert hasattr(recovery, 'action_type')
        assert hasattr(recovery, 'should_retry')
    
    def test_global_timeout_components(self):
        """Test global timeout component instances."""
        # Test that global instances are available
        assert timeout_handler is not None
        assert adaptive_timeout_manager is not None
        assert rate_limit_manager is not None
        
        # Test basic functionality
        timeout = adaptive_timeout_manager.get_adaptive_timeout("test_operation")
        assert timeout > 0
        
        allowed, wait_time = rate_limit_manager.check_rate_limit("unknown_resource")
        assert allowed  # Should allow unknown resources
        assert wait_time == 0.0