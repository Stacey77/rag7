# LangFlow Service

This directory contains the LangFlow service configuration for the Epic Platform.

## Overview

LangFlow is a visual workflow builder for creating AI agent flows. It provides a drag-and-drop interface for connecting components like LLMs, prompts, tools, and data sources.

## Service Details

- **Port**: 7860
- **Base Image**: python:3.11-slim
- **Command**: `langflow run --host 0.0.0.0 --port 7860`

## Accessing LangFlow

Once the services are running, access LangFlow at:
```
http://localhost:7860
```

## Creating Workflows

1. Open LangFlow UI
2. Use the visual editor to create your workflow
3. Connect components (LLMs, prompts, tools, etc.)
4. Test your flow within LangFlow
5. Export as JSON for use with the backend API

## Exporting Flows

To export a flow:
1. Click the "Export" button in LangFlow UI
2. Save the JSON file
3. Upload to the backend via:
   - Web Client Agent Builder page
   - Backend API `/save_flow/` endpoint
   - Direct file placement in `langflow-backend/flows/`

## Security Considerations

### ⚠️ Development Mode Warning

The LangFlow UI is currently **open and unsecured** for development convenience.

### 🔒 Production Recommendations

Before deploying to production:

1. **Enable Authentication**
   - Configure LangFlow authentication
   - Use environment variables for credentials
   - Integrate with OAuth/SSO provider

2. **Network Security**
   - Do not expose port 7860 publicly
   - Use reverse proxy with authentication
   - Implement rate limiting

3. **Access Control**
   - Restrict access to authorized users only
   - Implement audit logging
   - Monitor for suspicious activity

4. **Data Protection**
   - Encrypt sensitive data in flows
   - Use secrets management for API keys
   - Implement data retention policies

## Configuration

### Environment Variables

The LangFlow service supports these environment variables:

- `LANGFLOW_HOST`: Host to bind to (default: 0.0.0.0)
- `LANGFLOW_PORT`: Port to listen on (default: 7860)
- `LANGFLOW_DATABASE_URL`: Database connection string (optional)
- `LANGFLOW_SAVE_DB`: Save flows to database (optional)

### Custom Configuration

To customize LangFlow configuration, modify the Dockerfile or add environment variables in `docker-compose.yml`:

```yaml
langflow:
  environment:
    - LANGFLOW_HOST=0.0.0.0
    - LANGFLOW_PORT=7860
    - LANGFLOW_DATABASE_URL=postgresql://user:pass@db:5432/langflow
```

## Troubleshooting

### Service Won't Start

Check logs:
```bash
docker compose logs langflow
```

Common issues:
- Port 7860 already in use
- Insufficient memory
- Network connectivity issues

### Can't Access UI

1. Verify service is running: `docker compose ps`
2. Check health status: `curl http://localhost:7860/health`
3. Review logs: `docker compose logs langflow`
4. Ensure no firewall blocking port 7860

### Flow Export Fails

- Ensure flow is saved in LangFlow first
- Check browser console for errors
- Verify sufficient disk space
- Review LangFlow logs for errors

## Advanced Usage

### Custom Components

Add custom LangFlow components by extending the Dockerfile:

```dockerfile
COPY ./custom_components /app/custom_components
RUN pip install -e /app/custom_components
```

### Database Integration

For production, use a persistent database:

```yaml
langflow:
  environment:
    - LANGFLOW_DATABASE_URL=postgresql://user:pass@db:5432/langflow
    - LANGFLOW_SAVE_DB=true
```

### Volume Mounting

Mount custom directories for components or data:

```yaml
langflow:
  volumes:
    - ./custom_components:/app/custom_components
    - ./flows:/app/flows
```

## Resources

- [LangFlow Documentation](https://docs.langflow.org/)
- [LangFlow GitHub](https://github.com/logspace-ai/langflow)
- [LangFlow Community](https://discord.gg/langflow)

## Best Practices

1. **Version Control**: Export and version control your flows
2. **Testing**: Test flows thoroughly in LangFlow before production
3. **Documentation**: Document complex flows with descriptions
4. **Modularity**: Break complex flows into reusable components
5. **Security**: Never commit API keys or sensitive data in flows

## Support

For LangFlow-specific issues:
- Check LangFlow documentation
- Review GitHub issues
- Ask in community Discord

For integration issues with Epic Platform:
- Check backend logs
- Review docker-compose configuration
- Open issue on Epic Platform repository
