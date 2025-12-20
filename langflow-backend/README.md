# LangFlow Backend

FastAPI backend for the Epic Platform, providing flow management and execution capabilities.

## Overview

The backend provides RESTful APIs for:
- Saving and retrieving LangFlow workflows
- Listing available flows
- Executing flows with user input
- Health monitoring

## Service Details

- **Port**: 8000
- **Framework**: FastAPI with Uvicorn
- **Base Image**: python:3.11-slim
- **API Documentation**: http://localhost:8000/docs

## Endpoints

### Health Check
```bash
GET /health
```
Returns service status and configuration.

### Save Flow
```bash
POST /save_flow/
Content-Type: multipart/form-data

Parameters:
  - flow: JSON file (multipart upload)

Response:
  {
    "success": true,
    "filename": "myflow.json",
    "path": "/app/flows/myflow.json",
    "message": "Flow saved successfully"
  }
```

### List Flows
```bash
GET /list_flows/

Response:
  [
    {
      "name": "myflow.json",
      "size": 1024,
      "created": "2023-11-15T10:00:00",
      "modified": "2023-11-15T12:00:00"
    }
  ]
```

### Get Flow
```bash
GET /get_flow/{flow_name}

Response:
  {
    "success": true,
    "flow_name": "myflow.json",
    "flow_data": { ... }
  }
```

### Run Flow
```bash
POST /run_flow/
Content-Type: multipart/form-data

Parameters:
  - flow_file: JSON file (multipart upload)
  - user_input: string (form field)

Response:
  {
    "success": true,
    "result": { ... },
    "simulated": false,
    "message": "Flow executed successfully"
  }
```

## Environment Variables

- `LANGFLOW_URL`: URL of LangFlow service (default: http://langflow:7860)
- `LOG_LEVEL`: Logging level (default: INFO)

## Flow Persistence

Flows are stored in `/app/flows` directory, which is mounted as a volume from `./langflow-backend/flows` on the host.

This ensures flows persist across container restarts.

## LangFlow Integration

The backend attempts to import `langflow.load_flow_from_json` for flow execution. If LangFlow is not available:

- The `/run_flow/` endpoint returns simulated responses
- A warning is logged indicating LangFlow is not available
- This allows the backend to run in environments without LangFlow installed

To enable real flow execution, ensure LangFlow is installed (included in requirements.txt).

## Security Considerations

### ⚠️ Current Limitations (Development Only)

1. **No Authentication**: All endpoints are open and unauthenticated
2. **No Authorization**: No role-based access control
3. **No Flow Validation**: Uploaded flows are not validated
4. **CORS Wide Open**: Configured for localhost development
5. **Arbitrary Code Execution**: User flows can execute arbitrary code
6. **Simple File Storage**: No versioning or access controls

### 🔒 Production Recommendations

Before production deployment:

1. **Authentication & Authorization**
   ```python
   # Add JWT middleware
   from fastapi_jwt_auth import AuthJWT
   
   @app.post("/save_flow/")
   async def save_flow(
       flow: UploadFile = File(...),
       Authorize: AuthJWT = Depends()
   ):
       Authorize.jwt_required()
       # ... rest of endpoint
   ```

2. **Flow Validation**
   ```python
   # Validate flow schema
   from jsonschema import validate
   
   FLOW_SCHEMA = { ... }
   validate(instance=flow_data, schema=FLOW_SCHEMA)
   ```

3. **Sandboxing**
   - Execute flows in isolated Docker containers
   - Use container orchestration (Kubernetes)
   - Implement resource limits and timeouts
   - Whitelist allowed tools and components

4. **CORS Restrictions**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://app.example.com"],
       allow_credentials=True,
       allow_methods=["GET", "POST"],
       allow_headers=["Authorization"],
   )
   ```

5. **Database Storage**
   - Migrate from file system to PostgreSQL/MongoDB
   - Implement versioning and audit trails
   - Add access control and encryption
   - Use cloud storage (S3) for large files

6. **Rate Limiting**
   ```python
   from slowapi import Limiter
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   
   @app.post("/run_flow/")
   @limiter.limit("10/minute")
   async def run_flow(...):
       # ...
   ```

## Development

### Local Development (without Docker)

```bash
cd langflow-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Save a flow
curl -X POST http://localhost:8000/save_flow/ \
  -F "flow=@test-flow.json"

# List flows
curl http://localhost:8000/list_flows/

# Get specific flow
curl http://localhost:8000/get_flow/test-flow.json

# Run flow
curl -X POST http://localhost:8000/run_flow/ \
  -F "flow_file=@test-flow.json" \
  -F "user_input=Hello, agent!"
```

### View API Documentation

Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Service Won't Start

Check logs:
```bash
docker compose logs backend
```

Common issues:
- Port 8000 already in use
- Missing requirements.txt
- Invalid Python syntax in main.py

### Can't Connect to LangFlow

Verify LangFlow is running:
```bash
docker compose ps langflow
curl http://localhost:7860/health
```

Check network connectivity from backend:
```bash
docker compose exec backend ping langflow
```

### Flow Execution Fails

1. Check if LangFlow is available:
   ```bash
   docker compose exec backend python -c "import langflow; print('OK')"
   ```

2. Review backend logs:
   ```bash
   docker compose logs -f backend
   ```

3. Verify flow JSON structure

### Simulated Responses

If you see "simulated" responses:
- LangFlow is not available in the backend
- Check backend logs for import errors
- Ensure langflow is in requirements.txt
- Rebuild backend: `docker compose build backend`

## File Structure

```
langflow-backend/
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
├── flows/                  # Persisted flows (mounted volume)
├── app/
│   ├── __init__.py        # Package init
│   └── main.py            # FastAPI application
└── README.md              # This file
```

## Best Practices

1. **Version Control**: Track flows with git or database versioning
2. **Validation**: Validate all inputs before processing
3. **Error Handling**: Return informative error messages
4. **Logging**: Log all flow operations and errors
5. **Testing**: Write tests for all endpoints
6. **Documentation**: Keep API documentation up to date
7. **Monitoring**: Add metrics and alerting for production

## API Client Examples

### Python

```python
import requests

# Save flow
with open('myflow.json', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/save_flow/',
        files={'flow': f}
    )
    print(response.json())

# Run flow
with open('myflow.json', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/run_flow/',
        files={'flow_file': f},
        data={'user_input': 'Hello'}
    )
    print(response.json())
```

### JavaScript

```javascript
// Save flow
const formData = new FormData();
formData.append('flow', fileInput.files[0]);

const response = await fetch('http://localhost:8000/save_flow/', {
  method: 'POST',
  body: formData
});
const result = await response.json();

// Run flow
const runData = new FormData();
runData.append('flow_file', fileInput.files[0]);
runData.append('user_input', 'Hello');

const runResponse = await fetch('http://localhost:8000/run_flow/', {
  method: 'POST',
  body: runData
});
const runResult = await runResponse.json();
```

### cURL

```bash
# Save flow
curl -X POST http://localhost:8000/save_flow/ \
  -F "flow=@myflow.json"

# List flows
curl http://localhost:8000/list_flows/

# Get flow
curl http://localhost:8000/get_flow/myflow.json

# Run flow
curl -X POST http://localhost:8000/run_flow/ \
  -F "flow_file=@myflow.json" \
  -F "user_input=Hello, agent!"
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangFlow Documentation](https://docs.langflow.org/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Support

For backend-specific issues:
- Review logs: `docker compose logs backend`
- Check health: `curl http://localhost:8000/health`
- View API docs: http://localhost:8000/docs
- Open issue on GitHub
