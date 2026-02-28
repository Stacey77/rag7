# System Architecture

This document describes the architecture of the LangGraph Multi-Agent System with n8n integration.

## Overview

The system combines two powerful platforms:
- **LangGraph**: For stateful agent orchestration and complex workflow patterns
- **n8n**: For visual workflow automation and external integrations

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           External Clients                               │
│                    (Web Apps, APIs, Webhooks)                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              n8n Layer                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ Orchestrator│ │  Parallel   │ │  Approval   │ │   Data      │       │
│  │  Workflow   │ │  Processor  │ │  Workflow   │ │  Pipeline   │       │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘       │
│         │               │               │               │               │
│         └───────────────┴───────────────┴───────────────┘               │
│                                 │                                        │
└─────────────────────────────────┼────────────────────────────────────────┘
                                  │ HTTP/Webhooks
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FastAPI Integration Layer                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        API Routes                                │   │
│  │  /api/v1/run  │  /api/v1/sequential  │  /api/v1/parallel  │ ... │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     Webhook Handlers                             │   │
│  │         TaskWebhook  │  ApprovalWebhook  │  Callbacks           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────┼────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         LangGraph Core                                   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        Graph Patterns                             │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐        │   │
│  │  │Sequential │ │ Parallel  │ │   Loop    │ │  Router   │        │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘        │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐                      │   │
│  │  │Aggregator │ │Hierarchic │ │  Network  │                      │   │
│  │  └───────────┘ └───────────┘ └───────────┘                      │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                          Agents                                   │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐        │   │
│  │  │Researcher │ │  Writer   │ │ Reviewer  │ │  Router   │        │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘        │   │
│  │  ┌───────────┐ ┌───────────┐                                    │   │
│  │  │Aggregator │ │  Manager  │                                    │   │
│  │  └───────────┘ └───────────┘                                    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                     State Management                              │   │
│  │        AgentState  │  Message  │  Checkpoint  │  History         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Infrastructure                                   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐           │
│  │      Redis      │ │   PostgreSQL    │ │    OpenAI API   │           │
│  │  (Cache/State)  │ │  (n8n Storage)  │ │   (LLM Backend) │           │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. LangGraph Core

The heart of the system, providing:

- **Agents**: Specialized AI agents for different tasks
  - `ResearcherAgent`: Information gathering and analysis
  - `WriterAgent`: Content generation
  - `ReviewerAgent`: Quality review and feedback
  - `RouterAgent`: Task classification and routing
  - `AggregatorAgent`: Output consolidation

- **Graph Patterns**: Orchestration patterns for agent coordination
  - Sequential, Parallel, Loop, Router, Aggregator, Hierarchical, Network

- **State Management**: Shared state with checkpointing support

### 2. FastAPI Integration Layer

RESTful API exposing LangGraph capabilities:

- `/api/v1/run`: Execute any pattern
- `/api/v1/patterns`: List available patterns
- Pattern-specific endpoints (`/sequential`, `/parallel`, etc.)
- Webhook handlers for async processing

### 3. n8n Workflow Layer

Visual workflow automation:

- Pre-built workflows for common use cases
- Webhook triggers for external integration
- Human-in-the-loop approval workflows
- Data transformation and aggregation

### 4. Infrastructure

Supporting services:

- **Redis**: State caching and inter-service communication
- **PostgreSQL**: n8n workflow and execution persistence
- **OpenAI API**: LLM backend for agent intelligence

## Data Flow

### Request Processing

1. External request arrives via n8n webhook or direct API call
2. n8n workflow validates and routes the request
3. FastAPI receives and parses the request
4. LangGraph executes the appropriate pattern
5. Agents process the task, sharing state
6. Result is returned through the same path

### State Management

```
┌─────────────────────────────────────────────────────────────────┐
│                         AgentState                               │
├─────────────────────────────────────────────────────────────────┤
│  messages: List[Message]        # Conversation history          │
│  current_task: str              # Active task                   │
│  research_results: List[str]    # Research findings             │
│  draft_content: str             # Written content               │
│  review_feedback: str           # Review comments               │
│  final_output: str              # Final result                  │
│  quality_score: float           # Quality metric (0-1)          │
│  iteration_count: int           # Loop iteration counter        │
│  route: str                     # Routing decision              │
│  metadata: Dict                 # Additional context            │
├─────────────────────────────────────────────────────────────────┤
│                       Checkpointing                              │
│  - Periodic state snapshots                                      │
│  - Recovery from failures                                        │
│  - Human-in-the-loop pause/resume                               │
└─────────────────────────────────────────────────────────────────┘
```

## Scalability Considerations

### Horizontal Scaling

- LangGraph API can be scaled behind a load balancer
- Redis supports clustering for state distribution
- n8n supports worker mode for distributed execution

### Performance Optimization

- Agent responses can be cached in Redis
- Parallel patterns execute concurrently where possible
- Async processing for long-running tasks

## Security

### Authentication & Authorization

- n8n basic auth for workflow access
- API key authentication for LangGraph endpoints
- Webhook signature validation

### Data Protection

- Environment variables for sensitive configuration
- No secrets in code or logs
- CORS configuration for API access control
