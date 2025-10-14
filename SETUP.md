# Setup Guide - Market Intelligence Platform

Complete setup instructions for local development and production deployment.

## Prerequisites

### Required Software
- **Python 3.11+**: [Download](https://www.python.org/downloads/)
- **PostgreSQL 16+**: [Download](https://www.postgresql.org/download/)
- **Node.js 18+**: [Download](https://nodejs.org/) (for frontend)
- **Docker & Docker Compose**: [Download](https://www.docker.com/products/docker-desktop) (optional)

### Optional Software
- **Redis**: For caching (recommended for production)
- **Make**: For convenient commands (pre-installed on macOS/Linux)

## Quick Start with Docker (Recommended)

This is the fastest way to get started:

### 1. Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd market-intel-platform

# Copy environment template
cp .env.example .env

# Edit .env with your settings (or use defaults for local dev)
nano .env
```

### 2. Start Services

```bash
# Start all services (PostgreSQL, Backend, Redis)
docker-compose up -d

# View logs
docker-compose logs -f backend
```

### 3. Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create test users (admin@example.com / admin123)
docker-compose exec backend python scripts/init_db.py
```

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

### 5. Login and Test

```bash
# Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "yourname@example.com",
    "password": "secure_password_123",
    "full_name": "Your Name"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "yourname@example.com",
    "password": "secure_password_123"
  }'

# Save the access_token from response
export TOKEN="<your-access-token>"

# Get daily digest
curl -X GET http://localhost:8000/api/v1/digest/daily \
  -H "Authorization: Bearer $TOKEN"
```

## Local Development Setup (Without Docker)

If you prefer to run services locally without Docker:

### 1. Install PostgreSQL

**macOS (Homebrew):**
```bash
brew install postgresql@16
brew services start postgresql@16
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql-16 postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Create Database

```bash
# Create database user and database
createuser marketintel
createdb market_intelligence -O marketintel

# Set password for user
psql -c "ALTER USER marketintel WITH PASSWORD 'marketintel_dev';"
```

### 3. Set Up Python Environment

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy environment template
cp ../.env.example ../.env

# Edit with your local settings
nano ../.env

# Key settings for local development:
# DATABASE_URL=postgresql://marketintel:marketintel_dev@localhost:5432/market_intelligence
# SECRET_KEY=<generate-a-random-32-character-string>
# DEBUG=true
```

### 5. Run Migrations

```bash
# Ensure you're in backend directory with venv activated
alembic upgrade head
```

### 6. Initialize Database

```bash
# Create test users
python scripts/init_db.py
```

### 7. Start Development Server

```bash
# Start with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Verify Setup

- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Test with credentials: admin@example.com / admin123

## Configuration Details

### Environment Variables

#### Required Settings

```bash
# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-minimum-32-characters-long

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

#### Optional APIs

```bash
# NewsAPI (100 requests/day free)
# Sign up at: https://newsapi.org/
NEWSAPI_KEY=your-newsapi-key-here

# Alpha Vantage (25 calls/day free)
# Sign up at: https://www.alphavantage.co/
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key-here
```

#### Email Notifications (Optional)

```bash
# Gmail App Password Setup:
# 1. Enable 2FA on your Google account
# 2. Visit: https://myaccount.google.com/apppasswords
# 3. Generate app-specific password

EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=your-app-specific-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

#### Stripe Subscriptions (Optional)

```bash
# Get keys from: https://dashboard.stripe.com/apikeys
STRIPE_API_KEY=sk_test_your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
```

## Common Tasks

### Database Operations

```bash
# Create a new migration
cd backend
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# Reset database (WARNING: deletes all data!)
alembic downgrade base
alembic upgrade head
```

### Development Workflow

```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Docker Operations

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Rebuild images
docker-compose build

# Access PostgreSQL shell
docker-compose exec postgres psql -U marketintel -d market_intelligence

# Access backend container
docker-compose exec backend bash

# View running services
docker-compose ps
```

## Troubleshooting

### Database Connection Issues

**Problem:** `Connection refused` or `could not connect to server`

**Solutions:**
1. Verify PostgreSQL is running: `pg_isready`
2. Check DATABASE_URL in .env
3. Ensure PostgreSQL accepts connections on localhost:5432
4. For Docker: Check if postgres service is healthy: `docker-compose ps`

### Migration Issues

**Problem:** `alembic.util.exc.CommandError: Can't locate revision identified by`

**Solutions:**
1. Delete alembic/versions/*.py files
2. Drop database and recreate: `dropdb market_intelligence && createdb market_intelligence`
3. Run migrations again: `alembic upgrade head`

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'app'`

**Solutions:**
1. Ensure virtual environment is activated
2. Verify you're in the backend directory
3. Reinstall dependencies: `pip install -r requirements.txt`
4. Add backend to PYTHONPATH: `export PYTHONPATH="${PYTHONPATH}:/path/to/backend"`

### Docker Issues

**Problem:** `Port already in use`

**Solutions:**
1. Stop conflicting services: `lsof -ti:8000 | xargs kill`
2. Change port in docker-compose.yml
3. Stop all Docker containers: `docker-compose down`

## Production Deployment

### Security Checklist

Before deploying to production:

- [ ] Change SECRET_KEY to a strong random value
- [ ] Set DEBUG=false
- [ ] Use strong database passwords
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS_ORIGINS properly
- [ ] Set up firewall rules
- [ ] Enable database backups
- [ ] Configure log rotation
- [ ] Set up monitoring and alerts
- [ ] Review all environment variables

### Docker Production Setup

1. **Create production compose file:**

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - market-intel-network

  backend:
    build:
      context: ./backend
    environment:
      DEBUG: false
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - postgres
    networks:
      - market-intel-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
    networks:
      - market-intel-network

volumes:
  postgres_data:

networks:
  market-intel-network:
```

2. **Deploy:**

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Next Steps

After setup:

1. **Explore API Documentation**: http://localhost:8000/docs
2. **Test Authentication**: Register and login
3. **Generate a Digest**: Call `/api/v1/digest/daily`
4. **Review Code**: Explore backend/app/ structure
5. **Run Tests**: `pytest tests/ -v`
6. **Setup Frontend**: Follow frontend/README.md (coming soon)

## Support

For issues or questions:
- Check documentation: [README.md](README.md)
- Review API docs: http://localhost:8000/docs
- Open an issue on GitHub
- Contact: support@market-intel-platform.com
