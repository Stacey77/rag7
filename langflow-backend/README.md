# LangFlow Backend

FastAPI backend for managing and executing LangFlow flows.

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/save_flow/` | Save a flow JSON file |
| GET | `/list_flows/` | List all saved flows |
| GET | `/get_flow/{flow_name}` | Get a specific flow |
| POST | `/run_flow/` | Execute a flow with user input |

## Usage

### Save a Flow

```bash
curl -X POST "http://localhost:8000/save_flow/" \
  -F "flow_file=@my_flow.json"
```

### List Flows

```bash
curl "http://localhost:8000/list_flows/"
```

### Get a Flow

```bash
curl "http://localhost:8000/get_flow/my_flow.json"
```

### Run a Flow

```bash
curl -X POST "http://localhost:8000/run_flow/" \
  -F "flow_file=@my_flow.json" \
  -F "user_input=Hello, world!"
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLOWS_DIR` | Directory for flow storage | `/app/flows` |

## LangFlow Dependency

The backend attempts to import `langflow` for flow execution. If the package is not installed:
- `/run_flow/` will return a simulated response
- A warning will be logged
- Install with: `pip install langflow`

## Security Considerations

⚠️ **Important**: This is a development server. Before production deployment:

1. **Validate Flows**: Implement schema validation for flow JSON
2. **Sandbox Execution**: Run flows in isolated environments
3. **Whitelist Tools**: Only allow approved integrations
4. **Add Authentication**: Implement JWT/OAuth
5. **Secure CORS**: Restrict origins to your domains
6. **Use Database**: Replace filesystem storage with a database
7. **Add Rate Limiting**: Prevent abuse
8. **Enable Auditing**: Log all operations

## Local Development

```bash
cd langflow-backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Docker

```bash
docker build -t ragamuffin-backend .
docker run -p 8000:8000 -v $(pwd)/flows:/app/flows ragamuffin-backend
```
