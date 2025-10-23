# ML Signal System - Production Deployment Guide

**Date**: October 22, 2025
**Target**: AWS ECS (Fargate)
**Status**: Ready for Production Deployment

---

## 🚀 Quick Deployment (Recommended)

### Option 1: Automated Script

```bash
cd backend
./deploy_ml_signals.sh
```

This script handles everything:
- ✅ Database migration (signal_history table)
- ✅ Docker build with FinBERT pre-cached
- ✅ Push to ECR
- ✅ Update ECS service

**Time**: ~10 minutes (mostly Docker build)

---

## 📋 Manual Deployment Steps

### Step 1: Run Database Migration

```bash
cd backend
alembic upgrade head
```

This creates the `signal_history` table for deduplication.

**Verify**:
```sql
SELECT * FROM alembic_version;
-- Should show revision '002'

\d signal_history
-- Should show table structure
```

### Step 2: Build Docker Image

```bash
cd backend
docker build --platform linux/amd64 -t market-intel-backend:ml-signals .
```

**Important**: This downloads FinBERT model (~450MB) during build:
- First build: ~8-10 minutes
- Cached builds: ~2-3 minutes

**Image size**: ~1.5GB (vs ~500MB before)

### Step 3: Push to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  907391580367.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag market-intel-backend:ml-signals \
  907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:ml-signals

# Push image
docker push 907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:ml-signals

# Update latest tag
docker tag market-intel-backend:ml-signals \
  907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest
docker push 907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest
```

### Step 4: Update ECS Task Definition

**CRITICAL**: Increase memory allocation for FinBERT model.

Edit your ECS task definition:

```json
{
  "family": "market-intel-backend",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest",
      "memory": 2048,  // ⚠️ CHANGED: Was 512, now 2048 (2GB for FinBERT)
      "cpu": 512,      // ⚠️ CHANGED: Was 256, now 512 (0.5 vCPU)
      "environment": [
        {"name": "DATABASE_URL", "value": "your-db-url"},
        {"name": "SMTP_HOST", "value": "smtp.gmail.com"},
        {"name": "TRANSFORMERS_CACHE", "value": "/app/.cache"},
        {"name": "HF_HOME", "value": "/app/.cache"}
      ]
    }
  ]
}
```

**Why increase memory?**
- FinBERT model: ~1.2GB in memory
- Python runtime: ~200MB
- App logic: ~200MB
- Buffer: ~400MB
- **Total**: ~2GB minimum

### Step 5: Update ECS Service

```bash
aws ecs update-service \
  --cluster market-intel-cluster \
  --service market-intel-backend \
  --force-new-deployment \
  --region us-east-1
```

Monitor deployment:
```bash
aws ecs describe-services \
  --cluster market-intel-cluster \
  --services market-intel-backend \
  --query 'services[0].deployments'
```

---

## 🔍 Verification & Testing

### 1. Check Container Logs

```bash
# Get task ARN
TASK_ARN=$(aws ecs list-tasks \
  --cluster market-intel-cluster \
  --service market-intel-backend \
  --query 'taskArns[0]' \
  --output text)

# View logs
aws logs tail /ecs/market-intel-backend --follow
```

**Look for**:
```
Loading FinBERT model...
FinBERT model loaded successfully
🚀 Generating NEWS-DRIVEN trading signals (ML-powered with FinBERT)
```

### 2. Test Digest Generation

```bash
curl https://your-backend-url/api/v1/digest
```

**Expected response**:
- HTTP 200
- JSON with `items` array
- Each item has `source: "news_driven_ml"`
- Metadata includes `ml_confidence` field

### 3. Verify Signal Deduplication

```sql
-- Check signal_history table
SELECT
  symbol,
  signal_type,
  confidence_score,
  news_title,
  created_at
