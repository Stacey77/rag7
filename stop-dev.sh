#!/bin/bash

# Ragamuffin Development Environment - Stop Script
# This script stops all Ragamuffin services

set -e

echo "🛑 Stopping Ragamuffin development environment..."
echo ""

# Stop and remove all services
docker compose down

echo ""
echo "✅ Ragamuffin services stopped successfully!"
echo ""
