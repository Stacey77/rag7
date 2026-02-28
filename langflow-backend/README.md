# LangFlow Backend

FastAPI backend for managing and executing LangFlow flows.

## Features

- **RESTful API**: Manage LangFlow flows via HTTP endpoints
- **Flow Storage**: Save and retrieve flows from disk
- **Flow Execution**: Run flows with user input
- **Graceful Fallback**: Works without LangFlow installed (simulated responses)
- **CORS Enabled**: Frontend integration ready
- **Auto Documentation**: Swagger UI and ReDoc included

## API Endpoints

### `GET /`
Health check endpoint

### `POST /save_flow/`
Save a LangFlow JSON flow

**Request Body:**
```json
{
  "flow_name": "my_flow",
  "flow_data": { ... }
}
```

### `GET /list_flows/`
List all saved flows

**Response:**
```json
{
  "success": true,
  "message": "Found 5 flows",
  "data": {
    "flows": [
      {
        "name": "flow1",
        "path": "/app/flows/flow1.json",
        "size": 1234
      }
    ],
    "count": 5
  }
}
```

### `GET /get_flow/{flow_name}`
Retrieve a specific flow by name

**Response:**
```json
{
  "success": true,
  "message": "Flow retrieved successfully",
  "data": {
    "flow_name": "my_flow",
    "flow_data": { ... }
  }
}
```

### `POST /run_flow/`
Execute a flow with user input

**Request Body:**
```json
{
  "flow_data": { ... },
  "user_input": "Hello, how are you?"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Flow executed successfully",
  "data": {
    "result": "AI response here",
    "user_input": "Hello, how are you?"
  }
}
```

### `GET /health`
Health check with system status

## Running the Backend

### Via Docker Compose (Recommended)

From the root directory:
```bash
docker-compose up backend
```

### Standalone with Docker

```bash
# Build the image
docker build -t epic-backend .

# Run the container
docker run -p 8000:8000 -v $(pwd)/app:/app/app epic-backend
```

### Local Development (without Docker)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Accessing the API

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

- `LANGFLOW_URL`: URL of the LangFlow service (default: http://langflow:7860)
- `CORS_ORIGINS`: Comma-separated list of allowed CORS origins

Create a `.env` file in the `langflow-backend` directory:
```
LANGFLOW_URL=http://langflow:7860
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Development

### Hot Reloading

When running with Docker Compose, the `/app/app` directory is mounted as a volume, enabling hot reloading. Changes to Python files are automatically detected.

### Testing Endpoints

```bash
# List flows
curl http://localhost:8000/list_flows/

# Save a flow
curl -X POST http://localhost:8000/save_flow/ \
  -H "Content-Type: application/json" \
  -d '{"flow_name": "test", "flow_data": {"nodes": []}}'

# Get a flow
curl http://localhost:8000/get_flow/test

# Run a flow
curl -X POST http://localhost:8000/run_flow/ \
  -H "Content-Type: application/json" \
  -d '{"flow_data": {...}, "user_input": "Hello"}'
```

## Security Considerations

⚠️ **Important**: This is a development setup. Before production:

1. **Authentication**: Add user authentication (JWT, OAuth, etc.)
2. **Authorization**: Implement role-based access control
3. **CORS**: Restrict origins to your production domain
4. **Input Validation**: Validate and sanitize all inputs
5. **Flow Validation**: Validate flow_data structure and content
6. **Rate Limiting**: Add rate limiting to prevent abuse
7. **Logging**: Implement comprehensive logging and monitoring
8. **HTTPS**: Use SSL/TLS in production
9. **Secrets**: Use environment variables or secret management
10. **Timeouts**: Add timeouts for flow execution

## Architecture

```
langflow-backend/
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── app/
    ├── __init__.py        # Package init
    └── main.py            # FastAPI application
```

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for FastAPI
- **LangFlow**: Visual flow builder (optional)
- **Pydantic**: Data validation
- **Python-multipart**: File upload support

## Troubleshooting

### LangFlow Import Error

If you see warnings about LangFlow not being available:
- This is expected if LangFlow isn't installed
- The backend will still work with simulated responses
- To enable real flow execution, ensure LangFlow is installed

### CORS Errors

If frontend can't connect:
1. Check `CORS_ORIGINS` environment variable
2. Ensure frontend URL is included
3. Restart backend after changing CORS settings

### Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process or use a different port
```

### Flow Not Found

Ensure flows are saved in `/app/flows` directory within the container.

## Contributing

When adding new endpoints:
1. Add proper type hints
2. Include security comments
3. Add error handling
4. Update this README
5. Test with Swagger UI

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangFlow Documentation](https://docs.langflow.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