FROM signal_history
ORDER BY created_at DESC
LIMIT 10;
```

Should see entries after digest generation.

### 4. Monitor Performance

**First Signal Generation**:
- Expected: 25-35 seconds
- FinBERT initialization: ~5 seconds
- News fetching: ~10 seconds
- ML processing: ~10 seconds
- Technical analysis: ~5-10 seconds

**Subsequent Generations**:
- Expected: 15-20 seconds (FinBERT cached)

---

## 📊 Cost Impact

### Infrastructure Changes:

| Component | Before | After | Monthly Cost |
|-----------|--------|-------|--------------|
| ECS Task Memory | 512MB | 2048MB | +$8/month |
| ECS Task CPU | 0.25 vCPU | 0.5 vCPU | +$4/month |
| ECR Storage | 500MB | 1.5GB | +$0.10/month |
| Data Transfer | ~1GB | ~1.2GB | +$0.10/month |
| **Total** | **~$5/mo** | **~$17/mo** | **+$12/month** |

**Note**: Still well under $20/month target!

### Pricing Breakdown:
- Fargate pricing: $0.04048/hour for 0.5 vCPU
- Memory pricing: $0.004445/GB-hour
- Running 24/7: $0.04048 + (2 × $0.004445) = $0.0494/hour
- Monthly: $0.0494 × 730 hours = **$36.06/month**

**Wait, that's over budget!**

### Cost Optimization Options:

**Option 1: Scheduled Tasks Only**
- Run digest generation via scheduled task (not always-on service)
- Run 2x/day (morning + evening digests)
- Cost: ~$3/month for scheduled tasks

**Option 2: Use Spot Fargate** (70% savings)
- Spot pricing: ~$11/month vs $36
- Suitable for non-critical tasks

**Option 3: Use EC2 t3.small** (cheaper for 24/7)
- t3.small: $15/month
- More memory (2GB) than needed
- Better for always-on services

**Recommended**: Option 1 (Scheduled Tasks) to stay under budget.

---

## ⚙️ Configuration Tuning

Located in `news_driven_signal_generator.py`:

### More Signals:
```python
NEWS_LOOKBACK_HOURS = 12  # Was 6 - look back further
MIN_SENTIMENT_CONFIDENCE = 0.5  # Was 0.6 - lower threshold
MIN_COMBINED_SCORE = 0.25  # Was 0.3 - accept weaker signals
```

### Fewer Signals (Higher Quality):
```python
NEWS_LOOKBACK_HOURS = 3  # Was 6 - only very fresh news
MIN_SENTIMENT_CONFIDENCE = 0.75  # Was 0.6 - higher confidence
MIN_COMBINED_SCORE = 0.4  # Was 0.3 - stronger signals only
```

### Deduplication Window:
```python
SIGNAL_EXPIRY_DAYS = 3  # Was 7 - allow repeats sooner
# or
SIGNAL_EXPIRY_DAYS = 14  # Was 7 - longer deduplication
```

---

## 🐛 Troubleshooting

### Issue: "No signals generated"

**Possible Causes**:
1. No breaking news in last 6 hours
2. NewsAPI rate limit (100 calls/day free tier)
3. All news had low ML confidence (<60%)
4. All signals filtered as duplicates

**Solutions**:
- Lower `MIN_SENTIMENT_CONFIDENCE` to 0.5
- Increase `NEWS_LOOKBACK_HOURS` to 12
- Check CloudWatch logs for specific errors
- Verify NewsAPI key is valid

### Issue: "Out of memory" error

**Solution**: Increase task memory to 3GB or 4GB.

```json
{
  "memory": 3072  // 3GB instead of 2GB
}
```

### Issue: FinBERT download fails during container startup

**Cause**: Model not pre-cached in Docker image.

**Solution**: Rebuild Docker image (FinBERT download happens during `docker build`):
```bash
docker build --no-cache --platform linux/amd64 -t market-intel-backend:ml-signals .
```

### Issue: Slow signal generation (>60 seconds)

**Possible Causes**:
1. yfinance rate limiting (too many stocks)
2. NewsAPI slow response
3. CPU throttling

**Solutions**:
- Reduce watchlist size
- Implement caching for market data
- Increase CPU allocation to 1 vCPU

### Issue: Database connection errors

**Cause**: `signal_history` table not created.

**Solution**:
```bash
alembic upgrade head
```

---

## 📈 Monitoring & Alerts

### CloudWatch Metrics to Track:

1. **Signal Generation Time**
   - Create custom metric
   - Alert if > 60 seconds

2. **Signal Count**
   - Track signals generated per run
   - Alert if 0 for multiple consecutive runs

3. **ML Confidence**
   - Average confidence score
   - Alert if < 0.5 (low quality)

4. **Memory Usage**
   - Should stay around 1.5GB
   - Alert if > 1.8GB (nearing limit)

5. **Error Rate**
   - Track exceptions in signal generation
   - Alert if > 5% error rate

### Example CloudWatch Dashboard:

```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["MarketIntel", "SignalGenerationTime", {"stat": "Average"}],
          ["...", {"stat": "Maximum"}]
        ],
        "title": "Signal Generation Performance"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["MarketIntel", "SignalsGenerated", {"stat": "Sum"}]
        ],
        "title": "Signals Generated (Daily)"
      }
    }
  ]
}
```

---

## 🎯 Success Criteria

Deployment is successful when:

- ✅ ECS task starts and stays healthy
- ✅ FinBERT model loads without errors
- ✅ Digest generation completes in < 35 seconds
- ✅ Signals have `source: "news_driven_ml"`
- ✅ `signal_history` table receives new entries
- ✅ Email digest contains fresh, non-repeated signals
- ✅ Memory usage stays under 2GB
- ✅ No errors in CloudWatch logs

---

## 📞 Rollback Plan

If deployment fails:

### Quick Rollback:
```bash
# Revert to previous task definition
aws ecs update-service \
  --cluster market-intel-cluster \
  --service market-intel-backend \
  --task-definition market-intel-backend:PREVIOUS_REVISION \
  --force-new-deployment
