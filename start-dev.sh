#!/bin/bash

# Ragamuffin Platform - Start Development Environment
# This script starts all services using Docker Compose

echo "🚀 Starting Ragamuffin Platform with Milvus & n8n..."
echo "===================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    exit 1
fi

# Create required directories
mkdir -p langflow-backend/flows
mkdir -p rag-service/data
echo "✓ Data directories ready"

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file. Edit it to add your OPENAI_API_KEY if needed."
fi

# Start services
echo ""
echo "Building and starting services..."
echo "This may take several minutes on first run (downloading images)..."
echo ""
echo "Services starting:"
echo "  • Etcd (Milvus metadata)"
echo "  • MinIO (Milvus storage)"
echo "  • Milvus (vector database)"
echo "  • n8n (workflow automation)"
echo "  • RAG Service (multimodal RAG)"
echo "  • LangFlow (flow designer)"
echo "  • Backend (API)"
echo "  • Frontend (UI)"
echo ""

docker-compose up --build

echo ""
echo "===================================================="
echo "✓ Ragamuffin Platform started!"
echo ""
echo "Access points:"
echo "  • Frontend:       http://localhost:8080"
echo "  • Backend API:    http://localhost:8000/docs"
echo "  • RAG Service:    http://localhost:8001/docs"
echo "  • LangFlow:       http://localhost:7860"
echo "  • n8n:            http://localhost:5678 (admin/admin)"
echo "  • MinIO Console:  http://localhost:9001 (minioadmin/minioadmin)"
echo ""
echo "Press Ctrl+C to stop all services"
echo "Or run ./stop-dev.sh in another terminal"
