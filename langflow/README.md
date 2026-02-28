# LangFlow

LangFlow is a visual flow-based builder for LLM applications.

## Usage

The LangFlow UI is accessible at http://localhost:7860 when running via Docker Compose.

## Features

- Visual drag-and-drop interface for building LLM flows
- Export flows as JSON for use with the backend API
- Test flows directly in the UI

## Security Considerations

⚠️ **Important**: Before deploying to production:

1. **Enable Authentication**: LangFlow supports authentication. Configure it before exposing to the internet.
   ```bash
   langflow run --superuser admin --superuser-password <secure-password>
   ```

2. **Secure the UI**: 
   - Use a reverse proxy (nginx, traefik) with SSL/TLS
   - Restrict access by IP or VPN
   - Implement rate limiting

3. **Validate Flows**: 
   - Review all flows before deployment
   - Audit tool and function usage
   - Whitelist approved integrations

4. **Monitor Access**:
   - Enable logging
   - Monitor for suspicious activity
   - Set up alerts for unauthorized access attempts

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LANGFLOW_HOST` | Host to bind to | `0.0.0.0` |
| `LANGFLOW_PORT` | Port to listen on | `7860` |
| `LANGFLOW_WORKERS` | Number of workers | `1` |

## Persisting Data

Flows created in LangFlow should be exported and saved to the backend for persistence.