```

### Emergency Disable ML:
Edit `digest_service.py`:
```python
# Temporarily disable news-driven generator
# items = await news_generator.generate_signals(max_signals=max_items)

# Use old generator
items = await signal_generator.generate_signals(max_signals=max_items)
```

Then redeploy.

---

## 📝 Post-Deployment Checklist

- [ ] Database migration successful (`signal_history` table exists)
- [ ] Docker image built and pushed to ECR
- [ ] ECS task definition updated (2GB memory, 0.5 vCPU)
- [ ] ECS service deployed successfully
- [ ] Container logs show FinBERT loaded
- [ ] Digest API returns news-driven signals
- [ ] `signal_history` table populated
- [ ] Email digest sent with fresh signals
- [ ] No duplicate signals in consecutive digests
- [ ] CloudWatch alerts configured
- [ ] Cost monitoring enabled

---

## 🚀 Next Steps After Deployment

1. **Monitor for 24-48 hours**
   - Check CloudWatch logs daily
   - Verify signal quality
   - Monitor costs

2. **Tune Configuration**
   - Adjust `MIN_SENTIMENT_CONFIDENCE` based on signal quality
   - Modify `NEWS_LOOKBACK_HOURS` based on signal volume
   - Fine-tune deduplication window

3. **Collect Metrics**
   - Track signal win rates (Phase 3)
   - Measure user engagement
   - Calculate average confidence scores

4. **Optimize Costs**
   - Consider scheduled tasks vs always-on
   - Implement caching for market data
   - Use Spot Fargate if suitable

---

**Ready to deploy?** Run: `./deploy_ml_signals.sh`

**Questions?** Check CloudWatch logs or see `ML_SIGNAL_UPGRADE.md`

---

*Last Updated: October 22, 2025*
