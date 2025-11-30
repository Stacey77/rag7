"""Example: Using the REST API client."""
import asyncio
import httpx


async def main():
    """Demonstrate REST API usage."""
    base_url = "http://localhost:8000"
    
    print("=" * 70)
    print("RAG7 Example: REST API Client")
    print("=" * 70)
    print("\nNote: Make sure the API server is running (python main.py)")
    
    async with httpx.AsyncClient() as client:
        # Check health
        print("\n1. Checking API health...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                health = response.json()
                print(f"   Status: {health['status']}")
                print(f"   Providers: {health['providers']}")
            else:
                print(f"   Error: {response.status_code}")
                return
        except Exception as e:
            print(f"   ✗ Cannot connect to API: {e}")
            print("   Make sure to start the server first: python main.py")
            return
        
        # Single LLM query
        print("\n2. Single LLM query...")
        request_data = {
            "prompt": "What is artificial intelligence?",
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = await client.post(
            f"{base_url}/api/v1/generate",
            json=request_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Provider: {result['provider']}")
            print(f"   ✓ Tokens: {result['tokens_used']}")
            print(f"   ✓ Cost: ${result['cost']:.4f}")
            print(f"   Response: {result['content'][:100]}...")
        else:
            print(f"   ✗ Error: {response.status_code}")
        
        # Multi-LLM query
        print("\n3. Multi-LLM query with fusion...")
        multi_request = {
            "prompt": "List 3 programming languages for beginners",
            "fusion_strategy": "voting",
            "parallel": True,
            "temperature": 0.7
        }
        
        response = await client.post(
            f"{base_url}/api/v1/multi-generate",
            json=multi_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Strategy: {result['fusion_strategy']}")
            print(f"   ✓ Providers queried: {len(result['individual_responses'])}")
            print(f"   ✓ Total cost: ${result['total_cost']:.4f}")
            print(f"   ✓ Confidence: {result.get('confidence_score', 'N/A')}")
        else:
            print(f"   ✗ Error: {response.status_code}")
        
        # Get metrics
        print("\n4. Fetching metrics...")
        response = await client.get(f"{base_url}/api/v1/metrics")
        
        if response.status_code == 200:
            metrics = response.json()
            print(f"   ✓ Total cost: ${metrics['total_cost']:.4f}")
            print(f"   ✓ Providers: {list(metrics['cost_by_provider'].keys())}")
        else:
            print(f"   ✗ Error: {response.status_code}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
