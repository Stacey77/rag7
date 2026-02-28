# AGI System with Symbolic and Emotional Reasoning

A comprehensive Artificial General Intelligence (AGI) system that integrates symbolic reasoning, emotional intelligence, and autonomous agent capabilities.

## 🌟 Features

### Core Capabilities

- **🤖 Autonomous Agent Controller (AutoGPT-inspired)**
  - Goal management and task decomposition
  - Self-directed planning and execution
  - Multi-step reasoning and action loops

- **🧠 Symbolic Reasoning Engine**
  - Logic inference (forward and backward chaining)
  - Knowledge graph management
  - Rule-based reasoning
  - Integration with SymPy for symbolic mathematics

- **❤️ Emotional Reasoning Engine**
  - Emotion recognition from text
  - Affective state modeling
  - Empathy simulation
  - Emotion-influenced decision making

- **🔗 LangChain Integration**
  - Chain-of-thought reasoning
  - Multi-layered memory systems (short-term, long-term, episodic)
  - Tool integration and orchestration
  - Prompt management

- **📚 Knowledge Layer with RAG**
  - Vector database for semantic search
  - Knowledge graph for structured knowledge
  - Hybrid retrieval engine
  - Retrieval-Augmented Generation

- **📈 Learning Module**
  - Online learning from interactions
  - Reinforcement learning
  - Transfer learning across domains
  - Meta-learning capabilities

- **☕ Multi-Language Support**
  - Python for AI/ML components
  - Java for enterprise integration (Apache Jena, Drools)
  - gRPC for Python-Java interoperability

## 📋 Architecture

```
AGI System Architecture:
├── Core Agent Controller (AutoGPT-based)
│   ├── Goal Management
│   ├── Task Decomposition
│   └── Execution Loop
├── Reasoning Layer
│   ├── Symbolic Reasoning Engine
│   │   ├── Logic Inference System
│   │   ├── Knowledge Graph Reasoner
│   │   └── Rule Engine
│   └── Emotional Reasoning Engine
│       ├── Emotion Recognition
│       ├── Affective State Modeling
│       └── Empathy Simulator
├── LangChain Integration Layer
│   ├── Chain Orchestrator
│   ├── Memory Systems
│   │   ├── Short-term Memory
│   │   ├── Long-term Memory
│   │   └── Episodic Memory
│   ├── Tool Integration
│   └── Prompt Management
├── Knowledge Layer (RAG Integration)
│   ├── Vector Database
│   ├── Knowledge Graph
│   └── Retrieval Engine
├── Learning Module
│   ├── Online Learning
│   ├── Reinforcement Learning
│   └── Transfer Learning
└── Multi-Language Bridge
    ├── Python Services
    └── Java Services
```

## 🚀 Installation

### Python Setup

```bash
# Clone the repository
git clone https://github.com/Stacey77/rag7.git
cd rag7

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Java Setup

```bash
# Build Java services
cd java_services
mvn clean install

# Run Java services
mvn exec:java -Dexec.mainClass="com.agi.AGIServiceMain"
```

### Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
- OpenAI API key (if using LLM features)
- Database connections
- Service ports

## 📖 Quick Start

### Basic Usage

```python
from agi_system import create_agi_system

# Initialize the AGI system
agi = create_agi_system()

# Process user input
result = agi.process_input("I'm excited to learn about AI!")
print(result['response'])
print(f"Detected emotion: {result['emotional_analysis']['affective_state']['primary_emotion']}")

# Add knowledge
agi.add_knowledge("AI is transforming the world")
agi.add_structured_knowledge("AI", "is_a", "Technology")

# Query knowledge
results = agi.query_knowledge("What is AI?", method="hybrid")

# Symbolic reasoning
agi.symbolic_engine.logic_system.add_fact("All humans are mortal")
agi.symbolic_engine.logic_system.add_fact("Socrates is a human")
proven = agi.symbolic_engine.logic_system.backward_chaining("Socrates is mortal")

# Set and execute goals
goal_id = agi.set_goal("Learn about machine learning", priority="high")
result = agi.execute_goal(goal_id)
```

### Running the API Server

```bash
# Start the REST API
python -m agi_system.api.rest_api

# Or using uvicorn directly
uvicorn agi_system.api.rest_api:app --reload --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`

Interactive API docs: `http://localhost:8000/docs`

## 🔌 API Endpoints

### Core Endpoints

- `POST /process` - Process user input with full AGI pipeline
- `POST /goal/set` - Set a high-level goal
- `POST /goal/execute` - Execute a goal autonomously
- `GET /status` - Get comprehensive system status

