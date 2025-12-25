# Troubleshooting Guide

This guide helps resolve common issues when setting up and running the RAG7 AI Agent Platform.

## Table of Contents
- [404 Error When Accessing Frontend](#404-error-when-accessing-frontend)
- [Backend Not Starting](#backend-not-starting)
- [Docker Issues](#docker-issues)
- [Dependency Problems](#dependency-problems)
- [WebSocket Connection Failures](#websocket-connection-failures)
- [Integration Issues](#integration-issues)

---

## 404 Error When Accessing Frontend

### Problem
When you visit `http://localhost:3000`, you get a 404 error or blank page.

### Causes & Solutions

#### 1. Frontend Dependencies Not Installed

**Check:**
```bash
cd frontend
ls node_modules/
```

**Fix:**
```bash
cd frontend
npm install
npm start
```

#### 2. Frontend Not Running

**Check:**
```bash
# See if port 3000 is in use
lsof -i :3000
# or
netstat -tuln | grep 3000
```

**Fix:**
```bash
cd frontend
npm start
```

You should see:
```
Compiled successfully!

You can now view rag7-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

#### 3. Using Docker Compose (Port Not Exposed)

The current `docker-compose.yml` doesn't include the frontend service. You have two options:

**Option A: Run Frontend Locally** (Recommended for development)
```bash
# Terminal 1: Start backend services
docker-compose up

# Terminal 2: Start frontend
cd frontend
npm install
npm start
```

**Option B: Add Frontend to Docker Compose**

Add this to your `docker-compose.yml`:

```yaml
  # React Frontend (add this service)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
    depends_on:
      - api
    command: npm start
    networks:
      - rag7-network
```

Then run:
```bash
docker-compose up --build
```

---

## Backend Not Starting

### Problem
Backend API at `http://localhost:8000` is not accessible.

### Solutions

#### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Environment Variables Missing

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and add your `OPENAI_API_KEY`:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

#### 3. Run Backend Manually

```bash
# From project root
uvicorn src.interfaces.web_api:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Check Port Availability

```bash
lsof -i :8000
```

If port is in use, kill the process or use a different port:
```bash
uvicorn src.interfaces.web_api:app --reload --port 8001
```

---

## Docker Issues

### Problem: Services Won't Start

#### Check Docker Status
```bash
docker ps
docker-compose ps
```

#### View Logs
```bash
docker-compose logs api
docker-compose logs redis
docker-compose logs chromadb
```

#### Clean Rebuild
```bash
# Stop everything
docker-compose down

# Remove volumes
docker-compose down -v

# Rebuild and start
docker-compose up --build
```

### Problem: Permission Issues

```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Or run with sudo
sudo docker-compose up
```

---

## Dependency Problems

### Frontend Dependencies

#### Problem: npm install fails

**Solution 1: Clear cache**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Solution 2: Use specific Node version**
```bash
# Install nvm if needed
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Use Node 18
nvm install 18
nvm use 18
cd frontend
npm install
```

### Backend Dependencies

#### Problem: pip install fails

**Solution 1: Upgrade pip**
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Solution 2: Use virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## WebSocket Connection Failures

### Problem
Floating bot or chat shows connection errors.

### Solutions

#### 1. Check Backend is Running
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "agent_ready": true,
  "integrations": ["slack", "gmail", "notion"]
}
```

#### 2. CORS Issues

If you see CORS errors in browser console, verify the backend CORS settings in `src/interfaces/web_api.py`.

#### 3. WebSocket Not Available

The frontend will automatically fall back to REST API if WebSocket fails. Check browser console for:
```
WebSocket connection error: ...
Falling back to REST API
```

---

## Integration Issues

### Slack Integration Not Working

#### Check Token
```bash
# In .env file
SLACK_BOT_TOKEN=xoxb-your-real-token-here
```

#### Test Slack Connection
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List my Slack channels"}'
```

### OpenAI API Errors

#### Problem: "No API key provided"

**Solution:**
```bash
# Check .env file
cat .env | grep OPENAI_API_KEY

# Should show: OPENAI_API_KEY=sk-...
```

#### Problem: Rate limit errors

**Solution:** Wait a few seconds between requests or upgrade your OpenAI plan.

---

## Quick Diagnosis Checklist

Run these commands to check your setup:

```bash
# 1. Check Python version (need 3.8+)
python --version

# 2. Check Node version (need 16+)
node --version

# 3. Check if backend dependencies installed
pip list | grep fastapi

# 4. Check if frontend dependencies installed
ls frontend/node_modules/ | head

# 5. Check if .env exists
ls -la .env

# 6. Test backend health
curl http://localhost:8000/health

# 7. Check running processes
ps aux | grep -E "(uvicorn|node|npm)"

# 8. Check ports
lsof -i :3000
lsof -i :8000
```

---

## Complete Fresh Setup

If nothing works, start from scratch:

```bash
# 1. Clean everything
docker-compose down -v
cd frontend && rm -rf node_modules package-lock.json
cd ..
rm -rf __pycache__ **/__pycache__

# 2. Set up Python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Set up Frontend
cd frontend
npm install
cd ..

# 4. Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 5. Start backend
uvicorn src.interfaces.web_api:app --reload &

# 6. Start frontend (in new terminal)
cd frontend
npm start
```

Visit:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Still Having Issues?

### Collect Debug Information

```bash
# Create debug log
cat > debug_info.txt << EOF
Python Version: $(python --version)
Node Version: $(node --version)
OS: $(uname -a)
Docker: $(docker --version)

Backend Running:
$(curl -s http://localhost:8000/health || echo "Backend not running")

Frontend Files:
$(ls frontend/src/)

Environment:
$(cat .env | grep -v "API_KEY" || echo "No .env file")
EOF

cat debug_info.txt
```

### Check the Logs

**Backend Logs:**
```bash
# If running with uvicorn
tail -f uvicorn.log

# If running with docker
docker-compose logs -f api
```

**Frontend Logs:**
Check browser console (F12) for JavaScript errors.

---

## Common Error Messages

### "Module not found: Error: Can't resolve 'Dashboard'"

**Fix:**
```bash
cd frontend
npm install
```

### "Connection refused" when accessing backend

**Fix:**
```bash
# Make sure backend is running
uvicorn src.interfaces.web_api:app --reload
```

### "Cannot find module 'react'"

**Fix:**
```bash
cd frontend
rm -rf node_modules
npm install
```

### "ImportError: No module named 'fastapi'"

**Fix:**
```bash
pip install -r requirements.txt
```

---

## Getting Help

If you're still stuck:

1. **Check the README.md** for setup instructions
2. **Review QUICKSTART.md** for simplified steps
3. **Examine the logs** for specific error messages
4. **Try the Fresh Setup** procedure above
5. **Open an issue** on GitHub with:
   - The debug_info.txt output
   - Exact error messages
   - Steps to reproduce

---

## Success Indicators

When everything is working, you should see:

✅ **Backend** - Visit http://localhost:8000/docs
- Should see FastAPI Swagger UI
- Health endpoint returns `{"status": "healthy"}`

✅ **Frontend** - Visit http://localhost:3000
- Dashboard loads with sidebar
- Can navigate between Chat, Integrations, Analytics, Settings
- Floating bot button visible in bottom-right

✅ **Chat** - Try sending a message
- Type "Hello" in chat
- Get response from AI agent
- See response in both dashboard and floating bot

✅ **Integrations** - Check status
- Navigate to Integrations view
- See cards for Slack, Gmail, Notion
- Health indicators show connection status

That's it! You're ready to use the RAG7 AI Agent Platform! 🚀
