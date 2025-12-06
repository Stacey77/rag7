# n8n Workflows

This directory contains n8n workflow templates for orchestrating LangGraph API calls and automation.

## Overview

The workflows provide webhook-based triggers for executing LangGraph operations with n8n's powerful automation capabilities.

## Workflows

### 1. Main Orchestrator (`main_orchestrator.json`)

A comprehensive workflow that:
- Receives webhook POST requests
- Validates input parameters
- Calls the LangGraph API
- Formats and returns responses
- Handles errors gracefully

**Webhook URL**: `http://your-n8n-host:5678/webhook/langgraph-webhook`

**Usage**:
```bash
curl -X POST http://localhost:5678/webhook/langgraph-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "action": "run_graph",
    "input": {
      "query": "What is the weather today?",
      "context": {}
    },
    "config": {
      "recursion_limit": 50
    }
  }'
```

### 2. LangGraph Trigger (`langgraph_trigger.json`)

A simplified trigger workflow that:
- Accepts webhook requests with query parameters
- Extracts and processes input
- Makes direct LangGraph API calls
- Returns formatted responses

**Webhook URL**: `http://your-n8n-host:5678/webhook/langgraph-trigger`

**Usage**:
```bash
curl -X POST http://localhost:5678/webhook/langgraph-trigger \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Summarize this document",
    "session_id": "user-123"
  }'
```

## Setup Instructions

### 1. Start n8n

Using Docker Compose:
```bash
docker-compose -f docker-compose.prod.yml up -d n8n
```

Access n8n at: `http://localhost:5678`

### 2. Import Workflows

1. Log in to n8n
2. Click on "Workflows" in the left sidebar
3. Click "Import from File"
4. Select and import each workflow JSON file:
   - `main_orchestrator.json`
   - `langgraph_trigger.json`

### 3. Configure Credentials

#### Option A: Manual Configuration

1. Go to Settings > Credentials
2. Click "Add Credential"
3. Select "Header Auth"
4. Configure:
   - **Name**: LangGraph API Key
   - **Header Name**: `X-API-Key`
   - **Header Value**: Your LangGraph API key
5. Save

#### Option B: Import from Template

1. Copy `credentials_template.json` to `credentials.json`
2. Fill in actual credential values
3. Import via n8n UI
4. **IMPORTANT**: Do not commit `credentials.json` to git!

### 4. Configure Environment Variables

Set these in your n8n environment (via `.env.prod` or docker-compose.prod.yml):

```bash
LANGGRAPH_API_URL=http://langgraph:8000
N8N_WEBHOOK_URL=https://your-domain.com
```

### 5. Activate Workflows

1. Open each imported workflow
2. Click "Active" toggle in the top-right
3. Verify the webhook is listening

### 6. Test Workflows

Test the main orchestrator:
```bash
curl -X POST http://localhost:5678/webhook/langgraph-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "action": "test",
    "input": {
      "query": "Hello, world!"
    }
  }'
```

Expected response:
```json
{
  "status": "success",
  "result": {...},
  "execution_id": "..."
}
```

## Workflow Architecture

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│   Webhook   │────▶│  Validation  │────▶│  LangGraph    │
│   Trigger   │     │   & Logic    │     │  API Call     │
└─────────────┘     └──────────────┘     └───────────────┘
                                                  │
                                                  ▼
                                         ┌───────────────┐
                                         │   Format &    │
                                         │   Response    │
                                         └───────────────┘
```

## Customization

### Adding Custom Logic

Edit workflows to add:
- Additional validation rules
- Data transformations
- Multiple LangGraph calls
- Database operations
- Email/Slack notifications
- Error handling logic

### Example: Add Logging

Add a "Function" node before the LangGraph call:

```javascript
// Log incoming request
console.log('Request received:', {
  timestamp: new Date().toISOString(),
  input: $json.body.input
});

return $input.all();
```

### Example: Add Database Storage

Add a "Postgres" node after successful execution:

```sql
INSERT INTO execution_log (execution_id, input, output, timestamp)
VALUES ($1, $2, $3, NOW())
```

## Security

### Production Checklist

- [ ] Use HTTPS for webhook URLs
- [ ] Enable n8n authentication
- [ ] Rotate API keys regularly
- [ ] Use environment variables for secrets
- [ ] Enable webhook authentication
- [ ] Set up IP whitelisting if needed
- [ ] Monitor webhook access logs

### Webhook Authentication

Add authentication to webhook node:

1. Edit webhook node
2. Enable "Authentication"
3. Select "Header Auth"
4. Configure header name and expected value

Example with Bearer token:
```bash
curl -X POST http://localhost:5678/webhook/langgraph-webhook \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "test", "input": {...}}'
```

## Monitoring

### Check Workflow Executions

1. Go to "Executions" in n8n
2. Filter by workflow
3. View execution details and logs

### Common Issues

**Workflow not triggering**:
- Check if workflow is active
- Verify webhook URL is correct
- Check n8n logs: `docker logs rag7-n8n`

**API call failing**:
- Verify `LANGGRAPH_API_URL` environment variable
- Check credentials are configured correctly
- Test LangGraph API directly: `curl http://langgraph:8000/health`

**Timeout errors**:
- Increase timeout in HTTP Request node settings
- Default is 5 minutes; adjust as needed

## Advanced Features

### Scheduling

Convert webhook to cron trigger for scheduled executions:
1. Replace webhook with "Cron" node
2. Set schedule (e.g., "0 0 * * *" for daily)

### Error Handling

Add error workflow:
1. Create new workflow
2. Use "Error Trigger" node
3. Add notification/logging logic

### Multi-step Workflows

Chain multiple LangGraph calls:
1. First call generates prompt
2. Second call processes result
3. Third call validates output

## Support

- n8n Documentation: https://docs.n8n.io
- LangGraph API Docs: (link to your API docs)
- Report issues: [GitHub Issues](https://github.com/Stacey77/rag7/issues)

## Next Steps

1. Import workflows into n8n
2. Configure credentials
3. Test with sample requests
4. Customize for your use case
5. Set up monitoring and alerts
6. Document any custom workflows you create
