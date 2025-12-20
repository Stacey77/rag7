# LangFlow Backend

FastAPI backend service for managing and executing LangFlow flows.

## Overview

This service provides a RESTful API for:
- Saving LangFlow flow definitions
- Listing all saved flows
- Retrieving specific flows
- Executing flows with user input

## API Endpoints

### `POST /save_flow/`
Save a LangFlow flow definition.

**Parameters:**
- `flow_name` (form): Name for the flow
- `flow_json` (file): JSON file containing flow definition

**Example:**
```bash
curl -X POST "http://localhost:8000/save_flow/" \
  -F "flow_name=my_flow" \
  -F "flow_json=@flow.json"
```

### `GET /list_flows/`
List all saved flows with metadata.

**Example:**
```bash
curl "http://localhost:8000/list_flows/"
```

### `GET /get_flow/{flow_name}`
Retrieve a specific flow definition.

**Example:**
```bash
curl "http://localhost:8000/get_flow/my_flow.json"
```

### `POST /run_flow/`
Execute a flow with user input.

**Parameters:**
- `flow_name` (form): Name of the flow to execute
- `user_input` (form): Input text for the flow
- `flow_json` (file, optional): Flow JSON (uses saved flow if not provided)

**Example:**
```bash
curl -X POST "http://localhost:8000/run_flow/" \
  -F "flow_name=my_flow" \
  -F "user_input=Hello, world!"
```

### `GET /health`
Health check endpoint.

### `GET /docs`
Interactive API documentation (Swagger UI).

## Environment

### Docker
The service runs in a Docker container with:
- Python 3.11
- FastAPI + Uvicorn
- LangFlow (if available)
- Volume mount for flow persistence

### Environment Variables
- `PYTHONUNBUFFERED=1`: Disable Python output buffering

## Data Persistence

Flows are persisted to `/app/flows` in the container, which is mounted to `./langflow-backend/flows` on the host.

```
./langflow-backend/flows/
├── my_flow.json
├── another_flow.json
└── ...
```

## Development

### Local Development (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Development

```bash
# Rebuild and restart
docker compose build backend
docker compose up -d backend

# View logs
docker compose logs -f backend

# Access container shell
docker compose exec backend /bin/bash
```

### Testing Endpoints

```bash
# Health check
curl http://localhost:8000/health

# List flows
curl http://localhost:8000/list_flows/

# Create a test flow
echo '{"nodes": [], "edges": []}' > test_flow.json
curl -X POST "http://localhost:8000/save_flow/" \
  -F "flow_name=test_flow" \
  -F "flow_json=@test_flow.json"

# Get flow
curl http://localhost:8000/get_flow/test_flow.json

# Run flow (simulated if langflow not available)
curl -X POST "http://localhost:8000/run_flow/" \
  -F "flow_name=test_flow" \
  -F "user_input=Test input"
```

## CORS Configuration

**Development Mode:**
The service allows CORS from:
- http://localhost:8080 (frontend)
- http://localhost:3000 (alternative dev port)
- http://localhost:5173 (Vite default)

**Production:**
Update `app/main.py` to restrict origins:
```python
allow_origins=[
    "https://your-production-domain.com",
]
```

## Security Considerations

### Before Production Deployment

1. **CORS**: Restrict to specific production domains
2. **Authentication**: Add API key or OAuth authentication
3. **Validation**: Implement strict flow JSON schema validation
4. **Rate Limiting**: Add rate limiting to prevent abuse
5. **Input Sanitization**: Validate and sanitize all user inputs
6. **Timeouts**: Add execution timeouts for flow runs
7. **Logging**: Implement comprehensive logging and monitoring
8. **File Uploads**: Enforce size limits and file type validation

### Current Safeguards

- Flow name validation (prevents directory traversal)
- JSON validation before saving
- Error handling and logging
- Flow execution in try-catch blocks

## Simulation Mode

If the `langflow` module cannot be imported, the API runs in simulation mode:
- All endpoints remain functional
- `/run_flow/` returns simulated responses
- Warning logged on startup
- `langflow_available` field in responses indicates mode

This allows the service to run and be tested even if LangFlow is not fully configured.

## Troubleshooting

### Import Error: langflow
The service will run in simulation mode. To enable full functionality:
```bash
docker compose exec backend pip install langflow
docker compose restart backend
```

### Flows Not Persisting
Check volume mount:
```bash
docker volume inspect rag7_backend-flows
ls -la ./langflow-backend/flows/
```

### CORS Errors
Add your frontend origin to `allow_origins` in `app/main.py`.

### API Not Responding
Check logs:
```bash
docker compose logs backend
```

## Architecture

```
app/
├── __init__.py       # Package initialization
└── main.py           # FastAPI application with all endpoints

flows/                # Persisted flow definitions
├── flow1.json
└── flow2.json
```

## Dependencies

- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `langflow`: LangFlow runtime (optional)
- `python-multipart`: Form data handling
- `pydantic`: Data validation

## Future Enhancements

- Database integration for flow metadata
- User authentication and authorization
- Flow versioning
- Flow execution history
- Async flow execution with webhooks
- Flow templates library
- Metrics and analytics
