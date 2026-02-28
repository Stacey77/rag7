FROM python:3.11-slim

WORKDIR /app

# Install LangGraph and dependencies
RUN pip install --no-cache-dir langgraph langgraph-cli

# Expose port
EXPOSE 7878

# Run LangGraph server
CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "7878"]
