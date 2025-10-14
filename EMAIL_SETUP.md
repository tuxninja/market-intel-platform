# Email Delivery Setup Guide

This guide explains how to set up daily digest email delivery for the Market Intelligence Platform. The system is configured exactly like the trade-ideas project, sending beautiful HTML emails with market analysis at 6:30 AM AZ time daily.

## Overview

The platform sends **daily market intelligence digest emails** with:
- 📊 Market snapshot (VIX, regime info)
- 🟢 Bullish signals with trading insights
- 🔴 Bearish signals with trading insights
- ⚪ Neutral/mixed signals
- 💡 WHY THIS MATTERS explanations
- 🎯 Trading impact analysis

**Schedule** (Arizona Time):
- 6:30 AM: Daily digest email
- 7:00 AM: Full market analysis

---

## Quick Setup

### 1. Configure Email Settings

Edit `.env` or set environment variables:

```bash
# Email service configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_USE_TLS=true

# Email sender info
EMAIL_FROM=noreply@marketintel.com
EMAIL_FROM_NAME=Market Intelligence Platform

# Digest recipient
DIGEST_RECIPIENT_EMAIL=your-email@example.com
```

### 2. Get Gmail App Password

If using Gmail (recommended for testing):

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to **Security** → **2-Step Verification**
3. Scroll to **App Passwords**
4. Generate new app password for "Mail"
5. Use this as `SMTP_PASSWORD`

### 3. Test Email Delivery

```bash
cd backend
python scripts/send_daily_digest.py --email your@email.com
```

---

## Email Service Options

### Option 1: Gmail (Easy, Free for Testing)

**Pros**: Easy setup, reliable, free
**Cons**: 500 emails/day limit, may be flagged as spam

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-gmail@gmail.com
SMTP_PASSWORD=your-16-digit-app-password
SMTP_USE_TLS=true
```

### Option 2: AWS SES (Production Recommended)

**Pros**: Scalable, cheap ($0.10/1000 emails), high deliverability
**Cons**: Requires AWS setup, initial sandbox mode

```bash
SMTP_SERVER=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your-aws-smtp-username
SMTP_PASSWORD=your-aws-smtp-password
SMTP_USE_TLS=true
```

**Setup AWS SES:**
1. Go to [AWS SES Console](https://console.aws.amazon.com/ses/)
2. Verify your sender email address
3. Request production access (to send to any email)
4. Create SMTP credentials under "SMTP Settings"
5. Use credentials in `.env`

### Option 3: SendGrid (Alternative)

**Pros**: Free tier (100 emails/day), good deliverability
**Cons**: Requires account, API key management

```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_USE_TLS=true
```

---

## GitHub Actions Setup

The platform uses GitHub Actions to run scheduled emails via AWS ECS (same as trade-ideas).

### Required GitHub Secrets

Go to **Settings** → **Secrets and variables** → **Actions** and add:

```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
DIGEST_RECIPIENT_EMAIL=your@email.com
```

### Workflow Files

Two workflows are configured:

#### 1. Daily Digest (`.github/workflows/daily-digest.yml`)
- **Schedule**: 6:30 AM AZ Time (1:30 PM UTC)
- **Days**: Monday-Friday
- **Purpose**: Quick morning news brief

#### 2. Scheduled Analysis (`.github/workflows/scheduled-analysis.yml`)
- **Schedule**: 7:00 AM AZ Time (2:00 PM UTC)
- **Days**: Monday-Friday
- **Purpose**: Full market analysis

### Enable Scheduled Workflows

Workflows are **disabled by default**. To enable:

1. Open workflow file
2. Uncomment the `schedule` section:

```yaml
schedule:
  # Run at 6:30 AM Arizona Time (13:30 UTC) Monday-Friday
  - cron: '30 13 * * 1-5'
```

3. Commit and push

---

## AWS ECS Setup (Production)

The system runs on AWS ECS Fargate (serverless containers), identical to trade-ideas setup.

### Prerequisites

- AWS Account
- AWS CLI installed and configured
- Docker image pushed to ECR

### 1. Create ECR Repository

```bash
aws ecr create-repository \
  --repository-name market-intel-backend \
  --region us-east-1
```

### 2. Build and Push Docker Image

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build image
cd backend
docker build -t market-intel-backend .

# Tag and push
docker tag market-intel-backend:latest \
  ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest

docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest
```

### 3. Create ECS Cluster

