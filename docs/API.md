# AGI System - API Documentation

## Overview

The AGI System provides a comprehensive REST API for interacting with all system components including symbolic reasoning, emotional intelligence, knowledge management, and autonomous goal execution.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. In production, implement appropriate authentication mechanisms.

## API Endpoints

### Health & Status

#### GET /
Get basic API information

**Response:**
```json
{
  "name": "AGI System API",
  "version": "0.1.0",
  "status": "running",
  "description": "AGI System with Symbolic and Emotional Reasoning"
}
```

#### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "system": "operational"
}
```

#### GET /status
Get comprehensive system status

**Response:**
```json
{
  "agent_controller": {
    "active_goal": "Learn about AI",
    "total_goals": 5,
    "completed_tasks": 10,
    "pending_tasks": 2
  },
  "symbolic_reasoning": {
    "num_facts": 15,
    "num_rules": 8,
    "knowledge_graph": {...}
  },
  "emotional_intelligence": {...},
  "langchain_layer": {...},
  "knowledge_layer": {...},
  "learning_module": {...}
}
```

### Input Processing

#### POST /process
Process user input through the complete AGI pipeline

**Request Body:**
```json
{
  "input": "I'm excited to learn about artificial intelligence!",
  "context": {
    "user_id": "user123",
    "session_id": "session456"
  }
}
```

**Response:**
```json
{
  "response": "I'm glad to hear that! It's wonderful to see you happy.",
  "emotional_analysis": {
    "detected_emotions": [
      {
        "type": "joy",
        "intensity": 0.8,
        "triggers": ["excited"]
      }
    ],
    "affective_state": {
      "primary_emotion": "joy",
      "valence": 0.7,
      "arousal": 0.6,
      "dominance": 0.5
    }
  },
  "knowledge_context": [...],
  "reasoning": {...},
  "status": "success"
}
```

### Goal Management

#### POST /goal/set
Set a high-level goal for autonomous execution

**Request Body:**
```json
{
  "description": "Research and summarize recent advances in quantum computing",
  "priority": "high"
}
```

**Priority Values:** `low`, `medium`, `high`, `critical`

**Response:**
```json
{
  "goal_id": "goal_123456789",
  "description": "Research and summarize recent advances in quantum computing",
  "priority": "high",
  "status": "created"
}
```

#### POST /goal/execute
Execute a goal autonomously

**Query Parameters:**
- `goal_id` (optional): Specific goal ID to execute. If not provided, executes active goal.

**Response:**
```json
{
  "goal_id": "goal_123456789",
  "iterations": 10,
  "completed_tasks": 8,
  "remaining_tasks": 0,
  "status": "completed"
}
```

### Knowledge Management

#### POST /knowledge/add
Add unstructured knowledge to the vector database

**Request Body:**
```json
{
  "content": "Artificial Intelligence is revolutionizing healthcare through predictive analytics and personalized medicine.",
  "metadata": {
    "domain": "healthcare",
    "topic": "AI_applications",
    "source": "research_paper",
    "date": "2024-01-15"
  }
}
```

**Response:**
```json
{
  "doc_id": "doc_1705334400_0",
  "status": "added"
}
```

#### POST /knowledge/add_structured
Add structured knowledge (RDF triple) to knowledge graph

**Request Body:**
```json
{
  "subject": "Artificial_Intelligence",
  "predicate": "transforms",
  "object": "Healthcare"
}
```

**Response:**
```json
{
  "subject": "Artificial_Intelligence",
  "predicate": "transforms",
  "object": "Healthcare",
  "status": "added"
}
```

#### POST /knowledge/query
Query the knowledge base

**Request Body:**
```json
{
  "query": "What is machine learning?",
  "method": "hybrid",
  "k": 5
}
```

**Method Values:**
- `vector`: Semantic search using vector embeddings
- `graph`: Graph traversal and pattern matching
- `hybrid`: Combined vector and graph search

**Response:**
```json
{
  "method": "hybrid",
  "results": {
    "vector_results": [
      {
        "id": "doc_123",
        "content": "Machine learning is a subset of AI...",
        "similarity": 0.92,
        "metadata": {...}
      }
    ],
    "graph_results": [
      {
        "id": "Machine_Learning",
        "type": "graph_entity",
        "info": {...},
        "relations": [
          ["Machine_Learning", "is_subset_of", "AI"]
        ]
      }
    ]
  }
}
```

#### GET /knowledge/graph/export
Export the complete knowledge graph

**Response:**
```json
{
  "entities": ["AI", "Machine_Learning", "Neural_Networks"],
  "relations": [
    ["Machine_Learning", "is_subset_of", "AI"],
    ["Neural_Networks", "implements", "Machine_Learning"]
  ],
  "stats": {
    "num_entities": 15,
    "num_relations": 25,
    "avg_connections": 1.67
  }
}
```

### Reasoning

#### POST /reason
Perform reasoning on a query

**Request Body:**
```json
{
  "query": "If all birds can fly and eagle is a bird, can eagle fly?",
  "reasoning_type": "symbolic"
}
```

**Reasoning Types:**
- `symbolic`: Logic-based inference and deduction
- `emotional`: Emotion-aware reasoning
- `hybrid`: Combined symbolic and emotional reasoning

**Response (Symbolic):**
```json
{
  "query": "If all birds can fly and eagle is a bird, can eagle fly?",
  "method": "forward_chaining",
  "result": [
    {
      "id": "fact_3",
      "statement": "eagle can fly",
      "confidence": 0.95
    }
  ],
  "explanation": ["eagle can fly"]
}
```

**Response (Emotional):**
```json
{
  "detected_emotions": [...],
  "affective_state": {...},
  "empathetic_response": "...",
  "emotional_context": {...}
}
```

### Memory Management

#### POST /memory/consolidate
Consolidate memories from short-term to long-term storage

**Response:**
```json
{
  "short_term_consolidated": 5,
  "short_term_remaining": 3,
  "long_term_total": 245
}
```

## Error Responses

All endpoints may return error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request - Invalid input
- `500`: Internal Server Error
- `503`: Service Unavailable - System not initialized

## Rate Limiting

Currently no rate limiting is implemented. Consider implementing rate limiting for production use.

## Usage Examples

### Python

```python
import requests

