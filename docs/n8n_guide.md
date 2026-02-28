# n8n Workflow Guide

This guide explains how to use and customize the n8n workflows for orchestrating the LangGraph multi-agent system.

## Overview

n8n provides visual workflow automation that integrates with the LangGraph API. The pre-built workflows handle common use cases and can be customized for specific needs.

## Prerequisites

- n8n >= 1.0.0
- Docker & Docker Compose
- LangGraph API running

## Getting Started

### Starting n8n

Using Docker Compose:

```bash
docker-compose up -d n8n postgres
```

Access n8n at: `http://localhost:5678`

Default credentials (configurable in `.env`):
- Username: `admin`
- Password: `admin`

### Importing Workflows

1. Navigate to n8n dashboard
2. Click **Workflows** → **Import from File**
3. Select a workflow JSON file from `n8n/workflows/`
4. Activate the workflow with the toggle switch

## Available Workflows

### 1. Main Orchestrator

**File:** `main_orchestrator.json`

**Purpose:** Central routing hub for all LangGraph patterns.

**Webhook URL:** `POST /webhook/orchestrator`

**Request Body:**
```json
{
  "task": "Your task description",
  "pattern": "sequential|parallel|loop|router|aggregator|hierarchical|network",
  "quality_threshold": 0.8,
  "max_iterations": 5
}
```

**Example:**
```bash
curl -X POST http://localhost:5678/webhook/orchestrator \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Write a blog post about cloud computing",
    "pattern": "sequential"
  }'
```

### 2. Parallel Processor

**File:** `parallel_processor.json`

**Purpose:** Process multiple tasks simultaneously.

**Webhook URL:** `POST /webhook/parallel-process`

**Request Body:**
```json
{
  "tasks": [
    {"task": "Analyze topic A"},
    {"task": "Analyze topic B"},
    {"task": "Analyze topic C"}
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:5678/webhook/parallel-process \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {"task": "Research AI trends"},
      {"task": "Research cloud trends"},
      {"task": "Research security trends"}
    ]
  }'
```

### 3. Approval Workflow

**File:** `approval_workflow.json`

**Purpose:** Human-in-the-loop content approval.

**Webhook URL:** `POST /webhook/approval-request`

**Flow:**
1. Submit task via webhook
2. LangGraph generates draft
3. Human reviews via form
4. If approved → finalize
5. If rejected → revise with feedback

**Request Body:**
```json
{
  "task": "Create marketing content for product launch"
}
```

### 4. Data Pipeline

**File:** `data_pipeline.json`

**Purpose:** Ingest and process data through smart routing.

**Webhook URL:** `POST /webhook/data-pipeline`

**Request Body:**
```json
{
  "source": "user_feedback",
  "data": {
    "ratings": [4, 5, 3, 5, 4],
    "comments": ["Great product!", "Could be better"]
  }
}
```

### 5. LangGraph Trigger

**File:** `langgraph_trigger.json`

**Purpose:** Generic trigger for any LangGraph pattern.

**Webhook URL:** `POST /webhook/langgraph-trigger`

**Request Body:**
```json
{
  "task": "Your task",
  "pattern": "sequential",
  "quality_threshold": 0.8,
  "max_iterations": 5,
  "metadata": {}
}
```

## Customizing Workflows

### Modifying API URLs

If LangGraph is not running in Docker:

1. Open the workflow in n8n editor
2. Find HTTP Request nodes
3. Change URL from `http://langgraph-api:8000` to your API URL
4. Save the workflow

### Adding Custom Nodes

Common customizations:

**Add Logging:**
```javascript
// In a Code node
console.log('Processing:', $json.task);
return items;
```

**Add Error Handling:**
```javascript
// In a Code node after HTTP Request
if (!$json.success) {
  throw new Error($json.message || 'Processing failed');
}
return items;
```

**Add Retry Logic:**
- Use the Retry option in HTTP Request nodes
- Set retry count and delay

### Creating New Workflows

1. Create new workflow in n8n
2. Add a Webhook trigger node
3. Add HTTP Request nodes to call LangGraph API
4. Add processing logic with Code nodes
5. Add Respond to Webhook node for output

