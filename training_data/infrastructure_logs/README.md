# Infrastructure Logs Training Data

This directory contains curated infrastructure log samples for training
log analysis and anomaly detection models.

## Data Categories

### System Logs
- `/var/log/syslog` samples with labeled anomalies
- Kernel logs with hardware failure indicators
- Boot sequence logs for baseline patterns

### Application Logs
- Web server access logs (Apache/Nginx format)
- Application error logs with stack traces
- Performance degradation log sequences

### Container & Kubernetes Logs
- Pod lifecycle events (OOMKilled, CrashLoopBackOff)
- Node pressure and eviction events
- Network policy violation logs

### Database Logs
- Slow query logs with execution plans
- Connection pool exhaustion events
- Replication lag indicators

## Data Format

Each log entry should follow structured format:
```json
{
  "timestamp": "2024-01-15T10:23:45.123Z",
  "level": "ERROR",
  "service": "api-gateway",
  "message": "Connection timeout after 30s",
  "labels": {
    "anomaly_type": "network_latency",
    "severity": "high",
    "affected_services": ["user-service", "auth-service"]
  }
}
```

## Collection Guidelines

1. Anonymize all PII before adding to this directory
2. Include balanced samples of normal and anomalous logs
3. Label each sample with anomaly type and severity
4. Minimum 1000 samples per log category
5. Maintain 80/20 normal/anomalous ratio

## Usage

```python
from dataops.data_ingestion.connectors import JSONConnector, ConnectorConfig

config = ConnectorConfig(
    name="infra_logs",
    connector_type="json",
    connection_params={"path": "training_data/infrastructure_logs/samples.json"}
)
```
