# LangGraph Usage Guide

This guide explains how to use the LangGraph multi-agent system for various tasks.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/rag7.git
cd rag7

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

### Running the CLI

```bash
# List available patterns
python -m langgraph.main --list

# Run a pattern
python -m langgraph.main --pattern sequential --task "Write about AI trends"

# Run with custom options
python -m langgraph.main --pattern loop --task "Create a blog post" --quality 0.9 --max-iterations 3
```

### Starting the API Server

```bash
# Start the FastAPI server
python -m integration.api.server

# Or with uvicorn directly
uvicorn integration.api.server:app --host 0.0.0.0 --port 8000 --reload
```

## Agents

### ResearcherAgent

Specializes in information gathering and analysis.

```python
from langgraph.agents import ResearcherAgent
from langgraph.state import AgentState

researcher = ResearcherAgent()
state = AgentState(current_task="Research quantum computing trends")
result = researcher.process(state)
print(result.research_results)
```

### WriterAgent

Creates well-structured content based on research and requirements.

```python
from langgraph.agents import WriterAgent
from langgraph.state import AgentState

writer = WriterAgent()
state = AgentState(
    current_task="Write a blog post about AI",
    research_results=["AI is transforming industries...", "Key trends include..."]
)
result = writer.process(state)
print(result.draft_content)
```

### ReviewerAgent

Reviews content quality and provides feedback.

```python
from langgraph.agents import ReviewerAgent
from langgraph.state import AgentState

reviewer = ReviewerAgent(quality_threshold=0.8)
state = AgentState(
    current_task="Review the blog post",
    draft_content="Your blog post content here..."
)
result = reviewer.process(state)
print(f"Quality: {result.quality_score}, Feedback: {result.review_feedback}")
```

### RouterAgent

Routes tasks to appropriate handlers.

```python
from langgraph.agents import RouterAgent
from langgraph.state import AgentState

router = RouterAgent()
state = AgentState(current_task="Analyze market data for Q4")
result = router.process(state)
print(f"Routed to: {result.route}")
```

### AggregatorAgent

Consolidates outputs from multiple sources.

```python
from langgraph.agents import AggregatorAgent
from langgraph.state import AgentState

aggregator = AggregatorAgent()
state = AgentState(
    current_task="Synthesize findings",
    research_results=["Finding 1...", "Finding 2..."],
    draft_content="Content piece..."
)
result = aggregator.process(state)
print(result.final_output)
```

## Graph Patterns

### Sequential Pattern

Agents work in a chain: Researcher → Writer → Reviewer

```python
from langgraph.graphs import create_sequential_graph

# Create and run the graph
graph = create_sequential_graph()
result = graph.invoke({
    "messages": [],
    "current_task": "Write about machine learning",
    "research_results": [],
    "draft_content": "",
    "review_feedback": "",
    "final_output": "",
    "quality_score": 0.0,
    "iteration_count": 0,
    "max_iterations": 1,
    "metadata": {}
})
```

### Parallel Pattern

Multiple researchers work simultaneously.

```python
from langgraph.graphs import create_parallel_graph

graph = create_parallel_graph()
result = graph.invoke({
    "messages": [],
    "current_task": "Analyze technology trends",
    # ... other state fields
})
```

### Loop Pattern

Iterative improvement until quality threshold.

```python
from langgraph.graphs import create_loop_graph

graph = create_loop_graph(quality_threshold=0.85, max_iterations=5)
result = graph.invoke({
    "messages": [],
    "current_task": "Create high-quality content",
    # ... other state fields
})
```

### Router Pattern

Smart routing to specialized handlers.

```python
from langgraph.graphs import create_router_graph

graph = create_router_graph()
result = graph.invoke({
    "messages": [],
    "current_task": "Technical analysis of system architecture",
    # ... other state fields
})
print(f"Routed to: {result['route']}")
```

### Aggregator Pattern

