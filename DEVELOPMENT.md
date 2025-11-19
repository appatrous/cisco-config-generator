# Development Guide

## 🛠️ Setup Development Environment

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional but recommended)

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd cisco-config-generator
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   nano .env
   ```

5. **Generate secure secrets:**
   ```bash
   python utils/generate_secrets.py --env
   # Copy the output to your .env file
   ```

6. **Initialize database:**
   ```bash
   # Start PostgreSQL and Redis
   docker-compose up -d postgres redis

   # Run migrations
   python init_db.py
   ```

7. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

---

## 🧪 Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit -v

# Integration tests only
pytest tests/integration -v

# Specific test file
pytest tests/unit/test_models.py -v

# Specific test function
pytest tests/unit/test_models.py::TestUserModel::test_create_user -v
```

### Run Tests with Coverage

```bash
# Generate coverage report
pytest --cov --cov-report=html --cov-report=term-missing

# Open HTML coverage report
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
```

### Test Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run all except slow tests
pytest -m "not slow"
```

---

## 🎨 Code Quality

### Pre-commit Hooks

Pre-commit hooks automatically run on every commit to ensure code quality:

```bash
# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run flake8 --all-files
```

### Manual Code Quality Checks

```bash
# Format code with Black
black . --line-length=100

# Sort imports with isort
isort . --profile=black --line-length=100

# Lint with flake8
flake8 . --max-line-length=100

# Type check with mypy
mypy . --ignore-missing-imports

# Security scan with bandit
bandit -r . -ll
```

### Fix Common Issues

```bash
# Auto-fix formatting issues
black .
isort .

# Fix trailing whitespace
pre-commit run trailing-whitespace --all-files

# Fix end of files
pre-commit run end-of-file-fixer --all-files
```

---

## 🏗️ Project Structure

```
cisco-config-generator/
├── app.py                  # Original monolithic app (legacy)
├── app_refactored.py       # New modular app entry point
├── app_api.py              # API backend with JWT auth
│
├── routes/                 # Flask blueprints
│   ├── __init__.py
│   ├── main.py            # Main UI routes
│   ├── devices.py         # Device pages
│   ├── protocols.py       # Protocol configuration
│   ├── configs.py         # Config management
│   └── troubleshoot.py    # Troubleshooting
│
├── services/               # Business logic layer
│   ├── __init__.py
│   └── protocol_service.py
│
├── schemas/                # Pydantic validation schemas
│   ├── __init__.py
│   ├── config_schemas.py
│   └── device_schemas.py
│
├── models/                 # SQLAlchemy models
│   └── __init__.py
│
├── utils/                  # Helper functions
│   ├── troubleshoot.py
│   ├── config_export.py
│   └── generate_secrets.py
│
├── tasks/                  # Celery background tasks
│   └── deployment_tasks.py
│
├── extensions/             # Flask extensions
│   └── __init__.py
│
├── tests/                  # Test suite
│   ├── conftest.py        # Test fixtures
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
│
├── templates/              # Jinja2 templates
├── static/                 # Static assets
├── frontend/               # React frontend
│
├── .github/                # GitHub Actions CI/CD
│   └── workflows/
│       ├── ci.yml
│       └── pre-commit.yml
│
├── config.py               # Configuration
├── config_enhanced.py      # Enhanced config with DB
├── requirements.txt        # Python dependencies
├── pytest.ini              # Pytest configuration
├── .coveragerc             # Coverage configuration
├── pyproject.toml          # Python project config
├── .pre-commit-config.yaml # Pre-commit hooks
├── docker-compose.yml      # Docker services
└── Dockerfile.enhanced     # Docker image
```

---

## 🔄 Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following the project structure
- Add tests for new features
- Update documentation

### 3. Run Tests Locally

```bash
# Run all tests
pytest

# Check coverage
pytest --cov --cov-report=term-missing
```

### 4. Check Code Quality

```bash
# Pre-commit will run automatically on commit
# Or run manually:
pre-commit run --all-files
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: your feature description"
```

Pre-commit hooks will run automatically. Fix any issues before committing.

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Create a pull request on GitHub. CI/CD will run automatically.

---

## 🚀 Running the Application

### Development Mode

#### Option 1: Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Option 2: Manual

**Terminal 1 - Flask API:**
```bash
python app_api.py
```

**Terminal 2 - Celery Worker:**
```bash
celery -A celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat (optional):**
```bash
celery -A celery_app beat --loglevel=info
```

### Quick Start Script

```bash
# Use the quick start script
./start_dev.sh
```

---

## 🐛 Debugging

### Enable Debug Mode

```env
# In .env
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
```

### View Logs

```bash
# Docker logs
docker-compose logs -f api
docker-compose logs -f celery_worker

# Application logs (if LOG_FILE is set)
tail -f logs/app.log
```

### Debug Tests

```bash
# Run with verbose output
pytest -vv

# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb

# Run last failed tests
pytest --lf
```

### Database Inspection

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U netconfig -d cisco_config_generator

# Common queries
\dt                          # List tables
\d+ devices                  # Describe devices table
SELECT * FROM devices;       # Query devices
```

---

## 📦 Building and Deployment

### Build Docker Image

```bash
docker build -f Dockerfile.enhanced -t cisco-config-generator:latest .
```

### Run Production Build

```bash
# Set production environment
export FLASK_ENV=production
export SECRET_KEY=$(python utils/generate_secrets.py)

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_api:app
```

---

## 📝 Adding New Features

### Adding a New API Endpoint

1. **Create Pydantic schema** in `schemas/`
2. **Add route** in appropriate blueprint in `routes/`
3. **Add business logic** in `services/`
4. **Add tests** in `tests/integration/`
5. **Update documentation**

### Adding a New Protocol

1. **Add template mapping** in `services/protocol_service.py`
2. **Implement generation method** in `ProtocolService`
3. **Create HTML template** in `templates/`
4. **Add tests** in `tests/unit/test_services.py`

### Adding a New Model

1. **Define model** in `models/__init__.py`
2. **Create migration:**
   ```bash
   flask db migrate -m "Add new model"
   flask db upgrade
   ```
3. **Add tests** in `tests/unit/test_models.py`

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure all tests pass
6. Submit a pull request

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: fix bug
docs: update documentation
test: add tests
refactor: refactor code
style: format code
chore: update dependencies
```

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Celery Documentation](https://docs.celeryq.dev/)

---

## 🆘 Troubleshooting

### Pre-commit Hook Failures

```bash
# Update hooks to latest versions
pre-commit autoupdate

# Clear cache
pre-commit clean

# Reinstall hooks
pre-commit uninstall
pre-commit install
```

### Test Failures

```bash
# Run specific test with verbose output
pytest tests/unit/test_models.py::TestUserModel -vv -s

# Clear pytest cache
rm -rf .pytest_cache

# Recreate test database
dropdb cisco_config_generator_test
createdb cisco_config_generator_test
```

### Database Migration Issues

```bash
# Rollback migration
flask db downgrade

# Reset migrations (CAUTION: destroys data)
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check existing documentation
- Review test examples for usage patterns
