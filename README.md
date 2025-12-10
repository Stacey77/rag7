# RAG7 - Multi-LLM Architecture

A modular system for orchestrating multiple Large Language Model (LLM) agents with response fusion capabilities.

## Overview

RAG7 is designed to leverage multiple LLM providers (GPT-4, Claude, Gemini) in parallel, combining their outputs through a sophisticated fusion layer. This architecture provides:

- **Redundancy**: Continue operating even if one provider is down
- **Consensus**: Combine insights from multiple models for better results
- **Flexibility**: Easy to add/remove agents or change fusion strategies
- **Robustness**: Built-in error handling and retry logic

## Architecture

```
User Request
    ↓
┌───────────────────────────┐
│   Request Distribution    │
└───────────────────────────┘
    ↓           ↓           ↓
┌────────┐  ┌────────┐  ┌────────┐
│  GPT-4 │  │ Claude │  │ Gemini │
│ Agent  │  │ Agent  │  │ Agent  │
└────────┘  └────────┘  └────────┘
    ↓           ↓           ↓
┌───────────────────────────┐
│   Response Fusion Layer   │
│  (Merge & Validate)       │
└───────────────────────────┘
    ↓
Final Response
```

## Features

### GPT-4 Agent
- ✅ OpenAI GPT-4 API integration
- ✅ Async request processing
- ✅ Context and conversation history support
- ✅ Automatic retry logic with exponential backoff
- ✅ Comprehensive error handling
- ✅ Detailed logging
- ✅ Configurable parameters (temperature, max_tokens, etc.)

### Response Fusion Layer
- ✅ Multiple fusion strategies:
  - **Consensus**: Find common elements/themes
  - **Best**: Select highest quality response
  - **Weighted**: Combine with configurable weights
  - **Concatenate**: Include all responses
- ✅ Response validation
- ✅ Confidence scoring
- ✅ Failure handling

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Stacey77/rag7.git
cd rag7
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. For development (includes testing tools):
```bash
pip install -r requirements-dev.txt
```

4. Set up environment variables:
```bash
# Create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## Quick Start

### Basic GPT-4 Agent Usage

```python
import asyncio
from agents.gpt4 import GPT4Agent
from agents.base import AgentRequest

async def main():
    # Initialize the agent
    agent = GPT4Agent(name="my-gpt4-agent")
    
    # Create a request
    request = AgentRequest(
        prompt="Explain quantum computing in simple terms.",
        max_tokens=500,
        temperature=0.7
    )
    
    # Process the request
    response = await agent.process_request(request)
    
    # Check the response
    if response.success:
        print(f"Response: {response.content}")
        print(f"Tokens used: {response.tokens_used}")
    else:
        print(f"Error: {response.error}")

asyncio.run(main())
```

### Using the Fusion Layer

```python
import asyncio
from agents.gpt4 import GPT4Agent
from agents.base import AgentRequest
from agents.fusion import ResponseFusionLayer

async def main():
    # Initialize agents
    gpt4_agent = GPT4Agent(name="gpt4")
    # claude_agent = ClaudeAgent(name="claude")  # Coming soon
    # gemini_agent = GeminiAgent(name="gemini")  # Coming soon
    
    # Initialize fusion layer
    fusion = ResponseFusionLayer(strategy="consensus")
    
    # Create request
    request = AgentRequest(prompt="What is artificial intelligence?")
    
    # Get responses from all agents in parallel
    responses = await asyncio.gather(
        gpt4_agent.process_request(request),
        # claude_agent.process_request(request),
        # gemini_agent.process_request(request),
    )
    
    # Fuse responses
    fused = await fusion.fuse_responses(responses)
    
    print(f"Fused response: {fused.content}")
    print(f"Confidence: {fused.confidence}")
    print(f"Contributing agents: {fused.contributing_agents}")

asyncio.run(main())
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `GPT4_MODEL`: Model to use (default: "gpt-4")
- `GPT4_MAX_TOKENS`: Maximum tokens per response (default: 2048)
- `GPT4_TEMPERATURE`: Sampling temperature (default: 0.7)
- `FUSION_STRATEGY`: Fusion strategy (default: "consensus")
- `FUSION_WEIGHTS`: Agent weights for weighted fusion (format: "gpt4:1.0,claude:0.9")

### Configuration File Example

```python
from config import Config

config = Config()
config.setup_logging(level="INFO", log_file="rag7.log")

gpt4_config = config.get_gpt4_config()
fusion_config = config.get_fusion_config()
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=agents --cov-report=html
```

## Project Structure

```
rag7/
├── agents/
│   ├── __init__.py
│   ├── base.py              # Base classes for all agents
│   ├── gpt4/
│   │   ├── __init__.py
│   │   └── agent.py         # GPT-4 agent implementation
│   └── fusion/
│       ├── __init__.py
│       └── layer.py         # Response fusion layer
├── tests/
│   ├── __init__.py
│   ├── test_gpt4_agent.py
│   └── test_fusion_layer.py
├── config.py                # Configuration management
├── examples.py              # Usage examples
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
└── README.md
```

## API Reference

### AgentRequest

```python
@dataclass
class AgentRequest:
    prompt: str                              # The prompt to send
    context: Optional[Dict[str, Any]]        # Additional context
    max_tokens: Optional[int]                # Maximum response tokens
    temperature: Optional[float]             # Sampling temperature
    metadata: Optional[Dict[str, Any]]       # Request metadata
```

### AgentResponse

```python
@dataclass
class AgentResponse:
    content: str                             # Response content
    agent_name: str                          # Name of responding agent
    model: str                               # Model used
    timestamp: datetime                      # Response timestamp
    tokens_used: Optional[int]               # Tokens consumed
    metadata: Optional[Dict[str, Any]]       # Response metadata
    error: Optional[str]                     # Error message if failed
    success: bool                            # Success status
```

### GPT4Agent

```python
agent = GPT4Agent(
    name="my-agent",                         # Agent name
    api_key="key",                           # OpenAI API key
    model="gpt-4",                           # Model to use
    config={}                                # Additional config
)

response = await agent.process_request(request)
```

### ResponseFusionLayer

```python
fusion = ResponseFusionLayer(
    strategy="consensus",                    # Fusion strategy
    config={"weights": {...}}                # Strategy-specific config
)

fused = await fusion.fuse_responses(responses)
```

## Roadmap

- [x] GPT-4 agent implementation
- [x] Response fusion layer
- [x] Error handling and retry logic
- [x] Comprehensive testing
- [ ] Claude agent implementation
- [ ] Gemini agent implementation
- [ ] Advanced fusion strategies
- [ ] Streaming support
- [ ] Rate limiting and quotas
- [ ] Caching layer
- [ ] Metrics and monitoring

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Contact

For questions or issues, please open an issue on GitHub.