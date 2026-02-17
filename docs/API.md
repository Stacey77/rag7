# RAG7 Platform API Guide

## Overview

The RAG7 platform provides a comprehensive REST API for building and deploying AI products powered by multiple LLM providers and multi-agent systems.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API is open for development. In production, add authentication headers:

```
Authorization: Bearer YOUR_API_TOKEN
```

## Endpoints

### 1. LLM Interactions

#### Generate Completion

Create a text completion using any supported LLM provider.

```http
POST /api/v1/llm/completion
Content-Type: application/json

{
  "prompt": "Explain machine learning",
  "provider": "openai",
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 500,
  "system_message": "You are a helpful AI assistant"
}
```

**Response:**
```json
{
  "content": "Machine learning is...",
  "provider": "openai",
  "model": "gpt-4",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 150,
    "total_tokens": 160
  }
}
```

#### Chat Completion

Multi-turn conversation with context.

```http
POST /api/v1/llm/chat
Content-Type: application/json

{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "What is AI?"},
    {"role": "assistant", "content": "AI stands for..."},
    {"role": "user", "content": "Tell me more"}
  ],
  "provider": "anthropic",
  "model": "claude-3-opus"
}
```

#### List Providers

```http
GET /api/v1/llm/providers
```

### 2. Multi-Agent System

#### Execute Single Agent

Run a specialized AI agent for a specific task.

```http
POST /api/v1/agents/execute
Content-Type: application/json

{
  "agent_type": "research",
  "instruction": "Research the latest AI trends in healthcare",
  "context": {
    "industry": "healthcare",
    "focus": "diagnostics"
  },
  "max_iterations": 5
}
```

**Agent Types:**
- `research`: Information gathering and analysis
- `analyst`: Data analysis and insights
- `writer`: Content generation
- `coder`: Code generation and review
- `orchestrator`: Multi-agent coordination

#### Multi-Agent Workflow

Execute multiple agents in a coordinated workflow.

```http
POST /api/v1/agents/multi-agent
Content-Type: application/json

{
  "tasks": [
    {
      "agent_type": "research",
      "instruction": "Research topic X"
    },
    {
      "agent_type": "analyst",
      "instruction": "Analyze findings"
    },
    {
      "agent_type": "writer",
      "instruction": "Write a report"
    }
  ]
}
```

### 3. Project Management

#### Create Project

```http
POST /api/v1/projects/
Content-Type: application/json

{
  "name": "Customer Support AI",
  "description": "AI-powered customer support system",
  "customer_id": "customer_123",
  "use_case": "customer_support",
  "llm_providers": ["openai", "anthropic"]
}
```

#### List Projects

```http
GET /api/v1/projects/
GET /api/v1/projects/?status=active
GET /api/v1/projects/?customer_id=customer_123
```

#### Get Project Details

```http
GET /api/v1/projects/{project_id}
```

### 4. Deployment Management

#### Create Deployment

Deploy an AI product to an environment.

```http
POST /api/v1/deployments/
Content-Type: application/json

{
  "project_id": "proj_001",
  "environment": "production",
  "config": {
    "replicas": 3,
    "auto_scaling": true,
    "max_replicas": 10,
    "cpu_threshold": 70
  }
}
```

#### List Deployments

```http
GET /api/v1/deployments/
GET /api/v1/deployments/?project_id=proj_001
GET /api/v1/deployments/?environment=production
```

#### Get Deployment Metrics

Monitor real-time metrics for a deployment.

```http
GET /api/v1/deployments/{deployment_id}/metrics
```

**Response:**
```json
{
  "deployment_id": "dep_001",
  "requests_per_minute": 125.5,
  "average_latency_ms": 350.2,
  "error_rate": 0.02,
  "uptime_percentage": 99.95,
  "cost_per_hour": 2.50
}
```

#### Scale Deployment

```http
POST /api/v1/deployments/{deployment_id}/scale
Content-Type: application/json

{
  "replicas": 5
}
```

#### Stop Deployment

```http
POST /api/v1/deployments/{deployment_id}/stop
```

## Rate Limits

- Development: No limits
- Production: 1000 requests/minute per API key

## Error Handling

All errors follow this format:

```json
{
  "detail": "Error message"
}
```

**HTTP Status Codes:**
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

## Examples

### Python Example

```python
import requests

# Generate completion
response = requests.post(
    "http://localhost:8000/api/v1/llm/completion",
    json={
        "prompt": "Explain quantum computing",
        "provider": "openai",
        "temperature": 0.7
    }
)
result = response.json()
print(result["content"])
```

### JavaScript Example

```javascript
// Generate completion
const response = await fetch('http://localhost:8000/api/v1/llm/completion', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    prompt: 'Explain quantum computing',
    provider: 'openai',
    temperature: 0.7
  })
});

const result = await response.json();
console.log(result.content);
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/api/v1/llm/completion" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing",
    "provider": "openai",
    "temperature": 0.7
  }'
```

## Interactive Documentation

Access interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

These interfaces allow you to test endpoints directly in your browser.
