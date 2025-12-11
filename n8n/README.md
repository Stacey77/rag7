# n8n Workflows for RAG7

This directory contains n8n workflow templates for orchestrating the RAG7 LangGraph application.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Workflows](#workflows)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

## Overview

n8n provides workflow automation for the RAG7 LangGraph system, enabling:

- **API Orchestration**: Manage incoming requests and route them to LangGraph
- **Scheduled Processing**: Execute batch tasks on a schedule
- **Error Handling**: Graceful error handling and retry logic
- **Monitoring**: Track execution metrics and logs
- **Integration**: Connect with external systems and APIs

## Prerequisites

### Required

- n8n instance (self-hosted or cloud)
- Access to RAG7 LangGraph API
- API keys for:
  - LangGraph API
  - OpenAI (or other LLM providers)
  - LangChain/LangSmith (optional)

### Optional

- PostgreSQL credentials (for direct database access)
- Redis credentials (for caching)
- Task queue system credentials

## Installation

### 1. Set Up n8n

**Self-hosted (Docker):**

```bash
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

**Self-hosted (Docker Compose):**

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=change-this-password
      - N8N_HOST=n8n.yourdomain.com
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://n8n.yourdomain.com/
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

**Cloud:**

Sign up at [n8n.cloud](https://n8n.cloud)

### 2. Configure Credentials

1. Open n8n UI (http://localhost:5678 or your n8n URL)
2. Navigate to **Credentials** → **Add Credential**
3. Create credentials based on `credentials/credentials_template.json`:

**LangGraph API Key:**
- Type: HTTP Header Auth
- Name: `X-API-Key`
- Value: Your LangGraph API key

**OpenAI API:**
- Type: OpenAI
- API Key: Your OpenAI key

**Database (Optional):**
- Type: PostgreSQL
- Host: `postgres.rag7.svc.cluster.local` (or external host)
- Port: `5432`
- Database: `langgraph_checkpoints`
- User: `langgraph`
- Password: Your database password

### 3. Import Workflows

1. Navigate to **Workflows** → **Add Workflow**
2. Click the **⋮** menu → **Import from File**
3. Import each workflow:
   - `workflows/main_orchestrator.json`
   - `workflows/langgraph_trigger.json`

### 4. Configure Environment Variables

In n8n, set environment variables for each workflow:

```bash
LANGGRAPH_API_URL=http://langgraph.rag7.svc.cluster.local:8123
TASK_QUEUE_URL=http://task-queue:8080
LOGGING_ENDPOINT=http://logging-service:8080
METRICS_ENDPOINT=http://metrics-service:9090
```

Or set them in your n8n deployment:

```yaml
environment:
  - LANGGRAPH_API_URL=http://langgraph.rag7.svc.cluster.local:8123
  - TASK_QUEUE_URL=http://task-queue:8080
```

## Workflows

### 1. Main Orchestrator

**File**: `workflows/main_orchestrator.json`

**Purpose**: Webhook-based orchestration for real-time LangGraph execution.

**Trigger**: Webhook (POST request)

**Flow**:
1. Receives webhook request
2. Validates input
3. Triggers LangGraph execution
4. Processes result
5. Returns response
6. Logs execution

**Webhook URL**: `https://your-n8n-instance/webhook/orchestrator`

**Example Request**:

```bash
curl -X POST https://your-n8n-instance/webhook/orchestrator \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the capital of France?",
    "user_id": "user123",
    "session_id": "session456",
    "metadata": {
      "source": "web"
    }
  }'
```

**Response**:

```json
{
  "status": "success",
  "result": {
    "answer": "The capital of France is Paris.",
    "confidence": 0.95
  },
  "execution_id": "exec_789",
  "duration_ms": 1234,
  "metadata": {
    "user_id": "user123",
    "session_id": "session456",
    "timestamp": "2024-01-15T10:30:45.123Z"
  }
}
```

### 2. LangGraph Trigger

**File**: `workflows/langgraph_trigger.json`

**Purpose**: Scheduled batch processing of pending tasks.

**Trigger**: Schedule (every 5 minutes by default)

**Flow**:
1. Fetches pending tasks from queue
2. Checks if tasks exist
3. Splits tasks for parallel processing
4. Executes each task via LangGraph
5. Marks tasks as complete
6. Sends metrics

**Configuration**:

Adjust schedule in the workflow:
- Every 5 minutes: `*/5 * * * *`
- Every hour: `0 * * * *`
- Every day at 2 AM: `0 2 * * *`

## Configuration

### Workflow Settings

**Timeout**:
- Default: 60 seconds
- For long-running graphs: Increase to 120-300 seconds

**Retry Logic**:
- Configure in each HTTP Request node
- Recommended: 3 retries with exponential backoff

**Batching**:
- Enable for high-volume processing
- Batch size: 5-10 requests
- Batch interval: 1-2 seconds

### Error Handling

All workflows include error handling:

1. **Validation Errors**: Return 400 with error details
2. **API Errors**: Retry with exponential backoff
3. **Timeout Errors**: Return 504 Gateway Timeout
4. **Server Errors**: Return 500 with error message

### Monitoring

Enable execution logging:

1. Navigate to **Settings** → **Executions**
2. Enable **Save execution data**
3. Set retention: 30 days (or as needed)

## Usage

### Activate Workflows

1. Open workflow in n8n
2. Click **Active** toggle
3. Verify webhook URL or schedule

### Test Workflows

**Manual Test**:
1. Open workflow
2. Click **Execute Workflow**
3. Provide test data
4. Review execution results

**Webhook Test**:

```bash
# Test main orchestrator
curl -X POST https://your-n8n-instance/webhook/orchestrator \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Test query",
    "user_id": "test_user"
  }'
```

### Monitor Executions

1. Navigate to **Executions**
2. View execution list
3. Click execution to see details
4. Check logs for errors

### Update Workflows

1. Deactivate workflow
2. Make changes
3. Test changes
4. Activate workflow

## Troubleshooting

### Webhook Not Receiving Requests

**Check**:
- Webhook URL is correct
- Workflow is active
- n8n is publicly accessible (or within VPN)
- Firewall allows traffic on port 5678

**Solution**:
```bash
# Test webhook locally
curl http://localhost:5678/webhook-test/orchestrator
```

### Authentication Errors

**Check**:
- Credentials are configured correctly
- API keys are valid
- Headers are set properly

**Solution**:
```bash
# Test API key manually
curl -H "X-API-Key: YOUR_KEY" http://langgraph:8123/health
```

### Timeout Errors

**Check**:
- Graph execution time
- Network latency
- Timeout settings in HTTP Request nodes

**Solution**:
- Increase timeout in node settings
- Optimize graph performance
- Use async processing

### Connection Errors

**Check**:
- Service is running
- Network connectivity
- DNS resolution

**Solution**:
```bash
# Test connectivity
kubectl run -it --rm debug --image=curlimages/curl --restart=Never \
  -- curl http://langgraph.rag7.svc.cluster.local:8123/health
```

### Memory/Performance Issues

**Check**:
- Execution data size
- Batch sizes
- Concurrent executions

**Solution**:
- Reduce batch size
- Limit concurrent executions
- Archive old execution data

## Advanced Usage

### Custom Workflows

Create custom workflows by:

1. Combining existing nodes
2. Adding custom code nodes
3. Integrating external services

### Integrations

Connect with:
- **Slack**: Send notifications
- **Email**: Send reports
- **Webhooks**: Trigger external systems
- **Databases**: Store results
- **Cloud Storage**: Save artifacts

### Example: Slack Notification

Add a Slack node after successful execution:

```json
{
  "parameters": {
    "channel": "#notifications",
    "text": "Graph execution completed: {{ $json.execution_id }}"
  },
  "type": "n8n-nodes-base.slack"
}
```

## Best Practices

1. **Use Descriptive Names**: Name workflows and nodes clearly
2. **Add Error Handling**: Always handle errors gracefully
3. **Enable Logging**: Keep execution logs for debugging
4. **Set Timeouts**: Prevent workflows from hanging
5. **Use Credentials**: Never hardcode API keys
6. **Test Thoroughly**: Test workflows before activating
7. **Monitor Executions**: Regularly check for failures
8. **Document Changes**: Keep notes on workflow modifications

## Next Steps

- Configure additional integrations
- Set up monitoring and alerting
- Create custom workflows for your use case
- Optimize performance and resource usage
- Review [Deployment Guide](../docs/deployment.md)
- Check [Observability Guide](../docs/observability.md)

## Support

For issues or questions:
- Check n8n documentation: https://docs.n8n.io
- Join n8n community: https://community.n8n.io
- Review LangGraph documentation
- Contact team via Slack #rag7-support
