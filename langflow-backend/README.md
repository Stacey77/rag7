# LangFlow Backend

## Overview
FastAPI backend service for the Ragamuffin platform. Provides RESTful API endpoints for saving, listing, retrieving, and executing LangFlow JSON flows.

## Features
- **Flow Management**: Save, list, retrieve, and delete flow files
- **Flow Execution**: Execute flows with user input
- **CORS Enabled**: Configured for localhost development
- **Graceful Fallback**: Returns simulated responses when LangFlow is unavailable
- **OpenAPI Documentation**: Auto-generated at `/docs` and `/redoc`

## API Endpoints

### GET /
Root endpoint with API information

### GET /health
Health check endpoint

### POST /save_flow/
Upload and save a flow JSON file
- **Input**: `flow_file` (multipart/form-data, .json file)
- **Output**: Confirmation with filename and path

Example:
```bash
curl -X POST -F "flow_file=@my_flow.json" http://localhost:8000/save_flow/
```

### GET /list_flows/
List all saved flow files with metadata
- **Output**: Array of flows with name, size, and modification time

Example:
```bash
curl http://localhost:8000/list_flows/
```

### GET /get_flow/{flow_name}
Retrieve a specific flow file by name
- **Input**: `flow_name` (path parameter)
- **Output**: Flow JSON content

Example:
```bash
curl http://localhost:8000/get_flow/my_flow.json
```

### POST /run_flow/
Execute a flow with user input
- **Input**: 
  - `flow_file` (multipart/form-data, .json file)
  - `user_input` (form field, string)
- **Output**: Execution result

Example:
```bash
curl -X POST \
  -F "flow_file=@my_flow.json" \
  -F "user_input=Hello, how are you?" \
  http://localhost:8000/run_flow/
```

### DELETE /delete_flow/{flow_name}
Delete a specific flow file
- **Input**: `flow_name` (path parameter)
- **Output**: Confirmation message

Example:
```bash
curl -X DELETE http://localhost:8000/delete_flow/my_flow.json
```

## Running the Backend

### With Docker (Recommended)
```bash
# From project root
docker-compose up backend

# Or with rebuild
docker-compose up --build backend
```

### Standalone Development
```bash
cd langflow-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Access
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

### Available Variables
```bash
# LangFlow connection (for future use)
LANGFLOW_HOST=langflow
LANGFLOW_PORT=7860

# Flow storage (default: /app/flows)
FLOWS_DIR=/app/flows
```

## Flow Storage
- Flows are persisted in the `flows/` directory
- Directory is mounted from host in Docker Compose
- Files survive container restarts

## Security Considerations

⚠️ **CRITICAL SECURITY WARNINGS**

This is a development scaffold. For production deployment:

### 1. Authentication & Authorization
```python
# Add dependencies
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/save_flow/")
async def save_flow(
    flow_file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme)
):
    # Verify token and user permissions
    ...
```

### 2. Flow Validation
```python
# Validate flow structure and content
def validate_flow(flow_data: dict) -> bool:
    # Check for required fields
    # Validate node types
    # Scan for suspicious patterns
    # Check against whitelist
    return True
```

### 3. Sandboxed Execution
- Use Docker containers for flow execution
- Implement resource limits (CPU, memory, time)
- Run in isolated network namespace
- Use read-only filesystem where possible

### 4. Input Validation
- Validate all file uploads
- Sanitize user input
- Check file sizes and types
- Prevent path traversal attacks

### 5. Rate Limiting
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/run_flow/")
@limiter.limit("10/minute")
async def run_flow(...):
    ...
```

### 6. CORS Configuration
```python
# Restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization"],
)
```

### 7. Logging & Monitoring
- Log all flow executions
- Monitor for suspicious activity
- Track resource usage
- Set up alerts

### 8. Error Handling
- Don't expose internal errors to clients
- Log detailed errors server-side
- Return generic error messages

## LangFlow Integration

### When LangFlow is Available
The backend can execute flows using the LangFlow runtime:
```python
from langflow.load import load_flow_from_json

flow = load_flow_from_json("path/to/flow.json")
result = flow(user_input)
```

### When LangFlow is Unavailable
The backend gracefully falls back to simulated responses:
- Logs a warning message
- Returns mock response with user input echoed
- Indicates execution mode as "simulated"

## Troubleshooting

### Import Error: langflow not found
```bash
# LangFlow is optional - backend will use simulated mode
# To install LangFlow:
pip install langflow
```

### Port 8000 Already in Use
```bash
# Find process
lsof -i :8000
kill -9 <PID>

# Or change port
uvicorn app.main:app --port 8001
```

### CORS Errors
- Ensure frontend URL is in `allow_origins` list
- Check browser console for specific CORS errors
- Verify credentials mode matches

### File Permission Errors
```bash
# Fix flows directory permissions
chmod -R 755 flows/
chown -R $USER:$USER flows/
```

## Development Tips

### Hot Reload
Use `--reload` flag for automatic restart on code changes:
```bash
uvicorn app.main:app --reload
```

### Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing with curl
```bash
# Save a test flow
echo '{"nodes": [], "edges": []}' > test.json
curl -X POST -F "flow_file=@test.json" http://localhost:8000/save_flow/

# List flows
curl http://localhost:8000/list_flows/

# Run flow
curl -X POST \
  -F "flow_file=@test.json" \
  -F "user_input=test" \
  http://localhost:8000/run_flow/
```

## Dependencies
- **FastAPI**: Modern, fast web framework
- **Uvicorn**: ASGI server
- **LangFlow**: Flow execution runtime (optional)
- **python-multipart**: File upload support

## Next Steps
1. Implement authentication
2. Add flow validation
3. Set up database for metadata
4. Implement versioning
5. Add user management
6. Configure monitoring
7. Set up CI/CD pipeline
