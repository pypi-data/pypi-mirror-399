#!/usr/bin/env python3
"""
Complete integration example for AI Council.

This example demonstrates the fully wired AI Council system with all components
integrated through the main application interface.
"""

import sys
import logging
from pathlib import Path

# Add the parent directory to the path so we can import ai_council
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_council import AICouncil, ExecutionMode, create_default_config


def setup_logging():
    """Set up logging for the example."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def demonstrate_complete_system():
    """Demonstrate the complete AI Council system integration."""
    print("\n" + "="*70)
    print("AI COUNCIL COMPLETE INTEGRATION DEMO")
    print("="*70)
    
    # Set up logging
    setup_logging()
    
    try:
        # Initialize AI Council with default configuration
        print("\n1. Initializing AI Council...")
        ai_council = AICouncil()
        
        # Check system status
        print("\n2. Checking system status...")
        status = ai_council.get_system_status()
        print(f"   System Status: {status.get('status', 'unknown')}")
        print(f"   Available Models: {len(status.get('available_models', []))}")
        print(f"   Health: {status.get('health', {}).get('overall_health', 'unknown')}")
        
        # Example requests to demonstrate different capabilities
        test_requests = [
            {
                "request": "Explain the benefits and drawbacks of microservices architecture",
                "mode": ExecutionMode.FAST,
                "description": "Simple reasoning task"
            },
            {
                "request": "Write a Python function to calculate the Fibonacci sequence and explain its time complexity",
                "mode": ExecutionMode.BALANCED,
                "description": "Code generation with analysis"
            },
            {
                "request": "Research the latest developments in quantum computing and their potential impact on cryptography. Provide specific examples and timeline predictions.",
                "mode": ExecutionMode.BEST_QUALITY,
                "description": "Complex research task"
            }
        ]
        
        # Process each request
        for i, test_case in enumerate(test_requests, 1):
            print(f"\n{'-'*50}")
            print(f"TEST CASE {i}: {test_case['description']}")
            print(f"Mode: {test_case['mode'].value}")
            print(f"Request: {test_case['request'][:80]}...")
            print(f"{'-'*50}")
            
            # Get cost estimate first
            print(f"\n   Estimating cost...")
            estimate = ai_council.estimate_cost(test_case['request'], test_case['mode'])
            print(f"   Estimated Cost: ${estimate.get('estimated_cost', 0):.4f}")
            print(f"   Estimated Time: {estimate.get('estimated_time', 0):.1f}s")
            print(f"   Confidence: {estimate.get('confidence', 0):.2f}")
            
            # Process the request
            print(f"\n   Processing request...")
            response = ai_council.process_request(test_case['request'], test_case['mode'])
            
            # Display results
            if response.success:
                print(f"\n   ✓ SUCCESS")
                print(f"   Response Length: {len(response.content)} characters")
                print(f"   Overall Confidence: {response.overall_confidence:.2f}")
                print(f"   Models Used: {', '.join(response.models_used)}")
                
                if response.execution_metadata:
                    print(f"   Execution Time: {response.execution_metadata.total_execution_time:.2f}s")
                    print(f"   Execution Path: {' → '.join(response.execution_metadata.execution_path)}")
                
                if response.cost_breakdown:
                    print(f"   Actual Cost: ${response.cost_breakdown.total_cost:.4f}")
                
                # Show first 200 characters of response
                content_preview = response.content[:200]
                if len(response.content) > 200:
                    content_preview += "..."
                print(f"\n   Response Preview:")
                print(f"   {content_preview}")
                
            else:
                print(f"\n   ✗ FAILED")
                print(f"   Error: {response.error_message}")
        
        # Demonstrate trade-off analysis
        print(f"\n{'-'*50}")
        print("TRADE-OFF ANALYSIS DEMO")
        print(f"{'-'*50}")
        
        analysis_request = "Design a scalable web application architecture for an e-commerce platform"
        print(f"\nAnalyzing trade-offs for: {analysis_request}")
        
        analysis = ai_council.analyze_tradeoffs(analysis_request)
        
        if 'error' not in analysis:
            print(f"\nTrade-off Analysis Results:")
            for mode, data in analysis.items():
                if mode != 'recommendations':
                    print(f"\n{mode.upper()} Mode:")
                    print(f"  Cost: ${data.get('total_cost', 0):.4f}")
                    print(f"  Time: {data.get('total_time', 0):.1f}s")
                    print(f"  Quality: {data.get('average_quality', 0):.2f}")
                    print(f"  Value Score: {data.get('trade_off_score', 0):.2f}")
            
            if 'recommendations' in analysis:
                print(f"\nRecommendations:")
                for criterion, recommendation in analysis['recommendations'].items():
                    print(f"  {criterion.replace('_', ' ').title()}: {recommendation}")
        else:
            print(f"Analysis failed: {analysis['error']}")
        
        # Final system status check
        print(f"\n{'-'*50}")
        print("FINAL SYSTEM STATUS")
        print(f"{'-'*50}")
        
        final_status = ai_council.get_system_status()
        health = final_status.get('health', {})
        
        print(f"System Status: {final_status.get('status', 'unknown')}")
        print(f"Overall Health: {health.get('overall_health', 'unknown')}")
        
        if 'circuit_breakers' in health:
            cb_status = health['circuit_breakers']
            print(f"Circuit Breakers: {len(cb_status)} active")
            for cb_name, cb_state in cb_status.items():
                print(f"  {cb_name}: {cb_state}")
        
        print(f"\n" + "="*70)
        print("INTEGRATION DEMO COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\nThe AI Council system is fully operational with all components")
        print("properly wired and integrated. The system demonstrates:")
        print("• Request processing through the complete pipeline")
        print("• Cost estimation and optimization")
        print("• Multiple execution modes (fast, balanced, best_quality)")
        print("• Trade-off analysis for informed decision making")
        print("• Comprehensive error handling and resilience")
        print("• System health monitoring and status reporting")
        
    except Exception as e:
        print(f"\n✗ Integration demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        try:
            ai_council.shutdown()
            print("\nSystem shutdown completed.")
        except:
            pass


def demonstrate_configuration_loading():
    """Demonstrate loading configuration from file."""
    print("\n" + "="*70)
    print("CONFIGURATION LOADING DEMO")
    print("="*70)
    
    # Create a sample configuration
    config = create_default_config()
    
    # Save to file
    config_path = Path("demo_config.yaml")
    config.save_to_file(config_path)
    print(f"Created sample configuration: {config_path}")
    
    # Load from file
    ai_council = AICouncil(config_path)
    print("Successfully loaded AI Council with custom configuration")
    
    # Show configuration details
    status = ai_council.get_system_status()
    if 'configuration' in status:
        config_info = status['configuration']
        print(f"\nConfiguration Details:")
        print(f"  Default Mode: {config_info.get('default_execution_mode')}")
        print(f"  Max Parallel: {config_info.get('max_parallel_executions')}")
        print(f"  Max Cost: ${config_info.get('max_cost_per_request')}")
        print(f"  Arbitration: {config_info.get('arbitration_enabled')}")
        print(f"  Synthesis: {config_info.get('synthesis_enabled')}")
    
    # Cleanup
    ai_council.shutdown()
    config_path.unlink()  # Remove demo config file
    print(f"Cleaned up demo configuration file")


if __name__ == "__main__":
    try:
        demonstrate_complete_system()
        demonstrate_configuration_loading()
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()