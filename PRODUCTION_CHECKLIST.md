# Ragamuffin Production Checklist

Use this checklist before deploying to production.

## Pre-Deployment

### Security Configuration
- [ ] Changed `SECRET_KEY` in `.env.production` (generate with `openssl rand -hex 32`)
- [ ] Changed `JWT_SECRET` in `.env.production` (generate with `openssl rand -hex 32`)
- [ ] Updated `ALLOWED_ORIGINS` to your production domain(s) only
- [ ] Set `ENABLE_AUTH=true` in `.env.production`
- [ ] Changed default admin password (in `app/auth.py` or use database)
- [ ] Reviewed and configured all environment variables in `.env.production`

### SSL/TLS
- [ ] Obtained SSL/TLS certificates (Let's Encrypt recommended)
- [ ] Configured nginx or reverse proxy for HTTPS
- [ ] Tested SSL configuration (use https://www.ssllabs.com/ssltest/)
- [ ] Enabled HSTS (HTTP Strict Transport Security)
- [ ] Configured automatic certificate renewal

### Infrastructure
- [ ] Set up firewall (allow only ports 80, 443)
- [ ] Configured DNS records for your domain
- [ ] Set up database for persistent storage (PostgreSQL/MongoDB)
- [ ] Configured backup strategy for database and flows
- [ ] Set up monitoring (Prometheus, Grafana, etc.)
- [ ] Configured logging aggregation
- [ ] Set up alerts for critical errors

### Application
- [ ] Updated `VITE_API_URL` in `.env.production` to production API URL
- [ ] Disabled debug mode (checked `ENVIRONMENT=production`)
- [ ] Configured rate limiting
- [ ] Set up file upload size limits
- [ ] Reviewed and tested all API endpoints
- [ ] Implemented flow validation logic
- [ ] Set up database migrations (if using database)

### Network
- [ ] Restricted LangFlow UI access (IP whitelist or remove from public)
- [ ] Restricted LangGraph access
- [ ] Configured CORS to production domains only
- [ ] Enabled compression (gzip)
- [ ] Configured CDN (optional but recommended)

## Deployment

### Build and Deploy
- [ ] Tested production build locally
- [ ] Reviewed docker-compose.prod.yml configuration
- [ ] Set resource limits in docker-compose (CPU, memory)
- [ ] Built production images: `docker compose -f docker-compose.prod.yml build`
- [ ] Started services: `./start-prod.sh`
- [ ] Verified all containers are healthy: `docker compose -f docker-compose.prod.yml ps`

### Testing
- [ ] Tested frontend accessibility (https://yourdomain.com)
- [ ] Tested backend API (https://yourdomain.com/api/)
- [ ] Tested authentication flow
- [ ] Tested flow upload and execution
- [ ] Tested SSL certificate
- [ ] Verified security headers (use https://securityheaders.com/)
- [ ] Load tested application
- [ ] Tested backup and restore procedures

### Monitoring
- [ ] Set up uptime monitoring
- [ ] Configured error tracking (Sentry, etc.)
- [ ] Set up log rotation
- [ ] Enabled health check endpoints monitoring
- [ ] Configured alert notifications (email, Slack, etc.)

## Post-Deployment

### Verification
- [ ] Verified all services are running
- [ ] Checked application logs for errors
- [ ] Tested critical user flows
- [ ] Verified SSL/HTTPS is working correctly
- [ ] Tested from different networks/devices
- [ ] Checked performance metrics

### Documentation
- [ ] Documented deployment process
- [ ] Created runbook for common issues
- [ ] Documented backup/restore procedures
- [ ] Created incident response plan
- [ ] Documented rollback procedure

### Maintenance
- [ ] Scheduled regular security updates
- [ ] Scheduled database backups
- [ ] Scheduled SSL certificate renewal checks
- [ ] Planned capacity monitoring and scaling
- [ ] Set up automated health checks

## Security Hardening

### Application Security
- [ ] Implement rate limiting at application level
- [ ] Add input validation and sanitization
- [ ] Implement CSRF protection
- [ ] Add request size limits
- [ ] Implement session management
- [ ] Add API versioning
- [ ] Implement audit logging

### Infrastructure Security
- [ ] Enable fail2ban or similar intrusion prevention
- [ ] Configure firewall rules
- [ ] Disable unnecessary services
- [ ] Update all system packages
- [ ] Implement Web Application Firewall (WAF)
- [ ] Set up DDoS protection
- [ ] Enable container security scanning

### Data Security
- [ ] Encrypt data at rest
- [ ] Encrypt data in transit
- [ ] Implement secure key management
- [ ] Configure database access controls
- [ ] Implement data retention policies
- [ ] Set up data backup encryption

## Compliance and Legal

- [ ] Privacy policy created and accessible
- [ ] Terms of service created
- [ ] GDPR compliance checked (if applicable)
- [ ] Data processing agreements in place
- [ ] Cookie consent implemented (if applicable)
- [ ] Security audit completed

## Scaling Preparation

- [ ] Documented scaling strategy
- [ ] Tested horizontal scaling
- [ ] Configured load balancer
- [ ] Set up auto-scaling rules (if on cloud)
- [ ] Identified performance bottlenecks
- [ ] Planned database scaling strategy

## Emergency Procedures

- [ ] Documented rollback procedure
- [ ] Tested rollback process
- [ ] Created emergency contact list
- [ ] Documented disaster recovery plan
- [ ] Tested restore from backup
- [ ] Created incident response checklist

---

## Notes

Use this space to document environment-specific notes:

- Production URL: _______________
- Deployment date: _______________
- Deployed by: _______________
- Database: _______________
- Backup location: _______________
- Monitoring dashboard: _______________

## Sign-off

- [ ] Security review completed by: _______________ Date: _______________
- [ ] Technical review completed by: _______________ Date: _______________
- [ ] Final approval by: _______________ Date: _______________
