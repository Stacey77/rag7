# n8n Workflow Configuration

This directory contains n8n workflow configurations for visual orchestration of the LangGraph multi-agent system.

## Workflows

### 1. Main Orchestrator (`main_orchestrator.json`)
The primary workflow that routes tasks to appropriate LangGraph patterns based on the request.

**Features:**
- Webhook trigger for external integrations
- Switch/Router for pattern selection
- HTTP requests to LangGraph API
- Response aggregation

### 2. Parallel Processor (`parallel_processor.json`)
Handles parallel processing of multiple tasks simultaneously.

**Features:**
- Batch splitting for concurrent processing
- Result aggregation
- Progress tracking

### 3. Approval Workflow (`approval_workflow.json`)
Implements human-in-the-loop approval for content review.

**Features:**
- Draft generation via LangGraph
- Wait node for human approval
- Feedback-based revision loop
- Approval routing

### 4. Data Pipeline (`data_pipeline.json`)
Processes and analyzes incoming data through the router pattern.

**Features:**
- Data validation and transformation
- Smart routing to appropriate handlers
- Result post-processing

### 5. LangGraph Trigger (`langgraph_trigger.json`)
Generic webhook trigger for any LangGraph pattern.

**Features:**
- Request validation
- Pattern selection
- Configurable quality thresholds

## Setup Instructions

### Prerequisites
- n8n >= 1.0.0
- Docker & Docker Compose
- LangGraph API running on `langgraph-api:8000`

### Importing Workflows

1. **Via n8n UI:**
   - Open n8n dashboard
   - Go to Workflows → Import from File
   - Select the JSON file to import

2. **Via n8n CLI:**
   ```bash
   n8n import:workflow --input=n8n/workflows/main_orchestrator.json
   ```

3. **Via Docker Compose:**
   The workflows are automatically available when using the provided `docker-compose.yml`.

### Configuration

1. **Update API URLs:**
   If not using Docker Compose, update the HTTP Request node URLs:
   ```
   http://langgraph-api:8000 → http://your-langgraph-host:port
   ```

2. **Set Credentials:**
   - Copy `credentials/credentials_template.json`
   - Update with your actual API credentials
   - Import into n8n via Settings → Credentials

### Webhook URLs

After importing, your webhook URLs will be:

| Workflow | Webhook Path | Full URL |
|----------|--------------|----------|
| Main Orchestrator | `/webhook/orchestrator` | `http://n8n-host:5678/webhook/orchestrator` |
| Parallel Processor | `/webhook/parallel-process` | `http://n8n-host:5678/webhook/parallel-process` |
| Approval Workflow | `/webhook/approval-request` | `http://n8n-host:5678/webhook/approval-request` |
| Data Pipeline | `/webhook/data-pipeline` | `http://n8n-host:5678/webhook/data-pipeline` |
| LangGraph Trigger | `/webhook/langgraph-trigger` | `http://n8n-host:5678/webhook/langgraph-trigger` |

## Usage Examples

### Main Orchestrator
```bash
curl -X POST http://localhost:5678/webhook/orchestrator \
  -H "Content-Type: application/json" \
  -d '{"task": "Write a blog post about AI", "pattern": "sequential"}'
```

### LangGraph Trigger
```bash
curl -X POST http://localhost:5678/webhook/langgraph-trigger \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Analyze market trends",
    "pattern": "router",
    "quality_threshold": 0.85
  }'
```

### Data Pipeline
```bash
curl -X POST http://localhost:5678/webhook/data-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "source": "user_feedback",
    "data": {"ratings": [4, 5, 3, 5, 4], "comments": ["Great!", "Good"]}
  }'
```

## Troubleshooting

### Common Issues

1. **Connection Refused:**
   - Ensure LangGraph API is running
   - Check network connectivity between n8n and LangGraph containers
   - Verify the API URL in HTTP Request nodes

2. **Timeout Errors:**
   - Increase timeout in HTTP Request node options
   - For complex patterns, timeout may need to be 120+ seconds

3. **Webhook Not Found:**
   - Ensure workflow is active (toggle on)
   - Check webhook path matches the request URL

### Logs

View n8n logs:
```bash
docker-compose logs -f n8n
```

View execution history in n8n UI:
- Go to Executions in the sidebar
- Filter by workflow name
