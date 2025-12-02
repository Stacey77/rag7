# RAG7 AI Agent Platform 🤖

A production-ready conversational AI agent platform with integrations for Slack, Gmail, and Notion. Built with FastAPI, React, and OpenAI function calling.

## ✨ New: Floating Bot Widget

The platform now includes a **floating bot widget** that provides real-time conversations from anywhere on the page! Click the floating button in the bottom-right corner to start chatting with the AI assistant.

**Features:**
- 💬 Real-time WebSocket communication
- 🎨 Sleek, modern UI with animations
- 📱 Fully responsive design
- ⚡ Function call visualization
- 🔄 Auto-reconnect on disconnect
- 🗑️ Clear chat history
- 🎯 Compact and non-intrusive

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│              WebSocket & REST API Communication              │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Conversational Agent (OpenAI GPT-4)            │ │
│  │              Function Calling Router                    │ │
│  └─────┬──────────────────────────────────┬───────────────┘ │
│        │                                   │                 │
│  ┌─────▼─────────┐  ┌──────────────┐  ┌──▼──────────────┐  │
│  │  Agent Memory │  │ Integrations │  │  Configuration  │  │
│  │   (ChromaDB)  │  │   Manager    │  │    Manager      │  │
│  └───────────────┘  └──────┬───────┘  └─────────────────┘  │
└─────────────────────────────┼──────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    ┌────▼─────┐       ┌──────▼──────┐     ┌─────▼──────┐
    │  Slack   │       │   Gmail     │     │   Notion   │
    │   SDK    │       │     API     │     │    API     │
    └──────────┘       └─────────────┘     └────────────┘
```

## ✨ Features

- **Conversational AI**: Natural language interface powered by OpenAI GPT-4
- **Function Calling**: Automatic tool execution based on user intent
- **Full GUI Dashboard**: 
  - 🖥️ Comprehensive dashboard with navigation
  - 💬 Dedicated chat interface view
  - 🔌 Integrations management panel
  - 📊 Analytics and monitoring
  - ⚙️ Settings and configuration
- **Floating Bot Widget**: Always-available compact chat
- **Dual UI Modes**: Use full dashboard OR floating widget independently
- **Multi-Integration Support**: 
  - 📱 Slack: Send messages, list channels
  - 📧 Gmail: Send/read emails (OAuth2 or SMTP)
  - 📝 Notion: Create/update pages, query databases
- **Memory Management**: Conversation context with ChromaDB vector storage
- **REST & WebSocket APIs**: Flexible communication methods
- **Docker Compose**: One-command deployment
- **React Frontend**: Modern, responsive interfaces
- **CI/CD**: GitHub Actions for automated testing

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- OpenAI API key

### 1. Clone and Setup

```bash
git clone https://github.com/Stacey77/rag7.git
cd rag7
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional integrations (configure as needed)
SLACK_BOT_TOKEN=xoxb-your-token
GMAIL_CREDENTIALS_FILE=path/to/credentials.json
NOTION_API_KEY=secret_your-key
```

### 3. Run with Docker Compose

```bash
docker-compose up --build
```

This starts:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- ChromaDB: http://localhost:8001
- Redis: localhost:6379

### 4. Or Run Manually

**Backend:**
```bash
pip install -r requirements.txt
uvicorn src.interfaces.web_api:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

### 5. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'

