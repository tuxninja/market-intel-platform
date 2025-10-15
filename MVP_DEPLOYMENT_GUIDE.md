# MVP Deployment Guide - Market Intelligence Platform

**Goal**: Get automated daily market intelligence emails working in 15 minutes

---

## What You're Deploying

A simple system that:
- Runs automatically every morning at 6:30 AM Arizona Time
- Analyzes stock market news and data
- Sends you a beautiful HTML email with trading insights
- Costs ~$1-2/month (or $6-8 if keeping the API server)

---

## Current Status ✅

### Already Deployed:
- ✅ Backend API at https://qwdhybryip.us-east-1.awsapprunner.com
- ✅ Database (Supabase PostgreSQL)
- ✅ Docker image in AWS ECR
- ✅ ECS Cluster (market-intel-cluster)
- ✅ ECS Task Definition (market-intel-task)
- ✅ GitHub Actions workflows configured
- ✅ All code pushed to GitHub

### What You Need to Do:
- ⏸️ Set up SMTP email credentials (5 min)
- ⏸️ Configure GitHub secrets (2 min)
- ⏸️ Test email delivery (3 min)
- ⏸️ Enable daily schedule (1 min)

**Total time**: 15 minutes

---

## Step 1: Set Up SMTP Email (5 minutes)

You need email credentials to send the daily digest. Choose one option:

### Option A: Gmail (Easiest - Recommended)

1. **Go to Google Account Security**: https://myaccount.google.com/security

2. **Enable 2-Factor Authentication** (if not already enabled):
   - Click "2-Step Verification"
   - Follow the setup wizard

3. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Other" → Type "Market Intel Platform"
   - Click "Generate"
   - **Copy the 16-character password** (format: xxxx xxxx xxxx xxxx)

4. **Save these credentials**:
   ```
   SMTP_USERNAME = your-email@gmail.com
   SMTP_PASSWORD = xxxx xxxx xxxx xxxx (16 characters)
   ```

### Option B: AWS SES (Production-grade)

1. **Verify your email**:
   ```bash
   aws ses verify-email-identity --email-address your@email.com --region us-east-1
   ```

2. **Check inbox and click verification link**

3. **Get SMTP credentials**:
   - Go to: AWS Console → SES → SMTP Settings
   - Click "Create My SMTP Credentials"
   - Download and save the credentials

4. **Note**:
   ```
   SMTP_SERVER = email-smtp.us-east-1.amazonaws.com
   SMTP_PORT = 587
   SMTP_USERNAME = (from download)
   SMTP_PASSWORD = (from download)
   ```

---

## Step 2: Configure GitHub Secrets (2 minutes)

1. **Go to GitHub Secrets**:
   - URL: https://github.com/tuxninja/market-intel-platform/settings/secrets/actions
   - Or: Repository → Settings → Secrets and variables → Actions

2. **Add these secrets** (click "New repository secret" for each):

   **DIGEST_RECIPIENT_EMAIL**:
   ```
   your@email.com
   ```

   **SMTP_USERNAME**:
   ```
   your-email@gmail.com
   ```
   (or AWS SES username)

   **SMTP_PASSWORD**:
   ```
   xxxx xxxx xxxx xxxx
   ```
   (your 16-char Gmail app password or AWS SES password)

3. **Verify all secrets are set**:
   - You should now have: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `DIGEST_RECIPIENT_EMAIL`, `SMTP_USERNAME`, `SMTP_PASSWORD`

---

## Step 3: Test Email Delivery (3 minutes)

### Test Locally (Fastest)

```bash
cd /Users/jasonriedel/PyCharmProjects/market-intel-platform/backend

# Set environment variables
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="xxxx xxxx xxxx xxxx"
export DATABASE_URL="postgresql://postgres:#Marjynh8338@db.urbxneuanylgeshiqmgi.supabase.co:5432/postgres"

# Send test email
python scripts/send_daily_digest.py --email your@email.com
```

**Expected output**:
```
======================================================
📧 Daily Market Intelligence Digest
======================================================
Recipient: your@email.com
Max Items: 20
Lookback:  24 hours
SMTP:      smtp.gmail.com:587
======================================================

Database initialized
Generating digest: max_items=20, lookback=24h
Generated digest with 15 items
Sending digest email to your@email.com
✅ Daily digest sent successfully!
```

**Check your inbox** - you should receive the email within 1-2 minutes.

### Test via AWS ECS (Production-like)

```bash
cd /Users/jasonriedel/PyCharmProjects/market-intel-platform

# Run test script
./scripts/test_ecs_digest.sh your@email.com
```

This runs the full production workflow via AWS ECS.

### Test via GitHub Actions (Full automation)

1. **Go to GitHub Actions**: https://github.com/tuxninja/market-intel-platform/actions

2. **Select workflow**: "Daily Market Intelligence Digest"

3. **Click "Run workflow"**

4. **Fill in**:
   - Branch: main
   - Recipient email: your@email.com (optional, uses secret if blank)
   - Max items: 20
   - Hours lookback: 24

