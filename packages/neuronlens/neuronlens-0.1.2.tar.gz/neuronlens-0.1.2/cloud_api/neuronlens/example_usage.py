"""
Example usage of neuronlens package.

This file demonstrates how to use the neuronlens package.
Run this after installing: pip install -e .
"""

import neuronlens

def example_local_mode():
    """Example using local server (no API key)"""
    print("=" * 60)
    print("Example: Local Mode (no API key)")
    print("=" * 60)
    
    # Initialize without API key - uses localhost:8000
    engine = neuronlens.Engine()
    
    # Example: Agent Lens
    try:
        result = engine.analyze_agent_query("Get Tesla stock price")
        print(f"Alignment Status: {result.get('alignment_status', 'N/A')}")
        print(f"Tool Called: {result.get('tool_called', 'N/A')}")
    except Exception as e:
        print(f"Error (expected if local server not running): {e}")


def example_cloud_mode():
    """Example using cloud API (with API key)"""
    print("\n" + "=" * 60)
    print("Example: Cloud Mode (with API key)")
    print("=" * 60)
    
    # Initialize with API key
    # In real usage, get this from environment or user input
    api_key = "nlive_your_api_key_here"  # Replace with actual key
    api_url = "https://your-runpod.net"  # Replace with actual URL
    
    try:
        engine = neuronlens.Engine(api_key=api_key, api_url=api_url)
        
        # Example: SLM Lens
        result = engine.analyze_slm_sentiment(
            text="Strong quarterly earnings exceeded expectations",
            top_n=5
        )
        print(f"Sentiment: {result.get('sentiment', {}).get('predicted_label', 'N/A')}")
        print(f"Top Features: {len(result.get('top_features', []))}")
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def example_environment_variables():
    """Example using environment variables"""
    print("\n" + "=" * 60)
    print("Example: Using Environment Variables")
    print("=" * 60)
    
    import os
    
    # Set environment variables (in real usage, set these in your shell)
    # os.environ['NEURONLENS_API_KEY'] = "nlive_your_key"
    # os.environ['NEURONLENS_API_URL'] = "https://your-runpod.net"
    
    # Initialize - automatically picks up from environment
    try:
        engine = neuronlens.Engine()
        print(f"API URL: {engine.api_url}")
        print(f"Has API Key: {engine.api_key is not None}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("NeuronLens Package - Usage Examples\n")
    
    # Run examples
    example_local_mode()
    example_cloud_mode()
    example_environment_variables()
    
    print("\n" + "=" * 60)
    print("For more examples, see neuronlens/README.md")
    print("=" * 60)

