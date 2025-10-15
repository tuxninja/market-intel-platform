# Quick Start - Market Intelligence Platform

**Your daily market intelligence emails start tomorrow at 6:30 AM Arizona Time!**

---

## ✅ Everything is Set Up

- Daily email automation: **ENABLED**
- Recipient: **jasonnetbiz@gmail.com**
- Schedule: **6:30 AM Arizona Time (Mon-Fri)**
- Cost: **~$1/month**

---

## 🧪 Test It Right Now

```bash
# Option 1: Via CLI
gh workflow run "Daily Market Intelligence Digest" --ref main

# Option 2: Via Web
# Go to: https://github.com/tuxninja/market-intel-platform/actions
# Click: "Daily Market Intelligence Digest" → "Run workflow"
```

**Check your email in 2-3 minutes**: jasonnetbiz@gmail.com

---

## 📧 What You'll Get

**Subject**: Daily Market Intelligence Digest - [Date]

**Content**:
- 🟢 **TRADE ALERTS**: High-confidence buy/sell signals
- ⚪ **WATCH LIST**: Stocks to monitor
- 💡 **MARKET CONTEXT**: Overall market analysis
- 📊 **VIX REGIME**: Volatility assessment

Each signal includes:
- **WHY THIS MATTERS**: Clear explanation
- **HOW TO TRADE**: Actionable steps
- **Confidence Score**: Reliability indicator

---

## 🔧 Useful Commands

### Monitor Workflow
```bash
# List recent runs
gh run list --workflow="Daily Market Intelligence Digest" --limit 5

# Watch live run
gh run watch

# View logs
gh run view [RUN_ID] --log
```

### Check ECS Logs
```bash
# View recent logs
aws logs tail /ecs/market-intel --since 10m --follow

# Search for errors
aws logs tail /ecs/market-intel --since 1h | grep -i error
```

### Manage Schedule
```bash
# Disable daily emails
# Edit: .github/workflows/daily-digest.yml
# Comment out the schedule section

# Re-enable
# Uncomment the schedule section
```

---

## 💰 Monthly Cost

| Service | Cost |
|---------|------|
| ECS Fargate | $0.50-1/mo |
| ECR Storage | $0.10/mo |
| **Total** | **~$0.60-1.10/mo** |

*(App Runner API server costs $5-7/mo but not needed for MVP)*

---

## 🐛 If Something Goes Wrong

### Email Doesn't Arrive
1. Check spam folder
2. View workflow logs: https://github.com/tuxninja/market-intel-platform/actions
3. Check ECS logs: `aws logs tail /ecs/market-intel --since 10m`

### Workflow Fails
**Likely cause**: Docker image not updated

**Fix**:
```bash
cd backend
docker buildx build --platform linux/amd64 \
  -t 907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest \
  --load .
docker push 907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest
```

Then trigger workflow again.

---

## 📚 Full Documentation

- `DEPLOYMENT_COMPLETE.md` - Complete summary
- `MVP_SUMMARY.md` - What was built
- `MVP_DEPLOYMENT_GUIDE.md` - Detailed setup guide

---

## 🎯 Next Steps

### Today
- ✅ Test manual email delivery
- ✅ Verify email looks good
- ✅ Confirm schedule is enabled

### This Week
- Replace demo signals with real market analysis
- Add more data sources (news, sentiment, etc.)
- Fine-tune signal quality

### This Month
- Enable database storage
- Track signal performance
- Add custom watchlists

---

**That's it! You're all set. Enjoy your daily market intelligence!** 📈

**Questions?** Check full docs or GitHub Actions logs.
