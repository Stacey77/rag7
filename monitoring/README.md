# Monitoring & Observability

This directory contains monitoring and observability infrastructure for the Ragamuffin platform.

## Overview

The monitoring stack includes:
- **Prometheus** - Metrics collection and alerting
- **Grafana** - Visualization and dashboards
- **Structured Logging** - JSON-formatted logs with correlation IDs

## Services

### Prometheus (port 9090)

Prometheus collects metrics from all services:
- Backend API (langflow-backend)
- RAG Service
- Milvus
- n8n

Access: http://localhost:9090

### Grafana (port 3000)

Grafana provides pre-built dashboards for monitoring:
- RAG Operations Dashboard
- API Performance Dashboard
- System Overview Dashboard

Access: http://localhost:3000
- Default username: `admin`
- Default password: `admin`

## Quick Start

```bash
# Start all services including monitoring
./start-dev.sh

# Access Prometheus
open http://localhost:9090

# Access Grafana
open http://localhost:3000
```

## Metrics Endpoints

Each service exposes a `/metrics` endpoint:

```bash
# Backend metrics
curl http://localhost:8000/metrics

# RAG service metrics
curl http://localhost:8001/metrics
```

## Available Metrics

### Backend API Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | Request latency |
| `http_requests_in_progress` | Gauge | Active requests |
| `flow_executions_total` | Counter | Flow execution count |

### RAG Service Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `rag_embeddings_total` | Counter | Total embeddings generated |
| `rag_searches_total` | Counter | Total search queries |
| `rag_queries_total` | Counter | Total RAG queries |
| `rag_operation_duration_seconds` | Histogram | Operation latency |
| `rag_collection_size` | Gauge | Documents per collection |

## Dashboards

### RAG Operations Dashboard

Visualizes RAG-specific metrics:
- Embedding generation rate
- Search query latency (p50, p95, p99)
- Query success/error rates
- Collection statistics

### API Performance Dashboard

Monitors API health:
- Request latency by endpoint
- Error rate trends
- Throughput (requests/second)
- Active connections

### System Overview Dashboard

System-level monitoring:
- CPU and memory usage
- Container health status
- Network I/O
- Disk usage

## Alerting

Alert rules are defined in `prometheus/alert_rules.yml`:

| Alert | Condition | Severity |
|-------|-----------|----------|
| HighErrorRate | Error rate > 5% | warning |
| HighLatency | p95 latency > 2s | warning |
| ServiceDown | Target unreachable | critical |
| HighMemoryUsage | Memory > 80% | warning |

## Configuration

### Prometheus

Configuration file: `prometheus/prometheus.yml`

```yaml
scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
  - job_name: 'rag-service'
    static_configs:
      - targets: ['rag-service:8001']
```

### Grafana

- Datasources: `grafana/provisioning/datasources/`
- Dashboards: `grafana/provisioning/dashboards/`
- Config: `grafana/grafana.ini`

## Structured Logging

All services use structured JSON logging:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Request completed",
  "correlation_id": "abc123",
  "method": "POST",
  "path": "/rag/query",
  "status_code": 200,
  "duration_ms": 150
}
```

### Log Fields

| Field | Description |
|-------|-------------|
| `timestamp` | ISO 8601 timestamp |
| `level` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `message` | Human-readable message |
| `correlation_id` | Request correlation ID |
| `service` | Service name |
| `method` | HTTP method |
| `path` | Request path |
| `status_code` | Response status |
| `duration_ms` | Request duration in milliseconds |

## Integration with External Tools

### ELK Stack

Logs are formatted for easy integration with Elasticsearch:

```bash
# Ship logs to Elasticsearch
docker logs backend 2>&1 | \
  jq -c '.' | \
  curl -X POST "http://elasticsearch:9200/logs/_bulk" \
    -H "Content-Type: application/x-ndjson" \
    --data-binary @-
```

### Loki

For Grafana Loki integration:

```yaml
# docker-compose.yml addition
loki:
  image: grafana/loki:2.9.0
  ports:
    - "3100:3100"
```

## Troubleshooting

### Prometheus Not Scraping

1. Check target status in Prometheus UI
2. Verify network connectivity between containers
3. Ensure metrics endpoints are accessible

### Grafana Dashboard Empty

1. Verify Prometheus datasource is configured
2. Check time range selection
3. Ensure metrics are being collected

### High Memory Usage

1. Adjust Prometheus retention settings
2. Reduce scrape frequency
3. Limit stored metrics cardinality
