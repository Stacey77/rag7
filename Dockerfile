# Multi-stage Dockerfile for RAG7 ADK Multi-Agent System

# Stage 1: Base image with Python
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Stage 2: Builder - Install dependencies
FROM base AS builder

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install production dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage 3: Runtime - Minimal production image
FROM base AS runtime

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=appuser:appuser src/ /app/src/
COPY --chown=appuser:appuser litellm_config.yaml /app/

# Create necessary directories
RUN mkdir -p /app/logs && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8080 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]

# Stage 4: Development - Include development tools
FROM runtime AS development

USER root

# Copy dev requirements and install
COPY requirements-dev.txt ./
RUN pip install -r requirements-dev.txt

# Install debugging tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    less \
    htop \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy tests
COPY --chown=appuser:appuser tests/ /app/tests/

USER appuser

# Development command with auto-reload
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
