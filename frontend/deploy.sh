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

echo "✅ Image pushed to ECR successfully!"
echo "📝 Next steps:"
echo "  1. Create App Runner service (if not exists)"
echo "  2. Or trigger deployment if service exists"
echo ""
echo "🌐 Check App Runner console: https://console.aws.amazon.com/apprunner"
