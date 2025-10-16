# Deployment Guide - AWS App Runner

**Infrastructure**: AWS Only (App Runner + ECR + Supabase)
**Cost**: ~$5-10/month total for both frontend and backend
**Date**: October 16, 2025

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                  AWS Cloud                       │
│                                                  │
│  ┌──────────────┐        ┌──────────────┐      │
│  │   ECR        │        │   ECR        │      │
│  │  (Backend)   │        │  (Frontend)  │      │
│  └──────┬───────┘        └──────┬───────┘      │
│         │                       │               │
│         ▼                       ▼               │
│  ┌──────────────┐        ┌──────────────┐      │
│  │ ECS Fargate  │◄──────►│ App Runner   │      │
│  │  (Backend)   │  API   │  (Frontend)  │      │
│  │              │        │              │      │
│  │ Port: 8000   │        │ Port: 3000   │      │
│  └──────┬───────┘        └──────────────┘      │
│         │                                       │
│         ▼                                       │
│  ┌──────────────┐                              │
│  │  EventBridge │                              │
│  │  (Cron Job)  │                              │
│  └──────────────┘                              │
└─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│    Supabase     │
│   PostgreSQL    │
└─────────────────┘
```

---

## 📦 Frontend Deployment (AWS App Runner)

### Option 1: Deploy via Docker Image (Recommended)

**Step 1: Build Docker Image**
```bash
cd frontend

# Build for linux/amd64 (required for AWS)
docker buildx build --platform linux/amd64 \
  -t 907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-frontend:latest \
  --load .
```

**Step 2: Push to ECR**
```bash
# Create ECR repository (first time only)
aws ecr create-repository \
  --repository-name market-intel-frontend \
  --region us-east-1

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  907391580367.dkr.ecr.us-east-1.amazonaws.com

# Push image
docker push 907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-frontend:latest
```

**Step 3: Create App Runner Service**
```bash
# Create service configuration file
cat > apprunner-service.json <<EOF
{
  "ServiceName": "market-intel-frontend",
  "SourceConfiguration": {
    "ImageRepository": {
      "ImageIdentifier": "907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-frontend:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "3000",
        "RuntimeEnvironmentVariables": {
          "NODE_ENV": "production",
          "NEXT_PUBLIC_API_URL": "https://YOUR-BACKEND-URL.com/api/v1",
          "NEXT_TELEMETRY_DISABLED": "1"
        }
      }
    },
    "AutoDeploymentsEnabled": true,
    "AuthenticationConfiguration": {
      "AccessRoleArn": "arn:aws:iam::907391580367:role/AppRunnerECRAccessRole"
    }
  },
  "InstanceConfiguration": {
    "Cpu": "0.25 vCPU",
    "Memory": "0.5 GB"
  },
  "HealthCheckConfiguration": {
    "Protocol": "HTTP",
    "Path": "/",
    "Interval": 10,
    "Timeout": 5,
    "HealthyThreshold": 1,
    "UnhealthyThreshold": 5
  }
}
EOF

# Create the service
aws apprunner create-service --cli-input-json file://apprunner-service.json
```

**Step 4: Get Service URL**
```bash
aws apprunner list-services --region us-east-1
# Output will show service URL: https://xxxxx.us-east-1.awsapprunner.com
```

### Option 2: Deploy via GitHub (Auto-Deploy on Push)

**Step 1: Create GitHub Connection**
```bash
# This creates a connection to GitHub
aws apprunner create-connection \
  --connection-name github-connection \
  --provider-type GITHUB
```

**Step 2: Create App Runner Service from GitHub**
```bash
aws apprunner create-service \
  --service-name market-intel-frontend \
  --source-configuration '{
    "CodeRepository": {
      "RepositoryUrl": "https://github.com/tuxninja/market-intel-platform",
      "SourceCodeVersion": {
        "Type": "BRANCH",
        "Value": "main"
      },
      "CodeConfiguration": {
        "ConfigurationSource": "API",
        "CodeConfigurationValues": {
          "Runtime": "NODEJS_18",
          "BuildCommand": "cd frontend && npm ci && npm run build",
          "StartCommand": "cd frontend && node server.js",
          "Port": "3000",
          "RuntimeEnvironmentVariables": {
            "NODE_ENV": "production",
            "NEXT_PUBLIC_API_URL": "https://YOUR-BACKEND-URL.com/api/v1"
          }
        }
      }
    },
    "AutoDeploymentsEnabled": true,
    "AuthenticationConfiguration": {
      "ConnectionArn": "YOUR-GITHUB-CONNECTION-ARN"
    }
  }' \
  --instance-configuration '{
    "Cpu": "0.25 vCPU",
    "Memory": "0.5 GB"
  }'