```bash
aws ecs create-cluster \
  --cluster-name market-intel-cluster \
  --region us-east-1
```

### 4. Create Task Definition

```bash
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json
```

**ecs-task-definition.json**:
```json
{
  "family": "market-intel-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "market-intel-container",
      "image": "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest",
      "essential": true,
      "environment": [
        {"name": "DATABASE_URL", "value": "your-db-url"},
        {"name": "SECRET_KEY", "value": "your-secret-key"},
        {"name": "SMTP_SERVER", "value": "smtp.gmail.com"},
        {"name": "SMTP_PORT", "value": "587"},
        {"name": "SMTP_USERNAME", "value": "your-email@gmail.com"},
        {"name": "SMTP_PASSWORD", "value": "your-app-password"},
        {"name": "SMTP_USE_TLS", "value": "true"},
        {"name": "EMAIL_FROM", "value": "noreply@marketintel.com"},
        {"name": "EMAIL_FROM_NAME", "value": "Market Intelligence Platform"},
        {"name": "DIGEST_RECIPIENT_EMAIL", "value": "your@email.com"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/market-intel",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### 5. Create CloudWatch Log Group

```bash
aws logs create-log-group \
  --log-group-name /ecs/market-intel \
  --region us-east-1
```

### 6. Test Manual Run

```bash
aws ecs run-task \
  --cluster market-intel-cluster \
  --task-definition market-intel-task \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

---

## Troubleshooting

### Email not sending

1. **Check SMTP credentials**:
   ```bash
   python -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587).starttls(); print('OK')"
   ```

2. **Check logs**:
   ```bash
   # Local
   tail -f backend/logs/app.log

   # AWS ECS
   aws logs tail /ecs/market-intel --follow
   ```

3. **Test email service directly**:
   ```python
   from app.services.email_service import email_service
   from app.schemas.digest import DigestResponse, DigestItemResponse
   from datetime import datetime

   # Create test digest
   digest = DigestResponse(
       generated_at=datetime.now(),
       items=[],
       total_items=0
   )

   # Send test
   await email_service.send_daily_digest("your@email.com", digest)
   ```

### Gmail "Less secure app" error

Gmail no longer supports "less secure apps". You MUST use an **App Password**:
1. Enable 2-Step Verification
2. Generate App Password
3. Use 16-digit password in `.env`

### AWS ECS task failing

1. **Check task logs**:
   ```bash
   aws ecs describe-tasks \
     --cluster market-intel-cluster \
     --tasks TASK_ARN
   ```

2. **Verify environment variables** in task definition

3. **Check security group** allows outbound SMTP (port 587)

### Emails going to spam

- Use AWS SES with verified domain
- Add SPF/DKIM records to your domain
- Warm up sender reputation gradually
- Avoid spammy keywords in subject/body

---

## Email Template

The digest uses a beautiful Robinhood-inspired dark theme with:
- Responsive HTML design
- Mobile-optimized layout
- Clean typography
- Color-coded signals (green/red/white)
- Professional disclaimers

Located at: `backend/app/services/email_service.py`

---

## Testing Commands

```bash
# Test digest generation (no email)
python scripts/send_daily_digest.py --help

# Send test digest
python scripts/send_daily_digest.py --email your@email.com

# Custom parameters
python scripts/send_daily_digest.py \
  --email your@email.com \
  --max-items 15 \
  --hours-lookback 48

# Test via GitHub Actions (manual trigger)
# Go to Actions → Daily Digest → Run workflow
```

---

## Migration from Trade-Ideas

If migrating from the old trade-ideas repository:

1. ✅ **Backup created**: `~/trade-ideas-backup-20251014.bundle`
2. ✅ **Workflows disabled**: Archive trade-ideas repo on GitHub
3. ✅ **Email service ported**: Same SMTP configuration
4. ✅ **Schedules maintained**: 6:30 AM and 7:00 AM AZ time
5. ✅ **AWS ECS compatible**: Same infrastructure

**No changes needed** - just update GitHub secrets and enable workflows!

---

## Support

**Issues?**
- Check logs: `backend/logs/app.log`
- Test SMTP connection
- Verify environment variables
- Review AWS ECS task logs

**Documentation:**
- Backend: `backend/README.md`
- Workflows: `.github/workflows/`
- Email service: `backend/app/services/email_service.py`

---

**Status**: ✅ Email delivery system configured and ready
**Date**: October 14, 2025
**Version**: 1.0.0
