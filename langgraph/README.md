# LangGraph

LangGraph is a library for building stateful, multi-actor applications with LLMs.

## Usage

The LangGraph server is accessible at http://localhost:7878 when running via Docker Compose.

## Features

- Graph-based agent orchestration
- Stateful conversations with checkpointing
- Multi-actor coordination
- Human-in-the-loop workflows

## Opening LangGraph UI

1. Start the services:
   ```bash
   docker compose up langgraph
   ```

2. Open your browser to http://localhost:7878

## Creating Graphs

Example graph definition:

```python
from langgraph.graph import StateGraph

# Define your graph
graph = StateGraph()

# Add nodes and edges
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.add_edge("agent", "tools")

# Compile
app = graph.compile()
```

## Security Considerations

⚠️ **Important**: Before deploying to production:

1. **Authentication**: Add authentication to the LangGraph server
2. **HTTPS**: Use TLS/SSL for production deployments
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **Monitoring**: Enable logging and monitoring
5. **Access Control**: Restrict access by IP or VPN

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LANGGRAPH_HOST` | Host to bind to | `0.0.0.0` |
| `LANGGRAPH_PORT` | Port to listen on | `7878` |

## Integration with Ragamuffin

LangGraph can be used alongside LangFlow for more complex agent workflows:

1. Create basic flows in LangFlow (port 7860)
2. Orchestrate multiple flows using LangGraph
3. Execute via the FastAPI backend (port 8000)
4. Monitor and interact through the web client (port 8080)

## Resources

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [LangGraph Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)
