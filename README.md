# RAG7 Multi-LLM Orchestration Framework

A comprehensive multi-LLM orchestration framework for GPT-4, Claude, and Gemini integration with intelligent routing, response fusion, and observability.

## Features

- 🤖 **Multi-LLM Support**: Integrate OpenAI GPT-4, Anthropic Claude, and Google Gemini
- 🎯 **Intelligent Routing**: Automatic LLM selection based on task complexity, cost, and latency
- 🔄 **Response Fusion**: Multiple strategies (voting, ranking, merging) to combine outputs
- 📊 **Monitoring & Observability**: Token counting, cost tracking, latency metrics
- ⚡ **Async Support**: High-performance async API with FastAPI
- 🔒 **Type Safety**: Pydantic models throughout for request/response validation
- 🛡️ **Error Handling**: Automatic retry logic and fallback chains
- 📈 **Prometheus Metrics**: Built-in metrics export for monitoring

## Architecture

```
Query Input → Router Agent → Individual Agents (GPT-4/Claude/Gemini)
                              ↓
                         Response Fusion Layer
                              ↓
                         Final Response
```

## Installation

```bash
# Clone the repository
git clone https://github.com/Stacey77/rag7.git
cd rag7

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# OPENAI_API_KEY=your-key-here
# ANTHROPIC_API_KEY=your-key-here
# GOOGLE_API_KEY=your-key-here
```

## Quick Start

### Running the API Server

```bash
# Start the server
python main.py

# Or with custom settings
python main.py --host 0.0.0.0 --port 8000 --reload
```

### Using the Python API

```python
import asyncio
from rag7 import orchestrator, LLMRequest, TaskComplexity

async def main():
    # Single LLM request with automatic routing
    request = LLMRequest(
        prompt="Explain quantum computing in simple terms",
        temperature=0.7,
        max_tokens=500
    )
    
    response = await orchestrator.execute_single(
        request,
        task_complexity=TaskComplexity.MEDIUM
    )
    
    print(f"Response from {response.provider.value}:")
    print(response.content)
    print(f"Cost: ${response.cost:.4f}")
    print(f"Tokens: {response.tokens_used}")

asyncio.run(main())
```

### Multi-LLM Query with Fusion

```python
from rag7 import orchestrator, response_fusion, LLMRequest, FusionStrategy

async def multi_llm_query():
    request = LLMRequest(
        prompt="What are the key benefits of renewable energy?",
        temperature=0.7
    )
    
    # Get responses from all providers
    responses = await orchestrator.execute_parallel(request)
    
    # Fuse responses using voting strategy
    fused = response_fusion.fuse_responses(
        responses,
        strategy=FusionStrategy.VOTING
    )
    
    print(f"Final fused response:")
    print(fused.final_content)
    print(f"Confidence: {fused.confidence_score:.2f}")
    print(f"Total cost: ${fused.total_cost:.4f}")

asyncio.run(multi_llm_query())
```

## API Endpoints

### Generate with Single LLM

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is machine learning?",
    "temperature": 0.7,
    "max_tokens": 200
  }'
```

### Multi-LLM Generation with Fusion

```bash
curl -X POST http://localhost:8000/api/v1/multi-generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain the theory of relativity",
    "fusion_strategy": "voting",
    "parallel": true,
    "temperature": 0.7
  }'
```

### Health Check

```bash
curl http://localhost:8000/health
```

### Metrics

```bash
# Get comprehensive metrics
curl http://localhost:8000/api/v1/metrics

# Prometheus format
curl http://localhost:8000/metrics
```

## Configuration

Configuration is managed through `config.yaml` and environment variables:

```yaml
providers:
  openai:
    enabled: true
    default_model: "gpt-4"
    max_tokens: 1000
    temperature: 0.7
  
  anthropic:
    enabled: true
    default_model: "claude-3-opus-20240229"
  
  google:
    enabled: true
    default_model: "gemini-pro"

router:
  default_provider: "openai"
  enable_fallback: true
  fallback_chain: ["openai", "anthropic", "google"]
  cost_optimization: true

fusion:
  default_strategy: "voting"
  min_agreement_threshold: 0.6
```

## Fusion Strategies

1. **Voting**: Selects the response with highest similarity to others
2. **Ranking**: Ranks responses by quality metrics and provider weights
3. **Merging**: Combines all responses into a comprehensive answer
4. **First**: Returns the first successful response

## Task Complexity Routing

The router can automatically select the best LLM based on task complexity:

- **Simple**: Quick questions, basic tasks → GPT-3.5 Turbo / cheaper models
- **Medium**: Standard queries, moderate complexity → GPT-4 / Claude Sonnet
- **Complex**: Deep reasoning, complex analysis → Claude Opus / Gemini Pro

## Monitoring

Built-in Prometheus metrics for:
- Request counts (total, success, failure)
- Token usage per provider/model
- Cost tracking
- Latency histograms
- Active request gauges

## Project Structure

```
rag7/
├── rag7/
│   ├── __init__.py          # Main package exports
│   ├── models/              # Pydantic models
│   ├── providers/           # LLM provider implementations
│   ├── agents/              # AI agent wrappers
│   ├── orchestrator/        # Routing and orchestration
│   ├── fusion/              # Response fusion strategies
│   ├── monitoring/          # Metrics and observability
│   ├── config/              # Configuration management
│   └── api/                 # FastAPI endpoints
├── main.py                  # Application entry point
├── requirements.txt         # Dependencies
├── config.yaml             # Configuration file
└── .env                    # Environment variables
```

## Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Format code
black rag7/

# Type checking
mypy rag7/

# Linting
flake8 rag7/
```

## Use Cases

- **RAG Applications**: Multi-agent retrieval and generation workflows
- **Content Generation**: Combine multiple LLM perspectives for better content
- **Code Generation**: Cross-validate code solutions from different models
- **Research**: Compare and analyze outputs from different AI models
- **Quality Assurance**: Use voting/ranking to improve output quality
- **Cost Optimization**: Automatically route to cheaper models when appropriate

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.