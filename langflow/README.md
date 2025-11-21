# LangFlow Service

This directory contains the LangFlow service for the Ragamuffin platform.

## What is LangFlow?

LangFlow is a visual programming interface for building AI agents and workflows. It provides a drag-and-drop interface for creating complex agent interactions without writing code.

## Configuration

The LangFlow service runs on port 7860 and is accessible at:
- http://localhost:7860

## Usage

### Creating Flows

1. Access the LangFlow UI at http://localhost:7860
2. Use the visual editor to create your agent workflow
3. Connect components like LLMs, prompts, tools, and data sources
4. Test your flow directly in the UI
5. Export your flow as JSON for use with the backend API

### Exporting Flows

Flows created in LangFlow can be exported as JSON files and then:
- Saved via the backend API (`POST /save_flow/`)
- Executed via the backend API (`POST /run_flow/`)
- Managed through the frontend UI

## Security Considerations

⚠️ **Important**: The LangFlow UI should be secured in production environments.

### Recommended Security Measures

1. **Authentication**
   - Enable authentication in LangFlow
   - Use environment variables for credentials
   - Integrate with your organization's SSO

2. **Network Security**
   - Run LangFlow behind a reverse proxy
   - Use HTTPS with valid certificates
   - Restrict access to internal networks only

3. **Access Control**
   - Implement role-based access control
   - Limit who can create/modify flows
   - Log all flow creation and modification activities

4. **Flow Validation**
   - Review flows before deployment
   - Restrict available components in production
   - Implement approval workflows for new flows

5. **Resource Limits**
   - Set memory and CPU limits in Docker
   - Implement rate limiting
   - Monitor resource usage

## Environment Variables

The following environment variables can be configured:

- `LANGFLOW_HOST` - Host to bind to (default: 0.0.0.0)
- `LANGFLOW_PORT` - Port to run on (default: 7860)
- `LANGFLOW_DATABASE_URL` - Database connection string
- `LANGFLOW_STORE_ENVIRONMENT_VARIABLES` - Store env vars (default: true)

Example docker-compose configuration:

```yaml
langflow:
  build:
    context: ./langflow
  ports:
    - "7860:7860"
  environment:
    - LANGFLOW_DATABASE_URL=sqlite:///langflow.db
    - LANGFLOW_STORE_ENVIRONMENT_VARIABLES=true
```

## Data Persistence

By default, LangFlow stores data in a local SQLite database. For production:

1. **Use a Production Database**
   - PostgreSQL
   - MySQL
   - Configure via `LANGFLOW_DATABASE_URL`

2. **Backup Strategy**
   - Regular database backups
   - Version control for flows
   - Export flows to external storage

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker compose logs langflow

# Restart service
docker compose restart langflow

# Rebuild from scratch
docker compose up --build langflow
```

### Port Already in Use

```bash
# Check what's using port 7860
lsof -i :7860

# Change port in docker-compose.yml if needed
```

### Connection Issues

```bash
# Test if service is responding
curl http://localhost:7860

# Check network connectivity
docker compose exec langflow ping backend
```

## Advanced Configuration

### Custom Components

You can add custom LangFlow components by:
1. Creating a custom component Python file
2. Mounting it as a volume in docker-compose.yml
3. Restarting the service

### Performance Tuning

For better performance:
- Increase container memory limits
- Use a production database (PostgreSQL)
- Enable caching
- Optimize component configurations

## Resources

- [LangFlow Documentation](https://docs.langflow.org/)
- [LangFlow GitHub](https://github.com/logspace-ai/langflow)
- [LangFlow Community](https://discord.gg/langflow)

## Development

To run LangFlow locally without Docker:

```bash
# Install LangFlow
pip install langflow

# Run with default settings
langflow run

# Run with custom host/port
langflow run --host 0.0.0.0 --port 7860

# Run with specific database
LANGFLOW_DATABASE_URL=postgresql://user:pass@localhost/db langflow run
```

## Notes

- LangFlow flows are stored in its own database
- The backend service can load and execute exported flows
- Flows should be exported as JSON for integration with the backend
- The frontend provides a unified interface for managing flows
