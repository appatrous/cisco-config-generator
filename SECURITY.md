# Security Configuration Guide

## 🔐 Overview

This guide covers security best practices for deploying and configuring the Cisco Configuration Generator application.

---

## ⚠️ Critical Security Requirements

### 1. Secret Keys

**NEVER use default secret keys in production!**

All secret keys must be:
- Cryptographically random
- At least 32 bytes (256 bits)
- Different for each environment (dev, staging, prod)
- Never committed to version control
- Rotated periodically (every 90 days recommended)

### 2. Required Secret Variables

| Variable | Purpose | Minimum Length | Must Be Unique |
|----------|---------|----------------|----------------|
| `SECRET_KEY` | Flask session encryption | 32 bytes | Yes |
| `JWT_SECRET_KEY` | JWT token signing | 32 bytes | Yes (different from SECRET_KEY) |
| `DATABASE_PASSWORD` | Database authentication | 24 bytes | Yes |
| `ADMIN_PASSWORD` | Initial admin user | 16 bytes | Yes |

---

## 🔑 Generating Secure Secrets

### Method 1: Using the Built-in Script (Recommended)

Generate all required secrets at once:

```bash
python utils/generate_secrets.py --env
```

Output:
```
# Flask Configuration
SECRET_KEY=Rj7K9mP2nQ5tX8wY1aB3cD6eF9gH0iJ4kL7mN0pQ3rS6tU9vW2xY5zA8bC1dE4f

# JWT Configuration
JWT_SECRET_KEY=aB3cD6eF9gH0iJ4kL7mN0pQ3rS6tU9vW2xY5zA8bC1dE4fG7hI0jK3lM6nO9pQ

# Database Configuration
DATABASE_PASSWORD=X8wY1aB3cD6eF9gH0iJ4kL7m

# Admin User
ADMIN_PASSWORD=P3nQ5tX8wY1aB3cD
```

Generate individual secrets:

```bash
# Generate a single secret (32 bytes)
python utils/generate_secrets.py

# Generate longer secret (64 bytes)
python utils/generate_secrets.py --length 64

# Generate multiple secrets
python utils/generate_secrets.py --count 5

# Generate hexadecimal secrets
python utils/generate_secrets.py --hex
```

### Method 2: Using Python Directly

```python
import secrets

# Generate URL-safe secret (recommended)
secret = secrets.token_urlsafe(32)
print(secret)

# Generate hexadecimal secret
secret_hex = secrets.token_hex(32)
print(secret_hex)
```

### Method 3: Using OpenSSL

```bash
# Generate base64-encoded secret
openssl rand -base64 32

# Generate hexadecimal secret
openssl rand -hex 32
```

---

## 🚀 Production Deployment Checklist

### Pre-Deployment

- [ ] Generate all unique secrets using secure methods
- [ ] Create `.env` file from `.env.example`
- [ ] Update all `CHANGE_ME_*` values in `.env`
- [ ] Verify `SECRET_KEY` and `JWT_SECRET_KEY` are different
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Configure strong database password
- [ ] Configure secure Redis password (if exposed)
- [ ] Review and update `CORS_ORIGINS`

### Post-Deployment

- [ ] Change default admin password immediately
- [ ] Create individual user accounts (disable default admin)
- [ ] Enable HTTPS/TLS (reverse proxy with SSL certificate)
- [ ] Configure firewall rules (limit access to required ports)
- [ ] Enable audit logging
- [ ] Set up automated backups
- [ ] Configure monitoring and alerting
- [ ] Review security headers
- [ ] Implement rate limiting
- [ ] Schedule periodic security audits

---

## 🔒 Environment Variables Security

### Storage Options

1. **Docker Secrets** (Recommended for Docker Swarm)
   ```yaml
   services:
     api:
       secrets:
         - secret_key
         - jwt_secret

   secrets:
     secret_key:
       external: true
     jwt_secret:
       external: true
   ```

2. **Kubernetes Secrets** (Recommended for K8s)
   ```bash
   kubectl create secret generic app-secrets \
     --from-literal=SECRET_KEY='your-secret-here' \
     --from-literal=JWT_SECRET_KEY='your-jwt-secret-here'
   ```

3. **HashiCorp Vault** (Enterprise)
   - Store secrets in Vault
   - Use dynamic secrets with short TTL
   - Enable secret rotation

4. **AWS Secrets Manager / Azure Key Vault** (Cloud)
   - Managed secret storage
   - Automatic rotation
   - Access control and auditing

