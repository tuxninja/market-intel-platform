#!/bin/bash
#
# Test ECS Digest Email Delivery
# Runs the market intelligence digest task manually to test email delivery
#

set -e

# Check if email provided
if [ -z "$1" ]; then
    echo "Usage: $0 <your@email.com> [max-items] [hours-lookback]"
    echo
    echo "Examples:"
    echo "  $0 your@email.com"
    echo "  $0 your@email.com 30"
    echo "  $0 your@email.com 30 48"
    exit 1
fi

EMAIL="$1"
MAX_ITEMS="${2:-20}"
HOURS_LOOKBACK="${3:-24}"

# Configuration
AWS_REGION="us-east-1"
CLUSTER="market-intel-cluster"
TASK_DEFINITION="market-intel-task"

echo "======================================================================"
echo "Testing Market Intelligence Digest Email"
echo "======================================================================"
echo "Recipient:     $EMAIL"
echo "Max Items:     $MAX_ITEMS"
echo "Hours Lookback: $HOURS_LOOKBACK"
echo "Cluster:       $CLUSTER"
echo "Task Def:      $TASK_DEFINITION"
echo "======================================================================"
echo

# Get VPC and subnet info
echo "Getting AWS network configuration..."
VPC_ID=$(aws ec2 describe-vpcs --filters Name=is-default,Values=true --query 'Vpcs[0].VpcId' --output text)
SUBNET_ID=$(aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC_ID --query 'Subnets[0].SubnetId' --output text)

echo "VPC ID:    $VPC_ID"
echo "Subnet ID: $SUBNET_ID"
echo

# Get or create security group
echo "Checking security group..."
SG_ID=$(aws ec2 describe-security-groups \
    --filters Name=group-name,Values=market-intel-sg \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null || echo "None")

if [[ "$SG_ID" == "None" ]]; then
    echo "Creating security group..."
    SG_ID=$(aws ec2 create-security-group \
        --group-name market-intel-sg \
        --description "Market Intelligence Platform" \
        --vpc-id $VPC_ID \
        --query 'GroupId' \
        --output text)

    # Add outbound rules
    aws ec2 authorize-security-group-egress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0

    aws ec2 authorize-security-group-egress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0

    aws ec2 authorize-security-group-egress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 587 \
        --cidr 0.0.0.0/0

    echo "✅ Security group created: $SG_ID"
else
    echo "✅ Using existing security group: $SG_ID"
fi

# Build command
COMMAND="[\"python\",\"scripts/send_daily_digest.py\",\"--email\",\"$EMAIL\",\"--max-items\",\"$MAX_ITEMS\",\"--hours-lookback\",\"$HOURS_LOOKBACK\"]"

echo
echo "Running ECS task..."
echo "Command: python scripts/send_daily_digest.py --email $EMAIL --max-items $MAX_ITEMS --hours-lookback $HOURS_LOOKBACK"
echo

# Run task
TASK_ARN=$(aws ecs run-task \
    --cluster $CLUSTER \
    --task-definition $TASK_DEFINITION \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_ID],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" \
    --overrides "{\"containerOverrides\":[{\"name\":\"market-intel-container\",\"command\":$COMMAND}]}" \
    --query 'tasks[0].taskArn' \
    --output text)

echo "✅ Task started: $TASK_ARN"
TASK_ID=$(basename $TASK_ARN)
echo "Task ID: $TASK_ID"
echo

# Wait for task to complete
echo "Waiting for task to complete (this may take 2-5 minutes)..."
echo

for i in {1..60}; do
    STATUS=$(aws ecs describe-tasks \
        --cluster $CLUSTER \
        --tasks $TASK_ARN \
        --query 'tasks[0].lastStatus' \
        --output text)

    echo "[$i/60] Task status: $STATUS"

    if [[ "$STATUS" == "STOPPED" ]]; then
        EXIT_CODE=$(aws ecs describe-tasks \
            --cluster $CLUSTER \
            --tasks $TASK_ARN \
            --query 'tasks[0].containers[0].exitCode' \
            --output text)

        echo
        echo "Task completed with exit code: $EXIT_CODE"

        if [[ "$EXIT_CODE" == "0" ]]; then
            echo
            echo "======================================================================"
            echo "✅ SUCCESS! Digest email sent successfully!"
            echo "======================================================================"
            echo
            echo "📧 Check your inbox: $EMAIL"
            echo "📧 Subject: Daily Market Intelligence Digest - [Date]"
            echo
            echo "If you don't see it:"
            echo "  1. Check spam/junk folder"
            echo "  2. Wait a few more minutes"
            echo "  3. Check logs below for errors"
            echo
        else
            echo
            echo "======================================================================"
            echo "❌ FAILED! Task exited with error code: $EXIT_CODE"
            echo "======================================================================"
            echo
            echo "Common issues:"
            echo "  - SMTP credentials not configured"
            echo "  - Email address invalid"
            echo "  - Network connectivity issues"
            echo
            echo "Check logs below for details:"
            echo
        fi
        break
    fi

    if [[ $i -eq 60 ]]; then
        echo
        echo "⚠️  Task did not complete within 10 minutes"
        echo "   This is unusual. Check CloudWatch logs for details."
        break
    fi

    sleep 10
done

# Show logs
echo
echo "======================================================================"
echo "Task Logs (last 50 lines):"
echo "======================================================================"
echo

aws logs get-log-events \
    --log-group-name "/ecs/market-intel" \
    --log-stream-name "ecs/market-intel-container/$TASK_ID" \
    --query 'events[-50:].message' \
    --output text 2>/dev/null || echo "No logs available yet (container may still be starting)"

echo
echo "======================================================================"
echo "To view full logs:"
echo "======================================================================"
echo "aws logs tail /ecs/market-intel --follow --region us-east-1"
echo
