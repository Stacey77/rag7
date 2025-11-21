# Ragamuffin Backend

FastAPI backend for the Ragamuffin AI agent platform. Provides flow management and execution endpoints.

## Overview

The backend serves as the API layer between the React frontend and LangFlow. It handles:

- **Flow Storage**: Save and retrieve agent flows as JSON
- **Flow Execution**: Run flows with user input
- **Flow Management**: List and delete saved flows

## API Endpoints

### Health Check

```http
GET /
```

Returns service status.

### Save Flow

```http
POST /save_flow/
Content-Type: multipart/form-data

file: <flow.json>
```

Save a flow JSON file to the flows directory.

**Security Notes:**
- Only accepts `.json` files
- Validates JSON structure
- Sanitizes filenames to prevent path traversal

### List Flows

```http
GET /list_flows/
```

Returns list of all saved flow files.

**Response:**
```json
{
  "status": "success",
  "flows": ["flow1.json", "flow2.json"],
  "count": 2
}
```

### Get Flow

```http
GET /get_flow/{flow_name}
```

Retrieve specific flow content by name.

**Response:**
```json
{
  "status": "success",
  "flow_name": "my-flow.json",
  "flow_data": { ... }
}
```

### Run Flow

```http
POST /run_flow/
Content-Type: multipart/form-data

flow_file: <flow.json>
user_input: "Your prompt here"
```

Execute a flow with user input.

**Behavior:**
- If LangFlow is installed: Executes the actual flow
- If LangFlow is not installed: Returns simulated response with warning

**Response (Real Execution):**
```json
{
  "status": "success",
  "result": "Flow output...",
  "flow_name": "my-flow.json",
  "user_input": "Your prompt here",
  "execution_mode": "langflow"
}
```

**Response (Simulated):**
```json
{
  "status": "success",
  "result": "[SIMULATED] Processed input...",
  "flow_name": "my-flow.json",
  "user_input": "Your prompt here",
  "execution_mode": "simulated",
  "note": "LangFlow not installed..."
}
```

### Delete Flow

```http
DELETE /delete_flow/{flow_name}
```

Delete a specific flow file.

## Environment

### Required Variables

None required for basic operation.

### Optional Variables

- `LANGFLOW_URL`: URL of LangFlow service (default: `http://langflow:7860`)
- `LOG_LEVEL`: Logging level (default: `info`)

## Running Locally

### Prerequisites

```bash
cd langflow-backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access API documentation at: http://localhost:8000/docs

## Running with Docker

### Build Image

```bash
docker build -t ragamuffin-backend .
```

### Run Container

```bash
docker run -p 8000:8000 \
  -v $(pwd)/flows:/app/flows \
  ragamuffin-backend
```

## Flow Persistence

Flows are stored in the `./flows/` directory, which is mounted as a Docker volume in the compose setup. This ensures flows persist across container restarts.

**Directory Structure:**
```
langflow-backend/
├── flows/              # Flow JSON files stored here
│   ├── flow1.json
│   └── flow2.json
├── app/
│   ├── __init__.py
│   └── main.py
├── Dockerfile
└── requirements.txt
```

## Security Considerations

⚠️ **CRITICAL: This backend is for development only!**

### Before Production Deployment:

1. **Authentication & Authorization**
   ```python
   # Add JWT or OAuth2 authentication
   from fastapi.security import HTTPBearer
   security = HTTPBearer()
   
   @app.post("/save_flow/")
   async def save_flow(
       file: UploadFile,
       token: str = Depends(security)
   ):
       # Verify token
       # ...
   ```

2. **Flow Validation**
   ```python
   # Validate flow structure
   def validate_flow(flow_data: dict) -> bool:
       required_fields = ["nodes", "edges"]
       if not all(field in flow_data for field in required_fields):
           raise ValueError("Invalid flow structure")
       # Add more validation...
       return True
   ```

3. **Sandboxed Execution**
   ```python
   # Use containers or VMs for flow execution
   # Set resource limits
   import resource
   resource.setrlimit(resource.RLIMIT_CPU, (10, 10))  # 10 seconds
   resource.setrlimit(resource.RLIMIT_AS, (512*1024*1024, 512*1024*1024))  # 512MB
   ```

4. **Tool Restrictions**
   ```python
   # Whitelist allowed tools/modules
   ALLOWED_TOOLS = ["llm", "prompt", "parser"]
   
   def validate_tools(flow_data: dict) -> bool:
       for node in flow_data.get("nodes", []):
           if node["type"] not in ALLOWED_TOOLS:
               raise ValueError(f"Tool {node['type']} not allowed")
       return True
   ```

5. **Rate Limiting**
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   
   @app.post("/run_flow/")
   @limiter.limit("5/minute")
   async def run_flow(...):
       # ...
   ```

