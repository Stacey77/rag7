# Ragamuffin Backend

FastAPI backend service for managing and executing LangFlow flows.

## Overview

The backend provides a REST API for:
- Saving flow definitions
- Listing available flows
- Retrieving flow definitions
- Executing flows with user input

## API Endpoints

### Health Check

```
GET /
GET /health
```

Returns service status and health information.

### Flow Management

#### Save Flow
```
POST /save_flow/
Content-Type: multipart/form-data

Body:
  flow_file: (JSON file)
```

Saves a flow definition to the flows directory.

#### List Flows
```
GET /list_flows/
```

Returns a list of all saved flows with metadata.

#### Get Flow
```
GET /get_flow/{flow_name}
```

Retrieves a specific flow definition.

#### Delete Flow
```
DELETE /delete_flow/{flow_name}
```

Deletes a flow (development only - requires auth in production).

### Flow Execution

#### Run Flow
```
POST /run_flow/
Content-Type: multipart/form-data

Body:
  flow_file: (JSON file)
  user_input: (string)
```

Executes a flow with the provided user input.

**Note**: If LangFlow is not installed, this endpoint returns a simulated response.

## API Documentation

Interactive API documentation is available when the service is running:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment

### Python Dependencies

- FastAPI: Web framework
- Uvicorn: ASGI server
- LangFlow: Flow execution engine (optional - graceful fallback)
- Python-multipart: File upload support

Install dependencies:
```bash
pip install -r requirements.txt
```

### Environment Variables

No environment variables are required for basic operation. Optional configurations:

- `FLOWS_DIR`: Custom flows directory (default: /app/flows)
- `LOG_LEVEL`: Logging level (default: INFO)

## Running Locally

### With Docker (Recommended)

```bash
# From repository root
docker compose up backend
```

### Without Docker

```bash
cd langflow-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Flow Storage

Flows are stored in the `/app/flows` directory inside the container, which is mapped to `./langflow-backend/flows` on the host via Docker volume.

This ensures flows persist across container restarts.

## LangFlow Integration

The backend attempts to import LangFlow for flow execution:

```python
from langflow.load import load_flow_from_json
```

### When LangFlow is Available
- Flows are executed using the LangFlow engine
- Full agent capabilities are enabled

### When LangFlow is Not Available
- The service continues to run
- `/run_flow/` endpoint returns simulated responses
- A warning is logged: "LangFlow is not available - /run_flow/ will return simulated responses"

This graceful fallback allows the service to remain operational even if LangFlow installation fails.

## Security Considerations

⚠️ **CRITICAL**: This implementation is for **DEVELOPMENT ONLY**.

### Current Security Issues

1. **No Authentication**: All endpoints are publicly accessible
2. **No Authorization**: No permission checks
3. **Arbitrary Code Execution**: Flows can execute any code
4. **No Sandboxing**: Flows run in the main process
5. **No Resource Limits**: No CPU, memory, or time limits
6. **Permissive CORS**: Allows requests from localhost origins
7. **No Rate Limiting**: Vulnerable to abuse
8. **File System Storage**: Not scalable or secure

### Required Production Security Measures

#### 1. Authentication & Authorization
```python
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/save_flow/")
async def save_flow(
    flow_file: UploadFile,
    token: str = Depends(oauth2_scheme)
):
    # Verify token and permissions
    user = verify_token(token)
    if not user.has_permission("flow:write"):
        raise HTTPException(403, "Insufficient permissions")
    # ...
```

#### 2. Flow Validation
```python
def validate_flow(flow_data: dict) -> bool:
    """Validate flow schema and components"""
    # Check required fields
    # Validate component types
    # Whitelist allowed tools
    # Check for dangerous operations
    pass
```

#### 3. Sandboxed Execution
```python
# Run flows in isolated Docker containers
import docker

