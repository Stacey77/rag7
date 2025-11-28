# Security Guidelines for Ragamuffin Platform

## ⚠️ Important Security Notice

**This is a development scaffold. DO NOT deploy to production without implementing the security measures outlined in this document.**

## Critical Security Issues to Address

### 1. Authentication & Authorization

**Current State:** Basic JWT implementation with hardcoded credentials
- Default admin credentials: `admin/admin123`
- In-memory user database
- No role-based access control (RBAC)

**Production Requirements:**
```bash
# Change these immediately:
- JWT_SECRET_KEY: Use a strong, randomly generated secret (256-bit minimum)
- Default passwords: Remove or change all default credentials
- Database: Use a real database (PostgreSQL, MySQL) for user storage
```

**Recommended Improvements:**
- Implement OAuth2/OIDC (Auth0, Keycloak, AWS Cognito)
- Add Multi-Factor Authentication (MFA/2FA)
- Implement Role-Based Access Control (RBAC)
- Add API key authentication for service-to-service calls
- Session management with secure tokens
- Password policies: minimum 12 characters, complexity requirements
- Account lockout after failed attempts
- Audit logging for all authentication events

### 2. CORS Configuration

**Current State:** Allows all localhost origins
```python
# INSECURE - Development only
origins = ["http://localhost:8080", "http://localhost:5173", "http://localhost:3000"]
```

**Production Configuration:**
```python
# Restrict to specific domains
origins = [
    "https://yourdomain.com",
    "https://app.yourdomain.com"
]

# Add CORS headers
allow_credentials=True
allow_methods=["GET", "POST", "PUT", "DELETE"]
allow_headers=["Authorization", "Content-Type"]
```

### 3. Flow Execution Security

**CRITICAL: Flows can execute arbitrary Python code**

**Current State:** No sandboxing or validation
- Flows run in the same process as the API
- No resource limits
- No code validation
- Can access file system and network

**Required Mitigations:**
1. **Sandboxing:** Run flows in isolated containers
   ```yaml
   # Docker-in-Docker or separate worker containers
   - Separate execution environment
   - Limited network access
   - Read-only file system
   - Resource limits (CPU, memory, time)
   ```

2. **Validation:** Validate flow JSON before execution
   ```python
   - JSON schema validation
   - Whitelist allowed components
   - Check for malicious patterns
   - Scan for sensitive data access
   ```

3. **Approval Workflow:** Require manual approval for untrusted flows
   ```
   - Review queue for new flows
   - Admin approval before execution
   - User reputation system
   - Automated security scanning
   ```

### 4. Input Validation

**Current State:** Minimal validation

**Required Improvements:**
- Validate all file uploads (type, size, content)
- Sanitize all text inputs
- Limit payload sizes
- Validate JSON structure
- Check for SQL injection patterns
- Prevent XXE attacks in XML/JSON
- Rate limit uploads

**Example:**
```python
# File upload limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {'.json', '.txt', '.pdf', '.jpg', '.png'}

# Text input limits
MAX_TEXT_LENGTH = 50000  # characters
MAX_BATCH_SIZE = 100  # items
```

### 5. Rate Limiting

**Current State:** Basic slowapi rate limiting

**Production Configuration:**
```python
# Adjust based on your needs
- API endpoints: 100 requests/minute per IP
- Authentication: 5 attempts/minute per IP
- File uploads: 10 uploads/hour per user
- RAG queries: 60 queries/minute per user
- Embedding generation: 100 items/hour per user
```

**Advanced Features:**
- User-based rate limiting (not just IP)
- Dynamic rate limits based on subscription tier
- Distributed rate limiting (Redis)
- Rate limit headers in responses
- Exponential backoff for repeated violations

### 6. Secrets Management

**NEVER commit secrets to git**

**Current Issues:**
- Hardcoded JWT secret
- Default credentials in docker-compose
- API keys in plaintext

**Solutions:**
```bash
# Use environment variables
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export DATABASE_URL="postgresql://..."
export OPENAI_API_KEY="sk-..."

# Use secrets management services
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Docker Secrets
- Kubernetes Secrets
```

**Update `.gitignore`:**
```
.env
.env.local
.env.production
*.key
*.pem
secrets/
```

### 7. Database Security

**Current State:** In-memory fake database

**Production Requirements:**
- Use a real database with authentication
- Encrypt data at rest
- Use prepared statements (prevent SQL injection)
- Regular backups with encryption
- Limit database user permissions
- Monitor for suspicious queries
- Enable audit logging

### 8. Network Security

**Required Configurations:**
```yaml
# Use HTTPS/TLS for all services
- Frontend: HTTPS with valid certificate
- Backend API: HTTPS only
- Internal services: mTLS for service-to-service

# Firewall rules
- Restrict Milvus, Etcd, MinIO to internal network only
- No direct external access to databases
- Use VPN for administrative access
```

### 9. Dependency Security

**Regular Updates Required:**
```bash
# Check for vulnerabilities
pip-audit  # Python
npm audit  # Node.js

# Update dependencies
pip install --upgrade -r requirements.txt
npm update
```

**Pinned Versions:**
```
# requirements.txt
fastapi==0.104.1  # Pin exact versions
uvicorn[standard]==0.24.0
# Not: fastapi>=0.100.0  # Too permissive
```

### 10. Logging & Monitoring

**Security Logging:**
```python
# Log these events:
- Authentication attempts (success/failure)
- Authorization failures
- Flow executions
- File uploads
- API rate limit violations
- Suspicious activity patterns
- Error rates and types
```

**Monitoring Alerts:**
- Unusual number of authentication failures
- Spike in 4xx/5xx errors
- Large file uploads
- Unexpected flow executions
- Resource exhaustion
- Database connection issues

## Security Checklist for Production

### Before Deployment:
- [ ] Change all default passwords and secrets
- [ ] Enable HTTPS/TLS on all services
- [ ] Configure production CORS origins
- [ ] Implement proper authentication (OAuth2/OIDC recommended)
- [ ] Add rate limiting appropriate for your use case
- [ ] Set up secrets management (not environment variables)
- [ ] Configure database with encryption and backups
- [ ] Implement flow validation and sandboxing
- [ ] Add comprehensive input validation
- [ ] Set up monitoring and alerting
- [ ] Enable security headers (CSP, HSTS, etc.)
- [ ] Perform security audit and penetration testing
- [ ] Set up WAF (Web Application Firewall)
- [ ] Implement DDoS protection
- [ ] Configure logging and audit trails
- [ ] Document incident response procedures
- [ ] Set up automatic security updates
- [ ] Implement data encryption at rest
- [ ] Add backup and disaster recovery plan
- [ ] Review and test all authentication flows

### Regular Maintenance:
- [ ] Update dependencies monthly
- [ ] Review security logs weekly
- [ ] Test backups monthly
- [ ] Rotate secrets quarterly
- [ ] Security audit annually
- [ ] Penetration testing annually
- [ ] Review access controls quarterly
- [ ] Update incident response plan annually

## Reporting Security Issues

If you discover a security vulnerability, please email: security@yourdomain.com

**Do NOT create public GitHub issues for security vulnerabilities.**

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)

## Compliance Considerations

Depending on your use case, you may need to comply with:
- **GDPR** (EU data protection)
- **CCPA** (California privacy)
- **HIPAA** (healthcare data in US)
- **SOC 2** (security audits)
- **ISO 27001** (information security)

Consult with legal and compliance teams before deploying with sensitive data.
