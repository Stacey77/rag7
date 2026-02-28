# RAG7 Multi-LLM Orchestration Framework - Usage Guide

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Quick Start](#quick-start)
4. [API Usage](#api-usage)
5. [Python SDK Usage](#python-sdk-usage)
6. [Advanced Features](#advanced-features)
7. [Monitoring & Metrics](#monitoring--metrics)
8. [Best Practices](#best-practices)

## Installation

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/Stacey77/rag7.git
cd rag7

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### Development Installation

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example
cp .env.example .env

# Edit with your API keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
```

### YAML Configuration

The `config.yaml` file is automatically created with defaults. Customize as needed:

```yaml
providers:
  openai:
    enabled: true
    default_model: "gpt-4"
    max_tokens: 1000
    temperature: 0.7
    cost_per_1k_tokens:
      gpt-4: 0.03
      gpt-3.5-turbo: 0.002

router:
  default_provider: "openai"
  enable_fallback: true
  fallback_chain: ["openai", "anthropic", "google"]
  cost_optimization: true

fusion:
  default_strategy: "voting"
  min_agreement_threshold: 0.6
  weights:
    openai: 1.0
    anthropic: 1.0
    google: 1.0
```

## Quick Start

### Starting the API Server

```bash
# Basic start
python main.py

# Custom host and port
python main.py --host 0.0.0.0 --port 8080

# With auto-reload for development
python main.py --reload
```

The server will be available at `http://localhost:8000`

### Interactive API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Usage

### Single LLM Query

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms",
    "temperature": 0.7,
    "max_tokens": 500,
    "system_prompt": "You are a helpful science educator"
  }'
```

Response:
```json
{
  "content": "Quantum computing is...",
  "provider": "openai",
  "model": "gpt-4",
  "tokens_used": 342,
  "cost": 0.01026,
  "latency_ms": 1523.45,
  "timestamp": "2025-11-16T18:40:00Z",
  "metadata": {}
}
```

### Multi-LLM Query with Fusion

```bash
curl -X POST http://localhost:8000/api/v1/multi-generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What are the benefits of renewable energy?",
    "fusion_strategy": "voting",
    "parallel": true,
    "temperature": 0.7,
    "providers": ["openai", "anthropic", "google"]
  }'
```

Response:
```json
{
  "final_content": "Renewable energy offers...",
  "individual_responses": [...],
  "fusion_strategy": "voting",
  "total_cost": 0.0234,
  "total_latency_ms": 2341.67,
  "confidence_score": 0.87,
  "metadata": {
    "selected_provider": "anthropic",
    "similarity_scores": {...}
  }
}
```

### Health Check

```bash
curl http://localhost:8000/health
```

### Get Metrics

```bash
# Comprehensive metrics
curl http://localhost:8000/api/v1/metrics

# Prometheus format
curl http://localhost:8000/metrics
```

### List Available Providers

```bash
curl http://localhost:8000/api/v1/providers
```

## Python SDK Usage

### Basic Single Query

```python
import asyncio
from rag7 import orchestrator, LLMRequest, TaskComplexity

async def main():
    request = LLMRequest(
        prompt="What is machine learning?",
        temperature=0.7,
        max_tokens=200
    )
    
    response = await orchestrator.execute_single(
        request,
        task_complexity=TaskComplexity.SIMPLE
    )
    
    print(f"Response: {response.content}")
    print(f"Cost: ${response.cost:.4f}")
    print(f"Provider: {response.provider.value}")

asyncio.run(main())
```

### Multi-LLM Query with Fusion

```python
from rag7 import orchestrator, response_fusion, LLMRequest, FusionStrategy

async def multi_query():
    request = LLMRequest(
        prompt="Compare Python and JavaScript",
        temperature=0.7
    )
    
    # Query all available providers in parallel
    responses = await orchestrator.execute_parallel(request)
    
    # Fuse responses using voting
    fused = response_fusion.fuse_responses(
        responses,
        strategy=FusionStrategy.VOTING
    )
    
    print(f"Final answer: {fused.final_content}")
    print(f"Confidence: {fused.confidence_score:.2f}")
    print(f"Total cost: ${fused.total_cost:.4f}")

asyncio.run(multi_query())
```

### Specify Provider

```python
from rag7 import LLMRequest, LLMProvider, orchestrator

request = LLMRequest(
    prompt="Write a haiku about AI",
    provider=LLMProvider.ANTHROPIC,
    temperature=0.9
)

response = await orchestrator.execute_single(request)
```

### Using Different Fusion Strategies

```python
from rag7 import FusionStrategy

# Voting - selects most similar response
fused = response_fusion.fuse_responses(responses, FusionStrategy.VOTING)

# Ranking - ranks by quality metrics
fused = response_fusion.fuse_responses(responses, FusionStrategy.RANKING)

# Merging - combines all responses
fused = response_fusion.fuse_responses(responses, FusionStrategy.MERGING)

# First - returns first successful response
fused = response_fusion.fuse_responses(responses, FusionStrategy.FIRST)
```

## Advanced Features

### Task Complexity Routing

The router automatically selects the best LLM based on task complexity:

```python
from rag7 import TaskComplexity

# Simple tasks → cheaper, faster models
response = await orchestrator.execute_single(
    request,
    task_complexity=TaskComplexity.SIMPLE
)

# Medium tasks → balanced models
response = await orchestrator.execute_single(
    request,
    task_complexity=TaskComplexity.MEDIUM
)

# Complex tasks → most capable models
response = await orchestrator.execute_single(
    request,
    task_complexity=TaskComplexity.COMPLEX
)
```

### Fallback Chains

Automatic fallback to alternative providers on failure:

```python
# If OpenAI fails, automatically tries Anthropic, then Google
router_config = config_manager.get_router_config()
print(f"Fallback chain: {router_config.fallback_chain}")
```

### Cost Optimization

Enable cost optimization in config:

```yaml
router:
  cost_optimization: true  # Prefers cheaper providers
```

### Custom Provider Weights

Adjust provider weights for fusion:

```yaml
fusion:
  weights:
    openai: 1.2      # Prefer OpenAI responses
    anthropic: 1.0
    google: 0.8      # De-prioritize Google
```

## Monitoring & Metrics

### Accessing Metrics

```python
from rag7 import monitoring_service

# Get comprehensive summary
summary = monitoring_service.get_summary()
print(f"Total cost: ${summary['total_cost']:.4f}")
print(f"Cost by provider: {summary['cost_by_provider']}")

# Get provider-specific metrics
metrics = monitoring_service.metrics_collector.get_provider_metrics("openai")
print(f"Total requests: {metrics.total_requests}")
print(f"Success rate: {metrics.successful_requests / metrics.total_requests:.2%}")
print(f"Average latency: {metrics.average_latency_ms:.2f}ms")
```

### Prometheus Integration

Metrics are automatically exported in Prometheus format:

```bash
# Scrape endpoint
curl http://localhost:8000/metrics

# Configure Prometheus to scrape
# prometheus.yml:
# scrape_configs:
#   - job_name: 'rag7'
#     static_configs:
#       - targets: ['localhost:8000']
```

### Cost Tracking

```python
from rag7.monitoring import monitoring_service

# Get total cost
total = monitoring_service.cost_tracker.get_total_cost()

# Get cost by provider
openai_cost = monitoring_service.cost_tracker.get_provider_cost("openai")

# Get daily cost
today_cost = monitoring_service.cost_tracker.get_daily_cost()

# Get detailed breakdown
breakdown = monitoring_service.cost_tracker.get_cost_breakdown()
```

### Latency Analysis

```python
# Get average latency
avg = monitoring_service.latency_tracker.get_average_latency("openai")

# Get percentile latency
p95 = monitoring_service.latency_tracker.get_percentile_latency("openai", 95)
p99 = monitoring_service.latency_tracker.get_percentile_latency("openai", 99)
```

## Best Practices

### 1. API Key Management

- Never commit API keys to version control
- Use environment variables or secrets management
- Rotate keys regularly

### 2. Error Handling

```python
from rag7 import orchestrator, LLMRequest

try:
    response = await orchestrator.execute_single(request)
except Exception as e:
    print(f"Request failed: {e}")
    # Implement your error handling logic
```

### 3. Cost Management

- Use task complexity routing to optimize costs
- Monitor daily costs with tracking
- Set up alerts for cost thresholds
- Prefer cheaper models for simple tasks

### 4. Performance Optimization

- Use parallel execution for multi-LLM queries
- Enable latency optimization for time-critical tasks
- Cache responses when appropriate (implement separately)

### 5. Quality Assurance

- Use voting strategy for important decisions
- Set appropriate confidence thresholds
- Review fused responses for critical applications

### 6. Testing

```python
# Mock API keys for testing
import os
os.environ['OPENAI_API_KEY'] = 'test-key'

# Use test fixtures
from tests.conftest import mock_api_key
```

### 7. Monitoring

- Set up Prometheus + Grafana for visualization
- Track success rates and errors
- Monitor latency percentiles
- Review cost trends regularly

## Examples

See the `examples/` directory for complete working examples:

- `basic_query.py` - Single LLM query with routing
- `multi_llm_fusion.py` - Multi-LLM query with fusion strategies
- `api_client.py` - REST API client usage

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/Stacey77/rag7/issues
- Documentation: See README.md

## License

MIT License - See LICENSE file for details
