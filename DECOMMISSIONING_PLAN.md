# Trade-Ideas Repository Decommissioning Plan

## Overview

This document outlines the plan to decommission the old "trade-ideas" repository in favor of the new "market-intel-platform" repository. The market-intel-platform is a complete rewrite and restructuring of the original trade-ideas project with enhanced architecture, full-stack implementation, and production-ready features.

**Date**: October 14, 2025
**Status**: Pending Execution
**Repository Owner**: jasonriedel

---

## Background

### What Was Migrated
The market-intel-platform repository was created as a successor to the trade-ideas project. The following components were migrated and enhanced:

1. **Core Intelligence Modules** (from trade-ideas):
   - `ml_digest_enhancer.py` - ML-enhanced pattern recognition
   - `news_digest.py` → renamed to `digest_generator.py`
   - `news_collector.py` - News aggregation from RSS feeds
   - `sentiment_analyzer.py` - Sentiment analysis (TextBlob + VADER)

2. **Strategy Documents** (preserved in `docs/`):
   - `PRODUCT_STRATEGY.md`
   - `GO_TO_MARKET_STRATEGY.md`
   - `MVP_ROADMAP.md`

### What's New in Market-Intel-Platform
- Complete FastAPI backend with async architecture
- PostgreSQL database with Alembic migrations
- JWT authentication system
- Next.js 14 frontend with TypeScript
- Docker Compose orchestration
- GitHub Actions CI/CD workflows
- Comprehensive documentation
- Production-ready deployment configuration

---

## Port Configuration Changes

### Issue
The original trade-ideas project was running on port 3000, conflicting with local development environments.

### Resolution
✅ **Completed**: Frontend port changed from 3000 to 3001
- Updated `frontend/package.json` scripts
- Updated `docker-compose.yml` CORS origins
- Updated all documentation files
- Updated Docker port mappings

**New Configuration**:
- Frontend: `http://localhost:3001`
- Backend: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

---

## GitHub Actions Workflows

### Current Workflows in Market-Intel-Platform

#### 1. Backend CI (`backend-ci.yml`)
**Triggers**:
- Push to main/develop branches
- Pull requests to main/develop
- Changes in backend/ directory

**Actions**:
- Sets up Python 3.11 environment
- Runs PostgreSQL service container
- Installs dependencies
- Runs linting (black, flake8)
- Runs tests with pytest
- Uploads coverage to Codecov
- Builds Docker image

#### 2. Frontend CI (`frontend-ci.yml`)
**Triggers**:
- Push to main/develop branches
- Pull requests to main/develop
- Changes in frontend/ directory

**Actions**:
- Sets up Node.js 18 environment
- Installs npm dependencies
- Runs ESLint
- Runs TypeScript type checking
- Builds Next.js production bundle
- Builds Docker image

#### 3. Production Deployment (`deploy-production.yml`)
**Triggers**:
- Push to main branch
- Git tags matching 'v*'
- Manual workflow dispatch

**Actions**:
- **Backend Deployment**:
  - Configures AWS credentials
  - Logs in to Amazon ECR
  - Builds and pushes backend Docker image
  - Deploys to AWS ECS

- **Frontend Deployment**:
  - Deploys to Vercel using vercel-action

- **Notifications**:
  - Sends deployment status updates

---

## Decommissioning Steps

### Phase 1: Preparation (Before Decommissioning)

#### Step 1.1: Verify Market-Intel-Platform is Fully Functional
```bash
# Clone and test the new repository
git clone <market-intel-platform-repo-url>
cd market-intel-platform

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Initialize test data
docker-compose exec backend python scripts/init_db.py

# Start frontend
cd frontend
npm install
npm run dev

# Verify services
open http://localhost:3001
open http://localhost:8000/docs
```

**Verification Checklist**:
- [ ] Backend API responds at http://localhost:8000
- [ ] Frontend loads at http://localhost:3001
- [ ] User registration works
- [ ] User login works
- [ ] Digest API returns data
- [ ] All CI/CD workflows pass

#### Step 1.2: Backup Trade-Ideas Repository Data
```bash
# Navigate to old repository
cd /path/to/trade-ideas

# Create full backup
git bundle create trade-ideas-backup.bundle --all

# Backup any production data/configs
cp -r .env* ../trade-ideas-configs-backup/
cp -r deployment/ ../trade-ideas-deployment-backup/

# Export any production secrets
# (Document any AWS/Vercel/Stripe secrets that need migration)
```

#### Step 1.3: Document Production Workflows
Create a document listing:
- [ ] All active GitHub Actions workflows in trade-ideas
- [ ] Any scheduled cron jobs
- [ ] External services that depend on trade-ideas
- [ ] Production URLs and endpoints
- [ ] Environment variables and secrets
- [ ] Third-party integrations

---

### Phase 2: Migration (Transition Period)

#### Step 2.1: Update GitHub Repository Settings

**Old Repository (trade-ideas)**:
1. Add deprecation notice to README:
   ```markdown
   # ⚠️ DEPRECATED - This repository is no longer maintained

   This project has been migrated to [market-intel-platform](link-to-new-repo).

   Please use the new repository for all future development.

   **Migration Date**: October 14, 2025
   ```

2. Disable GitHub Actions:
   - Go to Settings → Actions → General
   - Select "Disable Actions for this repository"

3. Archive the repository:
   - Go to Settings → General
   - Scroll to "Danger Zone"
   - Click "Archive this repository"

**New Repository (market-intel-platform)**:
1. Ensure all secrets are configured:
   ```
   Required Secrets:
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - VERCEL_TOKEN
   - VERCEL_ORG_ID
   - VERCEL_PROJECT_ID
   - STRIPE_API_KEY (if using)
   - NEWSAPI_KEY (if using)
   ```

