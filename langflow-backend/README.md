# FastAPI Backend - Epic Platform

This directory contains the FastAPI backend service for managing and executing LangFlow flows.

## Overview

The backend provides a RESTful API for:
- **Saving flows**: Store LangFlow JSON configurations
- **Listing flows**: Get all available flows
- **Retrieving flows**: Get specific flow details
- **Running flows**: Execute flows with input data

## API Endpoints

### Health Check
- **GET** `/` - API information and status
- **GET** `/health` - Health check with system info

### Flow Management
- **POST** `/save_flow/` - Save a new flow
- **GET** `/list_flows/` - List all flows
- **GET** `/get_flow/{flow_name}` - Get specific flow
- **POST** `/run_flow/` - Execute a flow

## Quick Start

### Using Docker Compose (Recommended)

```bash
# From repository root
./start-dev.sh
```

### Running Locally

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r app/requirements.txt

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, access interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

- `LANGFLOW_HOST`: LangFlow service hostname (default: langflow)
- `LANGFLOW_PORT`: LangFlow service port (default: 7860)
- `PYTHONUNBUFFERED`: Enable real-time logging (default: 1)

## Flow Storage

Flows are stored as JSON files in the `/app/flows` directory (mounted as volume in Docker).

### Flow File Structure

```json
{
  "nodes": [
    {
      "id": "1",
      "type": "LLMChain",
      "data": { ... }
    }
  ],
  "edges": [
    {
      "source": "1",
      "target": "2"
    }
  ]
}
```

## Usage Examples

### Save a Flow

```bash
curl -X POST "http://localhost:8000/save_flow/" \
  -H "Content-Type: application/json" \
  -d '{
    "flow_name": "chatbot",
    "flow_data": {
      "nodes": [],
      "edges": []
    }
  }'
```

### List Flows

```bash
curl http://localhost:8000/list_flows/
```

Response:
```json
{
  "flows": ["chatbot", "summarizer"],
  "count": 2
}
```

### Get a Flow

```bash
curl http://localhost:8000/get_flow/chatbot
```

### Run a Flow

```bash
curl -X POST "http://localhost:8000/run_flow/" \
  -H "Content-Type: application/json" \
  -d '{
    "flow_name": "chatbot",
    "input_data": {
      "message": "Hello, how are you?"
    }
  }'
```

## LangFlow Integration

The backend integrates with LangFlow in two modes:

### 1. Full Integration (Production)
When LangFlow is installed and available:
- Uses `langflow.load_flow_from_json` for execution
- Real flow processing with actual results
- Full error handling and validation

### 2. Simulation Mode (Development/Fallback)
When LangFlow is not available:
- Returns simulated responses
- Logs warnings about simulation mode
- Allows testing API without LangFlow dependency

## Security Considerations

⚠️ **Current Configuration is for Development Only**

### CORS
Current: Allows localhost origins
Production: Restrict to specific domains

```python
origins = [
    "https://yourdomain.com",
]
```

### Required for Production:
1. **Authentication**: Add JWT or OAuth2
2. **Authorization**: Implement role-based access
3. **Rate Limiting**: Prevent API abuse
4. **Input Validation**: Sanitize all inputs
5. **Flow Validation**: Verify flow JSON before execution
6. **Sandboxing**: Isolate flow execution
7. **Timeouts**: Prevent long-running flows
8. **Logging**: Add audit logs
9. **HTTPS**: Enable TLS/SSL
10. **Secrets**: Use proper secret management

## Development

### Project Structure

```
langflow-backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # Main FastAPI application
│   └── requirements.txt
├── flows/                # Stored flows (volume mount)
├── Dockerfile
└── README.md
```

### Adding New Endpoints

1. Edit `app/main.py`
2. Add endpoint function with `@app.post()` or `@app.get()`
3. Define request/response models with Pydantic
4. Add documentation strings
5. Test with `/docs` interface

### Error Handling

The API uses standard HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid input)
- `404`: Resource not found
- `500`: Server error

### Logging

Logs include:
- Info: Successful operations
- Warning: Simulation mode, missing features
- Error: Failures and exceptions

View logs:
```bash
docker-compose logs -f backend
```

## Testing

### Manual Testing

Use the interactive docs at http://localhost:8000/docs

### Automated Testing (Future)

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

## Troubleshooting

### Port Already in Use

```bash
# Change port in docker-compose.yml or:
uvicorn app.main:app --port 8001
```

### LangFlow Not Available

Check logs for warnings about simulation mode:
```bash
docker-compose logs backend | grep "LangFlow"
```

### Flow Not Found

Ensure flow exists:
```bash
ls langflow-backend/flows/
```

### Permission Errors

Fix flow directory permissions:
```bash
chmod -R 755 langflow-backend/flows/
```

## Performance

### Optimization Tips

1. **Caching**: Implement flow result caching
2. **Async**: Use async operations for I/O
3. **Connection Pooling**: For database connections
4. **Load Balancing**: Multiple backend instances
5. **CDN**: For static assets

## Monitoring

Add monitoring in production:

```python
# Prometheus metrics
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

## Contributing

1. Follow PEP 8 style guide
2. Add docstrings to all functions
3. Include type hints
4. Update tests for new features
5. Update documentation

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangFlow Documentation](https://docs.langflow.org/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Support

- Check logs: `docker-compose logs -f backend`
- API docs: http://localhost:8000/docs
- GitHub Issues: Report bugs and feature requests
