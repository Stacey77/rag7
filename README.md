# RAG7 - Multi-Agent AI System

A fully integrated AI system using **LangGraph** for stateful agent orchestration and **n8n** for visual workflow automation.

## 🚀 Features

- **7 Agentic Patterns**: Sequential, Parallel, Loop, Router, Aggregator, Hierarchical, Network
- **5 Specialized Agents**: Researcher, Writer, Reviewer, Router, Aggregator
- **n8n Integration**: Visual workflow automation with pre-built templates
- **FastAPI Backend**: RESTful API for programmatic access
- **Docker Ready**: One-command deployment with Docker Compose

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        External Clients                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│   n8n Workflows  │  FastAPI Server  │  CLI Interface            │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LangGraph Core                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Patterns: Sequential│Parallel│Loop│Router│...          │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Agents: Researcher│Writer│Reviewer│Router│Aggregator    │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         Redis (State)  │  PostgreSQL (n8n)  │  OpenAI API       │
└─────────────────────────────────────────────────────────────────┘
```

## 🏃 Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/rag7.git
cd rag7

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Start all services
docker-compose up -d

# Access:
# - LangGraph API: http://localhost:8000
# - n8n Dashboard: http://localhost:5678
# - API Docs: http://localhost:8000/docs
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run the CLI
python -m langgraph.main --list

# Run a pattern
python -m langgraph.main --pattern sequential --task "Write about AI"

# Start the API server
python -m integration.api.server
```

## 🎯 Agent Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Sequential** | Agents work in chain order | Content pipelines |
| **Parallel** | Multiple agents work simultaneously | Multi-source analysis |
| **Loop** | Iterative improvement until threshold | Quality refinement |
| **Router** | Direct tasks to specialized handlers | Query classification |
| **Aggregator** | Consolidate multiple outputs | Report generation |
| **Hierarchical** | Manager-worker delegation | Complex projects |
| **Network** | Dynamic bidirectional communication | Collaborative tasks |

### Pattern Examples

**Sequential Pattern** (Research → Write → Review):
```bash
curl -X POST http://localhost:8000/api/v1/sequential \
  -H "Content-Type: application/json" \
  -d '{"task": "Write a blog post about quantum computing"}'
```

**Loop Pattern** (Iterative Refinement):
```bash
curl -X POST http://localhost:8000/api/v1/loop \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Create a perfect executive summary",
    "quality_threshold": 0.9,
    "max_iterations": 5
  }'
```

## 🤖 Agents

### ResearcherAgent
Gathers and analyzes information on any topic.

### WriterAgent
Generates well-structured content based on research.

### ReviewerAgent
Reviews content and provides quality feedback.

### RouterAgent
Classifies tasks and routes to appropriate handlers.

### AggregatorAgent
Combines outputs from multiple agents.

## 🔧 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/patterns` | List available patterns |
| POST | `/api/v1/run` | Execute any pattern |
| POST | `/api/v1/sequential` | Run sequential pattern |
| POST | `/api/v1/parallel` | Run parallel pattern |
| POST | `/api/v1/loop` | Run loop pattern |
| POST | `/api/v1/router` | Run router pattern |
| POST | `/api/v1/aggregator` | Run aggregator pattern |
| POST | `/api/v1/hierarchical` | Run hierarchical pattern |
| POST | `/api/v1/network` | Run network pattern |

### Request Body

```json
{
  "task": "Your task description",
  "pattern": "sequential",
  "quality_threshold": 0.8,
  "max_iterations": 5,
  "metadata": {}
}
```

### Response

```json
{
  "success": true,
  "pattern": "sequential",
  "task": "Your task",
  "final_output": "Generated content...",
  "quality_score": 0.85,
  "iteration_count": 1,
  "metadata": {}
}
```

## 📁 Project Structure

