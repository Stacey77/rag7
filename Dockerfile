FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create directories for credentials and data
RUN mkdir -p /app/credentials /app/chroma_data

EXPOSE 8000

CMD ["uvicorn", "src.interfaces.web_api:app", "--host", "0.0.0.0", "--port", "8000"]
