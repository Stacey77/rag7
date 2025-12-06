# Incident Runbook

This runbook provides step-by-step procedures for responding to incidents, performing rollbacks, and troubleshooting common issues in the Rag7 production environment.

## 🚨 Emergency Contacts

- **On-call Engineer**: [Contact info]
- **Team Lead**: [Contact info]
- **DevOps/SRE**: [Contact info]
- **Slack Channel**: #rag7-incidents
- **Status Page**: https://status.example.com

---

## Incident Response Process

### 1. Acknowledge & Assess

- [ ] Acknowledge the alert/incident
- [ ] Determine severity (P0-Critical, P1-High, P2-Medium, P3-Low)
- [ ] Notify team in #rag7-incidents
- [ ] Start incident log/timeline

### 2. Investigate

- [ ] Check health endpoints
- [ ] Review recent deployments
- [ ] Check logs for errors
- [ ] Review metrics/dashboards
- [ ] Verify external dependencies

### 3. Mitigate

- [ ] Implement immediate fix or rollback
- [ ] Verify mitigation is working
- [ ] Update status page
- [ ] Continue monitoring

### 4. Resolve

- [ ] Confirm issue is fully resolved
- [ ] Update status page
- [ ] Notify stakeholders
- [ ] Schedule post-mortem

### 5. Post-Mortem

- [ ] Document timeline of events
- [ ] Identify root cause
- [ ] Define action items
- [ ] Update runbook/documentation

---

## Common Incidents

### High Error Rate (5xx Errors)

#### Symptoms
- Alert: `HighErrorRate`
- Users reporting failures
- Increased 5xx responses in logs

#### Investigation Steps

```bash
# Check application logs
docker-compose -f docker-compose.prod.yml logs langgraph --tail=100

# Or for Kubernetes
kubectl logs -n rag7-staging -l app=langgraph-api --tail=100

# Check error patterns
kubectl logs -n rag7-staging -l app=langgraph-api | grep ERROR

# Check database connectivity
docker exec rag7-postgres pg_isready -U rag7user

# Check Redis
docker exec rag7-redis redis-cli ping
```

#### Resolution Steps

1. **If database connection issues**:
   ```bash
   # Restart database (Docker Compose)
   docker-compose -f docker-compose.prod.yml restart postgres
   
   # Or check database pods (K8s)
   kubectl get pods -n rag7-staging -l app=postgres
   ```

2. **If application error**:
   - Check recent code changes
   - Review application logs for stack traces
   - Consider rollback (see Rollback Procedures)

3. **If external API failure**:
   - Verify API credentials
   - Check API status pages
   - Implement circuit breaker if needed

---

### High Latency / Slow Responses

#### Symptoms
- Alert: `HighLatency`
- Users reporting slow performance
- P95 latency > 2 seconds

#### Investigation Steps

```bash
# Check resource usage
docker stats

# Or for Kubernetes
kubectl top pods -n rag7-staging

# Check database performance
docker exec rag7-postgres psql -U rag7user -d rag7_prod -c "
  SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
  FROM pg_stat_activity 
  WHERE state = 'active' 
  ORDER BY duration DESC;
"

# Check Redis performance
docker exec rag7-redis redis-cli --latency
```

#### Resolution Steps

1. **If CPU/Memory exhaustion**:
   ```bash
   # Scale up (Docker Compose - increase limits in docker-compose.prod.yml)
   
   # Scale up (Kubernetes)
   kubectl scale deployment langgraph-api -n rag7-staging --replicas=5
   ```

2. **If database slow queries**:
   - Review and optimize slow queries
   - Add missing indexes
   - Consider read replicas

3. **If cache issues**:
   - Check Redis memory usage
   - Clear cache if needed: `docker exec rag7-redis redis-cli FLUSHDB`

---

### Pod/Container Crash Loop

#### Symptoms
- Alert: `PodCrashLooping`
- Pods constantly restarting
- Service unavailable

#### Investigation Steps

```bash
# Check pod status
kubectl get pods -n rag7-staging -l app=langgraph-api

# View pod events
kubectl describe pod <pod-name> -n rag7-staging

# Check logs from previous instance
kubectl logs <pod-name> -n rag7-staging --previous

# For Docker Compose
docker-compose -f docker-compose.prod.yml ps
docker logs rag7-langgraph
```

#### Common Causes & Fixes

1. **Missing environment variables**:
   - Check secrets exist: `kubectl get secrets -n rag7-staging`
   - Verify .env.prod file (Docker Compose)

2. **Failed health checks**:
   - Increase `initialDelaySeconds` in deployment.yaml
   - Check health endpoint manually

3. **OOM (Out of Memory)**:
   - Increase memory limits in deployment
   - Check for memory leaks

4. **Image pull errors**:
   ```bash
   # Verify image exists
   docker pull ghcr.io/stacey77/rag7:latest
   
   # Check pull secret
   kubectl get secret ghcr-pull-secret -n rag7-staging
   ```

---

### Database Connection Pool Exhausted

#### Symptoms
- Errors: "connection pool exhausted"
- Unable to create new connections
- Increased latency

#### Investigation Steps

```bash
# Check active connections
docker exec rag7-postgres psql -U rag7user -d rag7_prod -c "
  SELECT count(*) as connection_count, state 
  FROM pg_stat_activity 
  GROUP BY state;
"

# Check connection limits
docker exec rag7-postgres psql -U rag7user -d rag7_prod -c "
  SHOW max_connections;
"
```

#### Resolution Steps

