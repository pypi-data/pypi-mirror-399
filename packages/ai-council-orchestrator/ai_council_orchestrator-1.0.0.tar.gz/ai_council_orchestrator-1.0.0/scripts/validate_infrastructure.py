#!/usr/bin/env python3
"""
Infrastructure validation script for AI Council.

This script validates that all core infrastructure components are properly
set up and working correctly.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_council.core.models import (
    Task, Subtask, SelfAssessment, AgentResponse, FinalResponse,
    TaskType, ExecutionMode, RiskLevel, Priority, ComplexityLevel,
    TaskIntent, ModelCapabilities, CostProfile, PerformanceMetrics,
    CostBreakdown, ExecutionMetadata
)
from ai_council.utils.config import (
    AICouncilConfig, ModelConfig, LoggingConfig, ExecutionConfig, CostConfig,
    load_config, create_default_config
)
from ai_council.utils.logging import configure_logging, get_logger, LoggerMixin


def validate_enumerations():
    """Validate all enumeration classes."""
    print("✓ Validating enumerations...")
    
    # Test TaskType
    assert TaskType.REASONING.value == "reasoning"
    assert TaskType.CODE_GENERATION.value == "code_generation"
    assert len(list(TaskType)) == 8
    
    # Test ExecutionMode
    assert ExecutionMode.FAST.value == "fast"
    assert ExecutionMode.BALANCED.value == "balanced"
    assert ExecutionMode.BEST_QUALITY.value == "best_quality"
    
    # Test RiskLevel
    assert RiskLevel.LOW.value == "low"
    assert RiskLevel.CRITICAL.value == "critical"
    
    print("  ✓ All enumerations working correctly")


def validate_data_models():
    """Validate all data model classes."""
    print("✓ Validating data models...")
    
    # Test Task
    task = Task(content="Test task", execution_mode=ExecutionMode.BALANCED)
    assert task.content == "Test task"
    assert task.id  # Should have UUID
    
    # Test Subtask
    subtask = Subtask(
        parent_task_id=task.id,
        content="Test subtask",
        task_type=TaskType.REASONING,
        accuracy_requirement=0.9
    )
    assert subtask.parent_task_id == task.id
    assert subtask.accuracy_requirement == 0.9
    
    # Test SelfAssessment
    assessment = SelfAssessment(
        confidence_score=0.85,
        assumptions=["Test assumption"],
        risk_level=RiskLevel.LOW,
        model_used="test-model"
    )
    assert assessment.confidence_score == 0.85
    
    # Test AgentResponse
    response = AgentResponse(
        subtask_id=subtask.id,
        model_used="test-model",
        content="Test response",
        self_assessment=assessment
    )
    assert response.success is True
    
    # Test FinalResponse
    final = FinalResponse(
        content="Final test response",
        overall_confidence=0.9,
        models_used=["test-model"]
    )
    assert final.overall_confidence == 0.9
    
    print("  ✓ All data models working correctly")


def validate_configuration():
    """Validate configuration system."""
    print("✓ Validating configuration system...")
    
    # Test default config creation
    config = create_default_config()
    assert isinstance(config, AICouncilConfig)
    assert len(config.models) >= 2
    
    # Test config validation
    config.validate()  # Should not raise
    
    # Test model config access
    gpt4_config = config.get_model_config("gpt-4")
    assert gpt4_config is not None
    assert gpt4_config.provider == "openai"
    
    # Test config serialization
    config_dict = config.to_dict()
    assert "logging" in config_dict
    assert "execution" in config_dict
    assert "models" in config_dict
    
    # Test config from dict
    new_config = AICouncilConfig.from_dict(config_dict)
    assert new_config.execution.default_mode == config.execution.default_mode
    
    print("  ✓ Configuration system working correctly")


def validate_logging():
    """Validate logging system."""
    print("✓ Validating logging system...")
    
    # Test basic configuration
    configure_logging(level="INFO")
    logger = get_logger("test_module")
    assert logger is not None
    
    # Test LoggerMixin
    class TestClass(LoggerMixin):
        def test_method(self):
            self.log_operation("test_operation")
            self.log_performance("test_perf", 1.5)
    
    test_instance = TestClass()
    test_instance.test_method()  # Should not raise
    
    print("  ✓ Logging system working correctly")


def validate_package_structure():
    """Validate package structure and imports."""
    print("✓ Validating package structure...")
    
    # Test main package import
    import ai_council
    assert ai_council.__version__ == "0.1.0"
    
    # Test module imports
    from ai_council import analysis
    from ai_council import arbitration
    from ai_council import core
    from ai_council import execution
    from ai_council import orchestration
    from ai_council import routing
    from ai_council import synthesis
    from ai_council import utils
    
    # Test core exports
    from ai_council import (
        Task, Subtask, SelfAssessment, AgentResponse, FinalResponse,
        TaskType, ExecutionMode, RiskLevel
    )
    
    print("  ✓ Package structure and imports working correctly")


def validate_data_integrity():
    """Validate data model validation and integrity checks."""
    print("✓ Validating data integrity checks...")
    
    # Test Task validation
    try:
        Task(content="")  # Should raise
        assert False, "Empty task content should raise ValueError"
    except ValueError:
        pass
    
    # Test Subtask validation
    try:
        Subtask(content="test", accuracy_requirement=1.5)  # Should raise
        assert False, "Invalid accuracy requirement should raise ValueError"
    except ValueError:
        pass
    
    # Test SelfAssessment validation
    try:
        SelfAssessment(confidence_score=1.5)  # Should raise
        assert False, "Invalid confidence score should raise ValueError"
    except ValueError:
        pass
    
    # Test AgentResponse validation
    try:
        AgentResponse(subtask_id="", model_used="test", content="test")  # Should raise
        assert False, "Empty subtask ID should raise ValueError"
    except ValueError:
        pass
    
    print("  ✓ Data integrity checks working correctly")


def main():
    """Run all validation checks."""
    print("AI Council Infrastructure Validation")
    print("=" * 50)
    
    try:
        validate_enumerations()
        validate_data_models()
        validate_configuration()
        validate_logging()
        validate_package_structure()
        validate_data_integrity()
        
        print("\n" + "=" * 50)
        print("✅ ALL INFRASTRUCTURE COMPONENTS VALIDATED SUCCESSFULLY!")
        print("✅ Ready for orchestration component implementation")
        print("=" * 50)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())