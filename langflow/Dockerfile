# LangFlow Docker Container

This Dockerfile sets up a LangFlow container for visual AI flow building.

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install LangFlow
RUN pip install --no-cache-dir langflow

# Expose LangFlow port
EXPOSE 7860

# Set environment variables
ENV LANGFLOW_HOST=0.0.0.0
ENV LANGFLOW_PORT=7860

# Create data directory
RUN mkdir -p /app/langflow

# Run LangFlow
CMD ["python", "-m", "langflow", "run", "--host", "0.0.0.0", "--port", "7860"]
