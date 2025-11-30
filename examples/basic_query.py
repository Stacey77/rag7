"""Example: Basic single LLM query with automatic routing."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag7 import orchestrator, LLMRequest, TaskComplexity


async def main():
    """Run a basic single LLM query."""
    print("=" * 70)
    print("RAG7 Example: Single LLM Query")
    print("=" * 70)
    
    # Create a request
    request = LLMRequest(
        prompt="Explain what machine learning is in 3 sentences.",
        temperature=0.7,
        max_tokens=200,
        system_prompt="You are a helpful AI assistant that explains concepts clearly."
    )
    
    print("\nSending query to LLM with automatic routing...")
    print(f"Prompt: {request.prompt}\n")
    
    try:
        # Execute with medium complexity (will select appropriate provider)
        response = await orchestrator.execute_single(
            request,
            task_complexity=TaskComplexity.SIMPLE
        )
        
        print(f"✓ Response received from {response.provider.value} ({response.model})")
        print("=" * 70)
        print(response.content)
        print("=" * 70)
        print(f"\nMetrics:")
        print(f"  - Tokens used: {response.tokens_used}")
        print(f"  - Cost: ${response.cost:.4f}")
        print(f"  - Latency: {response.latency_ms:.2f}ms")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print("\nNote: Make sure you have set API keys in .env file")


if __name__ == "__main__":
    asyncio.run(main())
