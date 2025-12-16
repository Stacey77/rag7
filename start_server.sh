#!/bin/bash
# Start the RAG7 API server

set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Dependencies not installed. Installing..."
    pip install -r requirements.txt
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found. Using .env.example values"
    echo "Please create a .env file with your configuration"
    export JWT_SECRET="temporary-secret-key-$(openssl rand -hex 16)"
    export JWT_ALGORITHM="HS256"
    export ACCESS_TOKEN_EXPIRE_MINUTES="30"
else
    echo "Loading configuration from .env file"
    set -a
    source .env
    set +a
fi

# Verify JWT_SECRET is set and secure
if [ -z "$JWT_SECRET" ] || [ "$JWT_SECRET" = "your-secret-key-here-replace-in-production" ]; then
    echo "ERROR: JWT_SECRET is not set or using default value"
    echo "Please set a secure JWT_SECRET in your .env file"
    echo "Generate one with: openssl rand -hex 32"
    exit 1
fi

# Start the server
echo "Starting RAG7 API server..."
echo "Host: ${APP_HOST:-0.0.0.0}"
echo "Port: ${APP_PORT:-8000}"
echo

python -m src.interfaces.web_api
