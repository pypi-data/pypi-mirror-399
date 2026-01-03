"""
AI Council - A production-grade multi-agent orchestration system.

This package provides intelligent coordination of multiple AI models
to solve complex problems through structured decomposition, routing,
execution, arbitration, and synthesis.
"""

__version__ = "0.1.0"
__author__ = "AI Council Team"

from .core.models import (
    Task,
    Subtask,
    SelfAssessment,
    AgentResponse,
    FinalResponse,
    TaskType,
    ExecutionMode,
    RiskLevel,
)

from .main import AICouncil
from .factory import AICouncilFactory
from .utils.config import AICouncilConfig, load_config, create_default_config

__all__ = [
    "Task",
    "Subtask", 
    "SelfAssessment",
    "AgentResponse",
    "FinalResponse",
    "TaskType",
    "ExecutionMode",
    "RiskLevel",
    "AICouncil",
    "AICouncilFactory",
    "AICouncilConfig",
    "load_config",
    "create_default_config",
]