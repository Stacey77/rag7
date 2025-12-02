#!/bin/bash
# Epic Platform - Development Startup Script
# This script starts all services in the Epic Platform using Docker Compose

set -e

echo "🚀 Starting Epic Platform services..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose is not installed. Please install it and try again."
    exit 1
fi

# Create flows directory if it doesn't exist
mkdir -p langflow-backend/flows

# Start all services
echo "📦 Building and starting containers..."
docker-compose up -d --build

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo ""
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "✅ Epic Platform is starting up!"
echo ""
echo "📍 Access the services at:"
echo "   - LangFlow:    http://localhost:7860"
echo "   - Backend API: http://localhost:8000"
echo "   - Web Client:  http://localhost:3000"
echo "   - API Docs:    http://localhost:8000/docs"
echo ""
echo "📝 View logs with: docker-compose logs -f"
echo "🛑 Stop services with: ./stop-dev.sh"
echo ""
