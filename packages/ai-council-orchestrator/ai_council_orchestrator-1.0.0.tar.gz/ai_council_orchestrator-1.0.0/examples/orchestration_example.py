#!/usr/bin/env python3
"""
Example demonstrating the AI Council Orchestration Layer with cost optimization.

This example shows how to:
1. Set up the complete AI Council pipeline
2. Process requests with different execution modes
3. Analyze cost vs quality trade-offs
4. Use cost optimization for model selection
"""

import logging
from ai_council.core.models import ExecutionMode, Task, TaskType, Priority, RiskLevel
from ai_council.orchestration import ConcreteOrchestrationLayer, CostOptimizer
from ai_council.analysis.engine import BasicAnalysisEngine
from ai_council.analysis.decomposer import BasicTaskDecomposer
from ai_council.routing.registry import ModelRegistryImpl
from ai_council.routing.context_protocol import ModelContextProtocolImpl
from ai_council.execution.agent import BaseExecutionAgent
from ai_council.execution.mock_models import MockModelFactory
from ai_council.arbitration.layer import ConcreteArbitrationLayer
from ai_council.synthesis.layer import SynthesisLayerImpl
from ai_council.core.models import ModelCapabilities, CostProfile, PerformanceMetrics


def setup_logging():
    """Set up logging for the example."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_orchestration_layer():
    """Create and configure the orchestration layer with all components."""
    
    # Initialize components
    analysis_engine = BasicAnalysisEngine()
    task_decomposer = BasicTaskDecomposer()
    model_registry = ModelRegistryImpl()
    
    # Create mock models with different characteristics
    models = [
        (MockModelFactory.create_specialized_model("mock-gpt", "reasoning", "high"), 
         ModelCapabilities(
            task_types=[TaskType.REASONING, TaskType.CODE_GENERATION, TaskType.CREATIVE_OUTPUT],
            cost_per_token=0.00002,
            average_latency=2.5,
            max_context_length=4000,
            reliability_score=0.95,
            strengths=["reasoning", "code generation"],
            weaknesses=["factual accuracy"]
        ), CostProfile(
            cost_per_input_token=0.00002,
            cost_per_output_token=0.00004,
            minimum_cost=0.001
        )),
        
        (MockModelFactory.create_specialized_model("mock-claude", "research", "high"), 
         ModelCapabilities(
            task_types=[TaskType.REASONING, TaskType.RESEARCH, TaskType.FACT_CHECKING],
            cost_per_token=0.00003,
            average_latency=3.0,
            max_context_length=8000,
            reliability_score=0.92,
            strengths=["research", "fact checking"],
            weaknesses=["creative tasks"]
        ), CostProfile(
            cost_per_input_token=0.00003,
            cost_per_output_token=0.00006,
            minimum_cost=0.002
        )),
        
        (MockModelFactory.create_fast_model("mock-llama"), 
         ModelCapabilities(
            task_types=[TaskType.REASONING, TaskType.CREATIVE_OUTPUT, TaskType.DEBUGGING],
            cost_per_token=0.00001,
            average_latency=4.0,
            max_context_length=2000,
            reliability_score=0.88,
            strengths=["cost efficiency", "creative output"],
            weaknesses=["complex reasoning"]
        ), CostProfile(
            cost_per_input_token=0.00001,
            cost_per_output_token=0.00002,
            minimum_cost=0.0005
        ))
    ]
    
    # Register models
    for model, capabilities, cost_profile in models:
        model_registry.register_model(model, capabilities)
        model_registry._cost_profiles[model.get_model_id()] = cost_profile
        model_registry._performance_metrics[model.get_model_id()] = PerformanceMetrics(
            average_response_time=capabilities.average_latency,
            success_rate=capabilities.reliability_score,
            average_quality_score=capabilities.reliability_score,
            total_requests=100,
            failed_requests=int(100 * (1 - capabilities.reliability_score))
        )
    
    # Create other components
    model_context_protocol = ModelContextProtocolImpl(model_registry)
    execution_agent = BaseExecutionAgent()
    arbitration_layer = ConcreteArbitrationLayer()
    synthesis_layer = SynthesisLayerImpl()
    
    # Create orchestration layer
    orchestration_layer = ConcreteOrchestrationLayer(
        analysis_engine=analysis_engine,
        task_decomposer=task_decomposer,
        model_context_protocol=model_context_protocol,
        execution_agent=execution_agent,
        arbitration_layer=arbitration_layer,
        synthesis_layer=synthesis_layer,
        model_registry=model_registry
    )
    
    return orchestration_layer


def demonstrate_cost_optimization():
    """Demonstrate cost optimization features."""
    print("\n" + "="*60)
    print("AI COUNCIL ORCHESTRATION LAYER DEMO")
    print("="*60)
    
    # Set up logging
    setup_logging()
    
    # Create orchestration layer
    orchestration_layer = create_orchestration_layer()
    
    # Example user request
    user_request = """
    I need help with a complex software architecture problem. Please analyze the trade-offs 
    between microservices and monolithic architectures for a medium-sized e-commerce platform. 
    Consider scalability, maintainability, development complexity, and operational overhead. 
    Then provide specific recommendations with code examples.
    """
    
    print(f"\nUser Request: {user_request[:100]}...")
    
    # Create task for analysis
    task = Task(
        content=user_request,
        execution_mode=ExecutionMode.BALANCED
    )
    
    # Demonstrate cost-quality analysis
    print("\n" + "-"*50)
    print("COST-QUALITY TRADE-OFF ANALYSIS")
    print("-"*50)
    
    analysis = orchestration_layer.analyze_cost_quality_tradeoffs(task)
    
    if 'error' not in analysis:
        for mode, data in analysis.items():
            if mode != 'recommendations':
                print(f"\n{mode.upper()} Mode:")
                print(f"  Total Cost: ${data['total_cost']:.4f}")
                print(f"  Total Time: {data['total_time']:.1f}s")
                print(f"  Avg Quality: {data['average_quality']:.2f}")
                print(f"  Value Score: {data['trade_off_score']:.2f}")
        
        print(f"\nRecommendations:")
        for criterion, recommendation in analysis['recommendations'].items():
            print(f"  {criterion.replace('_', ' ').title()}: {recommendation}")
    
    # Demonstrate execution with different modes
    print("\n" + "-"*50)
    print("EXECUTION MODE COMPARISON")
    print("-"*50)
    
    modes_to_test = [ExecutionMode.FAST, ExecutionMode.BALANCED, ExecutionMode.BEST_QUALITY]
    
    for mode in modes_to_test:
        print(f"\n--- {mode.value.upper()} MODE ---")
        
        # Estimate cost and time
        task.execution_mode = mode
        estimate = orchestration_layer.estimate_cost_and_time(task)
        
        print(f"Estimated Cost: ${estimate.estimated_cost:.4f}")
        print(f"Estimated Time: {estimate.estimated_time:.1f}s")
        print(f"Confidence: {estimate.confidence:.2f}")
        
        # Note: In a real implementation, you would call:
        # response = orchestration_layer.process_request(user_request, mode)
        # But for this demo, we'll just show the estimates
    
    # Demonstrate cost optimizer directly
    print("\n" + "-"*50)
    print("DIRECT COST OPTIMIZER DEMO")
    print("-"*50)
    
    cost_optimizer = orchestration_layer.cost_optimizer
    
    # Create a sample subtask
    from ai_council.core.models import Subtask
    subtask = Subtask(
        content="Analyze microservices vs monolithic architecture trade-offs",
        task_type=TaskType.REASONING,
        priority=Priority.MEDIUM,
        risk_level=RiskLevel.MEDIUM,
        accuracy_requirement=0.85
    )
    
    # Get available models
    available_models = ["mock-gpt", "mock-claude", "mock-llama"]
    
    # Test optimization for different modes
    for mode in modes_to_test:
        optimization = cost_optimizer.optimize_model_selection(
            subtask, mode, available_models
        )
        
        print(f"\n{mode.value.upper()} Mode Optimization:")
        print(f"  Selected Model: {optimization.recommended_model}")
        print(f"  Estimated Cost: ${optimization.estimated_cost:.4f}")
        print(f"  Estimated Time: {optimization.estimated_time:.1f}s")
        print(f"  Quality Score: {optimization.quality_score:.2f}")
        print(f"  Reasoning: {optimization.reasoning}")
    
    print("\n" + "="*60)
    print("DEMO COMPLETED")
    print("="*60)


if __name__ == "__main__":
    demonstrate_cost_optimization()