```

---

## 🔧 Environment Variables

### Frontend (.env.production)
```bash
NEXT_PUBLIC_API_URL=https://YOUR-BACKEND-URL.com/api/v1
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
```

### Backend (Already deployed - ECS task definition)
```bash
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:5432/postgres
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
JWT_SECRET_KEY=your-secret-key
```

---

## 💰 Cost Breakdown

### Frontend (App Runner):
- **Compute**: $0.007/vCPU-hour + $0.0008/GB-hour
- **0.25 vCPU + 0.5 GB**:
  - vCPU: 0.25 × 730 hrs × $0.007 = ~$1.28/month
  - Memory: 0.5 × 730 hrs × $0.0008 = ~$0.29/month
- **Provisioned instances**: 1 (minimum)
- **Total**: ~$1.50-3/month

### Backend (ECS Fargate):
- **Already deployed**: ~$1-5/month
- **No change**

### Database (Supabase):
- **Free tier**: $0/month

### **TOTAL MONTHLY COST**: ~$2.50-8/month

---

## 🚀 Quick Deploy Script

Create `frontend/deploy.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Deploying Market Intel Frontend to AWS App Runner..."

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="907391580367"
ECR_REPO="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/market-intel-frontend"
IMAGE_TAG="latest"

# Build Docker image
echo "📦 Building Docker image..."
docker buildx build --platform linux/amd64 \
  -t ${ECR_REPO}:${IMAGE_TAG} \
  --load .

# Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin ${ECR_REPO}

# Push to ECR
echo "⬆️  Pushing image to ECR..."
docker push ${ECR_REPO}:${IMAGE_TAG}

# Trigger App Runner deployment
echo "🔄 Triggering App Runner deployment..."
aws apprunner start-deployment \
  --service-arn $(aws apprunner list-services --query 'ServiceSummaryList[?ServiceName==`market-intel-frontend`].ServiceArn' --output text) \
  --region ${AWS_REGION}

echo "✅ Deployment initiated! Check App Runner console for status."
echo "🌐 URL: https://$(aws apprunner list-services --query 'ServiceSummaryList[?ServiceName==`market-intel-frontend`].ServiceUrl' --output text)"
```

Make executable and run:
```bash
chmod +x frontend/deploy.sh
./frontend/deploy.sh
```

---

## 🔍 Monitoring & Logs

### View App Runner Logs:
```bash
# Get service ARN
SERVICE_ARN=$(aws apprunner list-services \
  --query 'ServiceSummaryList[?ServiceName==`market-intel-frontend`].ServiceArn' \
  --output text)

# View logs in CloudWatch
aws logs tail /aws/apprunner/${SERVICE_ARN} --follow
```

### Check Service Status:
```bash
aws apprunner describe-service \
  --service-arn ${SERVICE_ARN} \
  --query 'Service.Status' \
  --output text
```

### App Runner Console:
https://console.aws.amazon.com/apprunner/home?region=us-east-1#/services

---

## 🔧 Troubleshooting

### Issue: Build fails with "Cannot find module"
**Solution**: Ensure all dependencies are in `package.json`
```bash
cd frontend
npm install
npm run build  # Test locally first
```

### Issue: App crashes immediately
**Solution**: Check logs for errors
```bash
aws logs tail /aws/apprunner/${SERVICE_ARN} --follow
```
Common causes:
- Missing environment variables
- Port not set to 3000
- `output: 'standalone'` not in next.config.js

### Issue: Can't connect to backend API
**Solution**: Verify `NEXT_PUBLIC_API_URL` environment variable
```bash
# Check current env vars
aws apprunner describe-service --service-arn ${SERVICE_ARN} \
  --query 'Service.SourceConfiguration.ImageRepository.ImageConfiguration.RuntimeEnvironmentVariables'
```

### Issue: Auto-deploy not working
**Solution**: Ensure Auto-Deployments enabled
```bash
aws apprunner update-service \
  --service-arn ${SERVICE_ARN} \
  --source-configuration '{"AutoDeploymentsEnabled": true}'
```

---

## 📊 Health Checks

App Runner automatically monitors:
- **HTTP health check**: GET /
- **Interval**: Every 10 seconds
- **Timeout**: 5 seconds
- **Unhealthy threshold**: 5 consecutive failures

If health check fails, App Runner automatically restarts the service.

---

## 🔄 CI/CD Pipeline (Future)

### GitHub Actions Workflow (.github/workflows/deploy-frontend.yml):
```yaml
name: Deploy Frontend to App Runner

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Login to Amazon ECR
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build and push Docker image
        working-directory: ./frontend
        run: |
          docker buildx build --platform linux/amd64 \
            -t 907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-frontend:latest \
            --push .

      - name: Deploy to App Runner
        run: |
          SERVICE_ARN=$(aws apprunner list-services \
            --query 'ServiceSummaryList[?ServiceName==`market-intel-frontend`].ServiceArn' \
            --output text)
          aws apprunner start-deployment --service-arn $SERVICE_ARN
```

---

## 🎯 Post-Deployment Checklist

- [ ] Frontend accessible at App Runner URL
- [ ] News articles display correctly
- [ ] Market Snapshot shows VIX and indices
- [ ] Login/signup works
- [ ] Digest page loads signals
- [ ] Expandable sections work
- [ ] Links open in new tab
- [ ] Mobile responsive
- [ ] SSL certificate active
- [ ] Health checks passing

---

## 🔗 Useful Links

- **App Runner Console**: https://console.aws.amazon.com/apprunner
- **ECR Console**: https://console.aws.amazon.com/ecr
- **CloudWatch Logs**: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups
- **App Runner Pricing**: https://aws.amazon.com/apprunner/pricing/
- **App Runner Docs**: https://docs.aws.amazon.com/apprunner/

---

**Next Steps**: Deploy frontend, test with backend, move to Phase 3 (Stripe)!
