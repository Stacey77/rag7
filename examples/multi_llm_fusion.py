"""Example: Multi-LLM query with response fusion."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag7 import orchestrator, response_fusion, LLMRequest, FusionStrategy


async def main():
    """Run a multi-LLM query with fusion."""
    print("=" * 70)
    print("RAG7 Example: Multi-LLM Query with Fusion")
    print("=" * 70)
    
    # Create a request
    request = LLMRequest(
        prompt="What are the top 3 benefits of using renewable energy?",
        temperature=0.7,
        max_tokens=300
    )
    
    print(f"\nPrompt: {request.prompt}")
    print("\nQuerying multiple LLMs in parallel...")
    
    try:
        # Execute on all available providers
        responses = await orchestrator.execute_parallel(request)
        
        print(f"\n✓ Received {len(responses)} responses")
        
        # Show individual responses
        print("\n" + "=" * 70)
        print("Individual Responses:")
        print("=" * 70)
        for i, resp in enumerate(responses, 1):
            print(f"\n{i}. {resp.provider.value} ({resp.model}):")
            print(f"   Tokens: {resp.tokens_used}, Cost: ${resp.cost:.4f}")
            print(f"   {resp.content[:200]}...")
        
        # Fuse responses using different strategies
        print("\n" + "=" * 70)
        print("Fusion Strategies:")
        print("=" * 70)
        
        for strategy in [FusionStrategy.VOTING, FusionStrategy.RANKING]:
            fused = response_fusion.fuse_responses(responses, strategy)
            
            print(f"\n{strategy.value.upper()} Strategy:")
            print(f"  Confidence: {fused.confidence_score:.2f}")
            print(f"  Total Cost: ${fused.total_cost:.4f}")
            print(f"  Selected: {fused.metadata.get('selected_provider', 'N/A')}")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("\nNote: Make sure you have set API keys in .env file")


if __name__ == "__main__":
    asyncio.run(main())