1. **Increase connection pool size** (application config)
2. **Increase database max_connections** (PostgreSQL config)
3. **Implement connection timeout** to prevent hanging connections
4. **Scale application horizontally** to distribute load

---

### Disk Space Full

#### Symptoms
- Write operations failing
- Database errors
- Logs not being written

#### Investigation Steps

```bash
# Check disk usage
df -h

# For Docker volumes
docker system df -v

# For Kubernetes persistent volumes
kubectl get pv
kubectl describe pv <pv-name>
```

#### Resolution Steps

1. **Clean up logs**:
   ```bash
   # Docker
   docker system prune -a --volumes
   
   # Application logs
   find /var/log -type f -name "*.log" -mtime +30 -delete
   ```

2. **Expand volume** (cloud provider specific)

3. **Implement log rotation**:
   - Configure logrotate
   - Set retention policies

---

## Rollback Procedures

### Kubernetes Rollback

```bash
# Check deployment history
kubectl rollout history deployment/langgraph-api -n rag7-staging

# Rollback to previous version
kubectl rollout undo deployment/langgraph-api -n rag7-staging

# Rollback to specific revision
kubectl rollout undo deployment/langgraph-api -n rag7-staging --to-revision=3

# Monitor rollback
kubectl rollout status deployment/langgraph-api -n rag7-staging

# Verify
kubectl get pods -n rag7-staging -l app=langgraph-api
```

### Docker Compose Rollback

```bash
# Stop current deployment
docker-compose -f docker-compose.prod.yml down

# Pull previous image version
docker pull ghcr.io/stacey77/rag7:v1.2.3

# Update docker-compose.prod.yml to use specific version
# Then restart
docker-compose -f docker-compose.prod.yml up -d

# Verify
docker-compose -f docker-compose.prod.yml ps
curl http://localhost:8000/health
```

---

## Troubleshooting Checklist

### Application Won't Start

- [ ] Check environment variables are set
- [ ] Verify secrets/config files exist
- [ ] Check database is accessible
- [ ] Verify Redis is accessible
- [ ] Check application logs for startup errors
- [ ] Verify image exists and is pullable
- [ ] Check port conflicts
- [ ] Verify sufficient resources (CPU/memory)

### Deployment Failing

- [ ] Check CI/CD pipeline logs
- [ ] Verify GHCR token has correct permissions
- [ ] Check kubeconfig secret is valid
- [ ] Verify cluster has sufficient resources
- [ ] Check image was built successfully
- [ ] Verify namespace exists
- [ ] Check RBAC permissions

### Performance Degradation

- [ ] Check resource utilization (CPU, memory, disk)
- [ ] Review recent code changes
- [ ] Check database performance
- [ ] Verify cache is working
- [ ] Check for increased traffic
- [ ] Review slow query logs
- [ ] Check for network issues
- [ ] Verify external API performance

### Data Issues

- [ ] Check database backups exist
- [ ] Verify data integrity
- [ ] Check for recent migrations
- [ ] Review audit logs
- [ ] Verify replication status
- [ ] Check for disk space issues

---

## Useful Commands

### Health Checks

```bash
# Application health
curl http://localhost:8000/health
curl http://localhost:8000/ready

# Database health
docker exec rag7-postgres pg_isready -U rag7user

# Redis health
docker exec rag7-redis redis-cli ping
```

### Logs

```bash
# Docker Compose - tail logs
docker-compose -f docker-compose.prod.yml logs -f --tail=100

# Kubernetes - tail logs
kubectl logs -n rag7-staging -l app=langgraph-api -f --tail=100

# Filter for errors
kubectl logs -n rag7-staging -l app=langgraph-api | grep ERROR
```

### Resource Usage

```bash
# Docker stats
docker stats --no-stream

# Kubernetes pod resources
kubectl top pods -n rag7-staging

# Kubernetes node resources
kubectl top nodes
```

### Database Operations

```bash
# Connect to database
docker exec -it rag7-postgres psql -U rag7user -d rag7_prod

# Create backup
docker exec rag7-postgres pg_dump -U rag7user rag7_prod > backup_$(date +%Y%m%d).sql

# Restore backup
docker exec -i rag7-postgres psql -U rag7user -d rag7_prod < backup.sql
```

---

## Escalation Matrix

| Severity | Response Time | Escalation |
|----------|--------------|------------|
| P0 - Critical | Immediate | Page on-call + Team Lead |
| P1 - High | 15 minutes | On-call engineer |
| P2 - Medium | 1 hour | On-call engineer |
| P3 - Low | Next business day | Team queue |

---

## Post-Incident Actions

1. **Document the incident**:
   - Timeline of events
   - Root cause
   - Impact assessment
   - Resolution steps taken

2. **Schedule post-mortem** (within 48 hours for P0/P1)

3. **Create action items**:
   - Preventive measures
   - Monitoring improvements
   - Documentation updates
   - Code/infrastructure fixes

4. **Update runbook** with lessons learned

5. **Share learnings** with team

---

## Maintenance Windows

Schedule regular maintenance during low-traffic periods:

- **Database maintenance**: Weekly, Sundays 2-4 AM UTC
- **Security patches**: As needed, Tuesdays 2-4 AM UTC
- **Major upgrades**: Quarterly, scheduled in advance

Always notify users via status page before maintenance.

---

## Additional Resources

- [Deployment Guide](./deployment.md)
- [Observability Guide](./observability.md)
- Monitoring Dashboard: http://grafana.example.com
- Logs: http://kibana.example.com
- Traces: http://jaeger.example.com

---

**Remember**: When in doubt, rollback first, investigate second. User experience is priority #1.
