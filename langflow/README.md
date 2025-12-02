# LangFlow Service

This service provides the LangFlow visual interface for building AI agent flows.

## 🎯 Purpose

LangFlow is a visual tool for creating and editing LangChain flows. It provides a drag-and-drop interface for building complex AI agent workflows.

## 🚀 Usage

### Access LangFlow UI
Once the service is running, access the LangFlow interface at:
```
http://localhost:7860
```

### Create a Flow
1. Open the LangFlow UI
2. Use the drag-and-drop interface to create your flow
3. Connect components to build your agent logic
4. Export the flow as JSON

### Save and Manage Flows
- Flows can be exported from LangFlow as JSON files
- Save flows via the Backend API (`POST /save_flow/`)
- Run flows via the Backend API (`POST /run_flow/`)

## 🐳 Docker

### Build
```bash
docker build -t ragamuffin-langflow .
```

### Run Standalone
```bash
docker run -p 7860:7860 ragamuffin-langflow
```

## 📦 Dependencies

- Python 3.11
- LangFlow package (includes LangChain dependencies)

## �� Data Persistence

Flow data is persisted in the Docker volume `langflow_data` mounted at `/root/.langflow`.

## 🔧 Configuration

Environment variables:
- `LANGFLOW_HOST`: Host address (default: 0.0.0.0)
- `LANGFLOW_PORT`: Port number (default: 7860)

## 📚 Resources

- [LangFlow Documentation](https://docs.langflow.org/)
- [LangChain Documentation](https://docs.langchain.com/)

## ⚠️ Notes

- This is a development configuration
- For production, consider adding authentication
- Review security settings before exposing to the internet
