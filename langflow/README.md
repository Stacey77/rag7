# LangFlow Service

This directory contains the LangFlow visual agent builder service.

## What is LangFlow?

LangFlow is a visual programming interface for building LangChain flows. It provides a drag-and-drop interface for:
- Creating AI agent workflows
- Connecting LLMs, tools, and data sources
- Testing and debugging flows visually
- Exporting flows as JSON

## Usage

### Access LangFlow UI
After starting services with `./start-dev.sh`, access LangFlow at:
```
http://localhost:7860
```

### Creating Flows

1. **Design**: Use the visual interface to create your agent flow
2. **Configure**: Set up LLM connections, prompts, and tools
3. **Test**: Run the flow directly in LangFlow
4. **Export**: Download the flow as JSON
5. **Upload**: Use the AgentBuilder page in the web client to upload and manage flows

### Exporting Flows

1. In LangFlow UI, click the **Export** button
2. Choose **JSON** format
3. Save the file
4. Upload it via the AgentBuilder page at http://localhost:8080

## ⚠️ Security Considerations

### Development vs Production

**Current State (Development)**:
- No authentication required
- All features publicly accessible
- Suitable for local development only

**For Production**:
- ✅ Enable authentication (LangFlow supports auth plugins)
- ✅ Restrict network access (use firewall/VPN)
- ✅ Use HTTPS/TLS encryption
- ✅ Implement user management
- ✅ Audit flow execution logs
- ✅ Validate and sandbox untrusted flows

### Securing LangFlow

```yaml
# docker-compose.yml example with auth
environment:
  - LANGFLOW_AUTH_ENABLED=true
  - LANGFLOW_USERNAME=admin
  - LANGFLOW_PASSWORD=your-secure-password
```

**Never expose LangFlow directly to the internet without authentication!**

## Configuration

### Environment Variables

- `LANGFLOW_HOST`: Bind address (default: 0.0.0.0)
- `LANGFLOW_PORT`: Port to run on (default: 7860)
- `LANGFLOW_WORKERS`: Number of worker processes
- `LANGFLOW_DATABASE_URL`: Database connection string (for persistence)

### Persisting LangFlow Data

By default, LangFlow data is stored inside the container. To persist data:

```yaml
volumes:
  - ./langflow-data:/root/.langflow
```

## Troubleshooting

### Port Already in Use
```bash
# Check what's using port 7860
lsof -i :7860

# Change port in docker-compose.yml
ports:
  - "7861:7860"
```

### LangFlow Won't Start
```bash
# Check logs
docker compose logs langflow

# Restart service
docker compose restart langflow
```

### Flow Export Issues
- Ensure flow is saved before exporting
- Check for validation errors in LangFlow UI
- Try exporting individual components first

## Resources

- [LangFlow Documentation](https://docs.langflow.org/)
- [LangFlow GitHub](https://github.com/logspace-ai/langflow)
- [LangChain Documentation](https://docs.langchain.com/)

## Integration with Backend

The backend service (`langflow-backend`) can:
- Load and execute flows exported from LangFlow
- Store flows in the `flows/` directory
- Provide API endpoints for flow management

Upload your exported flows via:
- Web UI: http://localhost:8080 (AgentBuilder page)
- API: `POST http://localhost:8000/save_flow/`

---

**Note**: This service runs in a Docker container and is accessible only on localhost by default. Configure networking and security appropriately for your deployment.
