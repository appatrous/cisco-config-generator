# Backend Setup Guide - Complete Stack

## 🎯 Overview

The backend now includes:
- ✅ **PostgreSQL** database with SQLAlchemy ORM
- ✅ **JWT Authentication** with Flask-JWT-Extended
- ✅ **Celery** for asynchronous tasks (deployments, health checks)
- ✅ **Redis** for Celery broker and caching
- ✅ **WebSockets** for real-time updates (Flask-SocketIO)
- ✅ **Multi-tenancy** support for organizations
- ✅ **Complete REST API** with all CRUD endpoints
- ✅ **Audit logging** for all actions

---

## 📦 Prerequisites

### Required Software

```bash
# PostgreSQL 15+
sudo apt-get install postgresql postgresql-contrib

# Redis 7+
sudo apt-get install redis-server

# Python 3.11+
python --version
```

### OR Use Docker (Recommended)

```bash
# Install Docker and Docker Compose
docker --version
docker-compose --version
```

---

## 🚀 Quick Start with Docker

### 1. Clone and Setup

```bash
cd cisco-config-generator

# Copy environment file
cp .env.example .env

# Edit .env with your settings (optional for dev)
nano .env
```

### 2. Start All Services

```bash
# Build and start all containers
docker-compose up -d

# Check status
docker-compose ps
```

You should see:
- ✅ `cisco-config-db` (PostgreSQL) - Port 5432
- ✅ `cisco-config-redis` (Redis) - Port 6379
- ✅ `cisco-config-api` (Flask API) - Port 5000
- ✅ `cisco-config-celery` (Worker)
- ✅ `cisco-config-celery-beat` (Scheduler)

### 3. Initialize Database

```bash
# Run database migrations
docker-compose exec api python init_db.py
```

This creates:
- Database schema
- Default organization ("Default Organization")
- Admin user (username: `admin`, password: `admin123`)

⚠️ **IMPORTANT**: Change the admin password immediately!

### 4. Access the Application

- **API**: http://localhost:5000
- **Frontend**: http://localhost:3000 (if running separately)
- **Health Check**: http://localhost:5000/api/health

---

## 🛠️ Manual Setup (Without Docker)

### 1. Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql

postgres=# CREATE DATABASE cisco_config_generator;
postgres=# CREATE USER netconfig WITH PASSWORD 'netconfig';
postgres=# GRANT ALL PRIVILEGES ON DATABASE cisco_config_generator TO netconfig;
postgres=# \q
```

### 2. Install Redis

```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify
redis-cli ping  # Should return PONG
```

### 3. Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit configuration
nano .env
```

Update `.env` with your settings:

```env
FLASK_ENV=development
DATABASE_URL=postgresql://netconfig:netconfig@localhost:5432/cisco_config_generator
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0
```

### 5. Initialize Database

```bash
python init_db.py
```

### 6. Start Services

You need **3 terminals**:

**Terminal 1 - Flask API Server:**
```bash
python app_api.py
```

**Terminal 2 - Celery Worker:**
```bash
celery -A celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat (optional, for scheduled tasks):**
```bash
celery -A celery_app beat --loglevel=info
```

---

## 🔐 Authentication Flow

### 1. Register a User

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "john_doe",
    "password": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe",
    "organization_name": "My Company"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "is_admin": true,
    "organization_id": 1
  }
}
```

### 3. Use Token

```bash
# Add header to all requests
Authorization: Bearer <access_token>
```

Example:
```bash
curl http://localhost:5000/api/devices \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Get current user

### Devices
- `GET /api/devices` - List all devices
- `POST /api/devices` - Create device
- `GET /api/devices/<id>` - Get device
- `PUT /api/devices/<id>` - Update device
- `DELETE /api/devices/<id>` - Delete device
- `POST /api/devices/bulk-import` - Bulk import CSV
- `POST /api/devices/<id>/ping` - Test connectivity

### Configurations
- `GET /api/devices/<id>/configs` - Get config history
- `GET /api/configs/<id>` - Get specific config
- `POST /api/configs` - Create config version
- `POST /api/configs/compare-detailed` - Compare configs

### Deployment
- `POST /api/deploy` - Deploy configuration
- `GET /api/deploy/history` - Deployment history

### Validation
- `POST /api/validate/config` - Validate configuration
- `POST /api/validate/compliance` - Check compliance

### Audit
- `GET /api/changes/history` - Get audit logs
- `GET /api/changes/history/<device_id>` - Device audit logs

---

## 🔌 WebSocket Events

### Namespaces

**`/deployments`** - Deployment updates
**`/devices`** - Device health updates

### Example (JavaScript)

```javascript
import io from 'socket.io-client'

