"""
Example usage of the GPT-4 agent and fusion layer.

This demonstrates how to:
1. Initialize the GPT-4 agent
2. Send requests
3. Handle responses
4. Use the fusion layer with multiple agents
"""

import asyncio
import logging
from agents.gpt4 import GPT4Agent
from agents.base import AgentRequest
from agents.fusion import ResponseFusionLayer
from config import Config


async def simple_gpt4_example():
    """
    Simple example of using the GPT-4 agent.
    """
    print("\n=== Simple GPT-4 Agent Example ===\n")
    
    # Initialize agent
    agent = GPT4Agent(name="gpt4-demo", api_key="your-api-key-here")
    
    # Create a request
    request = AgentRequest(
        prompt="Explain quantum computing in simple terms.",
        max_tokens=500,
        temperature=0.7
    )
    
    # Process the request
    response = await agent.process_request(request)
    
    # Handle the response
    if response.success:
        print(f"✓ Success from {response.agent_name}")
        print(f"Model: {response.model}")
        print(f"Tokens used: {response.tokens_used}")
        print(f"\nResponse:\n{response.content}\n")
    else:
        print(f"✗ Error: {response.error}")


async def gpt4_with_context_example():
    """
    Example using GPT-4 with context and conversation history.
    """
    print("\n=== GPT-4 with Context Example ===\n")
    
    agent = GPT4Agent(name="gpt4-context", api_key="your-api-key-here")
    
    # Create request with system context
    request = AgentRequest(
        prompt="What are the implications for cryptography?",
        context={
            "system_message": "You are an expert in quantum physics and computer science.",
            "history": [
                {"role": "user", "content": "Tell me about quantum computing."},
                {"role": "assistant", "content": "Quantum computing uses quantum mechanics principles..."}
            ]
        },
        max_tokens=300
    )
    
    response = await agent.process_request(request)
    
    if response.success:
        print(f"✓ Response: {response.content[:200]}...\n")
    else:
        print(f"✗ Error: {response.error}")


async def fusion_layer_example():
    """
    Example of using the fusion layer with multiple agents.
    
    Note: This example assumes you have multiple agents configured.
    For a real implementation, you would initialize Claude and Gemini agents too.
    """
    print("\n=== Fusion Layer Example ===\n")
    
    # Initialize agents (in real scenario, you'd have Claude and Gemini too)
    gpt4_agent = GPT4Agent(name="gpt4", api_key="your-api-key-here")
    
    # Initialize fusion layer
    fusion = ResponseFusionLayer(strategy="consensus")
    
    # Create a request
    request = AgentRequest(
        prompt="What are the main challenges in artificial general intelligence?",
        max_tokens=400
    )
    
    # Get responses from all agents (parallel execution)
    responses = await asyncio.gather(
        gpt4_agent.process_request(request),
        # claude_agent.process_request(request),  # Add when implemented
        # gemini_agent.process_request(request),  # Add when implemented
        return_exceptions=True
    )
    
    # Filter out exceptions
    valid_responses = [r for r in responses if not isinstance(r, Exception)]
    
    # Fuse responses
    if valid_responses:
        fused = await fusion.fuse_responses(valid_responses)
        
        print(f"✓ Fused response from {len(fused.contributing_agents)} agents")
        print(f"Confidence: {fused.confidence:.2f}")
        print(f"Strategy: {fused.metadata['strategy']}")
        print(f"\nFused content:\n{fused.content[:300]}...\n")


async def error_handling_example():
    """
    Example demonstrating error handling.
    """
    print("\n=== Error Handling Example ===\n")
    
    # Initialize with invalid configuration
    try:
        agent = GPT4Agent(name="gpt4-test", api_key="invalid-key")
        
        request = AgentRequest(prompt="Test prompt")
        response = await agent.process_request(request)
        
        if not response.success:
            print(f"✓ Error handled gracefully: {response.error}")
            print(f"Processing time: {response.metadata.get('processing_time', 0):.2f}s")
    
    except Exception as e:
        print(f"✓ Exception caught during initialization: {e}")


async def main():
    """
    Main function to run all examples.
    """
    # Setup logging
    config = Config()
    config.setup_logging(level="INFO")
    
    print("=" * 60)
    print("RAG7 Multi-LLM Architecture - GPT-4 Agent Examples")
    print("=" * 60)
    
    print("\nNote: These examples require valid API keys.")
    print("Set OPENAI_API_KEY environment variable or update the examples.\n")
    
    # Run examples (comment out as needed)
    try:
        # await simple_gpt4_example()
        # await gpt4_with_context_example()
        # await fusion_layer_example()
        await error_handling_example()
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("This is expected if API keys are not configured.")


if __name__ == "__main__":
    asyncio.run(main())
