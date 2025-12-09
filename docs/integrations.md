# Integration Guide

## Overview

This guide covers integrating the RAG7 LangGraph API with external automation platforms like n8n, kiro.ai, and lindy.ai.

## Integration Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│    n8n      │────────▶│  LangGraph API   │────────▶│  Providers  │
│  Workflow   │         │  (FastAPI)       │         │  (kiro/lindy)│
└─────────────┘         └──────────────────┘         └─────────────┘
      │                          │
      │                          ▼
      │                   ┌─────────────┐
      └──────────────────▶│  Database   │
                          └─────────────┘
```

## n8n Integration

### Setup n8n Workflows

1. **Import Workflow Templates**

   Navigate to the `n8n/workflows` directory:
   ```bash
   cd n8n/workflows
   ```

   Import workflows into n8n:
   - Open n8n UI (http://localhost:5678)
   - Click "Import from File"
   - Select `main_orchestrator.json` and `langgraph_trigger.json`

2. **Configure Credentials**

   Use the template at `n8n/credentials/credentials_template.json`:

   In n8n UI:
   - Go to Credentials
   - Add new "HTTP Request" credential
   - Name: "RAG7 API"
   - Authentication: Header Auth
   - Header Name: `Authorization`
   - Header Value: `Bearer YOUR_API_KEY`

3. **Test Connection**

   ```bash
   # Test n8n webhook
   curl -X POST http://localhost:5678/webhook/langgraph \
     -H "Content-Type: application/json" \
     -d '{"input": "test message", "user_id": "test_user"}'
   ```

### n8n Workflow Examples

#### Main Orchestrator Workflow

Coordinates between n8n automation and LangGraph execution:

1. Webhook trigger receives request
2. Pre-process data
3. Call LangGraph API
4. Post-process results
5. Return response or trigger next action

#### LangGraph Trigger Workflow

Triggers LangGraph graph execution:

1. HTTP Request node calls `/v1/graph/run`
2. Wait for completion (or async callback)
3. Parse response
4. Store results or trigger downstream actions

### n8n Best Practices

- Use error handling nodes for reliability
- Implement retry logic for API calls
- Store sensitive data in n8n credentials
- Use variables for configuration
- Test workflows in staging first

## kiro.ai Provider Integration

### Overview

The kiro.ai provider enables RAG7 to leverage kiro.ai's automation capabilities.

### Configuration

```bash
# In .env.prod
KIRO_AI_API_KEY=your_kiro_api_key_here
KIRO_AI_BASE_URL=https://api.kiro.ai/v1
```

### API Endpoints

The kiro provider exposes the following operations:

**Execute Automation**
```bash
curl -X POST http://localhost:8000/v1/integrations/kiro/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "automation_id": "auto_123",
    "parameters": {
      "input": "process this data",
      "options": {"async": true}
    }
  }'
```

**Get Automation Status**
```bash
curl http://localhost:8000/v1/integrations/kiro/status/job_456 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**List Available Automations**
```bash
curl http://localhost:8000/v1/integrations/kiro/automations \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### kiro.ai Integration Patterns

**Pattern 1: Sync Execution**
```python
# Request
POST /v1/integrations/kiro/execute
{
  "automation_id": "auto_123",
  "parameters": {...},
  "wait_for_completion": true
}

# Response
{
  "status": "completed",
  "result": {...},
  "execution_time_ms": 1234
}
```

**Pattern 2: Async with Callback**
```python
# Request
POST /v1/integrations/kiro/execute
{
  "automation_id": "auto_123",
  "parameters": {...},
  "callback_url": "https://your-app.com/callback"
}

# Response
{
  "status": "running",
  "job_id": "job_456"
}

