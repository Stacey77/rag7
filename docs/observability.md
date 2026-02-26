# Observability Guide

## Overview

This guide covers monitoring, logging, and observability for the RAG7 LangGraph integration API.

## Monitoring Stack

The production setup includes:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Metrics visualization and dashboards
- **Application logs**: Structured JSON logging

## Accessing Monitoring Tools

### Docker Compose

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (default credentials: admin / see .env.prod)

### Kubernetes

```bash
# Port-forward Prometheus
kubectl port-forward -n rag7-prod svc/prometheus 9090:9090

# Port-forward Grafana
kubectl port-forward -n rag7-prod svc/grafana 3000:3000
```

## Application Metrics

The integration API exposes metrics at `/metrics` endpoint in Prometheus format.

### Key Metrics

- `http_requests_total`: Total HTTP requests by method, endpoint, and status
- `http_request_duration_seconds`: Request latency histogram
- `langgraph_execution_duration_seconds`: LangGraph execution time
- `provider_api_calls_total`: Provider API calls (kiro.ai, lindy.ai)
- `provider_api_errors_total`: Provider API errors

### Example Queries

**Request Rate (QPS)**
```promql
rate(http_requests_total[5m])
```

**Error Rate**
```promql
rate(http_requests_total{status=~"5.."}[5m])
```

**95th Percentile Latency**
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Provider Success Rate**
```promql
sum(rate(provider_api_calls_total[5m])) - sum(rate(provider_api_errors_total[5m]))
```

## Logging

### Log Format

Application logs are structured in JSON format:

```json
{
  "timestamp": "2024-12-09T18:00:00Z",
  "level": "info",
  "message": "Request completed",
  "method": "POST",
  "path": "/v1/graph/run",
  "status": 200,
  "duration_ms": 145,
  "trace_id": "abc123",
  "user_id": "user_456"
}
```

### Viewing Logs

**Docker Compose**
```bash
# Tail all logs
docker-compose -f docker-compose.prod.yml logs -f

# Tail specific service
docker-compose -f docker-compose.prod.yml logs -f langgraph-api

# Search logs
docker-compose -f docker-compose.prod.yml logs langgraph-api | grep ERROR
```

**Kubernetes**
```bash
# Tail pod logs
kubectl logs -n rag7-prod -f deployment/langgraph-api

# Logs from all pods
kubectl logs -n rag7-prod -l app=langgraph-api --all-containers=true

# Previous container logs (for crashed pods)
kubectl logs -n rag7-prod <pod-name> --previous

# Export logs to file
kubectl logs -n rag7-prod deployment/langgraph-api > logs.txt
```

### Log Aggregation (Optional)

For production, consider integrating with a log aggregation service:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Grafana Loki**
- **AWS CloudWatch**
- **Google Cloud Logging**
- **Datadog**

## Grafana Dashboards

### Creating a Dashboard

1. Open Grafana (http://localhost:3000)
2. Login with admin credentials
3. Click "+" → "Dashboard" → "Add new panel"
4. Enter Prometheus query
5. Configure visualization
6. Save dashboard

### Recommended Dashboard Panels

**System Health Dashboard**
- CPU usage per pod
- Memory usage per pod
- Request rate (QPS)
- Error rate
- Response time (p50, p95, p99)
- Pod count

**LangGraph Operations Dashboard**
- Graph execution count
- Graph execution duration
- Graph execution errors
- Provider API call distribution

**Business Metrics Dashboard**
- API usage by endpoint
- Top users by request count
- Provider usage distribution (kiro.ai vs lindy.ai)

### Example Panel Configuration

**Request Rate Panel**
```yaml
Title: Request Rate (QPS)
Query: rate(http_requests_total[5m])
Legend: {{method}} {{path}}
Visualization: Time series
Unit: requests/sec
```

## Alerting

### Prometheus Alerts

Create alerts in Prometheus for critical conditions:

**High Error Rate**
```yaml
alert: HighErrorRate
expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
for: 5m
labels:
  severity: critical
annotations:
  summary: High error rate detected
  description: Error rate is {{ $value }} requests/sec
```

**High Latency**
```yaml
alert: HighLatency
expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
for: 5m
labels:
  severity: warning
annotations:
  summary: High request latency
  description: 95th percentile latency is {{ $value }}s
```

### Grafana Alerts

1. Open dashboard panel
2. Click "Alert" tab
3. Configure alert rule
4. Setup notification channel (email, Slack, PagerDuty)

## Distributed Tracing (Optional)

For detailed request tracing, integrate with:

- **Jaeger**
- **Zipkin**
- **OpenTelemetry**

Add tracing headers to track requests across services:
- `X-Trace-Id`: Unique trace identifier
- `X-Span-Id`: Current span identifier
- `X-Parent-Span-Id`: Parent span identifier

## Performance Profiling

### Application Profiling

Use Python profiling tools to identify bottlenecks:

```python
# Add to application for CPU profiling
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# ... code to profile ...
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Kubernetes Resource Monitoring

```bash
# Real-time pod resource usage
kubectl top pods -n rag7-prod

# Node resource usage
kubectl top nodes

# Detailed pod metrics
kubectl describe pod -n rag7-prod <pod-name>
```

## Health Check Monitoring

Setup external monitoring for health endpoints:

```bash
# Uptime monitoring services
# - UptimeRobot
# - Pingdom
# - StatusCake

# Example curl health check
curl -f https://api.yourdomain.com/health || alert "API is down"
```

## Best Practices

1. **Set up alerts for critical metrics** (error rate, latency, availability)
2. **Create runbooks** for common alerts (see [runbook.md](runbook.md))
3. **Regular dashboard reviews** to identify trends
4. **Log sensitive data carefully** (avoid logging passwords, API keys)
5. **Set appropriate log retention** (7-30 days typically)
6. **Monitor costs** of observability tools
7. **Test alerts** to ensure they fire correctly
8. **Document custom metrics** and their meaning

## Example Curl Commands

### Check Application Health
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

curl http://localhost:8000/ready
# Expected: {"status": "ready"}
```

### Query Prometheus
```bash
# Current metric value
curl 'http://localhost:9090/api/v1/query?query=http_requests_total'

# Metric over time range
curl 'http://localhost:9090/api/v1/query_range?query=rate(http_requests_total[5m])&start=2024-12-09T00:00:00Z&end=2024-12-09T23:59:59Z&step=15s'
```

## Next Steps

1. Import Grafana dashboards from community templates
2. Configure alert notification channels
3. Setup log aggregation service
4. Implement distributed tracing
5. Create custom dashboards for business metrics
