"""Model registry implementation for managing AI models and their capabilities."""

from typing import Dict, List, Optional
from datetime import datetime

from ..core.interfaces import ModelRegistry, AIModel
from ..core.models import (
    TaskType, ModelCapabilities, CostProfile, PerformanceMetrics
)


class ModelRegistryImpl(ModelRegistry):
    """Implementation of ModelRegistry for managing AI models and their capabilities."""
    
    def __init__(self):
        """Initialize the model registry."""
        self._models: Dict[str, AIModel] = {}
        self._capabilities: Dict[str, ModelCapabilities] = {}
        self._cost_profiles: Dict[str, CostProfile] = {}
        self._performance_metrics: Dict[str, PerformanceMetrics] = {}
        self._task_type_index: Dict[TaskType, List[str]] = {
            task_type: [] for task_type in TaskType
        }
    
    def register_model(self, model: AIModel, capabilities: ModelCapabilities) -> None:
        """Register a new AI model with its capabilities.
        
        Args:
            model: The AI model to register
            capabilities: The model's capabilities and characteristics
            
        Raises:
            ValueError: If model is already registered or capabilities are invalid
        """
        model_id = model.get_model_id()
        
        if model_id in self._models:
            raise ValueError(f"Model {model_id} is already registered")
        
        # Validate capabilities
        if not capabilities.task_types:
            raise ValueError("Model must support at least one task type")
        
        # Register the model
        self._models[model_id] = model
        self._capabilities[model_id] = capabilities
        
        # Create default cost profile from capabilities
        self._cost_profiles[model_id] = CostProfile(
            cost_per_input_token=capabilities.cost_per_token,
            cost_per_output_token=capabilities.cost_per_token,
            minimum_cost=0.0
        )
        
        # Create default performance metrics
        self._performance_metrics[model_id] = PerformanceMetrics(
            average_response_time=capabilities.average_latency,
            success_rate=capabilities.reliability_score,
            average_quality_score=capabilities.reliability_score,
            total_requests=0,
            failed_requests=0
        )
        
        # Update task type index
        for task_type in capabilities.task_types:
            if model_id not in self._task_type_index[task_type]:
                self._task_type_index[task_type].append(model_id)
    
    def get_models_for_task_type(self, task_type: TaskType) -> List[AIModel]:
        """Get all models capable of handling a specific task type.
        
        Args:
            task_type: The type of task
            
        Returns:
            List[AIModel]: List of capable models, sorted by reliability score
        """
        model_ids = self._task_type_index.get(task_type, [])
        
        # Sort by reliability score (descending) and then by cost (ascending)
        sorted_model_ids = sorted(
            model_ids,
            key=lambda mid: (
                -self._capabilities[mid].reliability_score,  # Higher reliability first
                self._capabilities[mid].cost_per_token       # Lower cost second
            )
        )
        
        return [self._models[model_id] for model_id in sorted_model_ids]
    
    def get_model_cost_profile(self, model_id: str) -> CostProfile:
        """Get the cost profile for a specific model.
        
        Args:
            model_id: The model identifier
            
        Returns:
            CostProfile: The model's cost profile
            
        Raises:
            KeyError: If model is not registered
        """
        if model_id not in self._cost_profiles:
            raise KeyError(f"Model {model_id} is not registered")
        
        return self._cost_profiles[model_id]
    
    def update_model_performance(self, model_id: str, performance: PerformanceMetrics) -> None:
        """Update performance metrics for a model.
        
        Args:
            model_id: The model identifier
            performance: Updated performance metrics
            
        Raises:
            KeyError: If model is not registered
        """
        if model_id not in self._performance_metrics:
            raise KeyError(f"Model {model_id} is not registered")
        
        self._performance_metrics[model_id] = performance
        
        # Update capabilities reliability score based on performance
        if model_id in self._capabilities:
            self._capabilities[model_id].reliability_score = performance.success_rate
    
    def get_model_capabilities(self, model_id: str) -> ModelCapabilities:
        """Get the capabilities for a specific model.
        
        Args:
            model_id: The model identifier
            
        Returns:
            ModelCapabilities: The model's capabilities
            
        Raises:
            KeyError: If model is not registered
        """
        if model_id not in self._capabilities:
            raise KeyError(f"Model {model_id} is not registered")
        
        return self._capabilities[model_id]
    
    def get_model_performance(self, model_id: str) -> PerformanceMetrics:
        """Get the performance metrics for a specific model.
        
        Args:
            model_id: The model identifier
            
        Returns:
            PerformanceMetrics: The model's performance metrics
            
        Raises:
            KeyError: If model is not registered
        """
        if model_id not in self._performance_metrics:
            raise KeyError(f"Model {model_id} is not registered")
        
        return self._performance_metrics[model_id]
    
    def get_all_models(self) -> List[AIModel]:
        """Get all registered models.
        
        Returns:
            List[AIModel]: List of all registered models
        """
        return list(self._models.values())
    
    def get_model_by_id(self, model_id: str) -> Optional[AIModel]:
        """Get a model by its ID.
        
        Args:
            model_id: The model identifier
            
        Returns:
            Optional[AIModel]: The model if found, None otherwise
        """
        return self._models.get(model_id)
    
    def unregister_model(self, model_id: str) -> None:
        """Unregister a model from the registry.
        
        Args:
            model_id: The model identifier to unregister
            
        Raises:
            KeyError: If model is not registered
        """
        if model_id not in self._models:
            raise KeyError(f"Model {model_id} is not registered")
        
        # Remove from all data structures
        del self._models[model_id]
        capabilities = self._capabilities.pop(model_id)
        del self._cost_profiles[model_id]
        del self._performance_metrics[model_id]
        
        # Remove from task type index
        for task_type in capabilities.task_types:
            if model_id in self._task_type_index[task_type]:
                self._task_type_index[task_type].remove(model_id)
    
    def is_model_registered(self, model_id: str) -> bool:
        """Check if a model is registered.
        
        Args:
            model_id: The model identifier
            
        Returns:
            bool: True if model is registered, False otherwise
        """
        return model_id in self._models
    
    def get_models_by_cost_range(self, min_cost: float, max_cost: float) -> List[AIModel]:
        """Get models within a specific cost range.
        
        Args:
            min_cost: Minimum cost per token
            max_cost: Maximum cost per token
            
        Returns:
            List[AIModel]: List of models within the cost range
        """
        matching_models = []
        
        for model_id, capabilities in self._capabilities.items():
            if min_cost <= capabilities.cost_per_token <= max_cost:
                matching_models.append(self._models[model_id])
        
        return matching_models
    
    def get_fastest_models(self, task_type: TaskType, limit: int = 5) -> List[AIModel]:
        """Get the fastest models for a specific task type.
        
        Args:
            task_type: The type of task
            limit: Maximum number of models to return
            
        Returns:
            List[AIModel]: List of fastest models for the task type
        """
        model_ids = self._task_type_index.get(task_type, [])
        
        # Sort by average latency (ascending)
        sorted_model_ids = sorted(
            model_ids,
            key=lambda mid: self._capabilities[mid].average_latency
        )
        
        return [self._models[model_id] for model_id in sorted_model_ids[:limit]]
    
    def get_most_reliable_models(self, task_type: TaskType, limit: int = 5) -> List[AIModel]:
        """Get the most reliable models for a specific task type.
        
        Args:
            task_type: The type of task
            limit: Maximum number of models to return
            
        Returns:
            List[AIModel]: List of most reliable models for the task type
        """
        model_ids = self._task_type_index.get(task_type, [])
        
        # Sort by reliability score (descending)
        sorted_model_ids = sorted(
            model_ids,
            key=lambda mid: -self._capabilities[mid].reliability_score
        )
        
        return [self._models[model_id] for model_id in sorted_model_ids[:limit]]