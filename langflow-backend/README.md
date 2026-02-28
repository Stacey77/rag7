# LangFlow Backend - FastAPI Service

This directory contains the FastAPI backend service for managing and executing LangFlow flows.

## API Endpoints

### Flow Management

#### `POST /save_flow/`
Upload and save a flow JSON file.

**Request**:
- Content-Type: `multipart/form-data`
- Field: `flow_file` (file upload)

**Response**:
```json
{
  "status": "success",
  "filename": "my_flow.json",
  "path": "/app/flows/my_flow.json"
}
```

#### `GET /list_flows/`
List all saved flow files.

**Response**:
```json
{
  "flows": ["flow1.json", "flow2.json"]
}
```

#### `GET /get_flow/{flow_name}`
Retrieve a specific flow's content.

**Response**:
```json
{
  "filename": "my_flow.json",
  "content": { ... }
}
```

#### `POST /run_flow/`
Execute a flow with user input.

**Request**:
- Content-Type: `multipart/form-data`
- Fields:
  - `flow_file` (file upload)
  - `user_input` (text)

**Response**:
```json
{
  "status": "success",
  "result": "Flow execution result...",
  "simulated": false
}
```

**Note**: If langflow library is not available, returns simulated response with `"simulated": true`.

### Health Check

#### `GET /`
API health check.

**Response**:
```json
{
  "status": "ok",
  "message": "LangFlow Backend API"
}
```

## Environment

### Environment Variables

Create a `.env` file (optional):
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# CORS Settings (development only)
CORS_ORIGINS=http://localhost:8080,http://localhost:3000

# Flow Storage
FLOWS_DIR=/app/flows
```

### Development

```bash
# Run backend locally (without Docker)
cd langflow-backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Access API docs
open http://localhost:8000/docs
```

## Architecture

```
langflow-backend/
├── Dockerfile              # Container build configuration
├── requirements.txt        # Python dependencies
├── flows/                  # Persistent flow storage (mounted volume)
├── app/
│   ├── __init__.py
│   └── main.py            # FastAPI application with endpoints
└── README.md              # This file
```

## Security Considerations

⚠️ **CRITICAL SECURITY WARNINGS**

### Current Implementation (Development Only)

This backend is designed for **local development** and has several security gaps:

1. **No Authentication**: All endpoints are publicly accessible
2. **No Authorization**: Any user can upload/execute flows
3. **No Flow Validation**: Uploaded flows are not validated
4. **No Sandboxing**: Flow execution is not sandboxed
5. **CORS Wide Open**: Allows requests from any localhost origin
6. **No Rate Limiting**: Vulnerable to DoS attacks
7. **No Input Validation**: User inputs are not sanitized

### Production Requirements

Before deploying to production, **YOU MUST**:

#### 1. Authentication & Authorization
```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/save_flow/")
async def save_flow(token: str = Depends(oauth2_scheme)):
    # Verify token
    # Check user permissions
    pass
```

#### 2. Flow Validation
```python
def validate_flow(flow_data: dict) -> bool:
    """Validate flow structure and components."""
    # Check for malicious code
    # Verify component types
    # Validate connections
    # Ensure no system access
    return True
```

#### 3. Sandboxed Execution
```python
# Use Docker, gVisor, or Firecracker for isolation
# Limit CPU, memory, network access
# Set execution timeouts
# Monitor resource usage
```

#### 4. Secure CORS
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains only
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization"],
)
```

#### 5. Input Validation & Sanitization
```python
from pydantic import BaseModel, validator

class FlowInput(BaseModel):
    user_input: str
    
    @validator('user_input')
    def validate_input(cls, v):
        if len(v) > 1000:
            raise ValueError('Input too long')
        # Sanitize input
        return v
```

#### 6. Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/run_flow/")
@limiter.limit("5/minute")
async def run_flow():
    pass
```

#### 7. Logging & Monitoring
```python
import logging

logger = logging.getLogger(__name__)

@app.post("/run_flow/")
async def run_flow():
    logger.info(f"Flow execution requested by {user_id}")
    # Log all actions
    # Monitor for suspicious activity
    # Set up alerts
```

#### 8. HTTPS/TLS
- Never run production API over HTTP
- Use valid TLS certificates
- Enforce HTTPS redirects
- Enable HSTS headers

#### 9. Secrets Management
- Use environment variables or secret managers (AWS Secrets Manager, HashiCorp Vault)
- Never commit secrets to Git
- Rotate credentials regularly

#### 10. Regular Security Audits
- Dependency scanning (Dependabot, Snyk)
- Code security analysis (Bandit, CodeQL)
- Penetration testing
- Security reviews

### Example Security Checklist

- [ ] Authentication implemented (OAuth2, JWT, API keys)
- [ ] Authorization with role-based access control
- [ ] Flow validation before execution
- [ ] Sandboxed execution environment
- [ ] CORS restricted to specific domains
- [ ] Rate limiting on all endpoints
- [ ] Input validation and sanitization
- [ ] SQL injection prevention (use ORMs)
- [ ] XSS protection
- [ ] CSRF protection
- [ ] HTTPS/TLS enabled
- [ ] Security headers (HSTS, CSP, etc.)
- [ ] Logging and monitoring
- [ ] Error handling (no sensitive data in errors)
- [ ] Regular dependency updates
- [ ] Security incident response plan

## Simulated Fallback

When the `langflow` library is not available (e.g., during frontend development), the backend returns simulated responses:

```json
{
  "status": "success",
  "result": "Simulated response: Hello! This is a simulated flow response...",
  "simulated": true,
  "warning": "LangFlow library not available - using simulated response"
}
```

This allows frontend development to proceed without requiring a full langflow installation.

## Troubleshooting

### Flow Execution Fails
```bash
# Check logs
docker compose logs backend

# Verify langflow is installed
docker compose exec backend pip list | grep langflow

# Test flow manually
docker compose exec backend python
>>> from langflow import load_flow_from_json
```

### Flows Not Persisting
```bash
# Verify volume mount
docker compose config | grep -A 5 backend

# Check flows directory
docker compose exec backend ls -la /app/flows/
```

### CORS Issues
```bash
# Check allowed origins in app/main.py
# Update CORS settings for your domain
```

## API Documentation

Once running, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

```bash
# Test health check
curl http://localhost:8000/

# Upload a flow
curl -X POST http://localhost:8000/save_flow/ \
  -F "flow_file=@my_flow.json"

# List flows
curl http://localhost:8000/list_flows/

# Get flow
curl http://localhost:8000/get_flow/my_flow.json

# Run flow
curl -X POST http://localhost:8000/run_flow/ \
  -F "flow_file=@my_flow.json" \
  -F "user_input=Hello, AI!"
```

---

**Remember**: This is a **development scaffold**. Never deploy to production without implementing proper security measures!