### .env File Security

**CRITICAL: Never commit .env to version control!**

Add to `.gitignore`:
```
.env
.env.local
.env.production
.env.*.local
```

Verify it's ignored:
```bash
git status --ignored
```

If accidentally committed:
```bash
# Remove from Git history (use with caution!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (coordinate with team!)
git push origin --force --all
```

Then immediately:
1. Rotate ALL secrets
2. Update production environment variables
3. Audit access logs for unauthorized access

---

## 🛡️ Security Best Practices

### 1. Password Policies

**For Admin Users:**
- Minimum 16 characters
- Mix of uppercase, lowercase, numbers, symbols
- No dictionary words
- Use password manager
- Enable MFA (if implemented)

**For Device Credentials:**
- Store per-device, not default credentials
- Encrypt at rest in database
- Use SSH keys when possible
- Rotate regularly (90 days)

### 2. Database Security

```env
# Use strong password
DATABASE_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Restrict network access
# Only allow application server IPs

# Enable SSL/TLS for connections
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

### 3. Redis Security

```env
# Enable password authentication
REDIS_PASSWORD=secure_random_password

# Update connection URLs
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/1
```

Configure Redis:
```conf
# redis.conf
requirepass ${REDIS_PASSWORD}
bind 127.0.0.1  # Only local connections
```

### 4. Network Security

**Firewall Rules:**
```bash
# Allow only necessary ports
# HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# SSH (change default port 22)
ufw allow 2222/tcp

# Block direct database access
ufw deny 5432/tcp

# Block direct Redis access
ufw deny 6379/tcp
```

**Reverse Proxy (nginx):**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000";

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. Audit Logging

All security-relevant events are logged:
- User authentication (success/failure)
- Configuration changes
- Device access
- Admin actions
- API access

Review logs regularly:
```bash
# View authentication failures
docker-compose logs api | grep "Failed login"

# View admin actions
docker-compose logs api | grep "admin_action"

# Export audit logs
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/audit/export?start=2025-01-01
```

### 6. Rate Limiting

Configure rate limits to prevent abuse:

```env
# API rate limit
API_RATE_LIMIT=100/hour

# Login attempts
LOGIN_RATE_LIMIT=5/minute
```

### 7. Input Validation

All inputs are validated using Pydantic schemas:
- IP addresses
- Hostnames
- Configuration syntax
- File uploads
- User input

### 8. Secure Headers

Configure Content Security Policy:

```env
CSP_POLICY=default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'
```

---

## 🔄 Secret Rotation

### Rotation Schedule

| Secret Type | Rotation Frequency | Impact |
|-------------|-------------------|--------|
| SECRET_KEY | 90 days | Users must re-login |
| JWT_SECRET_KEY | 90 days | All tokens invalidated |
| Database Password | 180 days | Application restart required |
| Device Credentials | 90 days | Per device |

### Rotation Procedure

1. **Generate new secret:**
   ```bash
   python utils/generate_secrets.py
   ```

2. **Update production environment:**
   ```bash
   # Update .env file or secrets manager
   nano .env
   ```

3. **Restart application:**
   ```bash
   docker-compose restart api
   ```

4. **Verify functionality:**
   ```bash
   curl http://localhost:5000/api/health
   ```

5. **Notify users** (for JWT_SECRET_KEY rotation)

---

## 📊 Security Monitoring

### Metrics to Monitor

- Failed authentication attempts
- Unusual API access patterns
- Configuration change frequency
- Database connection errors
- Celery task failures

### Alerting

Set up alerts for:
- More than 10 failed logins in 5 minutes
- Admin account access
- Configuration deployment failures
- Database connection issues
- Unauthorized API access attempts

---

## 🚨 Incident Response

### If Secrets Are Compromised

1. **Immediate Actions:**
   - Rotate ALL secrets immediately
   - Revoke all active sessions/tokens
   - Review access logs
   - Disable compromised accounts

2. **Investigation:**
   - Identify breach source
   - Determine scope of access
   - Check for unauthorized changes
   - Review audit logs

3. **Recovery:**
   - Update all secrets
   - Restart all services
   - Notify affected users
   - Document incident

4. **Prevention:**
   - Review security practices
   - Update security policies
   - Conduct security training
   - Implement additional controls

---

## 📚 References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)

---

## 📞 Support

For security-related questions or to report vulnerabilities:
- Email: security@yourcompany.com
- Create a private security advisory on GitHub

**Do NOT publicly disclose security vulnerabilities!**