6. **CORS Configuration**
   ```python
   # Replace permissive CORS with specific origins
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "https://yourdomain.com",
       ],
       allow_credentials=True,
       allow_methods=["GET", "POST"],
       allow_headers=["*"],
   )
   ```

7. **Input Validation**
   ```python
   from pydantic import BaseModel, validator
   
   class FlowInput(BaseModel):
       user_input: str
       
       @validator("user_input")
       def validate_input(cls, v):
           if len(v) > 1000:
               raise ValueError("Input too long")
           return v
   ```

8. **Logging & Monitoring**
   ```python
   # Add comprehensive logging
   import logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler("app.log"),
           logging.StreamHandler()
       ]
   )
   
   # Log all flow executions
   logger.info(f"Flow executed: {flow_name} by user {user_id}")
   ```

## Testing

### Manual API Testing

```bash
# Save a flow
curl -X POST http://localhost:8000/save_flow/ \
  -F "file=@test-flow.json"

# List flows
curl http://localhost:8000/list_flows/

# Get flow
curl http://localhost:8000/get_flow/test-flow.json

# Run flow
curl -X POST http://localhost:8000/run_flow/ \
  -F "flow_file=@test-flow.json" \
  -F "user_input=Hello, world!"

# Delete flow
curl -X DELETE http://localhost:8000/delete_flow/test-flow.json
```

### Automated Tests

Create `tests/test_api.py`:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_list_flows():
    response = client.get("/list_flows/")
    assert response.status_code == 200
    assert "flows" in response.json()
```

Run tests:
```bash
pip install pytest
pytest tests/
```

## Dependencies

- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **python-multipart**: File upload support
- **langflow**: Optional, for real flow execution

See `requirements.txt` for specific versions.

## Troubleshooting

### LangFlow Not Found

If you see "LangFlow not available" warnings:

1. LangFlow is optional for testing the API
2. To enable real execution: `pip install langflow`
3. The backend will return simulated responses without LangFlow

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Flow Execution Errors

Check logs:
```bash
docker-compose logs backend
```

Common issues:
- Invalid flow JSON structure
- Missing LangFlow dependencies
- Insufficient permissions for flows directory

### CORS Errors

If frontend can't connect:
1. Verify backend is running: `curl http://localhost:8000`
2. Check CORS settings in `app/main.py`
3. Ensure frontend URL is in `allow_origins` list

## Development Tips

### Hot Reload

When running locally with `--reload`, the server automatically restarts on code changes.

### API Documentation

FastAPI auto-generates interactive docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Debugging

Add breakpoints in `main.py`:
```python
import pdb; pdb.set_trace()
```

Or use VS Code debugger with `launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "jinja": true
    }
  ]
}
```

## Production Checklist

Before deploying to production:

- [ ] Add authentication/authorization
- [ ] Implement flow validation
- [ ] Sandbox flow execution
- [ ] Configure secure CORS
- [ ] Add rate limiting
- [ ] Set up monitoring/logging
- [ ] Use secrets management
- [ ] Enable HTTPS
- [ ] Set up backup for flows directory
- [ ] Implement error tracking (Sentry, etc.)
- [ ] Add health check endpoint with dependencies
- [ ] Configure proper logging levels
- [ ] Set up CI/CD pipeline
- [ ] Add automated tests
- [ ] Document API properly
- [ ] Review security with team

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [LangFlow Documentation](https://docs.langflow.org/)
- [API Security Best Practices](https://owasp.org/www-project-api-security/)

---

For issues or questions, refer to the main [README](../README.md).