### Knowledge Management

- `POST /knowledge/add` - Add knowledge to vector database
- `POST /knowledge/add_structured` - Add structured knowledge triple
- `POST /knowledge/query` - Query knowledge base (vector/graph/hybrid)

### Reasoning

- `POST /reason` - Perform reasoning (symbolic/emotional/hybrid)

### Memory

- `POST /memory/consolidate` - Consolidate memories

## 📚 Examples

### Emotion Recognition

```python
from agi_system import create_agi_system

agi = create_agi_system()

# Process emotionally-charged input
result = agi.process_input("I'm really frustrated with this bug!")

print(f"Primary Emotion: {result['emotional_analysis']['affective_state']['primary_emotion']}")
print(f"Empathetic Response: {result['empathetic_response']}")
```

### Symbolic Reasoning

```python
from agi_system import create_agi_system

agi = create_agi_system()

# Add facts and rules
logic = agi.symbolic_engine.logic_system
logic.add_fact("Birds can fly")
logic.add_fact("Eagle is a bird")
logic.add_rule(
    name="flight_capability",
    premises=["Birds can fly", "Eagle is a bird"],
    conclusion="Eagle can fly"
)

# Infer new facts
new_facts = logic.forward_chaining()
for fact in new_facts:
    print(f"Inferred: {fact.statement}")
```

### Knowledge Graph

```python
from agi_system import create_agi_system

agi = create_agi_system()

# Build knowledge graph
agi.add_structured_knowledge("Python", "is_a", "Programming_Language")
agi.add_structured_knowledge("TensorFlow", "written_in", "Python")
agi.add_structured_knowledge("TensorFlow", "used_for", "Machine_Learning")

# Query graph
result = agi.query_knowledge("Python", method="graph")
```

More examples in the `examples/` directory:
- `basic_usage.py` - Comprehensive basic usage
- `emotional_reasoning_demo.py` - Emotional intelligence demos
- `symbolic_reasoning_demo.py` - Symbolic AI demos

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_symbolic_reasoning.py

# Run with coverage
pytest --cov=agi_system tests/
```

## 📊 System Components

### Agent Controller

The agent controller manages goals and executes tasks autonomously:

```python
from agi_system.core import AGIAgentController

controller = AGIAgentController()
goal_id = controller.set_goal("Complete research on topic", priority="high")
result = controller.execute_goal(goal_id)
```

### Symbolic Engine

Performs logical inference and knowledge graph reasoning:

```python
from agi_system.reasoning.symbolic import SymbolicReasoningEngine

engine = SymbolicReasoningEngine()
engine.add_knowledge("AI is transforming healthcare")
result = engine.reason("healthcare transformation", method="forward_chaining")
```

### Emotional Engine

Recognizes and models emotions:

```python
from agi_system.reasoning.emotional import EmotionalReasoningEngine

engine = EmotionalReasoningEngine()
result = engine.process_input("I'm so happy about this!")
print(result['affective_state']['primary_emotion'])
```

### Knowledge Layer

Manages knowledge with vector DB and knowledge graph:

```python
from agi_system.knowledge import KnowledgeLayerRAG

knowledge = KnowledgeLayerRAG()
doc_id = knowledge.ingest_document("AI facts...")
results = knowledge.query("AI", method="hybrid")
```

### Learning Module

Enables continual learning:

```python
from agi_system.learning import LearningModule, LearningMode

learning = LearningModule()
learning.learn(
    learning_mode=LearningMode.ONLINE,
    interaction={"input": "user query"},
    feedback=0.8
)
```

## 🔧 Configuration

The system can be configured via environment variables or `AGIConfig`:

```python
from agi_system.config import AGIConfig

config = AGIConfig(
    openai_api_key="your-key",
    log_level="INFO"
)

from agi_system import AGISystem
agi = AGISystem(config)
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with LangChain for agent orchestration
- Inspired by AutoGPT for autonomous behavior
- Uses Apache Jena for knowledge graphs
- Integrates Drools for rule-based reasoning
- Sentiment analysis with VADER and TextBlob
- Symbolic mathematics with SymPy

## 📧 Support

For questions or issues:
- Open an issue on GitHub
- Check the documentation in `docs/`
- Review examples in `examples/`

## 🗺️ Roadmap

- [ ] Enhanced LLM integration
- [ ] More sophisticated meta-learning
- [ ] Advanced multi-agent coordination
- [ ] Improved visualization tools
- [ ] Extended Java service capabilities
- [ ] Mobile SDK
- [ ] Cloud deployment templates

---

**Built with ❤️ for advancing AGI research and applications**
