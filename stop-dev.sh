#!/bin/bash

# Epic Platform - Stop Development Environment
# This script stops all services using Docker Compose

echo "🛑 Stopping Epic Platform (Ragamuffin) services..."

docker compose down

echo ""
echo "✅ All services stopped!"
