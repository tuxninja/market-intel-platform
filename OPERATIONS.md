# TradeTheHype - Operations Guide

**Quick Reference**: How to scale infrastructure up/down to control AWS costs

---

## 🎛️ Current Configuration

### Architecture Overview
- **Backend**: FastAPI app running on AWS ECS Fargate
- **Database**: Supabase PostgreSQL (Free tier - always on)
- **Scheduled Task**: EventBridge rule triggers daily digest at 6:30 AM Arizona time
- **Frontend**: Not deployed (can use AWS App Runner when needed)

### Task Definition
- **Name**: market-intel-backend:6
- **CPU**: 512 (0.5 vCPU)
- **Memory**: 2048 MB (2 GB - required for FinBERT ML model)
- **Image**: `907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest`

---

## 💰 Cost Profiles

### Scale Down (Current - Recommended for Development)
- **ECS Desired Count**: 0
- **Backend Availability**: Only during scheduled digest (5 min/day)
- **Monthly Cost**: ~$2-3
- **Use Case**: Not actively developing, just testing daily emails

### Scale Up (Full Service)
- **ECS Desired Count**: 1
- **Backend Availability**: 24/7 continuous
- **Monthly Cost**: ~$15-17
- **Use Case**: Active development, testing API endpoints, web dashboard

---

## 🔧 Quick Commands

### Scale DOWN (Stop Continuous Running)
**Use when**: Done developing, just want daily emails

```bash
# Stop the always-on backend service
aws ecs update-service \
  --cluster market-intel-cluster \
  --service market-intel-backend-service \
  --desired-count 0 \
  --region us-east-1

# Verify it's scaled down
aws ecs describe-services \
  --cluster market-intel-cluster \
  --services market-intel-backend-service \
  --region us-east-1 \
  --query 'services[0].{desiredCount:desiredCount,runningCount:runningCount}'
```

**Result**:
- No tasks running continuously
- Scheduled task still runs daily at 6:30 AM
- Saves ~$13-15/month

---

### Scale UP (Start Continuous Running)
**Use when**: Developing, need backend API available 24/7

```bash
# Start the backend service (1 task continuously running)
aws ecs update-service \
  --cluster market-intel-cluster \
  --service market-intel-backend-service \
  --desired-count 1 \
  --region us-east-1

# Wait 2-3 minutes for task to start, then verify
aws ecs describe-services \
  --cluster market-intel-cluster \
  --services market-intel-backend-service \
  --region us-east-1 \
  --query 'services[0].{desiredCount:desiredCount,runningCount:runningCount,deployments:deployments[0].rolloutState}'
```

**Result**:
- 1 task running continuously
- Backend API available 24/7
- Costs ~$15-17/month

---

### Check Current Status

```bash
# See if backend is running
aws ecs list-tasks \
  --cluster market-intel-cluster \
  --region us-east-1

# Check service configuration
aws ecs describe-services \
  --cluster market-intel-cluster \
  --services market-intel-backend-service \
  --region us-east-1 \
  --query 'services[0].{desiredCount:desiredCount,runningCount:runningCount,taskDef:taskDefinition}'

# Check scheduled task status
aws events describe-rule \
  --name daily-market-digest \
  --region us-east-1 \
  --query '{Name:Name,State:State,Schedule:ScheduleExpression}'
```

---

## 🛑 Pause Everything (Complete Shutdown)

**Use when**: Not using at all, want $0 AWS costs

```bash
# 1. Disable scheduled digest emails
aws events disable-rule \
  --name daily-market-digest \
  --region us-east-1

# 2. Scale service to 0
aws ecs update-service \
  --cluster market-intel-cluster \
  --service market-intel-backend-service \
  --desired-count 0 \
  --region us-east-1

# 3. Verify everything is stopped
aws ecs list-tasks --cluster market-intel-cluster --region us-east-1
aws events describe-rule --name daily-market-digest --region us-east-1 --query 'State'
```

**Result**:
- No backend running
- No scheduled tasks
- No emails sent
- ~$0/month AWS costs

---

## 🔄 Resume Everything

**Use when**: Ready to start development again

```bash
# 1. Re-enable scheduled digest emails
aws events enable-rule \
  --name daily-market-digest \
  --region us-east-1

# 2. Scale service to 1 (if you want continuous running)
aws ecs update-service \
  --cluster market-intel-cluster \
  --service market-intel-backend-service \
  --desired-count 1 \
  --region us-east-1

# 3. Verify
aws events describe-rule --name daily-market-digest --region us-east-1 --query '{State:State,Schedule:ScheduleExpression}'
aws ecs describe-services --cluster market-intel-cluster --services market-intel-backend-service --region us-east-1 --query 'services[0].desiredCount'
```

