# LangFlow Container

This directory contains the Docker configuration for the LangFlow service.

## What is LangFlow?

LangFlow is a visual framework for building AI applications. It provides a drag-and-drop interface for creating complex AI workflows using LangChain components.

## Usage

### Running LangFlow

LangFlow is automatically started when you run the entire platform:

```bash
# From repository root
./start-dev.sh
```

Or run LangFlow independently:

```bash
# From repository root
docker-compose up -d langflow
```

### Accessing LangFlow

Once running, access LangFlow at:
- **URL**: http://localhost:7860
- **Container**: epic-langflow

### Building Flows

1. Open http://localhost:7860 in your browser
2. Use the visual editor to create your flow:
   - Add components from the sidebar
   - Connect components by dragging between ports
   - Configure component parameters
3. Test your flow in the LangFlow interface
4. Export the flow JSON for use with the backend API

### Flow Components

LangFlow provides various components:
- **LLMs**: OpenAI, Anthropic, HuggingFace models
- **Chains**: Sequential chains, conversational chains
- **Agents**: ReAct agents, conversational agents
- **Memory**: Conversation buffers, entity memory
- **Tools**: Python REPL, web search, calculators
- **Vector Stores**: Chroma, Pinecone, FAISS
- **Embeddings**: OpenAI embeddings, HuggingFace embeddings

### Exporting Flows

1. Design your flow in LangFlow
2. Click "Export" button
3. Download the JSON file
4. Save via the backend API or web client

## Configuration

### Environment Variables

- `LANGFLOW_HOST`: Host to bind to (default: 0.0.0.0)
- `LANGFLOW_PORT`: Port to listen on (default: 7860)
- `LANGFLOW_DATABASE_URL`: Database connection string

### Data Persistence

LangFlow data is stored in the `langflow_data` Docker volume:
- Database files
- Configuration
- Uploaded files

### Ports

- **7860**: LangFlow web interface

## Integration with Backend

The FastAPI backend connects to LangFlow to:
1. Execute flows programmatically
2. Validate flow configurations
3. Monitor flow execution

The backend uses the LangFlow Python API when available.

## Development

### Running Locally

```bash
# Install LangFlow
pip install langflow

# Run LangFlow
langflow run --host 0.0.0.0 --port 7860
```

### Custom Components

To add custom LangFlow components:

1. Create component Python file
2. Mount into container via docker-compose.yml:
   ```yaml
   volumes:
     - ./custom_components:/app/custom_components
   ```
3. LangFlow will auto-discover components

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs -f langflow

# Rebuild container
docker-compose up -d --build langflow
```

### Port Conflict

If port 7860 is in use, change the mapping in docker-compose.yml:

```yaml
ports:
  - "7861:7860"
```

### Database Issues

Reset the database:

```bash
# Remove volume and restart
docker-compose down -v
docker-compose up -d langflow
```

## Resources

- [LangFlow Documentation](https://docs.langflow.org/)
- [LangFlow GitHub](https://github.com/logspace-ai/langflow)
- [LangChain Documentation](https://python.langchain.com/)

## Security Notes

⚠️ **Production Considerations**:

1. **Authentication**: Enable authentication in LangFlow settings
2. **Network**: Restrict access to trusted networks only
3. **API Keys**: Use environment variables for API keys, never hardcode
4. **HTTPS**: Use HTTPS/TLS for production deployments
5. **Updates**: Keep LangFlow updated for security patches

## Support

For LangFlow-specific issues:
- Check LangFlow logs: `docker-compose logs -f langflow`
- Visit LangFlow documentation
- Open issue on LangFlow GitHub

For platform integration issues:
- Check backend logs: `docker-compose logs -f backend`
- Review backend API documentation
- Open issue in this repository
