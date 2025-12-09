# Operational Runbook

## Overview

This runbook provides step-by-step procedures for common operational tasks and incident response.

## Common Operations

### Restarting Services

**Docker Compose**
```bash
# Restart all services
docker-compose -f docker-compose.prod.yml restart

# Restart specific service
docker-compose -f docker-compose.prod.yml restart langgraph-api

# Full stop and start
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

**Kubernetes**
```bash
# Rolling restart
kubectl rollout restart deployment/langgraph-api -n rag7-prod

# Delete pod (will be recreated)
kubectl delete pod <pod-name> -n rag7-prod

# Scale to zero and back
kubectl scale deployment langgraph-api --replicas=0 -n rag7-prod
kubectl scale deployment langgraph-api --replicas=3 -n rag7-prod
```

### Updating Configuration

**Docker Compose**
```bash
# Update .env.prod file
nano .env.prod

# Recreate containers with new config
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

**Kubernetes**
```bash
# Update ConfigMap
kubectl edit configmap rag7-config -n rag7-prod

# Update Secret
kubectl edit secret rag7-secrets -n rag7-prod

# Restart pods to pick up changes
kubectl rollout restart deployment/langgraph-api -n rag7-prod
```

### Scaling Operations

**Manual Scaling (Kubernetes)**
```bash
# Scale up
kubectl scale deployment langgraph-api --replicas=5 -n rag7-prod

# Scale down
kubectl scale deployment langgraph-api --replicas=2 -n rag7-prod

# Check current scale
kubectl get deployment langgraph-api -n rag7-prod
```

**Update HPA Limits**
```bash
# Edit HPA
kubectl edit hpa langgraph-api-hpa -n rag7-prod

# Or apply updated file
kubectl apply -f k8s/hpa.yaml
```

### Viewing Logs

**Recent Logs**
```bash
# Docker Compose - last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 langgraph-api

# Kubernetes - last 100 lines
kubectl logs -n rag7-prod deployment/langgraph-api --tail=100
```

**Follow Logs in Real-Time**
```bash
# Docker Compose
docker-compose -f docker-compose.prod.yml logs -f langgraph-api

# Kubernetes
kubectl logs -n rag7-prod -f deployment/langgraph-api
```

**Search Logs**
```bash
# Docker Compose - search for errors
docker-compose -f docker-compose.prod.yml logs langgraph-api | grep -i error

# Kubernetes - search for specific pattern
kubectl logs -n rag7-prod deployment/langgraph-api | grep -i "connection refused"
```

## Incident Response Procedures

### Procedure 1: API is Down (Health Check Failing)

**Symptoms**
- Health check endpoint returns 503 or times out
- No response from API
- Users reporting errors

**Diagnosis**
```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps
# OR
kubectl get pods -n rag7-prod

# Check logs for errors
docker-compose -f docker-compose.prod.yml logs --tail=200 langgraph-api
# OR
kubectl logs -n rag7-prod deployment/langgraph-api --tail=200

# Test health endpoint directly
curl -v http://localhost:8000/health
```

**Resolution Steps**
1. Check if container/pod is running
2. Review recent logs for error messages
3. Verify environment variables are set correctly
4. Check database connectivity
5. Restart service
6. If restart fails, rollback to previous version
7. Escalate if issue persists

**Prevention**
- Setup alerting for health check failures
- Configure liveness/readiness probes correctly
- Implement graceful shutdown handling

### Procedure 2: High Error Rate (5xx Errors)

**Symptoms**
- Elevated 500/502/503 error responses
- Alert: HighErrorRate triggered
- Increased error logs

**Diagnosis**
```bash
# Check error rate in Prometheus
# Query: rate(http_requests_total{status=~"5.."}[5m])

# Review error logs
kubectl logs -n rag7-prod deployment/langgraph-api | grep -i "error\|exception"

# Check resource usage
kubectl top pods -n rag7-prod
```

**Resolution Steps**
1. Identify error pattern in logs
2. Check if specific endpoint or operation is failing
3. Verify external dependencies (database, providers)
4. Check resource constraints (CPU/memory)
5. Scale up if needed
6. Apply hotfix if code issue identified
7. Monitor error rate after changes

**Prevention**
- Implement circuit breakers for external calls
- Add proper error handling and retries
- Set resource limits appropriately

### Procedure 3: High Latency (Slow Response Times)

**Symptoms**
- Alert: HighLatency triggered
- Users reporting slow performance
- P95 latency > 2 seconds

**Diagnosis**
```bash
# Check latency metrics in Prometheus
# Query: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Check resource usage
kubectl top pods -n rag7-prod

# Analyze slow queries in logs
kubectl logs -n rag7-prod deployment/langgraph-api | grep "duration_ms" | sort -t: -k5 -rn | head -20
```

**Resolution Steps**
1. Identify bottleneck (CPU, memory, network, database)
2. Check for slow provider API calls
3. Scale up if resource-constrained
4. Optimize slow queries if identified
5. Enable caching if applicable
6. Monitor latency after changes

**Prevention**
- Implement request timeouts
- Add caching layer for frequent queries
- Optimize database indexes
- Load test before deployment

### Procedure 4: Database Connection Failures

**Symptoms**
- "Cannot connect to database" errors
- Application failing to start
- Health checks passing but ready checks failing

