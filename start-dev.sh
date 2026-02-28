#!/bin/bash

# Epic Platform - Start Development Environment
# This script starts all services using Docker Compose

echo "🚀 Starting Epic Platform (Ragamuffin) services..."
echo ""
echo "Services will be available at:"
echo "  - LangFlow UI:   http://localhost:7860"
echo "  - Backend API:   http://localhost:8000"
echo "  - API Docs:      http://localhost:8000/docs"
echo "  - Frontend App:  http://localhost:8080"
echo ""

docker compose up --build

echo ""
echo "✅ Services started successfully!"
