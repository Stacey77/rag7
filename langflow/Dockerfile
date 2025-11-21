FROM python:3.11-slim

WORKDIR /app

# Install langflow
RUN pip install --no-cache-dir langflow

# Expose LangFlow port
EXPOSE 7860

# Run LangFlow
CMD ["langflow", "run", "--host", "0.0.0.0", "--port", "7860"]
