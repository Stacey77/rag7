# FastAPI Backend Service

This service provides a REST API for managing and executing LangFlow flows.

## 🎯 Purpose

The backend acts as a bridge between the web client and LangFlow, providing endpoints to:
- Save flow definitions
- List saved flows
- Retrieve specific flows
- Execute flows with user input

## 🚀 API Endpoints

### Health Check
```
GET /
GET /health
```

### Flow Management

#### Save Flow
```
POST /save_flow/
Content-Type: multipart/form-data

Parameters:
- flow_name: string (flow identifier)
- flow_json: file (JSON flow definition)
```

#### List Flows
```
GET /list_flows/

Response:
{
  "flows": ["flow1", "flow2"],
  "count": 2
}
```

#### Get Flow
```
GET /get_flow/{flow_name}

Response:
{
  "flow_name": "my_flow",
  "flow_data": { ... }
}
```

#### Run Flow
```
POST /run_flow/
Content-Type: multipart/form-data

Parameters:
- flow_json: file (JSON flow definition)
- user_input: string (input to pass to the flow)

Response:
{
  "result": "...",
  "status": "success"
}
```

## 🐳 Docker

### Build
```bash
docker build -t ragamuffin-backend .
```

### Run Standalone
```bash
docker run -p 8000:8000 -v $(pwd)/flows:/app/flows ragamuffin-backend
```

## 💻 Local Development

### Setup
```bash
pip install -r requirements.txt
```

### Run
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📦 Dependencies

- FastAPI: Web framework
- Uvicorn: ASGI server
- LangFlow: Flow execution engine
- python-multipart: File upload support

## 💾 Data Persistence

Flow definitions are saved to `/app/flows` directory, which is mounted from the host.

## 🔧 Environment Variables

- `LANGFLOW_URL`: URL to LangFlow service (default: http://langflow:7860)

## 🔒 Security Considerations

**⚠️ This is a development configuration. For production:**

1. **CORS**: Restrict allowed origins in `main.py`
2. **Authentication**: Add JWT or OAuth2 authentication
3. **Flow Validation**: Implement comprehensive JSON schema validation
4. **Input Sanitization**: Validate and sanitize all user inputs
5. **Rate Limiting**: Add rate limiting to prevent abuse
6. **Secrets**: Use environment variables or secrets manager
7. **File Operations**: Add path traversal protection
8. **Sandboxing**: Consider sandboxing flow execution

## 🧪 Testing

### Test Endpoints with curl

```bash
# Health check
curl http://localhost:8000/health

# List flows
curl http://localhost:8000/list_flows/

# Save flow
curl -X POST http://localhost:8000/save_flow/ \
  -F "flow_name=test_flow" \
  -F "flow_json=@flow.json"

# Get flow
curl http://localhost:8000/get_flow/test_flow

# Run flow
curl -X POST http://localhost:8000/run_flow/ \
  -F "flow_json=@flow.json" \
  -F "user_input=Hello, world!"
```

## 📝 Notes

- If LangFlow cannot be imported, the API runs in simulation mode
- `/run_flow/` returns simulated responses when LangFlow is unavailable
- All errors are logged for debugging

## 🔗 Related Services

- LangFlow: http://localhost:7860
- Frontend: http://localhost:8080