5. **Click "Run workflow"**

6. **Monitor progress** - click on the running workflow to see logs

7. **Check inbox** after 2-3 minutes

---

## Step 4: Enable Daily Schedule (1 minute)

Once testing works, enable the automatic daily schedule:

### Edit Workflow File

```bash
cd /Users/jasonriedel/PyCharmProjects/market-intel-platform

# Edit the workflow file
open .github/workflows/daily-digest.yml
```

### Uncomment the Schedule Section

Find these lines (near the top):
```yaml
on:
  # Disabled by default - enable after AWS ECS setup
  # schedule:
  #   # Run at 6:30 AM Arizona Time (13:30 UTC) Monday-Friday
  #   # 30 minutes before main trading analysis for morning news brief
  #   - cron: '30 13 * * 1-5'
  workflow_dispatch:
```

Change to:
```yaml
on:
  # Runs at 6:30 AM Arizona Time (13:30 UTC) Monday-Friday
  schedule:
    # 30 minutes before main trading analysis for morning news brief
    - cron: '30 13 * * 1-5'
  workflow_dispatch:
```

### Commit and Push

```bash
git add .github/workflows/daily-digest.yml
git commit -m "Enable daily digest email schedule"
git push origin main
```

**Done!** You'll now receive daily market intelligence emails at 6:30 AM Arizona Time, Monday-Friday.

---

## What You'll Receive

### Email Subject
```
Daily Market Intelligence Digest - October 15, 2025
```

### Email Content

**Header**:
- Date and time
- Market regime (Bullish/Bearish/Neutral)
- VIX level (volatility)

**🟢 BULLISH SIGNALS** (3-7 items):
- Stock symbol
- **Why This Matters**: Clear explanation of the catalyst
- **How to Trade**: Actionable steps
- Confidence score (High/Medium/Low)

**🔴 BEARISH SIGNALS** (3-7 items):
- Stock symbol
- **Why This Matters**: Risk analysis
- **How to Trade**: Avoidance or short strategies
- Confidence score

**⚪ NEUTRAL SIGNALS (WATCH LIST)** (3-7 items):
- Stocks showing interesting patterns
- **Why This Matters**: What to watch for
- **How to Trade**: Entry/exit considerations
- Confidence score

**💡 MARKET SUMMARY**:
- Top movers
- Sector performance
- Key news headlines
- Economic calendar events

**Design**: Beautiful dark theme inspired by Robinhood

---

## Monitoring & Management

### View Logs

**GitHub Actions logs**:
```
https://github.com/tuxninja/market-intel-platform/actions
```

**AWS ECS logs**:
```bash
aws logs tail /ecs/market-intel --follow --region us-east-1
```

**CloudWatch Logs Console**:
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Fecs$252Fmarket-intel
```

### Manual Trigger

**Via GitHub Actions** (easiest):
1. Go to https://github.com/tuxninja/market-intel-platform/actions
2. Select "Daily Market Intelligence Digest"
3. Click "Run workflow"
4. Enter parameters (or use defaults)
5. Click "Run workflow"

**Via CLI**:
```bash
./scripts/test_ecs_digest.sh your@email.com
```

### Customize Settings

**Change schedule**:
- Edit `.github/workflows/daily-digest.yml`
- Modify the cron expression
- Commit and push

**Adjust digest content**:
```bash
# More items
./scripts/test_ecs_digest.sh your@email.com 30

# Longer lookback window
./scripts/test_ecs_digest.sh your@email.com 20 48
```

### Stop Receiving Emails

**Temporarily disable**:
1. Go to: https://github.com/tuxninja/market-intel-platform/settings/actions
2. Click "Disable Actions" (or just disable the specific workflow)

**Permanently stop**:
```bash
cd /Users/jasonriedel/PyCharmProjects/market-intel-platform

# Comment out schedule in workflow
vim .github/workflows/daily-digest.yml

# Commit and push
git add .github/workflows/daily-digest.yml
git commit -m "Disable daily digest schedule"
git push origin main
```

---

## Costs Breakdown

### Monthly Costs

| Service | Usage | Cost |
|---------|-------|------|
| **AWS ECS Fargate** | 5 min/day, 0.5 vCPU, 1 GB | $0.50-1.00 |
| **AWS ECR** | Docker image storage | $0.10 |
| **Supabase** | Database (free tier) | $0.00 |
| **Gmail SMTP** | Email delivery (free) | $0.00 |
| **AWS App Runner** | API server (optional) | $5-7.00 |
| **Total (MVP)** | | **$0.60-1.10** |
| **Total (with API)** | | **$5.60-8.10** |

### Cost Optimization

**Save $5-7/month**: Shut down App Runner since you don't need it for MVP

```bash
# Delete App Runner service (save $5-7/mo)
aws apprunner delete-service \
  --service-arn arn:aws:apprunner:us-east-1:907391580367:service/market-intel-api/b6383d469d8c4844867dcb5f565e9a3d \
  --region us-east-1
