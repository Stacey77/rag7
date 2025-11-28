# n8n Workflow Templates

Pre-built workflow templates for the Ragamuffin platform.

## Available Workflows

### 1. Document Ingestion Pipeline
**File:** `document-ingestion.json`

Automated pipeline for ingesting documents into the RAG system:
- Webhook trigger for document uploads
- Text extraction
- Embedding generation
- Optional Slack notification

### 2. Scheduled Embeddings Update
**File:** `scheduled-embeddings.json`

Periodic batch embedding generation:
- Runs every 6 hours (configurable)
- Lists all documents
- Batch processing with 10 documents at a time
- Generates embeddings for new content

### 3. RAG Query Pipeline
**File:** `rag-query-pipeline.json`

Complete RAG query workflow:
- Webhook trigger for queries
- Query preprocessing
- Vector search
- Response generation
- Formatted output

## How to Import

1. Open n8n at http://localhost:5678
2. Login with admin/admin (default)
3. Go to Workflows > Import from File
4. Select the JSON file
5. Configure any credentials (Slack, etc.)
6. Activate the workflow

## Customization

### Changing the Schedule
Edit the `Schedule Trigger` node in `scheduled-embeddings.json`:
```json
"interval": [
  {
    "field": "hours",
    "hoursInterval": 6  // Change this value
  }
]
```

### Adding Notifications
Enable the Slack notification node:
1. Import the workflow
2. Click on the `Notify Slack` node
3. Click the toggle to enable it
4. Configure your Slack credentials

### Changing Endpoints
Update the HTTP Request nodes with your backend URLs:
- Backend: `http://backend:8000` (Docker) or `http://localhost:8000` (local)
- RAG Service: `http://rag-service:8001` (Docker) or `http://localhost:8001` (local)

## Creating Custom Workflows

Use these templates as a starting point:

1. **Webhook Trigger** - For external integrations
2. **Schedule Trigger** - For periodic tasks
3. **HTTP Request** - To call RAG APIs
4. **Code** - For data transformation
5. **Set** - For simple data manipulation

## API Endpoints Reference

### Backend (port 8000)
- `POST /rag/embed` - Embed text
- `POST /rag/search` - Search vectors
- `POST /rag/query` - RAG query
- `GET /list_flows/` - List flows

### RAG Service (port 8001)
- `POST /embed/text` - Generate text embeddings
- `POST /embed/image` - Generate image embeddings
- `POST /search/text` - Search similar text
- `GET /collections` - List collections
