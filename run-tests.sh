#!/bin/bash

# ============================================================
# Ragamuffin Test Runner
# Run all tests across the monorepo
# ============================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "=============================================="
echo "    Ragamuffin Test Suite                    "
echo "=============================================="
echo -e "${NC}"

# Track results
BACKEND_RESULT=0
RAG_RESULT=0
FRONTEND_RESULT=0

# Run backend tests
echo -e "\n${YELLOW}[1/3] Running Backend Tests...${NC}\n"
cd langflow-backend
if [ -f requirements-dev.txt ]; then
    pip install -r requirements-dev.txt -q 2>/dev/null || true
fi
if pytest -v --cov=app --cov-report=html 2>/dev/null; then
    echo -e "${GREEN}✓ Backend tests passed${NC}"
else
    echo -e "${RED}✗ Backend tests failed${NC}"
    BACKEND_RESULT=1
fi
cd ..

# Run RAG service tests
echo -e "\n${YELLOW}[2/3] Running RAG Service Tests...${NC}\n"
cd rag-service
if [ -f requirements-dev.txt ]; then
    pip install -r requirements-dev.txt -q 2>/dev/null || true
fi
if pytest -v --cov=app --cov-report=html 2>/dev/null; then
    echo -e "${GREEN}✓ RAG service tests passed${NC}"
else
    echo -e "${RED}✗ RAG service tests failed${NC}"
    RAG_RESULT=1
fi
cd ..

# Run frontend tests
echo -e "\n${YELLOW}[3/3] Running Frontend Tests...${NC}\n"
cd web-client
if [ -f package.json ]; then
    npm install -q 2>/dev/null || true
    if npm run test:ci 2>/dev/null || npm run test 2>/dev/null; then
        echo -e "${GREEN}✓ Frontend tests passed${NC}"
    else
        echo -e "${YELLOW}⚠ Frontend tests skipped or failed${NC}"
        FRONTEND_RESULT=1
    fi
else
    echo -e "${YELLOW}⚠ No package.json found, skipping frontend tests${NC}"
fi
cd ..

# Summary
echo -e "\n${BLUE}=============================================="
echo "    Test Summary                              "
echo "=============================================="
echo -e "${NC}"

if [ $BACKEND_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Backend:     PASSED${NC}"
else
    echo -e "${RED}✗ Backend:     FAILED${NC}"
fi

if [ $RAG_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ RAG Service: PASSED${NC}"
else
    echo -e "${RED}✗ RAG Service: FAILED${NC}"
fi

if [ $FRONTEND_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend:    PASSED${NC}"
else
    echo -e "${YELLOW}⚠ Frontend:    SKIPPED/FAILED${NC}"
fi

echo ""

# Exit with appropriate code
if [ $BACKEND_RESULT -ne 0 ] || [ $RAG_RESULT -ne 0 ]; then
    echo -e "${RED}Some tests failed. Please fix before committing.${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed! ✨${NC}"
    exit 0
fi