# Later, kiro.ai calls callback_url with results
```

### Error Handling

```python
# Example error response
{
  "error": "KiroAPIError",
  "message": "Rate limit exceeded",
  "retry_after": 60,
  "details": {...}
}
```

## lindy.ai Provider Integration

### Overview

The lindy.ai provider integrates lindy.ai's AI agent capabilities.

### Configuration

```bash
# In .env.prod
LINDY_AI_API_KEY=your_lindy_api_key_here
LINDY_AI_BASE_URL=https://api.lindy.ai/v1
```

### API Endpoints

**Create Agent Task**
```bash
curl -X POST http://localhost:8000/v1/integrations/lindy/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "agent_id": "agent_789",
    "task": {
      "type": "research",
      "query": "Find information about topic X",
      "context": {...}
    }
  }'
```

**Get Task Status**
```bash
curl http://localhost:8000/v1/integrations/lindy/tasks/task_123 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**List Available Agents**
```bash
curl http://localhost:8000/v1/integrations/lindy/agents \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### lindy.ai Integration Patterns

**Pattern 1: Agent Execution**
```python
# Create task
POST /v1/integrations/lindy/tasks
{
  "agent_id": "agent_789",
  "task": {
    "type": "research",
    "query": "...",
    "max_duration_minutes": 5
  }
}

# Poll for completion
GET /v1/integrations/lindy/tasks/task_123

# Response when complete
{
  "status": "completed",
  "result": {
    "findings": [...],
    "sources": [...]
  }
}
```

**Pattern 2: Streaming Results**
```python
# Create streaming task
POST /v1/integrations/lindy/tasks
{
  "agent_id": "agent_789",
  "task": {...},
  "stream": true
}

# Connect to SSE endpoint
GET /v1/integrations/lindy/tasks/task_123/stream

# Receive events
data: {"event": "progress", "data": {...}}
data: {"event": "result", "data": {...}}
data: {"event": "complete"}
```

## LangGraph API Integration

### Core Endpoints

**Health Check**
```bash
curl http://localhost:8000/health
# Response: {"status": "healthy"}
```

**Readiness Check**
```bash
curl http://localhost:8000/ready
# Response: {"status": "ready", "dependencies": {"database": "ok", "redis": "ok"}}
```

**Execute Graph**
```bash
curl -X POST http://localhost:8000/v1/graph/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "graph_id": "main_graph",
    "input": {
      "query": "What is the weather?",
      "user_id": "user_123"
    },
    "config": {
      "timeout": 30,
      "provider": "kiro"
    }
  }'
```

**Response Format**
```json
{
  "status": "success",
  "graph_id": "main_graph",
  "output": {
    "result": "...",
    "metadata": {...}
  },
  "execution_time_ms": 1234,
  "trace_id": "trace_abc123"
}
```

### Error Responses

```json
{
  "status": "error",
  "error_code": "PROVIDER_TIMEOUT",
  "message": "Provider API request timed out",
  "details": {...},
  "trace_id": "trace_abc123"
}
```

### Common Error Codes

- `INVALID_INPUT`: Request validation failed
- `AUTHENTICATION_FAILED`: Invalid API key
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `PROVIDER_TIMEOUT`: Provider API timeout
- `PROVIDER_ERROR`: Provider API error
- `GRAPH_EXECUTION_FAILED`: Graph execution error
- `INTERNAL_ERROR`: Internal server error

## End-to-End Integration Example

### Scenario: Automated Content Processing

1. **Trigger**: User uploads document via n8n webhook
2. **n8n**: Pre-processes document, extracts metadata
3. **LangGraph API**: Analyzes document content
4. **kiro.ai**: Automates data extraction workflow
5. **lindy.ai**: Researches related information
6. **n8n**: Combines results and stores in database
7. **Response**: Returns processed data to user

### Implementation

**Step 1: n8n Webhook (Entry Point)**
```json
{
  "workflow": "document_processing",
  "document_url": "https://storage.example.com/doc123.pdf",
  "user_id": "user_456"
}
```

**Step 2: Call LangGraph API**
```bash
curl -X POST http://localhost:8000/v1/graph/run \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "document_analyzer",
    "input": {
      "document_url": "https://storage.example.com/doc123.pdf"
    }
  }'