# List integrations
curl http://localhost:8000/integrations
```

## 🔧 Integration Setup

### Slack Integration

1. **Create Slack App**: https://api.slack.com/apps
2. **Add Bot Token Scopes**:
   - `chat:write` - Send messages
   - `channels:read` - List channels
   - `users:read` - Read user info
3. **Install to Workspace**: Copy "Bot User OAuth Token"
4. **Add to .env**: `SLACK_BOT_TOKEN=xoxb-...`

📚 [Slack API Documentation](https://api.slack.com/docs)

### Gmail Integration

**Option 1: OAuth 2.0 (Recommended)**

1. **Enable Gmail API**: [Google Cloud Console](https://console.cloud.google.com/)
2. **Create OAuth Credentials**: Download `credentials.json`
3. **Add to .env**:
   ```
   GMAIL_CREDENTIALS_FILE=./credentials/credentials.json
   GMAIL_TOKEN_FILE=./credentials/token.json
   ```
4. **First Run**: Will prompt for authorization in browser

**Option 2: SMTP with App Password**

1. **Enable 2FA**: On your Google account
2. **Generate App Password**: https://myaccount.google.com/apppasswords
3. **Add to .env**:
   ```
   GMAIL_SMTP_USER=your-email@gmail.com
   GMAIL_SMTP_PASSWORD=your-app-password
   ```

📚 [Gmail API Documentation](https://developers.google.com/gmail/api)

### Notion Integration

1. **Create Integration**: https://www.notion.so/my-integrations
2. **Copy Integration Token**: Starts with `secret_`
3. **Share Database**: Share your database with the integration
4. **Get Database ID**: From database URL
   ```
   https://notion.so/workspace/Database-<DATABASE_ID>?v=...
   ```
5. **Add to .env**:
   ```
   NOTION_API_KEY=secret_...
   NOTION_DATABASE_ID=<database-id>
   ```

📚 [Notion API Documentation](https://developers.notion.com/)

## 📚 API Documentation

### REST Endpoints

- `GET /` - Service info
- `GET /health` - Health check
- `POST /chat` - Send message to agent
- `GET /integrations` - List integration status
- `GET /functions` - List available functions
- `WS /ws/chat` - WebSocket chat endpoint

Interactive API docs: http://localhost:8000/docs

### Chat Request Example

```json
POST /chat
{
  "message": "Send a message to #general saying 'Hello team!'",
  "user_id": "optional_user_id"
}
```

### Response Example

```json
{
  "response": "I've sent the message to #general",
  "function_calls": [
    {
      "function": "slack_send_message",
      "arguments": {"channel": "general", "text": "Hello team!"},
      "result": {"success": true, "data": {...}}
    }
  ],
  "error": null
}
```

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Lint code
flake8 src tests
black src tests
mypy src
```

## 🛠️ Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for:
- Adding new integrations
- Extending function capabilities
- Memory and RAG patterns
- Contributing guidelines

## 📁 Project Structure

```
rag7/
├── src/
│   ├── agent/
│   │   ├── core.py          # Conversational agent
│   │   └── memory.py        # Memory management
│   ├── integrations/
│   │   ├── base.py          # Base integration class
│   │   ├── slack.py         # Slack integration
│   │   ├── gmail.py         # Gmail integration
│   │   └── notion.py        # Notion integration
│   ├── interfaces/
│   │   └── web_api.py       # FastAPI app
│   └── utils/
│       └── config.py        # Configuration
├── frontend/
│   ├── src/
│   │   ├── App.js           # Main React component
│   │   └── App.css          # Styles
│   └── package.json
├── tests/
│   ├── test_web_api.py
│   └── test_integrations.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## 🔒 Security Notes

- **Never commit secrets** to version control
- Use `.env` for local development
- Use environment variables or secret managers in production
- Rotate API keys regularly
- Review OAuth scopes carefully

## 🐛 Troubleshooting

### Backend won't start
- Check `OPENAI_API_KEY` is set in `.env`
- Verify Python version: `python --version` (requires 3.11+)
- Install dependencies: `pip install -r requirements.txt`

### ChromaDB connection fails
- ChromaDB is optional; system falls back to in-memory storage
- Check Docker: `docker-compose logs chromadb`
- Verify port 8001 is available

### Integration not working
- Check API keys in `.env`
- Review logs: `docker-compose logs api`
- Verify integration health: `curl http://localhost:8000/integrations`

### Frontend can't connect
- Ensure backend is running on port 8000
- Check CORS settings in `.env`
- Verify `proxy` in `frontend/package.json`

## 📄 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

See [DEVELOPMENT.md](DEVELOPMENT.md) for contribution guidelines.

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ using FastAPI, React, and OpenAI