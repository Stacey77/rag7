# LangFlow Backend Service

FastAPI backend service for managing and executing LangFlow workflows in the Ragamuffin platform.

## Overview

This service provides a RESTful API for:
- Uploading and saving LangFlow workflow JSON files
- Listing available workflows
- Retrieving specific workflow definitions
- Executing workflows with user input

## Architecture

The backend acts as a bridge between the web frontend and LangFlow, providing:
- Flow persistence in the `/app/flows` directory (mounted volume)
- API endpoints for flow management
- Flow execution capabilities (when LangFlow is installed)
- CORS support for frontend integration

## API Endpoints

### `GET /`
Root endpoint with API information and available endpoints.

### `POST /save_flow/`
Upload and save a LangFlow workflow JSON file.

**Request:**
- Form data with `flow_file` (multipart/form-data)

**Response:**
```json
{
  "message": "Flow saved successfully",
  "flow_name": "my_flow.json",
  "path": "/app/flows/my_flow.json"
}
```

### `GET /list_flows/`
List all saved workflow files.

**Response:**
```json
{
  "flows": [
    {
      "name": "my_flow.json",
      "size": 1024,
      "modified": 1634567890.0
    }
  ],
  "count": 1
}
```

### `GET /get_flow/{flow_name}`
Retrieve a specific workflow by name.

**Response:**
```json
{
  "flow_name": "my_flow.json",
  "flow_data": { /* flow JSON */ }
}
```

### `POST /run_flow/`
Execute a workflow with user input.

**Request:**
- Form data with:
  - `flow_file`: Flow JSON file (multipart/form-data)
  - `user_input`: Text input for the flow (form field)

**Response:**
```json
{
  "status": "success",
  "output": "Flow execution result",
  "flow_name": "my_flow.json"
}
```

**Note:** If LangFlow is not installed, returns a simulated response with status "simulated".

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "langflow_available": true,
  "flows_directory": "/app/flows",
  "flows_count": 5
}
```

## Running the Backend

### With Docker Compose (Recommended)

From repository root:
```bash
docker compose up backend
```

### Standalone Docker

```bash
cd langflow-backend
docker build -t ragamuffin-backend .
docker run -p 8000:8000 -v $(pwd)/flows:/app/flows ragamuffin-backend
```

### Local Development

```bash
cd langflow-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Accessing the API

- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Environment Variables

Set in `docker-compose.yml` or `.env`:
- `LANGFLOW_HOST`: LangFlow service hostname (default: langflow)
- `LANGFLOW_PORT`: LangFlow service port (default: 7860)

## Flow Persistence

Flows are stored in the `flows/` directory, which is mounted as a Docker volume:
- Host: `./langflow-backend/flows`
- Container: `/app/flows`

This ensures flows persist across container restarts.

## Dependencies

See `requirements.txt`:
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **langflow**: LangFlow library (for flow execution)
- **python-multipart**: File upload support

## LangFlow Integration

The backend attempts to import LangFlow's `load_flow_from_json` function:
- **If available**: Real flow execution is enabled
- **If unavailable**: Returns simulated responses with warnings

This allows the backend to start even without LangFlow installed, useful for:
- Testing the API independently
- Development without full LangFlow setup
- Graceful degradation

## Security Considerations

⚠️ **CRITICAL - This is a development scaffold. Production deployment requires:**

### Authentication & Authorization
- [ ] Implement user authentication (JWT, OAuth, etc.)
- [ ] Add authorization for flow access
- [ ] Validate user permissions per endpoint

### Input Validation
- [ ] Comprehensive JSON schema validation for flows
- [ ] Input sanitization to prevent injection attacks
- [ ] File type and size validation (currently basic)
- [ ] Rate limiting per user/IP

### Flow Execution Security
- [ ] **Sandbox flow execution** (critical!)
- [ ] Timeout limits for long-running flows
- [ ] Resource limits (CPU, memory)
- [ ] Isolated execution environment
- [ ] Audit logging for all executions

### CORS Configuration
- [ ] Replace wildcard CORS with specific domains
- [ ] Configure for production frontend domain
- [ ] Remove localhost origins in production

### File Storage
- [ ] Use secure file storage with access controls
- [ ] Validate and sanitize filenames (basic implementation exists)
- [ ] Implement file encryption for sensitive flows
- [ ] Add virus scanning for uploaded files

### Additional Security
- [ ] HTTPS/TLS encryption
- [ ] Request size limits
- [ ] Error message sanitization (avoid exposing internals)
- [ ] Security headers (HSTS, CSP, etc.)
- [ ] Regular security audits
- [ ] Dependency vulnerability scanning

## Error Handling

The API returns standard HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid input)
- `404`: Resource not found
- `500`: Server error

Error responses include detail messages:
```json
{
  "detail": "Error description"
}
```

## Logging

Logs are written to stdout/stderr and include:
- Info: Successful operations
- Warning: Non-critical issues (e.g., LangFlow unavailable)
- Error: Failures and exceptions

View logs:
```bash
docker compose logs -f backend
```

## Testing the API

### Using curl

Save a flow:
```bash
curl -X POST "http://localhost:8000/save_flow/" \
  -F "flow_file=@my_flow.json"
```

List flows:
```bash
curl -X GET "http://localhost:8000/list_flows/"
```

Get a flow:
```bash
curl -X GET "http://localhost:8000/get_flow/my_flow.json"
```

Run a flow:
```bash
curl -X POST "http://localhost:8000/run_flow/" \
  -F "flow_file=@my_flow.json" \
  -F "user_input=Hello, how are you?"
```

### Using the Interactive Docs

Visit http://localhost:8000/docs for Swagger UI with:
- Interactive endpoint testing
- Request/response schemas
- Example requests

## Troubleshooting

### Backend Won't Start

Check logs:
```bash
docker compose logs backend
```

Common issues:
- Port 8000 already in use
- Missing dependencies in requirements.txt
- Volume mount permission issues

### Can't Save Flows

Ensure flows directory exists and has write permissions:
```bash
ls -la langflow-backend/flows/
chmod 777 langflow-backend/flows/  # Development only
```

### Flow Execution Fails

Check if LangFlow is available:
```bash
curl http://localhost:8000/health
```

If `langflow_available: false`, the backend will return simulated responses.

### CORS Errors

Update CORS origins in `app/main.py` to match your frontend URL.

## Development Tips

### Hot Reload

Run with auto-reload for development:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Changes to code will automatically restart the server.

### Debug Mode

Add debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### API Client Generation

Generate client code from OpenAPI schema:
```bash
# Install openapi-generator-cli
openapi-generator-cli generate -i http://localhost:8000/openapi.json -g python -o client/
```

## Production Deployment

For production:

1. **Use Production ASGI Server**: Gunicorn with Uvicorn workers
2. **Enable HTTPS**: Reverse proxy (nginx/traefik) with SSL
3. **Database**: Replace file storage with PostgreSQL/MongoDB
4. **Authentication**: Implement JWT or OAuth
5. **Monitoring**: Add APM (Prometheus, Grafana)
6. **Scaling**: Use load balancer for multiple instances
7. **Secrets**: Use environment variables or secret management

Example production command:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## Contributing

When adding new endpoints:
1. Add security validation
2. Include comprehensive error handling
3. Update this README
4. Add tests (if test framework exists)
5. Document in OpenAPI docstrings

## Support

- Check logs: `docker compose logs backend`
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs
- See [RUN_COMMANDS.md](../RUN_COMMANDS.md) for more help