```
rag7/
├── langgraph/                 # LangGraph Multi-Agent System
│   ├── agents/               # Agent implementations
│   │   ├── base_agent.py
│   │   ├── researcher_agent.py
│   │   ├── writer_agent.py
│   │   ├── reviewer_agent.py
│   │   ├── router_agent.py
│   │   └── aggregator_agent.py
│   ├── graphs/               # Graph patterns
│   │   ├── sequential_graph.py
│   │   ├── parallel_graph.py
│   │   ├── loop_graph.py
│   │   ├── router_graph.py
│   │   ├── aggregator_graph.py
│   │   ├── hierarchical_graph.py
│   │   └── network_graph.py
│   ├── state/                # State management
│   │   └── agent_state.py
│   ├── tools/                # Shared tools
│   │   └── shared_tools.py
│   ├── config.py             # Configuration
│   └── main.py               # CLI entry point
├── integration/              # API & Integration Layer
│   ├── api/
│   │   ├── server.py         # FastAPI server
│   │   └── routes.py         # API endpoints
│   └── webhooks/
│       └── handlers.py       # Webhook handlers
├── n8n/                      # n8n Workflows
│   ├── workflows/            # Workflow JSON files
│   │   ├── main_orchestrator.json
│   │   ├── parallel_processor.json
│   │   ├── approval_workflow.json
│   │   ├── data_pipeline.json
│   │   └── langgraph_trigger.json
│   ├── credentials/
│   │   └── credentials_template.json
│   └── README.md
├── docs/                     # Documentation
│   ├── architecture.md
│   ├── langgraph_guide.md
│   ├── n8n_guide.md
│   ├── patterns.md
│   └── deployment.md
├── docker-compose.yml        # Docker setup
├── Dockerfile               # Container image
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project metadata
├── .env.example            # Environment template
└── README.md               # This file
```

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| langgraph-api | 8000 | LangGraph FastAPI Server |
| n8n | 5678 | n8n Workflow Automation |
| redis | 6379 | State Cache |
| postgres | 5432 | n8n Database |

## ⚙️ Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...

# API Configuration
LANGGRAPH_API_HOST=0.0.0.0
LANGGRAPH_API_PORT=8000

# Agent Settings
AGENT_MAX_ITERATIONS=10
QUALITY_THRESHOLD=0.8

# n8n Settings
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=admin
```

## 📚 Documentation

- [Architecture Overview](docs/architecture.md)
- [LangGraph Usage Guide](docs/langgraph_guide.md)
- [n8n Workflow Guide](docs/n8n_guide.md)
- [Agentic Patterns](docs/patterns.md)
- [Deployment Guide](docs/deployment.md)

## 🧪 Example Use Cases

### 1. Content Pipeline (Sequential)
Research → Draft → Review → Publish

```python
from langgraph.graphs.sequential_graph import run_sequential_pipeline
result = run_sequential_pipeline("Write about cloud computing trends")
```

### 2. Multi-Source Analysis (Parallel)
Analyze from technical, market, and user perspectives simultaneously.

```python
from langgraph.graphs.parallel_graph import run_parallel_pipeline
result = run_parallel_pipeline("Analyze smartphone market")
```

### 3. Iterative Refinement (Loop)
Generate and improve until quality threshold met.

```python
from langgraph.graphs.loop_graph import run_loop_pipeline
result = run_loop_pipeline("Create executive summary", quality_threshold=0.9)
```

### 4. Smart Routing (Router)
Route queries to specialized agents based on type.

```python
from langgraph.graphs.router_graph import run_router_pipeline
result = run_router_pipeline("Debug the authentication module")
```

### 5. Report Generation (Aggregator)
Combine insights from multiple agents into comprehensive reports.

```python
from langgraph.graphs.aggregator_graph import run_aggregator_pipeline
result = run_aggregator_pipeline("Generate quarterly business report")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration framework
- [LangChain](https://github.com/langchain-ai/langchain) - LLM application framework
- [n8n](https://n8n.io/) - Workflow automation platform
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework