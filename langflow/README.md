# LangFlow Service

This directory contains the LangFlow service configuration for the Ragamuffin platform.

## Overview

LangFlow is a visual workflow designer for creating AI agent flows. It provides a drag-and-drop interface for building complex agent logic without writing code.

## Access

When running via Docker Compose, LangFlow is accessible at:
- **URL**: http://localhost:7860
- **Port**: 7860

## Usage

### Creating Flows

1. Open http://localhost:7860 in your browser
2. Use the visual interface to design your agent workflow
3. Add nodes for LLMs, tools, prompts, and more
4. Connect nodes to define the flow logic
5. Export your flow as JSON

### Exporting Flows

Flows created in LangFlow can be exported as JSON files and saved to the backend via the API:

```bash
curl -X POST http://localhost:8000/save_flow/ \
  -F "file=@my-flow.json"
```

## Configuration

### Environment Variables

- `LANGFLOW_HOST`: Host to bind to (default: `0.0.0.0`)
- `LANGFLOW_PORT`: Port to listen on (default: `7860`)

### Custom Configuration

To customize LangFlow settings, modify the Dockerfile or pass additional environment variables in `docker-compose.yml`.

## Security Considerations

⚠️ **IMPORTANT**: LangFlow UI should be secured in production!

### Recommendations:

1. **Authentication**: 
   - Add authentication layer (reverse proxy with auth, VPN, etc.)
   - Do not expose LangFlow directly to the internet

2. **Access Control**:
   - Restrict access to trusted users only
   - Use firewall rules to limit access
   - Consider using authentication middleware

3. **Network Security**:
   - Run LangFlow on an internal network
   - Use VPN for remote access
   - Implement IP whitelisting

4. **Flow Validation**:
   - Review flows before execution
   - Limit available tools and modules
   - Sandbox execution environment

5. **API Keys**:
   - Never commit API keys in flows
   - Use environment variables or secrets management
   - Rotate keys regularly

## Development

### Running Locally

```bash
# Install LangFlow
pip install langflow

# Run LangFlow
langflow run --host 0.0.0.0 --port 7860
```

### Building the Docker Image

```bash
# Build from this directory
docker build -t ragamuffin-langflow .

# Run container
docker run -p 7860:7860 ragamuffin-langflow
```

## Troubleshooting

### LangFlow Won't Start

Check logs:
```bash
docker-compose logs langflow
```

Common issues:
- Port 7860 already in use
- Insufficient memory (needs ~1GB)
- Python dependency conflicts

### Can't Access UI

1. Verify container is running: `docker-compose ps`
2. Check logs: `docker-compose logs langflow`
3. Ensure port is not blocked by firewall
4. Try accessing from localhost: http://localhost:7860

### Flow Export Issues

- Ensure flow is saved before exporting
- Check JSON is valid before uploading to backend
- Verify backend `/save_flow/` endpoint is accessible

## Resources

- [LangFlow Documentation](https://docs.langflow.org/)
- [LangFlow GitHub](https://github.com/logspace-ai/langflow)
- [Backend API Documentation](../langflow-backend/README.md)

## Notes

- LangFlow stores flows in memory by default
- For persistence, export flows and save via the backend API
- Flows are stored in `../langflow-backend/flows/` directory
- The backend gracefully handles LangFlow being unavailable

---

For production deployment, ensure proper security measures are in place!