**Diagnosis**
```bash
# Check database container status
docker-compose -f docker-compose.prod.yml ps postgres
# OR
kubectl get pods -n rag7-prod | grep postgres

# Test database connectivity
docker-compose -f docker-compose.prod.yml exec langgraph-api python -c "import psycopg2; conn=psycopg2.connect('$DATABASE_URL'); print('Connected')"

# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres
```

**Resolution Steps**
1. Verify database container is running
2. Check DATABASE_URL environment variable
3. Verify network connectivity
4. Check database user permissions
5. Restart database if needed
6. Check for connection pool exhaustion

**Prevention**
- Configure connection pooling
- Set appropriate connection limits
- Monitor database health
- Implement retry logic with backoff

### Procedure 5: Memory Leak / OOM (Out of Memory)

**Symptoms**
- Container/pod being killed (OOMKilled)
- Memory usage continuously growing
- Application becoming unresponsive

**Diagnosis**
```bash
# Check pod events
kubectl describe pod -n rag7-prod <pod-name>

# Monitor memory usage over time
kubectl top pods -n rag7-prod --watch

# Check memory metrics in Prometheus
# Query: container_memory_usage_bytes{pod=~"langgraph-api.*"}
```

**Resolution Steps**
1. Identify memory leak in application code
2. Increase memory limits as temporary measure
3. Restart affected pods
4. Review recent code changes
5. Profile application to find leak source
6. Deploy fix

**Prevention**
- Regular memory profiling
- Implement memory usage alerts
- Code reviews for resource management
- Load testing to catch leaks early

### Procedure 6: Provider API Failures (kiro.ai, lindy.ai)

**Symptoms**
- Increased provider API errors
- Timeout errors from providers
- Users unable to execute workflows

**Diagnosis**
```bash
# Check provider error rate
# Query: rate(provider_api_errors_total[5m])

# Review provider-specific logs
kubectl logs -n rag7-prod deployment/langgraph-api | grep -i "kiro\|lindy"

# Test provider connectivity
curl -H "Authorization: Bearer $KIRO_AI_API_KEY" https://api.kiro.ai/v1/health
```

**Resolution Steps**
1. Check provider status pages
2. Verify API keys are valid
3. Check rate limits
4. Implement fallback to alternate provider
5. Enable circuit breaker
6. Contact provider support if needed

**Prevention**
- Implement retry logic with exponential backoff
- Configure circuit breakers
- Monitor provider API metrics
- Have fallback providers configured

### Procedure 7: Deployment Failures

**Symptoms**
- New deployment not rolling out
- Pods in CrashLoopBackOff
- Rollout stuck

**Diagnosis**
```bash
# Check rollout status
kubectl rollout status deployment/langgraph-api -n rag7-prod

# Check pod events
kubectl describe pod -n rag7-prod <pod-name>

# View recent logs
kubectl logs -n rag7-prod <pod-name>
```

**Resolution Steps**
1. Review pod events and logs
2. Verify new configuration is correct
3. Check if new image is accessible
4. Rollback to previous version
5. Fix issue and redeploy

```bash
# Rollback deployment
kubectl rollout undo deployment/langgraph-api -n rag7-prod
```

**Prevention**
- Test deployments in staging first
- Use canary deployments
- Implement smoke tests
- Configure proper health checks

## Maintenance Tasks

### Database Backup

```bash
# Docker Compose
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U rag7user rag7_prod > backup_$(date +%Y%m%d).sql

# Restore
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U rag7user rag7_prod < backup_20241209.sql
```

### Certificate Renewal

```bash
# Check certificate expiration
openssl s_client -connect api.yourdomain.com:443 -servername api.yourdomain.com 2>/dev/null | openssl x509 -noout -dates

# Kubernetes with cert-manager auto-renews
# Verify cert-manager is running
kubectl get pods -n cert-manager
```

### Log Rotation

```bash
# Docker Compose - configure in /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}

# Restart Docker daemon
sudo systemctl restart docker
```

### Cleanup Old Resources

```bash
# Remove unused Docker images
docker image prune -a --filter "until=168h"

# Remove old pods (if any)
kubectl delete pod -n rag7-prod --field-selector=status.phase==Succeeded
kubectl delete pod -n rag7-prod --field-selector=status.phase==Failed
```

## On-Call Checklist

When you're on-call, ensure you have:

- [ ] Access to GitHub repository
- [ ] Access to production servers/cluster
- [ ] kubectl configured with production context
- [ ] Access to Grafana and Prometheus
- [ ] Provider API credentials for testing
- [ ] Escalation contacts
- [ ] This runbook readily available

## Emergency Contacts

- **Platform Team**: platform@example.com
- **Database Team**: database@example.com
- **Security Team**: security@example.com
- **Provider Support - kiro.ai**: support@kiro.ai
- **Provider Support - lindy.ai**: support@lindy.ai

## Post-Incident Checklist

After resolving an incident:

1. [ ] Update incident log with resolution
2. [ ] Create post-mortem document
3. [ ] Identify root cause
4. [ ] Create action items to prevent recurrence
5. [ ] Update runbook if new procedure discovered
6. [ ] Communicate resolution to stakeholders
7. [ ] Schedule follow-up review

## Related Documentation

- [Deployment Guide](deployment.md)
- [Observability Guide](observability.md)
- [Integrations Guide](integrations.md)