Combine outputs from multiple agents.

```python
from langgraph.graphs import create_aggregator_graph

graph = create_aggregator_graph()
result = graph.invoke({
    "messages": [],
    "current_task": "Generate comprehensive report",
    # ... other state fields
})
```

### Hierarchical Pattern

Manager coordinates worker agents.

```python
from langgraph.graphs import create_hierarchical_graph

graph = create_hierarchical_graph()
result = graph.invoke({
    "messages": [],
    "current_task": "Complete project deliverable",
    "metadata": {"phase": "start"},
    # ... other state fields
})
```

### Network Pattern

Interconnected agents with dynamic coordination.

```python
from langgraph.graphs import create_network_graph

graph = create_network_graph()
result = graph.invoke({
    "messages": [],
    "current_task": "Complex multi-step analysis",
    "communication_log": [],
    # ... other state fields
})
```

## API Usage

### Patterns Endpoint

```bash
# List all patterns
curl http://localhost:8000/api/v1/patterns
```

### Run Endpoint

```bash
# Run any pattern
curl -X POST http://localhost:8000/api/v1/run \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Write a technical blog post",
    "pattern": "sequential"
  }'
```

### Pattern-Specific Endpoints

```bash
# Sequential
curl -X POST http://localhost:8000/api/v1/sequential \
  -H "Content-Type: application/json" \
  -d '{"task": "Research AI trends"}'

# Loop with quality threshold
curl -X POST http://localhost:8000/api/v1/loop \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Write perfect content",
    "quality_threshold": 0.9,
    "max_iterations": 5
  }'
```

## State Management

### AgentState Fields

| Field | Type | Description |
|-------|------|-------------|
| `messages` | List[Message] | Conversation history |
| `current_task` | str | Active task description |
| `research_results` | List[str] | Research findings |
| `draft_content` | str | Generated content |
| `review_feedback` | str | Review comments |
| `final_output` | str | Final result |
| `quality_score` | float | Quality metric (0-1) |
| `iteration_count` | int | Loop counter |
| `route` | str | Routing decision |
| `metadata` | dict | Additional context |

### Creating Checkpoints

```python
from langgraph.state import AgentState, create_checkpoint

state = AgentState(current_task="My task", quality_score=0.85)
checkpoint = create_checkpoint(state, checkpoint_id="cp_001")
print(f"Checkpoint: {checkpoint.checkpoint_id}")
```

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...

# API Server
LANGGRAPH_API_HOST=0.0.0.0
LANGGRAPH_API_PORT=8000

# Agent Settings
AGENT_MAX_ITERATIONS=10
QUALITY_THRESHOLD=0.8

# Model Settings (in config.py)
MODEL_NAME=gpt-4o-mini
TEMPERATURE=0.7
```

### Custom Agent Configuration

```python
from langchain_openai import ChatOpenAI
from langgraph.agents import ResearcherAgent

# Use a custom model
custom_model = ChatOpenAI(
    model="gpt-4",
    temperature=0.5,
    max_tokens=2000
)

researcher = ResearcherAgent(
    name="custom_researcher",
    model=custom_model
)
```

## Best Practices

1. **Choose the Right Pattern**
   - Sequential: Linear workflows with dependencies
   - Parallel: Independent tasks that can run concurrently
   - Loop: Iterative improvement tasks
   - Router: Multi-type task handling
   - Aggregator: Combining multiple outputs
   - Hierarchical: Complex coordinated tasks
   - Network: Dynamic collaborative tasks

2. **Set Appropriate Quality Thresholds**
   - Higher thresholds = more iterations = better quality
   - Balance quality vs. execution time/cost

3. **Monitor State**
   - Check `quality_score` for loop patterns
   - Review `route` for router patterns
   - Inspect `communication_log` for network patterns

4. **Handle Errors**
   - Wrap graph invocations in try/except
   - Check for empty outputs
   - Validate state before processing
