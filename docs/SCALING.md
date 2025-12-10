# FortFail Scaling Architecture

This document describes how to scale FortFail for production workloads.

## Overview

FortFail can be scaled horizontally at multiple levels:
- **Orchestrator**: Multiple instances behind a load balancer
- **Agents**: Agent pools across regions/zones
- **Storage**: Distributed object storage
- **Database**: PostgreSQL with replication

## Architecture Patterns

### Multi-Orchestrator Setup

```
                     ┌─────────────────┐
                     │  Load Balancer  │
                     │   (nginx/HAProxy)│
                     └────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
        ┌─────▼─────┐   ┌────▼──────┐  ┌────▼──────┐
        │Orchestrator│   │Orchestrator│  │Orchestrator│
        │    #1      │   │    #2     │  │    #3     │
        └─────┬──────┘   └─────┬─────┘  └─────┬─────┘
              │                │              │
              └────────────────┼──────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Shared PostgreSQL  │
                    │    (w/ replication) │
                    └─────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    MinIO/S3         │
                    │  (distributed mode) │
                    └─────────────────────┘
```

### Key Considerations

#### 1. Stateless Orchestrators
All orchestrators must be stateless and share the same database and object storage.

#### 2. Session Affinity
WebSocket connections require sticky sessions at the load balancer level.

#### 3. Database Scaling
Use read replicas for query-heavy workloads and connection pooling (PgBouncer).

#### 4. Object Storage Scaling
Deploy MinIO in distributed mode or use AWS S3 with transfer acceleration.

#### 5. Agent Pools
Organize agents by region, environment, and function for better management.

See full documentation for detailed configuration examples.
