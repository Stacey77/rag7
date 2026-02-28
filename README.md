# Epic Platform (Ragamuffin) - Monorepo

Welcome to the **Epic Platform** – a complete monorepo scaffold for visual LangFlow agent building and execution.

## 🎨 UI Inspiration
![UI Reference](https://github.com/user-attachments/assets/placeholder-ui-reference.png)

## 🚀 Quick Start

```bash
# Start all services
./start-dev.sh

# Stop all services
./stop-dev.sh
```

## 🏗️ Architecture

- **LangFlow** (`:7860`) - Visual agent builder interface
- **Backend** (`:8000`) - FastAPI server for flow management
- **Frontend** (`:8080`) - React+TypeScript web client

## 📚 Documentation

- [Monorepo Overview](./README_MONOREPO.md)
- [Run Commands](./RUN_COMMANDS.md)
- [LangFlow Setup](./langflow/README.md)
- [Backend API](./langflow-backend/README.md)

## ⚠️ Security Notice

**This is a development scaffold.** Before deploying to production:
- Enable authentication and authorization
- Validate and sandbox flow execution
- Configure proper CORS policies
- Use secure environment variables
- Implement rate limiting and input validation

---

Built for rapid prototyping of AI agent systems with LangFlow visual programming.