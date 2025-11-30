FROM python:3.11-slim

WORKDIR /app

# Install LangFlow
RUN pip install --no-cache-dir langflow

# Expose port
EXPOSE 7860

# Run LangFlow
CMD ["langflow", "run", "--host", "0.0.0.0", "--port", "7860"]
