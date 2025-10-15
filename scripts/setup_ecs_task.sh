#!/bin/bash
#
# Setup ECS Task Definition for Market Intelligence Platform
# This script creates the ECS task definition needed for scheduled email digests
#

set -e  # Exit on error

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
TASK_FAMILY="market-intel-task"
ECR_REPO="market-intel-backend"
ECR_IMAGE="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:latest"
EXECUTION_ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/ecsTaskExecutionRole"

echo "======================================================================"
echo "Setting up ECS Task Definition for Market Intelligence Platform"
echo "======================================================================"
echo "AWS Account: $AWS_ACCOUNT_ID"
echo "Region:      $AWS_REGION"
echo "Task Family: $TASK_FAMILY"
echo "ECR Image:   $ECR_IMAGE"
echo "======================================================================"
echo

# Check if execution role exists, create if not
echo "Checking for ecsTaskExecutionRole..."
if ! aws iam get-role --role-name ecsTaskExecutionRole &>/dev/null; then
    echo "Creating ecsTaskExecutionRole..."

    # Create role
    aws iam create-role \
        --role-name ecsTaskExecutionRole \
        --assume-role-policy-document '{
          "Version": "2012-10-17",
          "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
            "Action": "sts:AssumeRole"
          }]
        }'

    # Attach policy
    aws iam attach-role-policy \
        --role-name ecsTaskExecutionRole \
        --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

    echo "✅ ecsTaskExecutionRole created"
    echo "Waiting 10 seconds for IAM propagation..."
    sleep 10
else
    echo "✅ ecsTaskExecutionRole already exists"
fi

# Create CloudWatch log group if it doesn't exist
echo
echo "Checking CloudWatch log group..."
if ! aws logs describe-log-groups --log-group-name-prefix "/ecs/market-intel" --region $AWS_REGION | grep -q "/ecs/market-intel"; then
    echo "Creating CloudWatch log group..."
    aws logs create-log-group \
        --log-group-name "/ecs/market-intel" \
        --region $AWS_REGION
    echo "✅ Log group created"
else
    echo "✅ Log group already exists"
fi

# Create task definition JSON
echo
echo "Creating task definition..."
cat > /tmp/market-intel-task-definition.json <<EOF
{
  "family": "${TASK_FAMILY}",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "${EXECUTION_ROLE_ARN}",
  "containerDefinitions": [
    {
      "name": "market-intel-container",
      "image": "${ECR_IMAGE}",
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/market-intel",
          "awslogs-region": "${AWS_REGION}",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "environment": [
        {
          "name": "APP_NAME",
          "value": "Market Intelligence Platform"
        },
        {
          "name": "ENVIRONMENT",
          "value": "production"
        },
        {
          "name": "DEBUG",
          "value": "false"
        },
        {
          "name": "DATABASE_URL",
          "value": "postgresql://postgres:#Marjynh8338@db.urbxneuanylgeshiqmgi.supabase.co:5432/postgres"
        },
        {
          "name": "SECRET_KEY",
          "value": "prod-mkt-intel-2025-secure-key-change-in-console-later"
        },
        {
          "name": "SMTP_SERVER",
          "value": "smtp.gmail.com"
        },
        {
          "name": "SMTP_PORT",
          "value": "587"
        },
        {
          "name": "SMTP_USE_TLS",
          "value": "true"
        }
      ],
      "command": ["python", "scripts/send_daily_digest.py", "--email", "placeholder@example.com"]
    }
  ]
}
EOF

# Register task definition
echo
echo "Registering ECS task definition..."
TASK_DEF_ARN=$(aws ecs register-task-definition \
    --cli-input-json file:///tmp/market-intel-task-definition.json \
    --region $AWS_REGION \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text)

echo "✅ Task definition registered: $TASK_DEF_ARN"

# Clean up
rm /tmp/market-intel-task-definition.json

echo
echo "======================================================================"
echo "✅ ECS Task Definition Setup Complete!"
echo "======================================================================"
echo
echo "Task Definition ARN: $TASK_DEF_ARN"
echo "Task Family:         $TASK_FAMILY"
echo "CPU:                 512 (0.5 vCPU)"
echo "Memory:              1024 MB (1 GB)"
echo "Log Group:           /ecs/market-intel"
echo
echo "======================================================================"
echo "Next Steps:"
echo "======================================================================"
echo
echo "1. Configure GitHub Secrets:"
echo "   Go to: https://github.com/tuxninja/market-intel-platform/settings/secrets/actions"
echo
echo "   Add these secrets:"
echo "   - DIGEST_RECIPIENT_EMAIL = your@email.com"
echo "   - SMTP_USERNAME = your-email@gmail.com"
echo "   - SMTP_PASSWORD = your-app-password"
echo
echo "2. Test the task manually:"
echo "   ./scripts/test_ecs_digest.sh your@email.com"
echo
echo "3. Enable GitHub Actions schedule:"
echo "   Edit .github/workflows/daily-digest.yml"
echo "   Uncomment the 'schedule' section"
echo "   Commit and push"
echo
echo "4. Monitor logs:"
echo "   aws logs tail /ecs/market-intel --follow --region us-east-1"
echo
echo "======================================================================"
