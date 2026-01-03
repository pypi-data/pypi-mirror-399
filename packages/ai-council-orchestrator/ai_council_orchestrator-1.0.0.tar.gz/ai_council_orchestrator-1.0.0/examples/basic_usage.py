#!/usr/bin/env python3
"""
Basic usage example for AI Council.

This example demonstrates how to use the core data models and configuration
system. Note that this is just the infrastructure - the actual orchestration
components will be implemented in later tasks.
"""

from ai_council.core.models import (
    Task, Subtask, SelfAssessment, AgentResponse, FinalResponse,
    TaskType, ExecutionMode, RiskLevel, Priority
)
from ai_council.utils.config import create_default_config, load_config
from ai_council.utils.logging import configure_logging, get_logger


def main():
    """Demonstrate basic AI Council infrastructure usage."""
    # Configure logging
    configure_logging(level="INFO", format_json=False)
    logger = get_logger(__name__)
    
    logger.info("Starting AI Council infrastructure demo")
    
    # Load configuration
    config = create_default_config()
    logger.info(f"Loaded configuration with {len(config.models)} models")
    
    # Create a sample task
    task = Task(
        content="Analyze the benefits and drawbacks of renewable energy adoption",
        execution_mode=ExecutionMode.BALANCED
    )
    logger.info(f"Created task: {task.id}")
    
    # Create sample subtasks
    subtasks = [
        Subtask(
            parent_task_id=task.id,
            content="Research current renewable energy technologies",
            task_type=TaskType.RESEARCH,
            priority=Priority.HIGH,
            accuracy_requirement=0.9
        ),
        Subtask(
            parent_task_id=task.id,
            content="Analyze economic impact of renewable energy",
            task_type=TaskType.REASONING,
            priority=Priority.MEDIUM,
            accuracy_requirement=0.8
        ),
        Subtask(
            parent_task_id=task.id,
            content="Evaluate environmental benefits",
            task_type=TaskType.FACT_CHECKING,
            priority=Priority.HIGH,
            accuracy_requirement=0.95
        )
    ]
    
    logger.info(f"Created {len(subtasks)} subtasks")
    
    # Create sample self-assessments and responses
    responses = []
    for i, subtask in enumerate(subtasks):
        assessment = SelfAssessment(
            confidence_score=0.85 + (i * 0.05),
            assumptions=[f"Assumption {i+1} for subtask"],
            risk_level=RiskLevel.LOW,
            estimated_cost=0.05 + (i * 0.02),
            token_usage=150 + (i * 50),
            execution_time=2.0 + (i * 0.5),
            model_used=f"model-{i+1}"
        )
        
        response = AgentResponse(
            subtask_id=subtask.id,
            model_used=f"model-{i+1}",
            content=f"Sample response for subtask {i+1}: {subtask.content}",
            self_assessment=assessment,
            success=True
        )
        responses.append(response)
    
    logger.info(f"Created {len(responses)} agent responses")
    
    # Create final response
    final_response = FinalResponse(
        content="Renewable energy adoption offers significant environmental benefits "
                "and long-term economic advantages, though initial costs and "
                "infrastructure challenges must be considered.",
        overall_confidence=0.88,
        models_used=[f"model-{i+1}" for i in range(len(subtasks))],
        success=True
    )
    
    logger.info("Created final response")
    
    # Display results
    print("\n" + "="*60)
    print("AI COUNCIL INFRASTRUCTURE DEMO")
    print("="*60)
    
    print(f"\nOriginal Task: {task.content}")
    print(f"Execution Mode: {task.execution_mode.value}")
    print(f"Task ID: {task.id}")
    
    print(f"\nSubtasks ({len(subtasks)}):")
    for i, subtask in enumerate(subtasks, 1):
        print(f"  {i}. [{subtask.task_type.value}] {subtask.content}")
        print(f"     Priority: {subtask.priority.value}, "
              f"Accuracy: {subtask.accuracy_requirement}")
    
    print(f"\nAgent Responses ({len(responses)}):")
    for i, response in enumerate(responses, 1):
        print(f"  {i}. Model: {response.model_used}")
        print(f"     Confidence: {response.self_assessment.confidence_score}")
        print(f"     Cost: ${response.self_assessment.estimated_cost:.3f}")
        print(f"     Tokens: {response.self_assessment.token_usage}")
    
    print(f"\nFinal Response:")
    print(f"  Content: {final_response.content}")
    print(f"  Overall Confidence: {final_response.overall_confidence}")
    print(f"  Models Used: {', '.join(final_response.models_used)}")
    
    print(f"\nConfiguration Summary:")
    print(f"  Default Execution Mode: {config.execution.default_mode.value}")
    print(f"  Max Parallel Executions: {config.execution.max_parallel_executions}")
    print(f"  Max Cost Per Request: ${config.cost.max_cost_per_request}")
    print(f"  Available Models: {', '.join(config.models.keys())}")
    
    logger.info("Infrastructure demo completed successfully")
    print("\n" + "="*60)
    print("Infrastructure is ready for orchestration components!")
    print("="*60)


if __name__ == "__main__":
    main()