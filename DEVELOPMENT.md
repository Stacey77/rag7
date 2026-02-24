# Development Guide

This guide explains how to extend the RAG7 AI Agent Platform with new integrations, functions, and capabilities.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Adding New Integrations](#adding-new-integrations)
- [Function Calling Design](#function-calling-design)
- [Memory and RAG Patterns](#memory-and-rag-patterns)
- [Testing Guidelines](#testing-guidelines)
- [Code Style](#code-style)
- [Deployment](#deployment)

## Architecture Overview

### Core Components

1. **ConversationalAgent** (`src/agent/core.py`)
   - Manages conversation flow
   - Routes function calls to integrations
   - Maintains conversation context

2. **BaseIntegration** (`src/integrations/base.py`)
   - Abstract base for all integrations
   - Defines function schema format
   - Converts to OpenAI function calling format

3. **AgentMemory** (`src/agent/memory.py`)
   - Stores conversation history
   - Provides semantic search via ChromaDB
   - Falls back to in-memory storage

4. **FastAPI Interface** (`src/interfaces/web_api.py`)
   - REST and WebSocket endpoints
   - Integration health monitoring
   - CORS and middleware configuration

## Adding New Integrations

### Step 1: Create Integration Class

Create a new file in `src/integrations/`:

```python
# src/integrations/my_service.py
from typing import Any, Dict, List, Optional
from .base import BaseIntegration, IntegrationFunction, FunctionParameter

class MyServiceIntegration(BaseIntegration):
    """Integration for MyService API."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key
        # Initialize your client here
    
    def get_functions(self) -> List[IntegrationFunction]:
        """Define available functions."""
        return [
            IntegrationFunction(
                name="my_function",
                description="What this function does",
                parameters=[
                    FunctionParameter(
                        name="param1",
                        type="string",
                        description="Parameter description",
                        required=True
                    )
                ]
            )
        ]
    
    async def execute(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a function."""
        if function_name == "my_function":
            return await self._my_function(**kwargs)
        
        return {
            "success": False,
            "error": f"Unknown function: {function_name}",
            "data": None
        }
    
    async def _my_function(self, param1: str) -> Dict[str, Any]:
        """Implementation of my_function."""
        try:
            # Your API call here
            result = "some result"
            
            return {
                "success": True,
                "data": {"result": result},
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def health_check(self) -> bool:
        """Check if integration is configured."""
        return bool(self.api_key)
```

### Step 2: Register Integration

Add to `src/interfaces/web_api.py` in the `lifespan` function:

```python
# Initialize MyService integration
if settings.my_service_api_key:
    my_service = MyServiceIntegration(
        api_key=settings.my_service_api_key
    )
    integrations.append(my_service)
    logger.info("MyService integration enabled")
```

### Step 3: Add Configuration

Update `src/utils/config.py`:

```python
class Settings(BaseSettings):
    # ... existing fields ...
    
    # MyService Integration
    my_service_api_key: str = ""
```

Update `.env.example`:

```bash
# MyService Integration
MY_SERVICE_API_KEY=your-api-key-here
```

### Step 4: Add Tests

Create `tests/test_my_service.py`:

```python
import pytest
from src.integrations.my_service import MyServiceIntegration

@pytest.mark.asyncio
async def test_my_service_integration():
    """Test MyService integration."""
    service = MyServiceIntegration(api_key="test-key")
    
    functions = service.get_functions()
    assert len(functions) > 0
    
    result = await service.execute("my_function", param1="test")
    assert "success" in result
```

## Function Calling Design

### Function Schema

Functions are defined using the `IntegrationFunction` model:

```python
IntegrationFunction(
    name="function_name",
    description="Clear description for the AI model",
    parameters=[
        FunctionParameter(
            name="param_name",
            type="string",  # string, integer, boolean, array, object
            description="What this parameter does",
            required=True,  # or False
            enum=["option1", "option2"]  # Optional: restrict values
        )
    ]
)
```

### Parameter Types

Supported types match JSON Schema:
- `string` - Text values
- `integer` - Whole numbers
- `number` - Decimals
- `boolean` - true/false
- `array` - Lists
- `object` - Nested structures

### Best Practices

1. **Clear Descriptions**: Help the AI understand when to use the function
   ```python
   description="Send a message to a Slack channel by name or ID"
   ```

2. **Required vs Optional**: Mark parameters appropriately
   ```python
   FunctionParameter(name="channel", required=True)
   FunctionParameter(name="thread_ts", required=False)
   ```

3. **Enums for Constraints**: Limit values when possible
   ```python
   FunctionParameter(
       name="priority",
       type="string",
       enum=["low", "medium", "high"]
   )
   ```

4. **Atomic Functions**: Each function should do one thing well
   - ✅ `send_message()` - Send a message
   - ❌ `send_message_and_create_channel()` - Too complex

## Memory and RAG Patterns

### Using Agent Memory

The `AgentMemory` class provides conversation persistence:

```python
# Add messages
await memory.add_message(
    role="user",
    content="User's question",
    metadata={"source": "web", "user_id": "123"}
)

# Get recent messages
messages = await memory.get_recent_messages(limit=10)

# Semantic search
similar = await memory.search_similar(
    query="questions about pricing",
    limit=5
)
```

### Implementing RAG

To add retrieval-augmented generation:

1. **Index Documents**:
   ```python
   # In your integration or startup
   for doc in documents:
       await memory.collection.add(
           ids=[doc.id],
           documents=[doc.content],
           metadatas=[{"type": "knowledge", "source": doc.source}]
       )
   ```

2. **Retrieve Context**:
   ```python
   # Before calling OpenAI
   relevant_docs = await memory.search_similar(user_message, limit=3)
   
   # Add to system message
   context = "\n".join([doc["content"] for doc in relevant_docs])
   system_message = f"Context:\n{context}\n\nAnswer based on this context."
   ```

3. **Cite Sources**:
   ```python
   # Include metadata in response
   sources = [doc["metadata"]["source"] for doc in relevant_docs]
   ```

### ChromaDB Collections

Create separate collections for different use cases:

```python
# Conversation history
conversation_memory = AgentMemory(collection_name="conversations")

# Knowledge base
knowledge_base = AgentMemory(collection_name="knowledge")

# User preferences
user_prefs = AgentMemory(collection_name="user_preferences")
```

## Testing Guidelines

### Test Structure

```python
# tests/test_my_feature.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_feature():
    """Test description."""
    # Arrange
    setup_data = {}
    
    # Act
    result = await function_to_test(setup_data)
    
    # Assert
    assert result["success"] is True
```

### Mocking External APIs

```python
@patch('src.integrations.slack.AsyncWebClient')
async def test_slack_mock(mock_client):
    """Test with mocked Slack client."""
    mock_client.return_value.chat_postMessage = AsyncMock(
        return_value={"ok": True, "ts": "123"}
    )
    
    slack = SlackIntegration(bot_token="test")
    result = await slack.execute("send_message", channel="test", text="hi")
    
    assert result["success"] is True
```

### Test Coverage

Aim for:
- ✅ Happy path tests
- ✅ Error handling tests
- ✅ Edge cases
- ✅ Integration tests
- ✅ API endpoint tests

Run coverage:
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Code Style

### Python Style Guide

Follow PEP 8 with these conventions:

```python
# Type hints
def process_message(message: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Process a message and return result."""
    pass

# Docstrings (Google style)
async def send_email(to: str, subject: str, body: str) -> bool:
    """
    Send an email via Gmail.
    
    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body content
        
    Returns:
        True if sent successfully, False otherwise
        
    Raises:
        ValueError: If recipient email is invalid
    """
    pass

# Error handling
try:
    result = await api_call()
except SpecificException as e:
    logger.error(f"Failed to call API: {e}")
    return {"success": False, "error": str(e)}
```

### Formatting Tools

```bash
# Format code
black src tests

# Check style
flake8 src tests

# Type checking
mypy src --ignore-missing-imports
```

### Commit Messages

Follow conventional commits:

```
feat: Add GitHub integration
fix: Handle timeout in Slack API
docs: Update integration setup guide
test: Add tests for memory search
refactor: Simplify function calling logic
```

## Deployment

### Docker Production Build

Create `Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV ENVIRONMENT=production
ENV API_RELOAD=False

CMD ["uvicorn", "src.interfaces.web_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

For production:

```bash
# Use secrets management
OPENAI_API_KEY=${SECRET_OPENAI_KEY}
DATABASE_URL=postgresql://user:pass@db:5432/rag7
REDIS_URL=redis://redis:6379/0
CHROMA_HOST=chromadb
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### Kubernetes Deployment

Example `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag7-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag7-api
  template:
    metadata:
      labels:
        app: rag7-api
    spec:
      containers:
      - name: api
        image: your-registry/rag7:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: rag7-secrets
              key: openai-key
        ports:
        - containerPort: 8000
```

### Health Checks

The `/health` endpoint returns:

```json
{
  "status": "healthy",
  "agent_ready": true,
  "openai_configured": true
}
```

Use for:
- Docker healthcheck
- Kubernetes liveness/readiness probes
- Load balancer health checks

### Monitoring

Add monitoring with:

1. **Prometheus**: Expose metrics
   ```python
   from prometheus_client import Counter, Histogram
   
   chat_requests = Counter('chat_requests_total', 'Total chat requests')
   chat_duration = Histogram('chat_duration_seconds', 'Chat processing time')
   ```

2. **Logging**: Use structured logging
   ```python
   import logging
   logger.info("Processing chat", extra={
       "user_id": user_id,
       "message_length": len(message)
   })
   ```

3. **Error Tracking**: Integrate Sentry
   ```python
   import sentry_sdk
   sentry_sdk.init(dsn=settings.sentry_dsn)
   ```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes following code style guidelines
4. Add tests for new functionality
5. Run tests: `pytest tests/ -v`
6. Format code: `black src tests`
7. Commit with conventional commits
8. Push and create a Pull Request

## Getting Help

- 📖 Review existing integrations for examples
- 🐛 Check GitHub Issues for known problems
- 💬 Ask questions in Pull Requests
- 📧 Contact maintainers for major changes

---

Happy coding! 🚀
