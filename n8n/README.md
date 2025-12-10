# n8n Workflows

This directory contains n8n workflow templates for integrating with the RAG7 LangGraph API.

## Workflows

### 1. Main Orchestrator (`main_orchestrator.json`)

Coordinates between n8n automation and LangGraph execution.

**Trigger**: Webhook at `/webhook/langgraph`

**Flow**:
1. Receives POST request with workflow data
2. Pre-processes and validates input
3. Calls LangGraph API to execute graph
4. Post-processes results
5. Returns response via webhook

**Usage**:
```bash
curl -X POST http://localhost:5678/webhook/langgraph \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "main_graph",
    "input": {
      "query": "What is the weather?",
      "user_id": "user_123"
    }
  }'
```

### 2. LangGraph Trigger (`langgraph_trigger.json`)

Scheduled workflow that triggers LangGraph executions at regular intervals.

**Trigger**: Schedule (every 5 minutes by default)

**Flow**:
1. Scheduled trigger fires
2. Prepares execution request
3. Calls LangGraph API (async mode)
4. Logs execution status
5. Separate webhook handles callbacks

**Callback Webhook**: `/webhook/langgraph-callback`

## Setup Instructions

### 1. Import Workflows

1. Open n8n UI (default: http://localhost:5678)
2. Navigate to "Workflows"
3. Click "Import from File"
4. Select each JSON file and import

### 2. Configure Credentials

1. In n8n, go to "Credentials"
2. Click "Add Credential"
3. Select "HTTP Header Auth"
4. Enter:
   - **Name**: RAG7 API
   - **Header Name**: Authorization
   - **Header Value**: Bearer YOUR_API_KEY_HERE
5. Save credential

Alternatively, import from `credentials_template.json` and update the API key.

### 3. Update Workflow Settings

Edit each workflow to update:

- **API URL**: Update `http://langgraph-api:8000` to your actual API endpoint
- **Callback URL**: Update callback URLs to match your n8n instance
- **Schedule**: Adjust trigger schedule as needed

### 4. Activate Workflows

1. Open each workflow
2. Click "Active" toggle in top right
3. Verify webhook URLs are accessible

## Testing Workflows

### Test Main Orchestrator

```bash
# Test webhook
curl -X POST http://localhost:5678/webhook/langgraph \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "test_graph",
    "input": {"test": true}
  }'
```

### Test LangGraph Trigger

1. Open workflow in n8n UI
2. Click "Execute Workflow" manually
3. Check execution log for results

### Monitor Executions

1. Navigate to "Executions" in n8n
2. View execution history and logs
3. Debug any failed executions

## Customization

### Adding Error Handling

Add "Error Trigger" node to handle errors:

```javascript
// Error handling function
const error = $input.first().json;

// Log error
console.error('Workflow error:', error);

// Send alert (e.g., to Slack, email)
return {
  json: {
    error: true,
    message: error.message,
    timestamp: new Date().toISOString()
  }
};
```

### Adding Retry Logic

Configure HTTP Request node:
- Options → Retry On Fail: Enabled
- Max Tries: 3
- Wait Between Tries: 1000ms

### Adding Data Transformation

Use Function node for custom transformations:

```javascript
// Transform data
const input = $input.first().json;

const transformed = {
  ...input,
  processed: true,
  timestamp: new Date().toISOString(),
  // Add custom transformations
};

return { json: transformed };
```

## Best Practices

1. **Always validate input** before calling external APIs
2. **Use error handling** to catch and log failures
3. **Set appropriate timeouts** for API calls
4. **Test in staging** before deploying to production
5. **Monitor executions** regularly
6. **Keep credentials secure** (use n8n's credential store)
7. **Document custom workflows** for team reference
8. **Version control** workflow exports

## Troubleshooting

### Workflow Not Triggering

- Verify webhook is active
- Check webhook URL is accessible
- Review n8n logs: `docker logs n8n`

### API Call Failing

- Verify API endpoint is reachable
- Check credentials are configured correctly
- Review API logs for errors
- Test API endpoint directly with curl

### Callback Not Received

- Verify callback URL is accessible from API
- Check firewall/network rules
- Use ngrok for local testing

## Integration Examples

### Connect to Database

Add PostgreSQL node to store results:

```javascript
// Store in database
INSERT INTO executions (
  execution_id,
  status,
  result,
  created_at
) VALUES (
  '{{ $json.execution_id }}',
  '{{ $json.status }}',
  '{{ $json.output }}',
  NOW()
)
```

### Send Slack Notification

Add Slack node for notifications:

```javascript
// Slack message
{
  "text": "LangGraph execution completed",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Status*: {{ $json.status }}\n*Execution ID*: {{ $json.execution_id }}"
      }
    }
  ]
}
```

### Chain Multiple Workflows

Use "Execute Workflow" node to chain workflows:

1. Main workflow completes
2. Triggers sub-workflow
3. Sub-workflow processes results
4. Returns to main workflow

## Resources

- [n8n Documentation](https://docs.n8n.io)
- [n8n Workflow Templates](https://n8n.io/workflows)
- [Integration Guide](../docs/integrations.md)

## Support

For issues with n8n workflows:
1. Check n8n execution logs
2. Review API logs for errors
3. Test components individually
4. Consult n8n documentation
5. Contact team for support