---

## 🐛 View Logs

### Recent Logs (Last 10 Minutes)
```bash
aws logs tail /ecs/market-intel-backend \
  --region us-east-1 \
  --since 10m \
  --follow
```

### Check for Errors
```bash
aws logs tail /ecs/market-intel-backend \
  --region us-east-1 \
  --since 1h \
  --format short | grep -i error
```

### Check Digest Generation
```bash
aws logs tail /ecs/market-intel-backend \
  --region us-east-1 \
  --since 1h \
  --format short | grep -E "Generated|signals|digest"
```

---

## 🚀 Deploy New Code

### 1. Build & Push Docker Image
```bash
cd /Users/jasonriedel/PyCharmProjects/tradethehype_com/backend

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  907391580367.dkr.ecr.us-east-1.amazonaws.com

# Build for AWS (linux/amd64)
docker build --platform linux/amd64 -t market-intel-backend:latest .

# Tag for ECR
docker tag market-intel-backend:latest \
  907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest

# Push to ECR
docker push 907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest
```

### 2. Force ECS to Pull New Image
```bash
# Force new deployment (pulls latest image)
aws ecs update-service \
  --cluster market-intel-cluster \
  --service market-intel-backend-service \
  --force-new-deployment \
  --region us-east-1

# If service is scaled to 0, you don't need to do anything
# The scheduled task will automatically use the new image next run
```

### 3. Verify Deployment
```bash
# Check deployment status
aws ecs describe-services \
  --cluster market-intel-cluster \
  --services market-intel-backend-service \
  --region us-east-1 \
  --query 'services[0].deployments[*].{Status:status,Desired:desiredCount,Running:runningCount,RolloutState:rolloutState}'

# Wait 2-3 minutes, then check logs
aws logs tail /ecs/market-intel-backend --region us-east-1 --since 5m --follow
```

---

## 📅 Scheduled Task Management

### Daily Digest Schedule
- **Rule Name**: `daily-market-digest`
- **Schedule**: `cron(30 13 * * ? *)` = 6:30 AM Arizona time (UTC-7, no DST)
- **Target**: ECS task (market-intel-backend:6)

### Disable Daily Emails
```bash
aws events disable-rule --name daily-market-digest --region us-east-1
```

### Enable Daily Emails
```bash
aws events enable-rule --name daily-market-digest --region us-east-1
```

### Change Schedule Time
```bash
# Example: Change to 7:00 AM Arizona time (14:00 UTC)
aws events put-rule \
  --name daily-market-digest \
  --schedule-expression 'cron(0 14 * * ? *)' \
  --region us-east-1
```

### Manually Trigger Digest (Test)
```bash
# Find the rule's target
aws events list-targets-by-rule \
  --rule daily-market-digest \
  --region us-east-1

# Trigger it manually via ECS (simpler approach)
aws ecs run-task \
  --cluster market-intel-cluster \
  --task-definition market-intel-backend:6 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-fa91b9c7,subnet-bb4775cd],securityGroups=[sg-25ef645e],assignPublicIp=ENABLED}" \
  --region us-east-1 \
  --overrides '{"containerOverrides":[{"name":"market-intel-backend","command":["python","-m","app.scripts.send_digest"]}]}'
```

---

## 🏗️ Infrastructure Resources

### ECS Cluster
- **Name**: `market-intel-cluster`
- **Region**: `us-east-1`

### ECS Service
- **Name**: `market-intel-backend-service`
- **Cluster**: `market-intel-cluster`
- **Scheduling Strategy**: REPLICA
- **Launch Type**: FARGATE

### Task Definition Revisions
- **Current**: `market-intel-backend:6` (0.5 vCPU, 2GB RAM, latest image)
- **Previous**: `market-intel-backend:5` (old image with bugs)

### ECR Repository
- **Name**: `market-intel-backend`
- **URI**: `907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend`
- **Region**: `us-east-1`

### Database
- **Provider**: Supabase
- **Type**: PostgreSQL
- **Cost**: $0 (free tier)
- **Connection**: Already configured in backend/.env

### EventBridge Rules
- **Rule**: `daily-market-digest`
- **Target**: ECS Task (market-intel-backend:6)

---

## 🚨 Common Issues