## Node Types Reference

### Webhook (Trigger)
- Receives external HTTP requests
- Configure method, path, and response mode

### HTTP Request
- Calls LangGraph API endpoints
- Supports all HTTP methods
- JSON body for task data

### Switch
- Routes based on conditions
- Use for pattern selection

### Wait
- Pauses execution for human input
- Form submission or external webhook

### Code
- Custom JavaScript logic
- Data transformation and validation

### Merge
- Combines outputs from multiple branches
- Various merge modes available

### Respond to Webhook
- Returns response to the trigger webhook
- JSON or custom response

## Webhook Configuration

### Setting Up Webhooks

1. **Determine Webhook URL:**
   - Production: `https://your-n8n-domain.com/webhook/path`
   - Local: `http://localhost:5678/webhook/path`

2. **Configure Webhook Node:**
   - Method: Usually POST
   - Path: Unique identifier (e.g., `my-workflow`)
   - Response Mode: `responseNode` to use Respond node

3. **Test Webhook:**
   ```bash
   curl -X POST http://localhost:5678/webhook/test \
     -H "Content-Type: application/json" \
     -d '{"test": "data"}'
   ```

### Webhook Security

1. **Authentication:**
   - Use Header Auth for API key validation
   - Add an IF node to check authentication

2. **Rate Limiting:**
   - Use n8n's built-in throttling
   - Add custom rate limit logic in Code node

## Error Handling

### HTTP Request Errors

```javascript
// Error handling in Code node
try {
  const result = $json;
  if (result.error) {
    return [{
      json: {
        success: false,
        error: result.error.message
      }
    }];
  }
  return items;
} catch (e) {
  return [{
    json: {
      success: false,
      error: e.message
    }
  }];
}
```

### Workflow-Level Error Handling

1. Enable "Error Workflow" in workflow settings
2. Create an error workflow that:
   - Logs the error
   - Sends notification
   - Attempts recovery

## Best Practices

1. **Use Descriptive Names**
   - Name nodes clearly (e.g., "Process Research Task")
   - Add notes to complex nodes

2. **Organize Workflow Layout**
   - Keep flows left-to-right
   - Group related nodes together
   - Use sticky notes for documentation

3. **Test Incrementally**
   - Use "Execute Node" to test individual nodes
   - Check data at each step

4. **Handle All Paths**
   - Account for success and failure cases
   - Provide meaningful error messages

5. **Secure Sensitive Data**
   - Use n8n credentials for API keys
   - Don't hardcode secrets in workflows

## Troubleshooting

### Common Issues

1. **Webhook Not Found (404)**
   - Ensure workflow is activated
   - Check webhook path spelling
   - Verify n8n is running

2. **Connection Refused**
   - Check LangGraph API is running
   - Verify network connectivity
   - Check firewall settings

3. **Timeout Errors**
   - Increase timeout in HTTP Request options
   - Check LangGraph processing time
   - Consider async processing

### Debugging

1. **Enable Debug Mode:**
   - Open workflow settings
   - Enable "Save Execution Progress"

2. **Check Execution History:**
   - Go to Executions tab
   - Click on failed execution
   - Inspect node outputs

3. **View Logs:**
   ```bash
   docker-compose logs -f n8n
   ```

## Integration Examples

### Slack Integration

```javascript
// Send result to Slack
// Add Slack node after LangGraph processing
{
  "channel": "#ai-results",
  "text": `Task completed: ${$json.task}\nQuality: ${$json.quality_score}\nOutput: ${$json.final_output.substring(0, 500)}...`
}
```

### Email Notification

```javascript
// Send email with results
// Add Send Email node
{
  "to": "team@example.com",
  "subject": `AI Task Completed: ${$json.task}`,
  "text": $json.final_output
}
```

### Database Storage

```javascript
// Store results in database
// Add database node (PostgreSQL, MySQL, etc.)
{
  "task": $json.task,
  "result": $json.final_output,
  "quality": $json.quality_score,
  "created_at": new Date().toISOString()
}
```
