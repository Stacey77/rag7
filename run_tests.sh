#!/bin/bash

# Run all tests for the RAG7 project

set -e

echo "========================================="
echo "Running Backend Tests"
echo "========================================="

cd backend
source venv/bin/activate
PYTHONPATH=$(pwd) pytest -v
deactivate

echo ""
echo "========================================="
echo "All tests passed successfully!"
echo "========================================="