def execute_flow_sandboxed(flow_data, user_input):
    client = docker.from_env()
    container = client.containers.run(
        "flow-executor:latest",
        command=["python", "run.py"],
        network_mode="none",  # No network access
        mem_limit="512m",     # Memory limit
        cpu_period=100000,    # CPU limit
        cpu_quota=50000,
        remove=True,
        detach=False
    )
    return container.decode()
```

#### 4. Resource Limits
```python
from contextlib import contextmanager
import signal

@contextmanager
def timeout(seconds):
    def timeout_handler(signum, frame):
        raise TimeoutError()
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

# Usage
with timeout(30):  # 30 second limit
    result = execute_flow(flow_data, user_input)
```

#### 5. Input Sanitization
```python
from bleach import clean

def sanitize_input(user_input: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    # Remove HTML/script tags
    cleaned = clean(user_input, tags=[], strip=True)
    # Limit length
    cleaned = cleaned[:10000]
    # Additional validation
    return cleaned
```

#### 6. Audit Logging
```python
import logging
from datetime import datetime

audit_logger = logging.getLogger("audit")

def log_flow_execution(user_id, flow_name, result):
    audit_logger.info({
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "action": "flow_execution",
        "flow_name": flow_name,
        "result": result,
        "ip_address": request.client.host
    })
```

#### 7. Database Storage
```python
from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Flow(Base):
    __tablename__ = "flows"
    
    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    definition = Column(JSON)
    created_by = Column(String)
    created_at = Column(DateTime)
```

#### 8. Rate Limiting
```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@app.post("/run_flow/")
@limiter.limit("10/minute")  # 10 requests per minute
async def run_flow(...):
    # ...
```

#### 9. CORS Restrictions
```python
# Production CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://app.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

#### 10. HTTPS Only
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
```

## Testing

### Manual Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# List flows
curl http://localhost:8000/list_flows/

# Save a flow
curl -X POST http://localhost:8000/save_flow/ \
  -F "flow_file=@test_flow.json"

# Get a flow
curl http://localhost:8000/get_flow/test_flow.json

# Run a flow
curl -X POST http://localhost:8000/run_flow/ \
  -F "flow_file=@test_flow.json" \
  -F "user_input=Hello, world!"
```

### Testing with Python

```python
import requests

# Save flow
with open("flow.json", "rb") as f:
    response = requests.post(
        "http://localhost:8000/save_flow/",
        files={"flow_file": f}
    )
print(response.json())

# Run flow
with open("flow.json", "rb") as f:
    response = requests.post(
        "http://localhost:8000/run_flow/",
        files={"flow_file": f},
        data={"user_input": "Test input"}
    )
print(response.json())
```

## Monitoring

### Logging

The application logs to stdout. In Docker:

```bash
# View logs
docker compose logs backend

# Follow logs
docker compose logs -f backend
```

### Metrics

Consider adding:
- Prometheus metrics
- Health check endpoints
- Performance monitoring
- Error tracking (Sentry)

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs backend

# Rebuild
docker compose build --no-cache backend
docker compose up backend
```

### LangFlow Import Issues

If LangFlow fails to import:
- Check requirements.txt
- Verify Python version (3.11 recommended)
- Check for dependency conflicts
- Review container logs

The service will still run with simulated responses.

### Permission Errors

```bash
# Ensure flows directory is writable
chmod -R 777 langflow-backend/flows

# Or set proper ownership
chown -R $USER:$USER langflow-backend/flows
```

## Development

### Adding New Endpoints

```python
@app.get("/my_endpoint")
async def my_endpoint():
    return {"message": "Hello"}
```

### Hot Reload

Use `--reload` flag for development:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Production Deployment Checklist

- [ ] Implement authentication (JWT/OAuth)
- [ ] Add authorization and RBAC
- [ ] Implement flow validation
- [ ] Add sandboxed execution
- [ ] Set resource limits
- [ ] Implement rate limiting
- [ ] Add audit logging
- [ ] Move to database storage
- [ ] Restrict CORS
- [ ] Enable HTTPS
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Security audit
- [ ] Load testing
- [ ] Documentation update

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangFlow Documentation](https://docs.langflow.org/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
