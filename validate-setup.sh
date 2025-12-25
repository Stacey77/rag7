#!/bin/bash
# RAG7 Platform Setup Validation Script

echo "========================================="
echo "  RAG7 Platform Setup Validation"
echo "========================================="
echo ""

PASS=0
WARN=0
FAIL=0

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASS++))
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARN++))
}

fail() {
    echo -e "${RED}❌ $1${NC}"
    ((FAIL++))
}

# 1. Check Backend Dependencies
echo "1. Checking Backend Dependencies..."
if python3 -c "import fastapi" 2>/dev/null; then
    pass "FastAPI installed"
else
    fail "FastAPI not installed - run 'pip install -r requirements.txt'"
fi

if python3 -c "import openai" 2>/dev/null; then
    pass "OpenAI library installed"
else
    fail "OpenAI library not installed"
fi

if python3 -c "import chromadb" 2>/dev/null; then
    pass "ChromaDB installed"
else
    warn "ChromaDB not installed (will use in-memory fallback)"
fi

if python3 -c "import pytest" 2>/dev/null; then
    pass "Pytest installed"
else
    warn "Pytest not installed - run 'pip install pytest'"
fi

echo ""

# 2. Check Frontend Dependencies
echo "2. Checking Frontend Dependencies..."
if [ -d "frontend/node_modules" ]; then
    pass "Frontend node_modules exists"
else
    fail "Frontend dependencies not installed - run 'cd frontend && npm install'"
fi

if [ -f "frontend/package.json" ]; then
    pass "package.json found"
else
    fail "package.json not found"
fi

echo ""

# 3. Check Environment Configuration
echo "3. Checking Environment Configuration..."
if [ -f ".env" ]; then
    pass ".env file exists"
    
    if grep -q "OPENAI_API_KEY=" .env && ! grep -q "OPENAI_API_KEY=$" .env; then
        pass "OPENAI_API_KEY is configured"
    else
        warn "OPENAI_API_KEY not set in .env (required for AI features)"
    fi
    
    if grep -q "SLACK_BOT_TOKEN=" .env; then
        if grep -q "SLACK_BOT_TOKEN=$" .env; then
            warn "SLACK_BOT_TOKEN empty (optional)"
        else
            pass "SLACK_BOT_TOKEN configured"
        fi
    fi
else
    warn ".env file not found - copy from .env.example"
fi

if [ -f ".env.example" ]; then
    pass ".env.example template exists"
else
    fail ".env.example not found"
fi

echo ""

# 4. Check File Structure
echo "4. Checking Project Structure..."
required_files=(
    "README.md"
    "docker-compose.yml"
    "requirements.txt"
    "setup.sh"
    "mockup-gui.html"
    "TROUBLESHOOTING.md"
    "GUI_TESTING_GUIDE.md"
    "src/agent/core.py"
    "src/interfaces/web_api.py"
    "frontend/src/Dashboard.js"
    "frontend/src/FloatingBot.js"
    "tests/test_web_api.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        pass "$file exists"
    else
        fail "$file missing"
    fi
done

echo ""

# 5. Check Running Services
echo "5. Checking Running Services..."
if command -v lsof &> /dev/null; then
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        pass "Backend running on port 8000"
    else
        warn "Backend not running on port 8000"
    fi

    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        pass "Frontend running on port 3000"
    else
        warn "Frontend not running on port 3000"
    fi
else
    warn "lsof not available - cannot check running services"
fi

echo ""

# 6. Run Backend Tests
echo "6. Running Backend Tests..."
if command -v pytest &> /dev/null; then
    if pytest tests/ -q --tb=no 2>&1 | grep -q "passed"; then
        test_count=$(pytest tests/ -q --tb=no 2>&1 | grep "passed" | awk '{print $1}')
        pass "Backend tests passing ($test_count tests)"
    else
        warn "Backend tests failed or no tests found"
    fi
else
    warn "pytest not available - cannot run tests"
fi

echo ""

# 7. Check Frontend Tests
echo "7. Checking Frontend Test Files..."
frontend_tests=(
    "frontend/src/Dashboard.test.js"
    "frontend/src/FloatingBot.test.js"
    "frontend/src/ChatInterface.test.js"
    "frontend/src/setupTests.js"
)

for test_file in "${frontend_tests[@]}"; do
    if [ -f "$test_file" ]; then
        pass "$(basename $test_file) exists"
    else
        warn "$(basename $test_file) not found"
    fi
done

echo ""

# 8. Check Documentation
echo "8. Checking Documentation..."
docs=(
    "README.md"
    "QUICKSTART.md"
    "DEVELOPMENT.md"
    "DASHBOARD_GUIDE.md"
    "FLOATING_BOT_GUIDE.md"
    "MOCKUP_GUIDE.md"
    "TROUBLESHOOTING.md"
    "GUI_TESTING_GUIDE.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        pass "$doc present"
    else
        warn "$doc missing"
    fi
done

echo ""

# 9. Check Docker Setup
echo "9. Checking Docker Configuration..."
if [ -f "docker-compose.yml" ]; then
    pass "docker-compose.yml exists"
else
    fail "docker-compose.yml not found"
fi

if command -v docker &> /dev/null; then
    pass "Docker is installed"
else
    warn "Docker not installed (optional)"
fi

if command -v docker-compose &> /dev/null; then
    pass "Docker Compose is installed"
else
    warn "Docker Compose not installed (optional)"
fi

echo ""

# Summary
echo "========================================="
echo "  Validation Summary"
echo "========================================="
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${YELLOW}Warnings: $WARN${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ Setup validation successful!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start backend: uvicorn src.interfaces.web_api:app --reload"
    echo "2. Start frontend: cd frontend && npm start"
    echo "3. Visit: http://localhost:3000"
    echo "4. Run tests: npm test (in frontend/) and pytest tests/"
    exit 0
else
    echo -e "${RED}❌ Setup validation found issues${NC}"
    echo ""
    echo "Please fix the failed items above and run validation again."
    echo "See TROUBLESHOOTING.md for help."
    exit 1
fi
