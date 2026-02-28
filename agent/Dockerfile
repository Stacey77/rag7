FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agent.py .

# Create directories
RUN mkdir -p /backups /restore

# Run agent
CMD ["python", "-u", "agent.py"]