```

You can always recreate it later if you want to add a web interface or API.

---

## Troubleshooting

### Email Not Received

**Check spam folder**:
- Gmail, Outlook, etc. may filter automated emails

**Verify SMTP credentials**:
```bash
# Test SMTP connection
python -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
print('✅ SMTP connection successful')
server.quit()
"
```

**Check GitHub Actions logs**:
- Go to: https://github.com/tuxninja/market-intel-platform/actions
- Click on the failed workflow
- Look for error messages

**Common issues**:
- Wrong SMTP password (must be app password, not account password)
- 2FA not enabled (required for Gmail app passwords)
- SMTP_USERNAME/SMTP_PASSWORD secrets not set
- Email address typo

### Task Fails to Start

**Check ECS task definition**:
```bash
aws ecs describe-task-definition \
  --task-definition market-intel-task \
  --region us-east-1
```

**Check cluster status**:
```bash
aws ecs describe-clusters \
  --clusters market-intel-cluster \
  --region us-east-1
```

**Check Docker image exists**:
```bash
aws ecr describe-images \
  --repository-name market-intel-backend \
  --region us-east-1
```

### Digest Content Issues

**No signals generated**:
- Market may be closed or no news available
- Try increasing `--hours-lookback` parameter
- Check if RSS feeds are accessible

**Poor quality signals**:
- Sentiment analysis needs tuning
- Adjust confidence thresholds in code
- Add more data sources

**Formatting issues**:
- Check email HTML template
- Test in different email clients
- View source in email to debug

---

## What to Work On Next

### Immediate (This Week)

1. ✅ Test daily email delivery for 3-5 days
2. ✅ Verify signals are useful and actionable
3. ✅ Adjust digest content (items, lookback, etc.)
4. ✅ Fine-tune schedule if needed
5. ✅ Decide if keeping App Runner or shutting it down

### Short Term (This Month)

1. **Improve signal quality**:
   - Add more data sources (Twitter, Reddit, SEC filings)
   - Improve sentiment analysis accuracy
   - Filter out low-quality signals

2. **Add features**:
   - Weekly summary emails
   - Custom watchlist support
   - Portfolio tracking
   - SMS alerts for high-confidence signals

3. **Optimize costs**:
   - Shut down App Runner if not needed
   - Consider reserved capacity for ECS
   - Evaluate free tier limits

### Medium Term (Next 3 Months)

1. **Validate value**:
   - Track profitable signals
   - Measure accuracy
   - Backtest strategies

2. **Share with others**:
   - Invite friends/colleagues to test
   - Get feedback on usefulness
   - Refine based on feedback

3. **Consider monetization**:
   - If signals are valuable, consider charging
   - Deploy frontend for user signups
   - Implement subscription system

### Long Term (6-12 Months)

1. **Full SaaS platform**:
   - Public web interface
   - User registration and authentication
   - Tiered pricing (free/pro/premium)
   - Payment processing (Stripe)

2. **Advanced features**:
   - Real-time alerts (not just daily)
   - AI-powered analysis (GPT integration)
   - Social features (leaderboards, signal sharing)
   - Mobile app

3. **Scale infrastructure**:
   - Migrate to AWS RDS
   - Add caching (ElastiCache)
   - Implement CDN
   - Set up monitoring and alerting

---

## Summary: You're Done!

### What You Have

✅ **Automated daily emails** with market intelligence
✅ **Production infrastructure** on AWS
✅ **Scheduled execution** via GitHub Actions
✅ **Beautiful HTML emails** with trading insights
✅ **Low cost** (~$1-2/month for MVP)
✅ **Easy to manage** (GitHub Actions UI)
✅ **Scalable foundation** (add features later)

### What You Do

📧 **Check your email** every morning at 6:30 AM Arizona Time
📊 **Review trading signals** (bullish, bearish, watchlist)
💰 **Make informed trading decisions**
🔍 **Monitor reliability** for first week
⚙️ **Adjust settings** as needed

### What's Next

Choose your path:

**Path A: MVP Only** ($1-2/month)
- Keep it simple
- Just receive daily emails
- Shut down App Runner to save money
- Perfect for personal use

**Path B: Full Platform** ($6-8/month)
- Keep App Runner running
- Ready to add web interface
- Can share with others
- Foundation for monetization

### Need Help?

**Documentation**:
- `MVP_SUMMARY.md` - Overview and context
- `MVP_DEPLOYMENT_GUIDE.md` - This file
- `PRODUCTION_DEPLOYED.md` - Infrastructure details
- `START_HERE.md` - Quick start guide

**Scripts**:
- `scripts/setup_ecs_task.sh` - Set up ECS task definition
- `scripts/test_ecs_digest.sh` - Test email delivery
- `backend/scripts/send_daily_digest.py` - Main digest script

**Resources**:
- GitHub Actions: https://github.com/tuxninja/market-intel-platform/actions
- CloudWatch Logs: AWS Console → CloudWatch → Logs
- Supabase Dashboard: https://supabase.com/dashboard

---

**Congratulations! Your automated market intelligence system is live!** 🎉

Check your email tomorrow morning for your first automated digest.