2. Configure branch protection rules:
   - Require pull request reviews
   - Require status checks (CI) to pass
   - Require up-to-date branches

#### Step 2.2: Migrate Production Deployments

**Backend Migration** (AWS ECS):
```bash
# Update ECS service to point to new ECR repository
aws ecs update-service \
  --cluster market-intel-cluster \
  --service market-intel-backend \
  --force-new-deployment

# Update task definition with new image
aws ecs register-task-definition \
  --cli-input-json file://new-task-definition.json
```

**Frontend Migration** (Vercel):
1. Connect new repository to Vercel
2. Configure environment variables:
   - `NEXT_PUBLIC_API_URL` → production backend URL
3. Deploy production build
4. Update DNS to point to new deployment

#### Step 2.3: Update External Integrations
- [ ] Update Stripe webhook URLs (if applicable)
- [ ] Update DNS records
- [ ] Update monitoring/alerting services
- [ ] Update documentation links
- [ ] Update API documentation URLs
- [ ] Notify team members

---

### Phase 3: Decommissioning (Post-Migration)

#### Step 3.1: Disable Old Workflows

Since trade-ideas workflows are being replaced by market-intel-platform workflows, ensure:

1. **Stop all running workflows in trade-ideas**:
   - Go to Actions tab
   - Cancel any running workflows

2. **Disable workflow files**:
   ```bash
   cd /path/to/trade-ideas

   # Option A: Delete workflow files
   rm -rf .github/workflows/

   # Option B: Archive them
   mkdir .github/workflows-archive
   mv .github/workflows/* .github/workflows-archive/
   ```

3. **Remove scheduled workflows**:
   - Check for any cron-triggered workflows
   - Ensure they're not running in production

#### Step 3.2: Decommission Production Infrastructure

**If trade-ideas had separate infrastructure**:

```bash
# AWS Resources
aws ecs delete-service --cluster old-cluster --service old-service --force
aws ecr delete-repository --repository-name trade-ideas --force
aws rds delete-db-instance --db-instance-identifier trade-ideas-db

# Vercel
vercel rm trade-ideas-project --yes

# Database backups (before deletion)
pg_dump -h old-db-host -U user trade_ideas_db > trade-ideas-final-backup.sql
```

#### Step 3.3: Archive Old Repository

1. **Final commit in trade-ideas**:
   ```bash
   cd /path/to/trade-ideas

   # Add deprecation notice
   echo "# DEPRECATED - Migrated to market-intel-platform" > DEPRECATED.md
   git add DEPRECATED.md README.md
   git commit -m "Archive repository - migrated to market-intel-platform"
   git push
   ```

2. **Archive on GitHub**:
   - Settings → General → Danger Zone
   - Click "Archive this repository"
   - Confirm archival

3. **Update repository description**:
   - "⚠️ DEPRECATED - Migrated to market-intel-platform"

---

## Post-Decommissioning Verification

### Checklist

- [ ] Market-intel-platform is fully operational in production
- [ ] All GitHub Actions workflows in market-intel-platform are passing
- [ ] All production traffic is routed to new deployment
- [ ] Old trade-ideas workflows are disabled
- [ ] Old trade-ideas repository is archived
- [ ] All team members are using new repository
- [ ] Documentation links are updated
- [ ] External integrations are working
- [ ] Monitoring/alerts are configured for new deployment
- [ ] Old infrastructure is decommissioned (if applicable)

### Rollback Plan

If issues arise during migration:

1. **Immediate Actions**:
   - Keep trade-ideas repository un-archived
   - Maintain old infrastructure for 30 days
   - Document any issues

2. **Rollback Steps**:
   ```bash
   # Revert DNS to old deployment
   # Re-enable old GitHub Actions
   # Restore from backup if needed
   ```

---

## Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1: Preparation** | 1-2 days | Backup, verify, document |
| **Phase 2: Migration** | 1-2 weeks | Update repos, migrate deployments, test |
| **Phase 3: Decommissioning** | 1 day | Disable old workflows, archive repo |
| **Monitoring Period** | 30 days | Monitor new deployment, keep backups |

---

## Contacts and Resources

### Key Stakeholders
- **Repository Owner**: jasonriedel
- **Development Team**: [List team members]
- **DevOps Team**: [List contacts]

### Important URLs

**New (Market-Intel-Platform)**:
- Repository: [GitHub URL]
- Production Frontend: [Vercel URL]
- Production Backend: [AWS ECS URL]
- API Docs: [Backend URL]/docs

**Old (Trade-Ideas)**:
- Repository: [GitHub URL] (to be archived)
- Backup Location: [Path to backups]

---

## Success Criteria

✅ **Migration Successful When**:
1. All GitHub Actions in market-intel-platform are passing
2. Production deployment is stable for 7+ days
3. No critical issues reported
4. All team members migrated to new repository
5. Old workflows are disabled without impact
6. Trade-ideas repository is archived
7. Documentation is updated

---

## Notes

### Why Decommission?
- Market-intel-platform is a complete rewrite with better architecture
- Eliminates confusion between two repositories
- Consolidates development efforts
- New repository has comprehensive CI/CD
- Better separation of concerns (frontend/backend)
- Production-ready with Docker orchestration

### What to Keep from Trade-Ideas?
- Git history (archived in bundle)
- Strategy documents (already copied)
- Core intelligence modules (already migrated)
- Any production data/configs (backed up)

### What to Discard?
- Old GitHub Actions workflows (replaced with new ones)
- Legacy deployment scripts (Docker Compose now used)
- Outdated dependencies (updated in new repo)

---

## Questions?

Contact: jasonriedel
Date Created: October 14, 2025
Last Updated: October 14, 2025
Status: **Ready for Execution**
