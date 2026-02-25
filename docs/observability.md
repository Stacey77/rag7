# Observability Guide

This guide covers monitoring, logging, and tracing for the RAG7 LangGraph application.

## Table of Contents

- [Metrics](#metrics)
- [Logging](#logging)
- [Tracing](#tracing)
- [Dashboards](#dashboards)
- [Alerting](#alerting)

## Metrics

### Prometheus Metrics Endpoint

The application exposes Prometheus-compatible metrics at `/metrics` on port 9090.

#### Key Metrics to Monitor

**Application Metrics:**
- `http_requests_total` - Total HTTP requests by endpoint and status
- `http_request_duration_seconds` - Request duration histogram
- `langgraph_execution_duration_seconds` - Graph execution time
- `langgraph_errors_total` - Total graph execution errors
- `active_graph_executions` - Currently running graph executions

**System Metrics:**
- `process_cpu_usage` - CPU usage percentage
- `process_memory_bytes` - Memory usage in bytes
- `process_open_fds` - Open file descriptors

**Database Metrics:**
- `db_connections_active` - Active database connections
- `db_query_duration_seconds` - Database query duration
- `db_errors_total` - Database errors

**Cache Metrics:**
- `cache_hits_total` - Cache hit count
- `cache_misses_total` - Cache miss count
- `cache_evictions_total` - Cache eviction count

### Scraping Configuration

Add to your Prometheus configuration:

```yaml
scrape_configs:
  - job_name: 'langgraph'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - rag7
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
```

### Example Queries

```promql
# Request rate per second
rate(http_requests_total[5m])

# 99th percentile latency
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(langgraph_errors_total[5m]) / rate(http_requests_total[5m])

# Memory usage over time
process_memory_bytes

# Cache hit rate
rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))
```

## Logging

### Log Levels

The application supports the following log levels:
- `DEBUG` - Detailed diagnostic information
- `INFO` - General informational messages
- `WARNING` - Warning messages for potentially harmful situations
- `ERROR` - Error events that might still allow the app to continue
- `CRITICAL` - Critical events that may cause the app to abort

Set log level via environment variable:
```bash
LOG_LEVEL=INFO
```

### Log Format

Logs are output in JSON format for easy parsing:

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "langgraph.api",
  "message": "Graph execution completed",
  "request_id": "req_abc123",
  "graph_id": "graph_xyz789",
  "duration_ms": 1234,
  "user_id": "user_456"
}
```

### Accessing Logs

#### Docker Compose

```bash
# View logs from all services
docker-compose -f docker-compose.prod.yml logs -f

# View logs from specific service
docker-compose -f docker-compose.prod.yml logs -f langgraph

# View last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 langgraph
```

#### Kubernetes

```bash
# View logs from all pods
kubectl logs -n rag7 -l app=langgraph --tail=100 -f

# View logs from specific pod
kubectl logs -n rag7 POD_NAME --tail=200 -f

# View logs from all containers in pod
kubectl logs -n rag7 POD_NAME --all-containers=true
```

### Centralized Logging

#### ELK Stack (Elasticsearch, Logstash, Kibana)

Configure Filebeat to ship logs to Elasticsearch:

```yaml
# filebeat.yml
filebeat.inputs:
  - type: container
    paths:
      - '/var/lib/docker/containers/*/*.log'
    processors:
      - add_kubernetes_metadata:
          host: ${NODE_NAME}
          matchers:
          - logs_path:
              logs_path: "/var/lib/docker/containers/"

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "langgraph-logs-%{+yyyy.MM.dd}"
```

#### Loki (Grafana Loki)

Deploy Promtail to collect and forward logs:

```yaml
# promtail-config.yaml
clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
```

## Tracing

### OpenTelemetry Integration

The application supports OpenTelemetry for distributed tracing.

#### Configuration

Set environment variables:

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
JAEGER_AGENT_HOST=jaeger
JAEGER_AGENT_PORT=6831
```

#### Trace Context

Each request includes trace context propagation:
- `traceparent` - W3C Trace Context
- `tracestate` - Additional trace state

#### Trace Attributes

Custom attributes added to spans:
- `graph.id` - LangGraph graph identifier
- `graph.execution.id` - Unique execution ID
- `user.id` - User identifier
- `llm.provider` - LLM provider (OpenAI, Anthropic, etc.)
- `llm.model` - Model name
- `llm.tokens` - Token count

### Jaeger UI

Access Jaeger UI to view traces:

```bash
# Port forward Jaeger UI
kubectl port-forward -n observability svc/jaeger-query 16686:16686

# Open in browser
open http://localhost:16686
```

### Trace Analysis

Use traces to identify:
- Slow operations and bottlenecks
- Service dependencies
- Error propagation
- Concurrent execution patterns

## Dashboards

### Grafana Dashboard

Import the pre-configured Grafana dashboard:

```bash
# TODO: Create and include dashboard JSON
# grafana-dashboard.json
```

#### Key Panels

1. **Overview**
   - Request rate (requests/sec)
   - Error rate (%)
   - 95th/99th percentile latency
   - Active executions

2. **Performance**
   - Request duration distribution
   - Graph execution time
   - Database query time
   - Cache hit rate

3. **Resources**
   - CPU usage
   - Memory usage
   - Network I/O
   - Disk I/O

4. **Errors**
   - Error count by type
   - Error rate trend
   - Failed executions

### Custom Dashboards

Create custom dashboards using Grafana or your preferred tool.

#### Example: Request Rate Dashboard

```json
{
  "title": "Request Rate",
  "targets": [
    {
      "expr": "rate(http_requests_total{namespace=\"rag7\"}[5m])",
      "legendFormat": "{{method}} {{endpoint}}"
    }
  ]
}
```

## Alerting

### Alert Rules

Configure alerts for critical conditions:

#### High Error Rate

```yaml
groups:
  - name: langgraph_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(langgraph_errors_total[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"
```

#### High Latency

```yaml
      - alert: HighLatency
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "99th percentile latency is {{ $value }}s (threshold: 5s)"
```

#### Pod Restart

```yaml
      - alert: PodRestarting
        expr: rate(kube_pod_container_status_restarts_total{namespace="rag7"}[15m]) > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pod {{ $labels.pod }} is restarting"
          description: "Pod has restarted {{ $value }} times in the last 15 minutes"
```

#### Resource Exhaustion

```yaml
      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes{namespace="rag7"} / container_spec_memory_limit_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is {{ $value | humanizePercentage }}"
```

### Alert Channels

Configure notification channels:

#### Slack

```yaml
receivers:
  - name: 'slack-notifications'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts'
        title: 'Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

#### PagerDuty

```yaml
receivers:
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
        description: '{{ .GroupLabels.alertname }}: {{ .CommonAnnotations.summary }}'
```

#### Email

```yaml
receivers:
  - name: 'email'
    email_configs:
      - to: 'oncall@example.com'
        from: 'alerts@example.com'
        smarthost: 'smtp.example.com:587'
        auth_username: 'alerts@example.com'
        auth_password: 'YOUR_SMTP_PASSWORD'
```

## Health Checks

### Endpoints

- `GET /health` - Basic health check (liveness probe)
- `GET /ready` - Readiness check (includes dependencies)
- `GET /metrics` - Prometheus metrics

### Example Health Check Response

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123Z",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "llm_provider": "ok"
  },
  "version": "1.0.0",
  "uptime_seconds": 86400
}
```

### Curl Commands

```bash
# Check health
curl -i http://localhost:8123/health

# Check readiness
curl -i http://localhost:8123/ready

# Fetch metrics
curl http://localhost:9090/metrics
```

## Best Practices

1. **Set up alerts before issues occur** - Don't wait for production incidents
2. **Monitor the full stack** - Application, infrastructure, and dependencies
3. **Use structured logging** - Enables better searching and analysis
4. **Implement distributed tracing** - Essential for debugging microservices
5. **Create runbooks** - Document response procedures (see [runbook.md](./runbook.md))
6. **Regular review** - Periodically review dashboards and alerts
7. **Load testing** - Test observability under realistic load conditions

## Next Steps

- Set up Prometheus and Grafana
- Configure alert notification channels
- Create custom dashboards for your use case
- Implement distributed tracing with Jaeger or Zipkin
- Review and test incident response procedures