const socket = io('http://localhost:5000/deployments')

socket.on('deployment_update', (data) => {
  console.log('Deployment update:', data)
  // data = { deployment_id, status, progress, message, logs }
})

socket.on('connect', () => {
  console.log('Connected to deployment WebSocket')
})
```

---

## 🗄️ Database Schema

### Organizations
- Multi-tenant support
- Each organization has isolated devices/users

### Users
- JWT authentication
- Role-based access (is_admin)
- Organization membership

### Devices
- Network equipment inventory
- Platform support (IOS, NX-OS, ASA, EOS, Junos)
- Real-time status tracking

### Configurations
- Version history
- Checksum validation
- Active/inactive states

### Deployments
- Async task tracking (Celery task_id)
- Full deployment logs
- Status tracking (pending, in_progress, success, failed)

### AuditLog
- Complete audit trail
- User actions tracking
- IP address logging

---

## ⚙️ Celery Tasks

### Available Tasks

**`deploy_configuration_task(deployment_id)`**
- Deploy config to device via SSH
- Backup current config
- Apply changes
- Update deployment status
- Emit WebSocket events

**`health_check_task(device_id)`**
- Test device connectivity
- Update device status
- Record health check history
- Emit WebSocket events

**`bulk_health_check_task()`**
- Run health checks on all devices
- Scheduled task (optional)

### Monitoring Tasks

```bash
# Check Celery status
celery -A celery_app inspect active

# View task results
celery -A celery_app result <task_id>

# Monitor in real-time
celery -A celery_app events
```

---

## 🧪 Testing

### Manual API Testing

```bash
# Health check
curl http://localhost:5000/api/health

# Login as admin
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# Create a device
curl -X POST http://localhost:5000/api/devices \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "router1",
    "ip_address": "192.168.1.1",
    "platform": "ios",
    "device_type": "router",
    "location": "Data Center 1"
  }'

# List devices
curl http://localhost:5000/api/devices \
  -H "Authorization: Bearer $TOKEN"
```

### Run Tests

```bash
pytest tests/
```

---

## 🔧 Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U netconfig -d cisco_config_generator -h localhost

# View logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### Redis Connection Issues

```bash
# Check if Redis is running
sudo systemctl status redis-server

# Test connection
redis-cli ping

# View logs
sudo tail -f /var/log/redis/redis-server.log
```

### Celery Not Processing Tasks

```bash
# Check Celery worker logs
celery -A celery_app worker --loglevel=debug

# Purge all tasks
celery -A celery_app purge

# Restart worker
docker-compose restart celery_worker  # Docker
# OR
# Kill and restart manually
```

### Database Migration Issues

```bash
# Reset migrations (CAUTION: Drops all data!)
rm -rf migrations/
python init_db.py

# OR manually
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## 🔐 Security Recommendations

### Production Deployment

1. **Change default credentials**
```bash
# Login as admin and create new admin user
# Then delete default admin account
```

2. **Use strong secrets**
```bash
# Generate random secrets
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

3. **Enable HTTPS**
```bash
# Use nginx reverse proxy with SSL
# Configure CORS properly
```

4. **Database security**
```bash
# Use strong database password
# Restrict network access
# Enable SSL connections
```

5. **Rate limiting** (TODO)
```python
# Add Flask-Limiter
from flask_limiter import Limiter
```

---

## 📊 Monitoring & Logs

### Application Logs

```bash
# Docker logs
docker-compose logs -f api
docker-compose logs -f celery_worker

# Manual logs (add to app_api.py)
import logging
logging.basicConfig(level=logging.INFO)
```

### Database Monitoring

```bash
# PostgreSQL stats
psql -U netconfig -d cisco_config_generator -c "
  SELECT schemaname, tablename, n_live_tup
  FROM pg_stat_user_tables;"
```

### Redis Monitoring

```bash
# Redis stats
redis-cli INFO

# Monitor commands
redis-cli MONITOR
```

---

## 📚 Additional Resources

- [Flask-SQLAlchemy Docs](https://flask-sqlalchemy.palletsprojects.com/)
- [Flask-JWT-Extended Docs](https://flask-jwt-extended.readthedocs.io/)
- [Celery Docs](https://docs.celeryq.dev/)
- [Flask-SocketIO Docs](https://flask-socketio.readthedocs.io/)

---

**Backend is now production-ready!** 🚀