### Issue: Backend Won't Start
**Symptom**: Logs show `Application startup failed`

**Check**:
```bash
aws logs tail /ecs/market-intel-backend --region us-east-1 --since 10m | grep -i error
```

**Common Causes**:
1. Database connection issues (check DATABASE_URL)
2. SSL certificate problems (should be fixed in database.py)
3. Missing environment variables

### Issue: No Emails Being Sent
**Check scheduled task**:
```bash
aws events describe-rule --name daily-market-digest --region us-east-1
```

**Verify it's ENABLED**. If disabled:
```bash
aws events enable-rule --name daily-market-digest --region us-east-1
```

### Issue: Getting Only Demo Signals
**Cause**: Backend can't connect to database or ML model failing

**Check logs**:
```bash
aws logs tail /ecs/market-intel-backend --region us-east-1 --since 30m | grep -E "Generated|signals|fallback|demo"
```

**Look for**: Messages about falling back to demo signals

---

## 📊 Cost Monitoring

### View Current Month Costs
```bash
# This requires AWS Cost Explorer CLI (not always available)
# Alternative: Check AWS Console → Cost Management → Cost Explorer

# Or use CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=market-intel-backend-service Name=ClusterName,Value=market-intel-cluster \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Average \
  --region us-east-1
```

### Estimated Monthly Costs

| Configuration | ECS Cost | EventBridge | ECR | Total |
|--------------|----------|-------------|-----|-------|
| **Scaled Down (desiredCount=0)** | $2-3/mo | $0.01/mo | $0.50/mo | **~$3/mo** |
| **Scaled Up (desiredCount=1)** | $15-17/mo | $0.01/mo | $0.50/mo | **~$17/mo** |
| **Paused (rule disabled)** | $0/mo | $0/mo | $0.50/mo | **~$0.50/mo** |

---

## 🎯 Development Workflow

### Typical Development Session

1. **Start**: Scale up to get backend running
   ```bash
   aws ecs update-service --cluster market-intel-cluster --service market-intel-backend-service --desired-count 1 --region us-east-1
   ```

2. **Develop**: Make code changes locally

3. **Test**: Deploy new code
   ```bash
   cd backend
   docker build --platform linux/amd64 -t market-intel-backend:latest .
   docker tag market-intel-backend:latest 907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest
   docker push 907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest
   aws ecs update-service --cluster market-intel-cluster --service market-intel-backend-service --force-new-deployment --region us-east-1
   ```

4. **Monitor**: Check logs
   ```bash
   aws logs tail /ecs/market-intel-backend --region us-east-1 --since 5m --follow
   ```

5. **End Session**: Scale down to save costs
   ```bash
   aws ecs update-service --cluster market-intel-cluster --service market-intel-backend-service --desired-count 0 --region us-east-1
   ```

---

## 🔐 Environment Variables

Located in ECS Task Definition (market-intel-backend:6):

- `DATABASE_URL`: Supabase PostgreSQL connection string
- `SMTP_USERNAME`: Gmail for sending emails
- `SMTP_PASSWORD`: Gmail app password
- `JWT_SECRET_KEY`: For authentication
- `SECRET_KEY`: General app secret

To update environment variables:
1. Create new task definition revision with updated env vars
2. Update service to use new task definition

---

## 📝 Notes

- **Always scale down when not developing** to save ~$13-15/month
- **Scheduled task works independently** of service desired count
- **New deployments take 2-5 minutes** due to 1.5GB Docker image with FinBERT
- **Database fix (commit 75a14cb)** resolved the crash-loop issue
- **Crypto filtering (commit 8bcf124)** removes crypto tickers from emails
- **Current status (as of 2025-11-08)**: Scaled down, scheduled task enabled

---

## 🆘 Emergency Commands

### Complete Teardown (Delete Everything)
**⚠️ WARNING: This deletes all infrastructure!**

```bash
# Stop and delete service
aws ecs update-service --cluster market-intel-cluster --service market-intel-backend-service --desired-count 0 --region us-east-1
aws ecs delete-service --cluster market-intel-cluster --service market-intel-backend-service --region us-east-1

# Delete scheduled rule
aws events remove-targets --rule daily-market-digest --ids 1 --region us-east-1
aws events delete-rule --name daily-market-digest --region us-east-1

# Delete cluster (after services are gone)
aws ecs delete-cluster --cluster market-intel-cluster --region us-east-1
```

**Note**: ECR images and task definitions remain (minimal cost). Delete manually if needed.

---

Last Updated: 2025-11-08
