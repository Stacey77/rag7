FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install langflow
RUN pip install --no-cache-dir langflow

# Expose port
EXPOSE 7860

# Run langflow
CMD ["langflow", "run", "--host", "0.0.0.0", "--port", "7860"]
