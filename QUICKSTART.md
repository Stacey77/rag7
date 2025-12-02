# Quick Start Guide

This guide gets you up and running with the RAG7 AI Agent Platform in minutes.

## Prerequisites

- Python 3.11+ and Node.js 18+ (for manual setup)
- OR Docker & Docker Compose (for containerized setup)
- OpenAI API key (get one at https://platform.openai.com/api-keys)
- (Optional) Slack Bot Token for Slack integration

## 🚀 Super Quick Setup (Automated)

### Use the Setup Script

```bash
# Clone the repository
git clone https://github.com/Stacey77/rag7.git
cd rag7

# Run the automated setup script
chmod +x setup.sh
./setup.sh
```

The script will:
1. Check if you have the required tools
2. Create `.env` file if needed
3. Let you choose Docker or Manual setup
4. Install all dependencies
5. Start the services

**Then visit http://localhost:3000 to see the dashboard!**

---

## 📝 Manual Setup (5 Minutes)

### 1. Clone and Configure

```bash
# Clone the repository
git clone https://github.com/Stacey77/rag7.git
cd rag7

# Copy environment template
cp .env.example .env
```

### 2. Add Your API Key

Edit `.env` and add at minimum:

```bash
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

### 3. Choose Your Setup Method

#### Option A: Docker Compose (Recommended)

```bash
docker-compose up --build
```

This starts:
- 🚀 Backend API on http://localhost:8000
- 🎨 Frontend UI on http://localhost:3000
- 💾 ChromaDB on http://localhost:8001
- 🔴 Redis on localhost:6379

#### Option B: Manual (No Docker)

**Terminal 1 - Backend:**
```bash
pip install -r requirements.txt
uvicorn src.interfaces.web_api:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm start
```

### 4. Open the Platform

Visit http://localhost:3000 in your browser.

You should see the RAG7 AI Agent Platform interface!

### 5. Test It Out

Try these messages in the chat:

```
Hello! What can you do?
```

```
What integrations are available?
```

## Without Docker (Alternative)

If you prefer to run without Docker:

### Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the API server
uvicorn src.interfaces.web_api:app --reload
```

Backend will be available at http://localhost:8000

### Frontend

```bash
# In a separate terminal
cd frontend

# Install Node dependencies
npm install

# Start development server
npm start
```

Frontend will be available at http://localhost:3000

## Adding Slack Integration

To enable Slack message sending:

### 1. Create a Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name your app (e.g., "RAG7 Agent")
4. Select your workspace

### 2. Add Bot Permissions

1. Go to "OAuth & Permissions"
2. Add these Bot Token Scopes:
   - `chat:write`
   - `channels:read`
   - `users:read`
3. Click "Install to Workspace"
4. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### 3. Configure in .env

Add to your `.env`:

```bash
SLACK_BOT_TOKEN=xoxb-your-token-here
```

### 4. Restart and Test

```bash
docker-compose restart api
```

Then try in chat:

```
Send a message to #general saying "Hello from RAG7!"
```

## API Endpoints

### Interactive Docs

Visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

```bash
# Health check
curl http://localhost:8000/health

# List integrations
curl http://localhost:8000/integrations

# List available functions
curl http://localhost:8000/functions

# Send a chat message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What can you do?"}'
```

## Troubleshooting

### API won't start

**Problem:** Error about OpenAI API key

**Solution:** Make sure `OPENAI_API_KEY` is set in `.env`

### Frontend can't connect

**Problem:** "Waiting for connection..." in UI

**Solution:** 
1. Check backend is running: `curl http://localhost:8000/health`
2. Check Docker logs: `docker-compose logs api`
3. Verify ports aren't in use: `lsof -i :8000`

### ChromaDB connection fails

**Problem:** ChromaDB errors in logs

**Solution:** ChromaDB is optional - the system will fall back to in-memory storage automatically. No action needed.

### Slack integration not working

**Problem:** "Slack not configured" error

**Solution:**
1. Verify `SLACK_BOT_TOKEN` in `.env`
2. Check token starts with `xoxb-`
3. Restart: `docker-compose restart api`
4. Verify integration health: `curl http://localhost:8000/integrations`

## Next Steps

- 📖 Read the full [README.md](README.md) for detailed setup
- 🛠️ See [DEVELOPMENT.md](DEVELOPMENT.md) to add new integrations
- 🔧 Configure Gmail and Notion integrations
- 🧪 Run tests: `pytest tests/ -v`
- 🚀 Deploy to production (see DEVELOPMENT.md)

## Common Usage Examples

### Ask the agent about capabilities

```
What integrations do you have access to?
```

### Send a Slack message (if configured)

```
Send "Meeting at 3pm" to #general
```

### Ask about configuration

```
What environment variables do I need to set?
```

### Test function calling

```
List all Slack channels
```

## Environment Variables Reference

### Required

- `OPENAI_API_KEY` - Your OpenAI API key

### Optional Integrations

- `SLACK_BOT_TOKEN` - Slack bot token for messaging
- `GMAIL_CREDENTIALS_FILE` - Path to Gmail OAuth credentials
- `GMAIL_SMTP_USER` - Gmail address for SMTP
- `GMAIL_SMTP_PASSWORD` - Gmail app password
- `NOTION_API_KEY` - Notion integration token
- `NOTION_DATABASE_ID` - Default Notion database

### Infrastructure

- `DATABASE_URL` - Database connection (default: SQLite)
- `REDIS_URL` - Redis connection (default: redis://localhost:6379/0)
- `CHROMA_HOST` - ChromaDB host (default: localhost)
- `CHROMA_PORT` - ChromaDB port (default: 8000)

See `.env.example` for all available options.

## Support

- 📝 Check [README.md](README.md) for detailed documentation
- 🐛 Open an issue on GitHub for bugs
- 💬 Contribute improvements via Pull Requests

---

Enjoy building with RAG7! 🤖✨
