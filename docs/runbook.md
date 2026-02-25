# Operations Runbook

This runbook provides step-by-step procedures for common operational tasks and incident response.

## Table of Contents

- [Emergency Contacts](#emergency-contacts)
- [Common Incidents](#common-incidents)
- [Operational Procedures](#operational-procedures)
- [Maintenance Tasks](#maintenance-tasks)
- [Recovery Procedures](#recovery-procedures)

## Emergency Contacts

### On-Call Schedule

| Role | Primary | Secondary |
|------|---------|-----------|
| Engineering | TODO: Add | TODO: Add |
| DevOps | TODO: Add | TODO: Add |
| Manager | TODO: Add | TODO: Add |

### Escalation Path

1. On-call engineer (15 min response time)
2. Secondary on-call (30 min response time)
3. Engineering manager (1 hour response time)

### Communication Channels

- **Slack**: #incidents (for incident coordination)
- **PagerDuty**: For critical alerts
- **Status Page**: TODO: Add URL

## Common Incidents

### High Error Rate

**Symptoms:**
- Alert: "HighErrorRate" firing
- Increased 5xx responses
- User reports of failures

**Diagnosis:**

```bash
# Check error logs
kubectl logs -n rag7 -l app=langgraph --tail=100 | grep ERROR

# Check error metrics
curl http://localhost:9090/metrics | grep error

# Check recent deployments
kubectl rollout history deployment/langgraph -n rag7
```

**Resolution Steps:**

1. **Identify error type**
   ```bash
   # Group errors by type
   kubectl logs -n rag7 -l app=langgraph | grep ERROR | cut -d' ' -f5- | sort | uniq -c | sort -rn
   ```

2. **Check dependencies**
   ```bash
   # Test database connection
   kubectl run -n rag7 -it --rm debug --image=postgres:15-alpine --restart=Never \
     -- psql -h postgres.rag7.svc.cluster.local -U langgraph -c "SELECT 1"
   
   # Test Redis connection
   kubectl run -n rag7 -it --rm debug --image=redis:7-alpine --restart=Never \
     -- redis-cli -h redis.rag7.svc.cluster.local ping
   ```

3. **Rollback if recent deployment**
   ```bash
   kubectl rollout undo deployment/langgraph -n rag7
   ```

4. **Scale up if capacity issue**
   ```bash
   kubectl scale deployment/langgraph -n rag7 --replicas=5
   ```

### High Latency

**Symptoms:**
- Alert: "HighLatency" firing
- Slow response times
- Request timeouts

**Diagnosis:**

```bash
# Check request latency
curl http://localhost:9090/metrics | grep duration

# Check resource usage
kubectl top pods -n rag7

# Check database slow queries
kubectl exec -n rag7 -it deployment/postgres -- \
  psql -U langgraph -c "SELECT query, calls, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10"
```

**Resolution Steps:**

1. **Check for resource constraints**
   ```bash
   kubectl describe pod -n rag7 POD_NAME | grep -A 5 "Limits\|Requests"
   ```

2. **Scale horizontally**
   ```bash
   kubectl scale deployment/langgraph -n rag7 --replicas=8
   ```

3. **Check for memory leaks**
   ```bash
   kubectl top pods -n rag7 --sort-by=memory
   ```

4. **Restart pods if necessary**
   ```bash
   kubectl rollout restart deployment/langgraph -n rag7
   ```

### Pod Crash Loop

**Symptoms:**
- Alert: "PodRestarting" firing
- Pods in CrashLoopBackOff state
- Service degradation

**Diagnosis:**

```bash
# Check pod status
kubectl get pods -n rag7

# View recent logs
kubectl logs -n rag7 POD_NAME --tail=100

# View previous container logs
kubectl logs -n rag7 POD_NAME --previous

# Describe pod for events
kubectl describe pod -n rag7 POD_NAME
```

**Resolution Steps:**

1. **Check for configuration issues**
   ```bash
   kubectl get configmap langgraph-config -n rag7 -o yaml
   kubectl get secret langgraph-secrets -n rag7 -o yaml
   ```

2. **Verify image**
   ```bash
   kubectl get deployment langgraph -n rag7 -o jsonpath='{.spec.template.spec.containers[0].image}'
   ```

3. **Check resource limits**
   ```bash
   kubectl describe pod -n rag7 POD_NAME | grep -A 5 "Limits"
   ```

4. **Fix and redeploy**
   ```bash
   # Update configuration
   kubectl edit configmap langgraph-config -n rag7
   
   # Restart deployment
   kubectl rollout restart deployment/langgraph -n rag7
   ```

### Database Connection Issues

**Symptoms:**
- Database connection errors in logs
- "connection refused" or "connection timeout"
- Service unavailable

**Diagnosis:**

```bash
# Check PostgreSQL pod status
kubectl get pods -n rag7 -l app=postgres

# Check PostgreSQL logs
kubectl logs -n rag7 -l app=postgres --tail=100

# Test connection from application pod
kubectl exec -n rag7 -it deployment/langgraph -- \
  python -c "import psycopg2; conn = psycopg2.connect('postgresql://langgraph:PASSWORD@postgres.rag7.svc.cluster.local/langgraph_checkpoints'); print('Connected')"
```

**Resolution Steps:**

1. **Check database is running**
   ```bash
   kubectl get statefulset postgres -n rag7
   ```

2. **Check connection limits**
   ```bash
   kubectl exec -n rag7 -it statefulset/postgres -- \
     psql -U langgraph -c "SHOW max_connections"
   
   kubectl exec -n rag7 -it statefulset/postgres -- \
     psql -U langgraph -c "SELECT count(*) FROM pg_stat_activity"
   ```

3. **Restart PostgreSQL if needed**
   ```bash
   kubectl delete pod -n rag7 -l app=postgres
   ```

4. **Check for disk space issues**
   ```bash
   kubectl exec -n rag7 -it statefulset/postgres -- df -h
   ```

### Out of Memory (OOM)

**Symptoms:**
- Pods killed by OOMKiller
- Memory usage at 100%
- Frequent restarts

**Diagnosis:**

```bash
# Check memory usage
kubectl top pods -n rag7

# Check OOM events
kubectl get events -n rag7 --sort-by='.lastTimestamp' | grep OOM

# Check memory limits
kubectl describe pod -n rag7 POD_NAME | grep -A 3 "Limits"
```

**Resolution Steps:**

1. **Increase memory limits**
   ```bash
   kubectl edit deployment langgraph -n rag7
   # Update memory limits under resources
   ```

2. **Check for memory leaks**
   ```bash
   # Monitor memory over time
   kubectl top pods -n rag7 --watch
   ```

3. **Scale horizontally instead**
   ```bash
   kubectl scale deployment/langgraph -n rag7 --replicas=6
   ```

### API Rate Limiting

**Symptoms:**
- 429 Too Many Requests errors
- LLM provider rate limit errors
- Requests being throttled

**Diagnosis:**

```bash
# Check rate limit errors
kubectl logs -n rag7 -l app=langgraph | grep "rate limit"

# Check metrics
curl http://localhost:9090/metrics | grep rate_limit
```

**Resolution Steps:**

1. **Implement exponential backoff** (code change required)

2. **Distribute load across multiple API keys**
   ```bash
   kubectl edit secret langgraph-secrets -n rag7
   # Add additional API keys
   ```

3. **Cache responses to reduce API calls**
   ```bash
   # Verify Redis is working
   kubectl get pods -n rag7 -l app=redis
   ```

4. **Contact provider for rate limit increase**

## Operational Procedures

### Deployment Procedure

**Standard Deployment:**

```bash
# 1. Review changes
git diff main..feature-branch

# 2. Merge to main
git checkout main
git merge feature-branch

# 3. Tag release
git tag -a v1.0.1 -m "Release 1.0.1"
git push origin v1.0.1

# 4. Build and push image (CI does this automatically)
# CI will build and push ghcr.io/stacey77/rag7:v1.0.1

# 5. Update deployment
kubectl set image deployment/langgraph -n rag7 \
  langgraph=ghcr.io/stacey77/rag7:v1.0.1

# 6. Monitor rollout
kubectl rollout status deployment/langgraph -n rag7

# 7. Verify deployment
curl http://API_ENDPOINT/health
```

**Hotfix Deployment:**

```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-fix main

# 2. Make minimal fix
# ... edit files ...

# 3. Test locally
docker build -t rag7:hotfix .
docker run -p 8123:8123 rag7:hotfix

# 4. Deploy directly
git commit -am "Hotfix: description"
git push origin hotfix/critical-fix

# 5. Trigger CD pipeline or deploy manually
kubectl set image deployment/langgraph -n rag7 \
  langgraph=ghcr.io/stacey77/rag7:hotfix-critical-fix

# 6. Monitor closely
kubectl logs -n rag7 -l app=langgraph -f
```

### Rollback Procedure

```bash
# 1. List rollout history
kubectl rollout history deployment/langgraph -n rag7

# 2. Rollback to previous version
kubectl rollout undo deployment/langgraph -n rag7

# 3. Or rollback to specific revision
kubectl rollout undo deployment/langgraph -n rag7 --to-revision=5

# 4. Monitor rollback
kubectl rollout status deployment/langgraph -n rag7

# 5. Verify service health
curl http://API_ENDPOINT/health
```

### Scaling Procedure

**Manual Scaling:**

```bash
# Scale up
kubectl scale deployment/langgraph -n rag7 --replicas=8

# Scale down
kubectl scale deployment/langgraph -n rag7 --replicas=2

# Verify
kubectl get pods -n rag7 -l app=langgraph
```

**Adjust HPA:**

```bash
# Update HPA limits
kubectl edit hpa langgraph-hpa -n rag7

# Check HPA status
kubectl get hpa -n rag7
kubectl describe hpa langgraph-hpa -n rag7
```

### Backup Procedure

**Database Backup:**

```bash
# 1. Create backup
kubectl exec -n rag7 statefulset/postgres -- \
  pg_dump -U langgraph langgraph_checkpoints > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Compress
gzip backup_*.sql

# 3. Upload to storage
aws s3 cp backup_*.sql.gz s3://rag7-backups/$(date +%Y/%m/%d)/

# 4. Verify backup
gunzip -c backup_*.sql.gz | head -n 20
```

**Configuration Backup:**

```bash
# Export all configurations
kubectl get all,configmap,secret -n rag7 -o yaml > rag7_backup_$(date +%Y%m%d).yaml

# Store securely
gpg -c rag7_backup_$(date +%Y%m%d).yaml
```

## Maintenance Tasks

### Certificate Renewal

```bash
# Check certificate expiration
kubectl get certificate -n rag7

# Renew certificate (cert-manager does this automatically)
kubectl describe certificate langgraph-tls -n rag7

# Manual renewal if needed
kubectl delete secret langgraph-tls -n rag7
# cert-manager will recreate
```

### Database Maintenance

```bash
# Vacuum database
kubectl exec -n rag7 statefulset/postgres -- \
  psql -U langgraph -c "VACUUM ANALYZE"

# Check database size
kubectl exec -n rag7 statefulset/postgres -- \
  psql -U langgraph -c "SELECT pg_size_pretty(pg_database_size('langgraph_checkpoints'))"

# Clean old checkpoints (if applicable)
kubectl exec -n rag7 statefulset/postgres -- \
  psql -U langgraph -c "DELETE FROM checkpoints WHERE created_at < NOW() - INTERVAL '30 days'"
```

### Log Rotation

```bash
# Check log volume sizes
kubectl exec -n rag7 POD_NAME -- du -sh /var/log

# Logs are automatically rotated by Kubernetes
# Configure retention in logging backend (ELK, Loki, etc.)
```

## Recovery Procedures

### Disaster Recovery

**Complete Cluster Failure:**

1. **Provision new cluster**
2. **Restore configurations**
   ```bash
   kubectl apply -f rag7_backup_YYYYMMDD.yaml
   ```
3. **Restore database**
   ```bash
   kubectl exec -n rag7 -it statefulset/postgres -- \
     psql -U langgraph langgraph_checkpoints < backup_YYYYMMDD.sql
   ```
4. **Verify services**
5. **Update DNS/Load Balancer**

### Data Corruption

```bash
# 1. Stop application
kubectl scale deployment/langgraph -n rag7 --replicas=0

# 2. Restore database from backup
kubectl exec -n rag7 -it statefulset/postgres -- \
  dropdb -U langgraph langgraph_checkpoints
kubectl exec -n rag7 -it statefulset/postgres -- \
  createdb -U langgraph langgraph_checkpoints
kubectl exec -n rag7 -it statefulset/postgres -- \
  psql -U langgraph langgraph_checkpoints < backup_YYYYMMDD.sql

# 3. Restart application
kubectl scale deployment/langgraph -n rag7 --replicas=2

# 4. Verify data integrity
# Run validation queries
```

## Appendix

### Useful Commands

```bash
# Get cluster info
kubectl cluster-info

# Get all resources in namespace
kubectl get all -n rag7

# Check resource usage
kubectl top nodes
kubectl top pods -n rag7

# Port forward for local testing
kubectl port-forward -n rag7 svc/langgraph 8123:8123

# Execute command in pod
kubectl exec -n rag7 -it POD_NAME -- /bin/bash

# Copy files from pod
kubectl cp rag7/POD_NAME:/path/to/file ./local/path

# View events
kubectl get events -n rag7 --sort-by='.lastTimestamp'
```

### Monitoring Dashboards

- **Grafana**: TODO: Add URL
- **Prometheus**: TODO: Add URL
- **Jaeger**: TODO: Add URL
- **Kibana/Loki**: TODO: Add URL

### Documentation Links

- [Deployment Guide](./deployment.md)
- [Observability Guide](./observability.md)
- [n8n Workflows](../n8n/README.md)
- [API Documentation](TODO)

---

**Remember:** Always follow the change management process and communicate with the team during incidents.
