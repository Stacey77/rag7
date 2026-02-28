# LangFlow Container

This directory contains the Dockerfile for running LangFlow in a containerized environment.

## What is LangFlow?

LangFlow is a visual programming interface for building Language Model (LLM) applications. It provides a drag-and-drop interface to create complex AI workflows without writing code.

## Running LangFlow

### Via Docker Compose (Recommended)

From the root directory:
```bash
docker-compose up langflow
```

### Standalone

```bash
# Build the image
docker build -t epic-langflow .

# Run the container
docker run -p 7860:7860 -v langflow_data:/root/.langflow epic-langflow
```

## Accessing LangFlow

Once running, access LangFlow at: **http://localhost:7860**

## Features

- **Visual Flow Builder**: Drag and drop components to build AI workflows
- **Pre-built Components**: Access to various LLM providers, vector stores, and tools
- **Export Flows**: Save flows as JSON for use in the backend API
- **Real-time Testing**: Test your flows directly in the UI

## Creating and Exporting Flows

1. Open LangFlow UI at http://localhost:7860
2. Create your flow using the visual builder
3. Click "Export" to save the flow as JSON
4. Use the exported JSON with the backend API's `/save_flow/` endpoint

## Usage with Backend

The FastAPI backend can:
- Load flows created in LangFlow
- Execute flows programmatically
- Store and retrieve flows

Example workflow:
1. Create flow in LangFlow UI
2. Export flow as JSON
3. Upload to backend via `/save_flow/` endpoint
4. Execute flow via `/run_flow/` endpoint

## Data Persistence

Flow data is persisted in a Docker volume:
- Volume name: `langflow_data`
- Mount point: `/root/.langflow`

To backup your flows:
```bash
docker run --rm -v langflow_data:/data -v $(pwd):/backup alpine tar czf /backup/langflow_backup.tar.gz -C /data .
```

To restore:
```bash
docker run --rm -v langflow_data:/data -v $(pwd):/backup alpine tar xzf /backup/langflow_backup.tar.gz -C /data
```

## Environment Variables

- `LANGFLOW_HOST`: Host to bind to (default: 0.0.0.0)
- `LANGFLOW_PORT`: Port to run on (default: 7860)

## Troubleshooting

### Port Already in Use
```bash
# Check what's using port 7860
lsof -i :7860

# Use a different port in docker-compose.yml
# Change "7860:7860" to "7861:7860"
```

### Memory Issues
LangFlow can be memory-intensive. Ensure Docker has at least 4GB RAM allocated.

### Lost Flows
Flows are stored in the Docker volume. Don't run `docker-compose down -v` unless you want to delete all data.

## Resources

- [LangFlow Documentation](https://docs.langflow.org/)
- [LangFlow GitHub](https://github.com/logspace-ai/langflow)
- [LangFlow Community](https://discord.gg/EqksyE2EX9)