```

**Step 3: Trigger kiro.ai Automation**
```bash
curl -X POST http://localhost:8000/v1/integrations/kiro/execute \
  -H "Content-Type: application/json" \
  -d '{
    "automation_id": "data_extraction",
    "parameters": {
      "document_analysis": {...}
    }
  }'
```

**Step 4: Request lindy.ai Research**
```bash
curl -X POST http://localhost:8000/v1/integrations/lindy/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "research_agent",
    "task": {
      "type": "research",
      "query": "Find additional context for: ..."
    }
  }'
```

**Step 5: n8n Combines Results**
- Aggregate all responses
- Format output
- Store in database
- Notify user

## Authentication

All API requests require authentication via Bearer token:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:8000/v1/graph/run
```

Generate API keys:
```bash
# TODO: Implement API key generation endpoint
POST /v1/auth/api-keys
{
  "name": "My Integration",
  "scopes": ["read", "write"]
}
```

## Rate Limiting

Default rate limits:
- 1000 requests per hour per API key
- 100 requests per minute per IP address

Rate limit headers in response:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1702140000
```

## Webhooks

Configure webhooks for async notifications:

**Register Webhook**
```bash
curl -X POST http://localhost:8000/v1/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhook",
    "events": ["graph.completed", "graph.failed"],
    "secret": "webhook_secret_123"
  }'
```

**Webhook Payload**
```json
{
  "event": "graph.completed",
  "timestamp": "2024-12-09T18:00:00Z",
  "data": {
    "graph_id": "main_graph",
    "execution_id": "exec_123",
    "output": {...}
  },
  "signature": "sha256=..."
}
```

## Testing Integrations

### Local Testing

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:8000/ready

# Test graph execution
curl -X POST http://localhost:8000/v1/graph/run \
  -H "Content-Type: application/json" \
  -d '{"graph_id": "test_graph", "input": {"test": true}}'

# Test provider integrations
curl http://localhost:8000/v1/integrations/kiro/automations
curl http://localhost:8000/v1/integrations/lindy/agents
```

### Integration Tests

```bash
# Run integration test suite
pytest tests/integration/ -v

# Run specific provider tests
pytest tests/integration/test_kiro_provider.py
pytest tests/integration/test_lindy_provider.py
```

## Troubleshooting

### Provider Connection Issues

```bash
# Test provider connectivity
curl -H "Authorization: Bearer $KIRO_AI_API_KEY" \
  https://api.kiro.ai/v1/health

curl -H "Authorization: Bearer $LINDY_AI_API_KEY" \
  https://api.lindy.ai/v1/health
```

### n8n Workflow Issues

1. Check n8n logs: `docker-compose logs n8n`
2. Verify webhook URLs are accessible
3. Test credentials in n8n UI
4. Check workflow execution history

### API Authentication Issues

1. Verify API key format
2. Check API key expiration
3. Review rate limit headers
4. Confirm API key has correct scopes

## Best Practices

1. **Use async patterns** for long-running operations
2. **Implement retries** with exponential backoff
3. **Monitor provider quotas** and rate limits
4. **Log all integration calls** for debugging
5. **Use webhooks** for event-driven architectures
6. **Validate inputs** before calling providers
7. **Handle errors gracefully** with proper error codes
8. **Test integrations** in staging before production
9. **Document custom workflows** for team reference
10. **Set timeouts** for all external API calls

## Next Steps

1. Import n8n workflow templates
2. Configure provider credentials
3. Test each integration independently
4. Build end-to-end workflows
5. Setup monitoring and alerts
6. Document custom integration patterns

## Related Documentation

- [Deployment Guide](deployment.md)
- [Observability Guide](observability.md)
- [Runbook](runbook.md)
- n8n documentation: https://docs.n8n.io
- kiro.ai API docs: https://docs.kiro.ai
- lindy.ai API docs: https://docs.lindy.ai
