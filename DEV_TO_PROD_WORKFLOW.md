# Development to Production Workflow

**Last Updated**: October 15, 2025
**Status**: Production-Ready System

---

## 🎯 Overview

This document describes the complete workflow for developing, testing, and deploying changes to the Market Intelligence Platform.

**Current Architecture:**
- **Local Development**: Docker Compose (PostgreSQL + Backend + Redis)
- **Production**: AWS ECS Fargate (Backend) + Supabase (Database) + GitHub Actions (Automation)

---

## 📋 Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Development Workflow](#development-workflow)
3. [Testing Changes](#testing-changes)
4. [Deployment to Production](#deployment-to-production)
5. [Rollback Procedures](#rollback-procedures)
6. [Environment Variables](#environment-variables)
7. [Common Tasks](#common-tasks)

---

## 🛠️ Local Development Setup

### Initial Setup (First Time Only)

```bash
# 1. Clone the repository (if not already done)
cd /Users/jasonriedel/PyCharmProjects/market-intel-platform

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env with your local settings
nano .env  # or use your preferred editor

# Required for local dev:
# - DATABASE_URL (will use local PostgreSQL)
# - SMTP credentials (optional, for testing emails)
# - API keys (optional, for real market data)

# 4. Start local environment
docker-compose up -d

# 5. Verify services are running
docker-compose ps

# 6. Check logs
docker-compose logs -f backend
```

### Local Environment Details

**Services Started:**
- **PostgreSQL**: `localhost:5432`
  - Database: `market_intelligence`
  - User: `marketintel`
  - Password: `marketintel_dev`

- **Backend API**: `http://localhost:8000`
  - Auto-reload enabled (code changes apply immediately)
  - API docs: `http://localhost:8000/docs`

- **Redis**: `localhost:6379` (optional, for caching)

---

## 🔄 Development Workflow

### Standard Development Cycle

```bash
# 1. CREATE A NEW BRANCH FOR YOUR FEATURE
git checkout -b feature/your-feature-name

# Example:
git checkout -b feature/add-real-market-data

# 2. START LOCAL ENVIRONMENT (if not running)
docker-compose up -d

# 3. MAKE CODE CHANGES
# Edit files in:
# - backend/app/services/
# - backend/app/api/
# - backend/app/models/
# etc.

# Changes are automatically detected (hot-reload enabled)
# Watch logs: docker-compose logs -f backend

# 4. TEST YOUR CHANGES LOCALLY
# A. Test API endpoints
curl http://localhost:8000/api/v1/digest/generate

# B. Test email generation (local test)
cd backend
python scripts/send_daily_digest.py --email your-email@gmail.com

# C. Access API documentation
open http://localhost:8000/docs

# 5. COMMIT YOUR CHANGES
git add .
git commit -m "Add descriptive commit message

- Bullet point of change 1
- Bullet point of change 2"

# 6. PUSH TO GITHUB
git push origin feature/your-feature-name

# 7. MERGE TO MAIN (when ready)
# Option A: Command line
git checkout main
git merge feature/your-feature-name
git push origin main

# Option B: GitHub Pull Request (recommended)
# - Create PR on GitHub
# - Review changes
# - Merge via GitHub UI
```

---

## 🧪 Testing Changes

### Local Testing Checklist

Before deploying to production, test locally:

#### 1. API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Generate digest
curl http://localhost:8000/api/v1/digest/generate

# Get specific digest
curl http://localhost:8000/api/v1/digest/latest
```

#### 2. Email Rendering
```bash
# Test email with real SMTP
cd backend
export SMTP_USERNAME="tuxninja@gmail.com"
export SMTP_PASSWORD="norm mrct wlpv yrna"
python scripts/send_daily_digest.py --email jasonnetbiz@gmail.com

# Check your email inbox to verify:
# - All text is visible
# - Market data displays correctly
# - Colors are correct
# - No layout issues
```

#### 3. Database Operations
```bash
# Connect to local database
docker-compose exec postgres psql -U marketintel -d market_intelligence

# Check tables
\dt

# View recent signals
SELECT * FROM signals ORDER BY created_at DESC LIMIT 5;

# Exit
\q
```

#### 4. Check Logs
```bash
# Backend logs
docker-compose logs -f backend

# All services
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100
```

---

## 🚀 Deployment to Production

### Automatic Deployment (Recommended)

**Production deploys automatically when you push to `main` branch.**

```bash
# 1. Merge your changes to main
git checkout main
git merge feature/your-feature-name
git push origin main

# 2. GitHub Actions will automatically:
#    - Build Docker image
#    - Push to ECR
#    - Update ECS task
#    - Deploy to production

# 3. Monitor deployment
gh run list --limit 5
gh run watch

# Deployment takes 5-10 minutes
```

### Manual Deployment (If Needed)

If automatic deployment fails or you need manual control:

```bash
# 1. BUILD DOCKER IMAGE
cd backend
docker buildx build --platform linux/amd64 \
  -t 907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest \
  --load .

# 2. AUTHENTICATE WITH ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  907391580367.dkr.ecr.us-east-1.amazonaws.com

# 3. PUSH IMAGE
docker push 907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest

# 4. VERIFY IMAGE IN ECR
aws ecr describe-images \
  --repository-name market-intel-backend \
  --region us-east-1 \
  --query 'sort_by(imageDetails,& imagePushedAt)[-1]'

# 5. ECS will automatically pull the new image on next task run
# Or force update:
aws ecs update-service \
  --cluster market-intel-cluster \
  --service market-intel-service \
  --force-new-deployment \
  --region us-east-1
```

### Post-Deployment Testing

```bash
# 1. TRIGGER TEST EMAIL (Production)
gh workflow run "Daily Market Intelligence Digest" --ref main

# 2. MONITOR WORKFLOW
gh run watch

# 3. CHECK EMAIL
# Wait 2-3 minutes, then check jasonnetbiz@gmail.com

# 4. VIEW PRODUCTION LOGS (if needed)
aws logs tail /ecs/market-intel-backend --follow --region us-east-1
```

---

## ⏪ Rollback Procedures

### Quick Rollback

If a deployment causes issues:

```bash
# 1. REVERT GIT COMMIT
git revert HEAD
git push origin main

# This will trigger automatic redeployment of previous version

# 2. OR: REDEPLOY PREVIOUS DOCKER IMAGE
# Find previous image digest
aws ecr describe-images \
  --repository-name market-intel-backend \
  --region us-east-1 \
  --query 'sort_by(imageDetails,& imagePushedAt)[-2].imageDigest'

# Tag it as latest
aws ecr batch-get-image \
  --repository-name market-intel-backend \
  --image-ids imageDigest=sha256:PREVIOUS_DIGEST \
  --region us-east-1 | \
  jq -r '.images[0].imageManifest' | \
  aws ecr put-image \
  --repository-name market-intel-backend \
  --image-tag latest \
  --image-manifest file:///dev/stdin \
  --region us-east-1

# 3. FORCE ECS TO USE ROLLED-BACK IMAGE
aws ecs update-service \
  --cluster market-intel-cluster \
  --service market-intel-service \
  --force-new-deployment \
  --region us-east-1
```

---

## 🔐 Environment Variables

### Local Development (.env)

```bash
# Minimal required for local dev
APP_NAME="Market Intelligence Platform"
DEBUG=true
ENVIRONMENT=development

# Local database (docker-compose)
DATABASE_URL=postgresql://marketintel:marketintel_dev@postgres:5432/market_intelligence

# Optional: For testing emails
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_FROM_NAME="Market Intel Dev"

# Optional: For real market data
NEWSAPI_KEY=your-key
ALPHA_VANTAGE_API_KEY=your-key
```

### Production (GitHub Secrets)

Production environment variables are stored in GitHub Secrets and configured in:
- `.github/workflows/daily-digest.yml` (for scheduled emails)

**Required Production Secrets:**
- `AWS_ACCESS_KEY_ID` - AWS credentials
- `AWS_SECRET_ACCESS_KEY` - AWS credentials
- `AWS_REGION` - `us-east-1`
- `ECR_REPOSITORY` - `market-intel-backend`
- `ECS_CLUSTER` - `market-intel-cluster`
- `DATABASE_URL` - Supabase PostgreSQL URL
- `SMTP_USERNAME` - Email sending credentials
- `SMTP_PASSWORD` - Email app password

**View/Update GitHub Secrets:**
```bash
# List secrets
gh secret list

# Set a secret
gh secret set SECRET_NAME

# Example: Update SMTP password
gh secret set SMTP_PASSWORD < password.txt
```

---

## 📝 Common Tasks

### Task 1: Add a New API Endpoint

```bash
# 1. Create new route file
nano backend/app/api/v1/endpoints/your_endpoint.py

# 2. Add route to router
nano backend/app/api/v1/api.py

# 3. Test locally
curl http://localhost:8000/api/v1/your-endpoint

# 4. Commit and deploy
git add backend/app/api/
git commit -m "Add new endpoint: your-endpoint"
git push origin main
```

### Task 2: Modify Email Template

```bash
# 1. Edit email service
nano backend/app/services/email_service.py

# Edit methods:
# - _format_digest_html() - Overall structure
# - _generate_header() - Email header
# - _generate_market_summary() - Market snapshot
# - _generate_body() - Signal sections
# - _get_email_styles() - CSS styling

# 2. Test email locally
cd backend
python scripts/send_daily_digest.py --email jasonnetbiz@gmail.com

# 3. Check email rendering in inbox

# 4. If looks good, commit and deploy
git add backend/app/services/email_service.py
git commit -m "Update email template: description of changes"
git push origin main

# 5. Test in production
gh workflow run "Daily Market Intelligence Digest" --ref main
```

### Task 3: Add Real Market Data Integration

```bash
# 1. Install dependencies
cd backend
echo "yfinance==0.2.31" >> requirements.txt
echo "alpha-vantage==2.3.1" >> requirements.txt

# 2. Create market data service
nano backend/app/services/market_data_service.py

# 3. Update digest service to use real data
nano backend/app/services/digest_service.py

# 4. Test locally
docker-compose down
docker-compose up --build -d
docker-compose logs -f backend

# 5. Test API
curl http://localhost:8000/api/v1/digest/generate

# 6. Commit and deploy
git add backend/
git commit -m "Add real market data integration"
git push origin main
```

### Task 4: Update Daily Email Schedule

```bash
# 1. Edit workflow file
nano .github/workflows/daily-digest.yml

# Find line with cron schedule:
# - cron: '30 13 * * 1-5'  # Current: 6:30 AM Arizona Time

# Change to desired time (UTC):
# - cron: '00 14 * * 1-5'  # 7:00 AM Arizona Time
# - cron: '00 13 * * 1-5'  # 6:00 AM Arizona Time

# 2. Commit and push
git add .github/workflows/daily-digest.yml
git commit -m "Update daily email schedule to X:XX AM"
git push origin main

# Next scheduled run will use new time
```

### Task 5: View Production Logs

```bash
# CloudWatch Logs (ECS tasks)
aws logs tail /ecs/market-intel-backend --follow --region us-east-1

# GitHub Actions logs (scheduled emails)
gh run list --workflow="Daily Market Intelligence Digest" --limit 5
gh run view RUN_ID --log

# Most recent run
gh run list --workflow="Daily Market Intelligence Digest" --limit 1 | \
  awk 'NR==2 {print $7}' | xargs gh run view --log
```

### Task 6: Stop/Start Local Environment

```bash
# STOP all services
docker-compose down

# STOP and remove volumes (fresh start)
docker-compose down -v

# START services
docker-compose up -d

# RESTART a single service
docker-compose restart backend

# REBUILD after dependency changes
docker-compose up --build -d

# VIEW resource usage
docker stats
```

### Task 7: Database Migrations

```bash
# Local database
docker-compose exec postgres psql -U marketintel -d market_intelligence

# Production database (Supabase)
psql "postgresql://postgres:#Marjynh8338@db.urbxneuanylgeshiqmgi.supabase.co:5432/postgres"

# Example: Add new column to signals table
ALTER TABLE signals ADD COLUMN price_target DECIMAL(10,2);

# Run migration in both local and production
```

---

## 🎯 Quick Reference

### Essential Commands

```bash
# LOCAL DEVELOPMENT
docker-compose up -d              # Start local environment
docker-compose logs -f backend    # View backend logs
docker-compose down               # Stop environment
docker-compose ps                 # Check service status

# TESTING
curl http://localhost:8000/docs   # API documentation
python scripts/send_daily_digest.py --email test@example.com  # Test email

# DEPLOYMENT
git push origin main              # Deploy to production (automatic)
gh run watch                      # Monitor deployment
gh workflow run "Daily Market Intelligence Digest" --ref main  # Test production email

# MONITORING
aws logs tail /ecs/market-intel-backend --follow --region us-east-1  # Production logs
gh run list --limit 5             # Recent workflow runs
```

### File Locations

| What | Location |
|------|----------|
| Email templates | `backend/app/services/email_service.py` |
| Digest generation | `backend/app/services/digest_service.py` |
| API endpoints | `backend/app/api/v1/endpoints/` |
| Database models | `backend/app/models/` |
| Scheduled workflows | `.github/workflows/` |
| Configuration | `backend/app/config.py` |
| Local environment | `docker-compose.yml` |

---

## 🔐 Best Practices

1. **Always test locally before deploying**
   - Use `docker-compose` to replicate production environment
   - Test email rendering in real inbox
   - Check API responses with curl/Postman

2. **Use feature branches**
   - Create branch for each feature: `feature/feature-name`
   - Merge to main only when tested
   - Keep main branch always deployable

3. **Write descriptive commit messages**
   - Use present tense: "Add feature" not "Added feature"
   - Include bullet points for complex changes
   - Reference issue numbers if applicable

4. **Monitor deployments**
   - Watch GitHub Actions runs: `gh run watch`
   - Check production logs after deployment
   - Test production email after deployment

5. **Keep documentation updated**
   - Update this file when workflow changes
   - Document new environment variables
   - Add new tasks to "Common Tasks" section

---

## 🆘 Troubleshooting

### Local Development Issues

**Problem**: Docker containers won't start
```bash
# Solution: Remove containers and volumes, restart fresh
docker-compose down -v
docker-compose up --build -d
```

**Problem**: Port already in use (8000, 5432, 6379)
```bash
# Solution: Find and kill process using port
lsof -ti:8000 | xargs kill -9  # Kill process on port 8000
# Or: Change port in docker-compose.yml
```

**Problem**: Code changes not reflected
```bash
# Solution: Restart backend service
docker-compose restart backend
# Or: Rebuild if dependencies changed
docker-compose up --build -d backend
```

### Production Deployment Issues

**Problem**: GitHub Actions workflow fails
```bash
# Solution: Check workflow logs
gh run list --limit 1
gh run view RUN_ID --log

# Common causes:
# - AWS credentials expired
# - ECR authentication failed
# - Docker build failed
```

**Problem**: Email not received
```bash
# Solution: Check workflow run logs
gh run view --log

# Verify:
# - SMTP credentials are correct
# - No rate limiting from Gmail
# - Email not in spam folder
```

**Problem**: ECS task fails to start
```bash
# Solution: Check ECS logs
aws logs tail /ecs/market-intel-backend --region us-east-1

# Common causes:
# - Environment variables missing
# - Database connection failed
# - Docker image corrupted
```

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs (local)
- **GitHub Repository**: https://github.com/jasonriedel/market-intel-platform
- **AWS Console**: https://console.aws.amazon.com/ecs/
- **Supabase Dashboard**: https://supabase.com/dashboard
- **GitHub Actions**: https://github.com/jasonriedel/market-intel-platform/actions

---

**Next Steps**: See [SAAS_ROADMAP.md](SAAS_ROADMAP.md) for SaaS product development plan.