# Process input
response = requests.post(
    "http://localhost:8000/process",
    json={
        "input": "I'm excited about AI!",
        "context": {}
    }
)
result = response.json()
print(result['response'])

# Add knowledge
response = requests.post(
    "http://localhost:8000/knowledge/add",
    json={
        "content": "AI is transforming industries",
        "metadata": {"topic": "AI"}
    }
)
doc_id = response.json()['doc_id']

# Query knowledge
response = requests.post(
    "http://localhost:8000/knowledge/query",
    json={
        "query": "AI applications",
        "method": "hybrid",
        "k": 5
    }
)
results = response.json()
```

### cURL

```bash
# Health check
curl http://localhost:8000/health

# Process input
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"input": "I am learning AI"}'

# Set goal
curl -X POST http://localhost:8000/goal/set \
  -H "Content-Type: application/json" \
  -d '{"description": "Learn machine learning", "priority": "high"}'

# Query knowledge
curl -X POST http://localhost:8000/knowledge/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AI?", "method": "vector", "k": 3}'
```

### JavaScript

```javascript
// Process input
fetch('http://localhost:8000/process', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    input: "I'm excited to learn!",
    context: {}
  })
})
.then(response => response.json())
.then(data => console.log(data.response));

// Query knowledge
fetch('http://localhost:8000/knowledge/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: "machine learning",
    method: "hybrid",
    k: 5
  })
})
.then(response => response.json())
.then(data => console.log(data.results));
```

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can:
- Explore all endpoints
- Test API calls directly
- View request/response schemas
- Download OpenAPI specification

## Best Practices

1. **Input Processing**: Always provide context when available for better results
2. **Knowledge Addition**: Include rich metadata to improve retrieval
3. **Query Methods**: Use `hybrid` method for best accuracy
4. **Goal Setting**: Be specific in goal descriptions for better task decomposition
5. **Error Handling**: Always check response status codes and handle errors gracefully

## Limitations

- No built-in authentication (implement before production)
- No rate limiting (add for production)
- Single instance only (no clustering support yet)
- In-memory storage (data not persisted across restarts)

## Support

For API issues or questions:
- Check the main README
- Review code examples
- Open an issue on GitHub
