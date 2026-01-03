"""Tests for routing components."""

import pytest
from unittest.mock import Mock

from ai_council.core.models import (
    TaskType, ExecutionMode, RiskLevel, Priority, ComplexityLevel,
    ModelCapabilities, CostProfile, PerformanceMetrics, Subtask
)
from ai_council.core.interfaces import AIModel
from ai_council.routing.registry import ModelRegistryImpl
from ai_council.routing.context_protocol import ModelContextProtocolImpl


class MockAIModel(AIModel):
    """Mock AI model for testing."""
    
    def __init__(self, model_id: str):
        self.model_id = model_id
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        return f"Response from {self.model_id}"
    
    def get_model_id(self) -> str:
        return self.model_id


class TestModelRegistryImpl:
    """Test cases for ModelRegistryImpl."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = ModelRegistryImpl()
        self.mock_model = MockAIModel("test-model-1")
        self.capabilities = ModelCapabilities(
            task_types=[TaskType.REASONING, TaskType.CODE_GENERATION],
            cost_per_token=0.001,
            average_latency=2.0,
            max_context_length=4096,
            reliability_score=0.9,
            strengths=["logical reasoning", "code generation"],
            weaknesses=["creative writing"]
        )
    
    def test_register_model_success(self):
        """Test successful model registration."""
        self.registry.register_model(self.mock_model, self.capabilities)
        
        assert self.registry.is_model_registered("test-model-1")
        assert len(self.registry.get_all_models()) == 1
        
        # Check that model is indexed by task types
        reasoning_models = self.registry.get_models_for_task_type(TaskType.REASONING)
        assert len(reasoning_models) == 1
        assert reasoning_models[0].get_model_id() == "test-model-1"
    
    def test_register_duplicate_model_fails(self):
        """Test that registering duplicate model fails."""
        self.registry.register_model(self.mock_model, self.capabilities)
        
        with pytest.raises(ValueError, match="already registered"):
            self.registry.register_model(self.mock_model, self.capabilities)
    
    def test_register_model_without_task_types_fails(self):
        """Test that registering model without task types fails."""
        invalid_capabilities = ModelCapabilities(
            task_types=[],  # Empty task types
            cost_per_token=0.001,
            average_latency=2.0,
            max_context_length=4096,
            reliability_score=0.9
        )
        
        with pytest.raises(ValueError, match="must support at least one task type"):
            self.registry.register_model(self.mock_model, invalid_capabilities)
    
    def test_get_models_for_task_type(self):
        """Test getting models for specific task type."""
        # Register multiple models
        model1 = MockAIModel("model-1")
        model2 = MockAIModel("model-2")
        
        caps1 = ModelCapabilities(
            task_types=[TaskType.REASONING],
            cost_per_token=0.001,
            reliability_score=0.9
        )
        caps2 = ModelCapabilities(
            task_types=[TaskType.REASONING, TaskType.RESEARCH],
            cost_per_token=0.002,
            reliability_score=0.8
        )
        
        self.registry.register_model(model1, caps1)
        self.registry.register_model(model2, caps2)
        
        # Test getting models for reasoning
        reasoning_models = self.registry.get_models_for_task_type(TaskType.REASONING)
        assert len(reasoning_models) == 2
        
        # Should be sorted by reliability (descending) then cost (ascending)
        assert reasoning_models[0].get_model_id() == "model-1"  # Higher reliability
        
        # Test getting models for research
        research_models = self.registry.get_models_for_task_type(TaskType.RESEARCH)
        assert len(research_models) == 1
        assert research_models[0].get_model_id() == "model-2"
    
    def test_get_model_cost_profile(self):
        """Test getting model cost profile."""
        self.registry.register_model(self.mock_model, self.capabilities)
        
        cost_profile = self.registry.get_model_cost_profile("test-model-1")
        assert cost_profile.cost_per_input_token == 0.001
        assert cost_profile.cost_per_output_token == 0.001
    
    def test_get_model_cost_profile_not_registered(self):
        """Test getting cost profile for unregistered model fails."""
        with pytest.raises(KeyError, match="not registered"):
            self.registry.get_model_cost_profile("nonexistent-model")
    
    def test_update_model_performance(self):
        """Test updating model performance metrics."""
        self.registry.register_model(self.mock_model, self.capabilities)
        
        new_performance = PerformanceMetrics(
            average_response_time=1.5,
            success_rate=0.95,
            average_quality_score=0.85,
            total_requests=100,
            failed_requests=5
        )
        
        self.registry.update_model_performance("test-model-1", new_performance)
        
        updated_performance = self.registry.get_model_performance("test-model-1")
        assert updated_performance.success_rate == 0.95
        
        # Check that capabilities reliability score is updated
        updated_capabilities = self.registry.get_model_capabilities("test-model-1")
        assert updated_capabilities.reliability_score == 0.95
    
    def test_unregister_model(self):
        """Test unregistering a model."""
        self.registry.register_model(self.mock_model, self.capabilities)
        assert self.registry.is_model_registered("test-model-1")
        
        self.registry.unregister_model("test-model-1")
        assert not self.registry.is_model_registered("test-model-1")
        
        # Check that model is removed from task type index
        reasoning_models = self.registry.get_models_for_task_type(TaskType.REASONING)
        assert len(reasoning_models) == 0


class TestModelContextProtocolImpl:
    """Test cases for ModelContextProtocolImpl."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = ModelRegistryImpl()
        self.protocol = ModelContextProtocolImpl(self.registry)
        
        # Register test models
        self.model1 = MockAIModel("fast-model")
        self.model2 = MockAIModel("accurate-model")
        
        self.caps1 = ModelCapabilities(
            task_types=[TaskType.REASONING],
            cost_per_token=0.001,
            average_latency=1.0,
            reliability_score=0.8
        )
        self.caps2 = ModelCapabilities(
            task_types=[TaskType.REASONING],
            cost_per_token=0.005,
            average_latency=3.0,
            reliability_score=0.95
        )
        
        self.registry.register_model(self.model1, self.caps1)
        self.registry.register_model(self.model2, self.caps2)
        
        self.test_subtask = Subtask(
            content="Solve this reasoning problem",
            task_type=TaskType.REASONING,
            priority=Priority.MEDIUM,
            risk_level=RiskLevel.LOW,
            accuracy_requirement=0.8
        )
    
    def test_route_task_success(self):
        """Test successful task routing."""
        selection = self.protocol.route_task(self.test_subtask)
        
        assert selection.model_id in ["fast-model", "accurate-model"]
        assert 0.0 <= selection.confidence <= 1.0
        assert selection.reasoning is not None
    
    def test_route_task_without_task_type_fails(self):
        """Test that routing without task type fails."""
        invalid_subtask = Subtask(
            content="Test content",
            task_type=None  # No task type
        )
        
        with pytest.raises(ValueError, match="must have a task type"):
            self.protocol.route_task(invalid_subtask)
    
    def test_route_task_no_available_models_fails(self):
        """Test routing when no models available for task type."""
        subtask = Subtask(
            content="Generate an image",
            task_type=TaskType.IMAGE_GENERATION  # No models registered for this
        )
        
        with pytest.raises(ValueError, match="No models available"):
            self.protocol.route_task(subtask)
    
    def test_select_fallback_success(self):
        """Test successful fallback selection."""
        # First route to get primary model
        primary_selection = self.protocol.route_task(self.test_subtask)
        
        # Then select fallback
        fallback_selection = self.protocol.select_fallback(
            primary_selection.model_id, 
            self.test_subtask
        )
        
        assert fallback_selection.model_id != primary_selection.model_id
        assert fallback_selection.confidence <= 1.0
        assert "fallback" in fallback_selection.reasoning.lower()
    
    def test_select_fallback_no_alternatives_fails(self):
        """Test fallback selection when no alternatives available."""
        # Create a subtask for task type with only one model
        single_model = MockAIModel("only-model")
        single_caps = ModelCapabilities(
            task_types=[TaskType.CREATIVE_OUTPUT],
            cost_per_token=0.001,
            reliability_score=0.8
        )
        self.registry.register_model(single_model, single_caps)
        
        creative_subtask = Subtask(
            content="Write a poem",
            task_type=TaskType.CREATIVE_OUTPUT
        )
        
        with pytest.raises(ValueError, match="No fallback models available"):
            self.protocol.select_fallback("only-model", creative_subtask)
    
    def test_determine_parallelism(self):
        """Test parallelism determination."""
        subtasks = [
            Subtask(content="Task 1", task_type=TaskType.REASONING, priority=Priority.CRITICAL),
            Subtask(content="Task 2", task_type=TaskType.REASONING, priority=Priority.MEDIUM),
            Subtask(content="Task 3", task_type=TaskType.CODE_GENERATION, priority=Priority.LOW)
        ]
        
        plan = self.protocol.determine_parallelism(subtasks)
        
        assert len(plan.parallel_groups) > 0
        assert len(plan.sequential_order) == 3
        
        # Critical tasks should be first
        first_group = plan.parallel_groups[0]
        assert first_group[0].priority == Priority.CRITICAL
    
    def test_determine_parallelism_empty_list(self):
        """Test parallelism determination with empty list."""
        plan = self.protocol.determine_parallelism([])
        
        assert len(plan.parallel_groups) == 0
        assert len(plan.sequential_order) == 0
    
    def test_routing_cache(self):
        """Test that routing decisions are cached."""
        # First routing call
        selection1 = self.protocol.route_task(self.test_subtask)
        
        # Second routing call with same subtask characteristics
        selection2 = self.protocol.route_task(self.test_subtask)
        
        # Should return same result (cached)
        assert selection1.model_id == selection2.model_id
        assert selection1.confidence == selection2.confidence
    
    def test_clear_cache(self):
        """Test clearing the routing cache."""
        # Route a task to populate cache
        self.protocol.route_task(self.test_subtask)
        
        # Clear cache
        self.protocol.clear_cache()
        
        # Check stats
        stats = self.protocol.get_routing_stats()
        assert stats["cached_decisions"] == 0
    
    def test_get_routing_stats(self):
        """Test getting routing statistics."""
        # Route a task
        self.protocol.route_task(self.test_subtask)
        
        stats = self.protocol.get_routing_stats()
        assert "cached_decisions" in stats
        assert "fallback_chains" in stats
        assert stats["cached_decisions"] >= 1