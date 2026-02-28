#!/bin/bash
# Stop Ragamuffin production environment

echo "Stopping Ragamuffin production services..."
docker compose -f docker-compose.prod.yml down

echo "✅ Ragamuffin stopped successfully!"
