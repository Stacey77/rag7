# Observability Guide

This guide covers monitoring, metrics, logging, and tracing for the Rag7 production deployment.

## Overview

A production-ready observability stack includes:
- **Metrics**: Application and infrastructure performance metrics
- **Logs**: Centralized log aggregation and analysis
- **Traces**: Distributed tracing for request flows
- **Alerts**: Proactive notification of issues

## Metrics Collection

### Prometheus

#### Docker Compose Setup

Add Prometheus to `docker-compose.prod.yml`:

```yaml
prometheus:
  image: prom/prometheus:latest
  container_name: rag7-prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
  ports:
    - "9090:9090"
  restart: unless-stopped
```

Example `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'langgraph-api'
    static_configs:
      - targets: ['langgraph:8000']
    metrics_path: '/metrics'
```

#### Kubernetes Setup

Deploy Prometheus using the Prometheus Operator or Helm:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
```

Add ServiceMonitor for your application:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: langgraph-api
  namespace: rag7-staging
spec:
  selector:
    matchLabels:
      app: langgraph-api
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

### Grafana Dashboards

Access Grafana and import dashboards:

1. FastAPI/Python application metrics
2. PostgreSQL database metrics
3. Redis metrics
4. Kubernetes cluster metrics (if applicable)

#### Key Metrics to Monitor

- **Request Rate**: Requests per second
- **Error Rate**: 4xx/5xx responses
- **Latency**: P50, P95, P99 response times
- **Resource Usage**: CPU, memory, disk I/O
- **Database**: Connection pool, query performance
- **Cache**: Redis hit/miss ratio

---

## Logging

### Structured Logging

Ensure the application outputs structured JSON logs:

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
        }
        return json.dumps(log_data)
```

### Log Aggregation

#### Docker Compose with Loki

Add Loki and Promtail:

```yaml
loki:
  image: grafana/loki:latest
  ports:
    - "3100:3100"
  volumes:
    - loki_data:/loki
  command: -config.file=/etc/loki/local-config.yaml

promtail:
  image: grafana/promtail:latest
  volumes:
    - /var/lib/docker/containers:/var/lib/docker/containers:ro
    - ./promtail-config.yml:/etc/promtail/config.yml
  command: -config.file=/etc/promtail/config.yml
```

#### Kubernetes with ELK/EFK Stack

Deploy Elasticsearch, Logstash/Fluentd, and Kibana:

```bash
# Using ECK (Elastic Cloud on Kubernetes)
kubectl create -f https://download.elastic.co/downloads/eck/2.10.0/crds.yaml
kubectl apply -f https://download.elastic.co/downloads/eck/2.10.0/operator.yaml
```

Or use Fluentd/Fluent Bit as a DaemonSet to collect logs from all pods.

### Log Retention

Configure retention policies based on compliance requirements:
- **Production logs**: 30-90 days
- **Error logs**: 6-12 months
- **Audit logs**: 1-7 years

---

## Distributed Tracing

### OpenTelemetry Integration

Add OpenTelemetry to your application:

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Initialize tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure exporter
otlp_exporter = OTLPSpanExporter(
    endpoint="http://jaeger:4317",
    insecure=True
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)
```

### Jaeger Setup

Add Jaeger to your stack:

```yaml
jaeger:
  image: jaegertracing/all-in-one:latest
  environment:
    - COLLECTOR_OTLP_ENABLED=true
  ports:
    - "16686:16686"  # Jaeger UI
    - "4317:4317"    # OTLP gRPC
    - "4318:4318"    # OTLP HTTP
```

Access Jaeger UI at `http://localhost:16686`

---

## Health Checks

### Endpoints

Implement comprehensive health checks:

```python
@app.get("/health")
async def health_check():
    """Liveness probe - is the app running?"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/ready")
async def readiness_check():
    """Readiness probe - can the app serve traffic?"""
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "external_api": await check_external_api()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks,
            "timestamp": datetime.utcnow()
        }
    )
```

### Testing Health Endpoints

```bash
# Liveness
curl http://localhost:8000/health

# Readiness
curl http://localhost:8000/ready

# Expected output
{
  "status": "ready",
  "checks": {
    "database": true,
    "redis": true,
    "external_api": true
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## Alerting

### Prometheus Alerting Rules

Create alerting rules:

```yaml
groups:
  - name: langgraph_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "P95 latency is {{ $value }} seconds"

      - alert: PodCrashLooping
        expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pod {{ $labels.pod }} is crash looping"
```

### Alertmanager Configuration

Configure notification channels:

```yaml
global:
  slack_api_url: 'YOUR_SLACK_WEBHOOK_URL'

route:
  group_by: ['alertname', 'cluster']
  group_wait: 10s
  group_interval: 5m
  repeat_interval: 3h
  receiver: 'slack-notifications'

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - channel: '#alerts'
        title: 'Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

---

## Performance Monitoring

### Application Performance Monitoring (APM)

Consider using APM tools:

1. **Sentry** - Error tracking and performance monitoring
2. **New Relic** - Full-stack observability
3. **Datadog** - Infrastructure and application monitoring
4. **Elastic APM** - Part of Elastic Stack

### Sentry Integration

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,  # 10% of transactions
    environment=os.getenv("APP_ENV", "production"),
)
```

---

## Dashboard Examples

### Key Dashboards to Create

1. **Application Overview**
   - Request rate, error rate, latency
   - Active users/sessions
   - API endpoint usage

2. **Infrastructure**
   - CPU, memory, disk usage
   - Network I/O
   - Container/pod status

3. **Database**
   - Connection pool usage
   - Query performance
   - Slow queries

4. **Business Metrics**
   - Graph executions per hour
   - Average processing time
   - Success/failure rates

---

## Best Practices

1. **Use consistent labels** across metrics for easy correlation
2. **Set up SLIs/SLOs** (Service Level Indicators/Objectives)
3. **Monitor the 4 golden signals**: Latency, Traffic, Errors, Saturation
4. **Test alerts** regularly to avoid alert fatigue
5. **Document runbooks** for each alert
6. **Rotate credentials** used in monitoring tools
7. **Implement sampling** for high-volume traces
8. **Archive old metrics** to reduce storage costs

---

## Next Steps

1. Deploy monitoring stack (Prometheus + Grafana)
2. Configure log aggregation (Loki or ELK)
3. Set up distributed tracing (Jaeger)
4. Create custom dashboards
5. Define and test alerting rules
6. Document on-call procedures

For incident response procedures, see [runbook.md](./runbook.md).
