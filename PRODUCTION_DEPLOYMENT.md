# Production Deployment - Market Intelligence Platform

## Deployment Status

**Date**: October 14, 2025
**Status**: ✅ Deployed to AWS
**ECR Repository**: `907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest`
**ECS Cluster**: `market-intel-cluster`

---

## What Was Deployed

### Infrastructure
- ✅ **ECR Repository**: market-intel-backend
- ✅ **ECS Cluster**: market-intel-cluster (us-east-1)
- ✅ **CloudWatch Logs**: /ecs/market-intel
- ✅ **Docker Image**: Built and pushed successfully

### Services
1. **Backend API** (FastAPI)
   - Daily digest generation
   - Email delivery service
   - User authentication
   - Digest API endpoints

2. **Scheduled Workflows** (GitHub Actions)
   - Daily digest: 6:30 AM AZ Time
   - Market analysis: 7:00 AM AZ Time

---

## Production URLs

### API Endpoints
Once deployed with ECS Service or App Runner, you'll have:
- **Health Check**: `https://your-domain.com/health`
- **API Docs**: `https://your-domain.com/docs`
- **Daily Digest**: `https://your-domain.com/api/v1/digest/daily`

---

## Email Configuration

The system is configured to send daily emails via SMTP. Set these environment variables:

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
EMAIL_FROM=noreply@marketintel.com
EMAIL_FROM_NAME=Market Intelligence Platform
DIGEST_RECIPIENT_EMAIL=your@email.com
```

---

## GitHub Actions Workflows

Two workflows are configured but **disabled by default** (commented out schedule):

### 1. Daily Digest (`.github/workflows/daily-digest.yml`)
- **Schedule**: 6:30 AM Arizona Time (1:30 PM UTC)
- **Runs**: Monday-Friday
- **Action**: Generates and emails daily market digest

### 2. Scheduled Analysis (`.github/workflows/scheduled-analysis.yml`)
- **Schedule**: 7:00 AM Arizona Time (2:00 PM UTC)
- **Runs**: Monday-Friday
- **Action**: Full market analysis with email

**To Enable**: Uncomment the `schedule:` section in each workflow file.

---

## Manual Testing

### Test Digest Generation Locally
```bash
cd backend
python scripts/send_daily_digest.py --email your@email.com
```

### Test via GitHub Actions
1. Go to **Actions** tab
2. Select "Daily Market Intelligence Digest"
3. Click "Run workflow"
4. Enter your email
5. Click "Run workflow"

---

## Next Steps for Full Production

### Option A: ECS Service with Application Load Balancer
```bash
# 1. Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# 2. Create application load balancer
aws elbv2 create-load-balancer \
  --name market-intel-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx

# 3. Create ECS service
aws ecs create-service \
  --cluster market-intel-cluster \
  --service-name market-intel-service \
  --task-definition market-intel-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...
```

### Option B: AWS App Runner (Simpler)
```bash
# Create App Runner service
aws apprunner create-service \
  --service-name market-intel-api \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "DATABASE_URL": "your-db-url",
          "SECRET_KEY": "your-secret"
        }
      }
    },
    "AutoDeploymentsEnabled": true
  }'
```

### Option C: Use Existing Trade-Ideas Infrastructure
Since trade-ideas-cluster exists, you can:
1. Update the task definition with market-intel image
2. Deploy to existing cluster
3. Keep same scheduled workflows

---

## Monitoring

### CloudWatch Logs
```bash
# View recent logs
aws logs tail /ecs/market-intel --follow

# Filter for errors
aws logs filter-log-events \
  --log-group-name /ecs/market-intel \
  --filter-pattern ERROR
```

### ECS Task Status
```bash
# List running tasks
aws ecs list-tasks --cluster market-intel-cluster

# Describe task
aws ecs describe-tasks \
  --cluster market-intel-cluster \
  --tasks TASK_ARN
```

---

## Costs

### Estimated Monthly Costs (Low Usage)
- **ECS Fargate** (1 task, 0.25 vCPU, 0.5 GB): ~$5/month
- **ECR Storage** (1 image): ~$0.10/month
- **CloudWatch Logs** (1 GB): ~$0.50/month
- **Data Transfer**: ~$1/month
- **SMTP (Gmail)**: Free (500/day limit)

**Total**: ~$7/month for development
**Total**: ~$50/month for production (with load balancer, auto-scaling)

---

## Security Checklist

- [ ] Rotate SECRET_KEY in production
- [ ] Use AWS Secrets Manager for credentials
- [ ] Enable HTTPS with SSL certificate
- [ ] Configure security groups (allow only HTTPS)
- [ ] Set up IAM roles with least privilege
- [ ] Enable CloudWatch alarms for errors
- [ ] Configure backup for database
- [ ] Set up DDoS protection with CloudFront

---

## Troubleshooting

### Docker Build Fails
- Check requirements.txt for conflicts
- Run `docker build` locally first
- Check Docker logs: `docker logs <container-id>`

### ECS Task Fails
- Check CloudWatch logs: `aws logs tail /ecs/market-intel`
- Verify environment variables in task definition
- Check security group allows outbound SMTP (port 587)

### Email Not Sending
- Verify SMTP credentials
- Check Gmail app password is correct
- Test SMTP connection: `telnet smtp.gmail.com 587`
- Check CloudWatch logs for email errors

---

## Rollback Plan

If issues occur:
```bash
# Stop ECS tasks
aws ecs update-service \
  --cluster market-intel-cluster \
  --service market-intel-service \
  --desired-count 0

# Deploy previous image version
docker pull 907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:previous
docker tag ... :latest
docker push ...
```

---

## Support

- **CloudWatch Logs**: `/ecs/market-intel`
- **GitHub Issues**: [Report issues](https://github.com/tuxninja/market-intel-platform/issues)
- **Documentation**: See EMAIL_SETUP.md, README.md

---

**Deployment completed**: October 14, 2025
**Docker image pushed**: ✅
**ECS cluster created**: ✅
**Ready for service deployment**: ✅
