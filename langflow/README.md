# LangFlow Service

This directory contains the LangFlow service configuration for visual AI workflow building.

## Overview

LangFlow is a visual framework for building LangChain flows. It provides a drag-and-drop interface for creating complex AI workflows without writing code.

## Docker Configuration

The service runs on port 7860 and persists data to a Docker volume.

### Environment Variables

- `LANGFLOW_HOST`: Host address (default: 0.0.0.0)
- `LANGFLOW_PORT`: Port number (default: 7860)

## Usage

### Access the UI

Once the services are running, access LangFlow at:
```
http://localhost:7860
```

### Creating Flows

1. Open LangFlow UI in your browser
2. Use the visual editor to create flows
3. Connect components by dragging connections
4. Configure each component's parameters
5. Export flows as JSON for use with the backend

### Exporting Flows

To use flows with the backend API:

1. In LangFlow, click "Export" on your flow
2. Select "JSON" format
3. Save the flow JSON
4. Use the backend's `/save_flow/` endpoint to persist it

### Data Persistence

All LangFlow data (flows, configurations, etc.) is stored in a Docker volume:
- Volume name: `rag7_langflow-data`
- Mount point: `/root/.langflow`

## Development

### Running Locally (without Docker)

```bash
# Install LangFlow
pip install langflow

# Run LangFlow
langflow run --host 0.0.0.0 --port 7860
```

### Rebuilding the Container

```bash
# Rebuild and restart
docker compose build langflow
docker compose up -d langflow

# View logs
docker compose logs -f langflow
```

## Integration with Backend

The backend service can load and execute flows created in LangFlow. Export your flows from LangFlow and save them via the backend API's `/save_flow/` endpoint.

## Troubleshooting

### LangFlow Won't Start

Check the logs:
```bash
docker compose logs langflow
```

Common issues:
- Port 7860 already in use
- Insufficient memory
- Volume permission issues

### Flows Not Persisting

Ensure the Docker volume is properly mounted:
```bash
docker volume inspect rag7_langflow-data
```

### Performance Issues

LangFlow can be resource-intensive. Ensure:
- At least 2GB RAM available
- Sufficient disk space for models
- Good network connection for downloading models

## Resources

- [LangFlow Documentation](https://docs.langflow.org/)
- [LangFlow GitHub](https://github.com/logspace-ai/langflow)
- [LangChain Documentation](https://python.langchain.com/)

## Notes

- LangFlow includes its own web server
- The service automatically restarts unless stopped
- Flows can be complex and may require significant compute resources
- Consider GPU support for large language models
