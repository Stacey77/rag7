# LangFlow Service

This directory contains the Dockerfile for the LangFlow service, which provides a visual workflow builder for creating AI agent flows.

## Overview

LangFlow is a low-code platform for building and testing language model workflows visually. It runs on port 7860 and provides a drag-and-drop interface for creating agent pipelines.

## Features

- Visual workflow editor
- Pre-built components for common LLM operations
- Export workflows as JSON
- Test and debug flows interactively
- Integration with various LLM providers

## Running LangFlow

### With Docker Compose (Recommended)

From the repository root:
```bash
docker compose up langflow
```

### Standalone

```bash
docker build -t ragamuffin-langflow .
docker run -p 7860:7860 ragamuffin-langflow
```

### Local Development

```bash
pip install langflow
langflow run --host 0.0.0.0 --port 7860
```

## Accessing LangFlow

Once running, access the LangFlow UI at:
- http://localhost:7860

## Creating Workflows

1. Open the LangFlow UI
2. Drag and drop components to create your workflow
3. Connect components to define data flow
4. Configure component parameters
5. Test the workflow using the built-in chat interface
6. Export the workflow as JSON

## Exporting Flows

Workflows can be exported as JSON files from the LangFlow UI:
1. Click the export button in the UI
2. Save the JSON file
3. Upload it to the backend via the Ragamuffin frontend or API

## Data Persistence

LangFlow data is persisted in a Docker volume (`langflow-data`) which includes:
- Database (SQLite by default)
- Configuration
- User settings

## Security Considerations

⚠️ **Important Security Notes**:

1. **Authentication**: By default, LangFlow has no authentication. Do not expose it directly to the internet.
2. **Input Validation**: Workflows can execute arbitrary code. Validate all inputs.
3. **Sandboxing**: Consider running LangFlow in a sandboxed environment for untrusted workflows.
4. **API Keys**: Never hardcode API keys in workflows. Use environment variables.
5. **Network Access**: Restrict network access to trusted services only.
6. **Rate Limiting**: Implement rate limiting to prevent abuse.

## Production Deployment

For production use:

1. **Enable Authentication**: Configure authentication in LangFlow settings
2. **Use HTTPS**: Place behind a reverse proxy with SSL/TLS
3. **Persistent Storage**: Use a production database instead of SQLite
4. **Monitoring**: Add logging and monitoring for workflow executions
5. **Resource Limits**: Set CPU and memory limits in Docker
6. **Backup**: Regular backups of the database and configurations

Example with resource limits in docker-compose.yml:
```yaml
langflow:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
```

## Environment Variables

Available environment variables:
- `LANGFLOW_DATABASE_URL`: Database connection string (default: sqlite)
- `LANGFLOW_CONFIG_DIR`: Configuration directory path
- `LANGFLOW_LOG_LEVEL`: Logging level (debug, info, warning, error)

## Troubleshooting

### Port Already in Use

Change the host port in docker-compose.yml:
```yaml
ports:
  - "7861:7860"
```

### Database Errors

Reset the database:
```bash
docker compose down -v
docker compose up langflow
```

### Performance Issues

- Increase Docker resource allocation
- Use a production database (PostgreSQL)
- Optimize complex workflows

## Integration with Backend

The backend service connects to LangFlow to execute workflows programmatically. The backend uses the LangFlow hostname and port configured in docker-compose.yml:
- `LANGFLOW_HOST=langflow`
- `LANGFLOW_PORT=7860`

## Further Reading

- [LangFlow Documentation](https://docs.langflow.org/)
- [LangFlow GitHub](https://github.com/logspace-ai/langflow)
- Backend API integration: See `/langflow-backend/README.md`

## Support

For LangFlow-specific issues:
- Check the official documentation
- Review GitHub issues
- Join the LangFlow community

For Ragamuffin integration issues:
- Check the backend logs: `docker compose logs backend`
- Review API documentation: http://localhost:8000/docs
