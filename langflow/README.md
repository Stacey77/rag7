# LangFlow Service

## Overview
This directory contains the LangFlow service for the Ragamuffin platform. LangFlow provides a visual interface for designing and testing AI agent workflows.

## What is LangFlow?
LangFlow is a UI for LangChain, designed with react-flow to provide an effortless way to experiment and prototype flows. It offers a drag-and-drop interface for building complex AI workflows.

## Running LangFlow

### With Docker (Recommended)
```bash
# From project root
docker-compose up langflow
```

### Standalone
```bash
pip install langflow
langflow run --host 0.0.0.0 --port 7860
```

## Access
- **URL**: http://localhost:7860
- **Port**: 7860 (configurable in docker-compose.yml)

## Usage

1. **Access UI**: Open http://localhost:7860 in your browser
2. **Create Flows**: Use the drag-and-drop interface to build AI workflows
3. **Test Flows**: Test your flows directly in the LangFlow UI
4. **Export Flows**: Export your flows as JSON files
5. **Save to Backend**: Upload exported JSON to the backend via the AgentBuilder page or API

## Flow Management

### Exporting Flows
1. Design your flow in LangFlow UI
2. Click "Export" button
3. Save the JSON file
4. Upload to backend using `POST /save_flow/` endpoint

### Running Flows
Flows can be executed through:
- LangFlow UI (for testing)
- Backend API `POST /run_flow/` endpoint
- Web Client AgentBuilder page

## Security Considerations

⚠️ **Important Security Notes**:

1. **Authentication**: LangFlow UI has no built-in authentication in this setup
   - Consider adding a reverse proxy with auth
   - Use VPN or firewall rules in production
   - Implement OAuth2 or basic auth

2. **Network Exposure**: 
   - Current setup exposes port 7860 to localhost only
   - Do NOT expose to public internet without authentication
   - Use internal networks in production

3. **Flow Validation**:
   - Review all flows before execution
   - Untrusted flows can execute arbitrary code
   - Implement sandboxing for production

4. **Resource Limits**:
   - LangFlow can consume significant resources
   - Set memory and CPU limits in docker-compose
   - Monitor resource usage

## Configuration

### Environment Variables
Add to docker-compose.yml service definition:

```yaml
environment:
  - LANGFLOW_DATABASE_URL=sqlite:///./langflow.db
  - LANGFLOW_CACHE_TYPE=memory
  - LANGFLOW_LOG_LEVEL=INFO
```

### Resource Limits
Add to docker-compose.yml:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 7860
lsof -i :7860
# Kill process or change port in docker-compose.yml
```

### Container Won't Start
```bash
# Check logs
docker-compose logs langflow

# Rebuild image
docker-compose build --no-cache langflow
docker-compose up langflow
```

### Performance Issues
- Increase memory allocation in docker-compose.yml
- Use faster storage for Docker volumes
- Consider using GPU support for LangChain models

## Advanced Configuration

### Persistent Storage
To persist LangFlow data:

```yaml
volumes:
  - ./langflow-data:/root/.langflow
```

### Custom Components
Place custom components in mounted volume:

```yaml
volumes:
  - ./langflow-components:/app/components
```

## Integration with Backend

The backend service can execute flows programmatically:
1. Backend receives flow JSON via API
2. Backend saves flow to `flows/` directory
3. Backend can execute flow using LangFlow runtime
4. Results returned to frontend

## Resources
- [LangFlow Documentation](https://docs.langflow.org/)
- [LangChain Documentation](https://python.langchain.com/)
- [GitHub Repository](https://github.com/logspace-ai/langflow)

## Next Steps
1. Secure the LangFlow UI
2. Create reusable flow templates
3. Document flow design patterns
4. Implement flow versioning
5. Add flow validation rules
