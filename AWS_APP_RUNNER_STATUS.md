# AWS App Runner Deployment Status

## Current Status: NOT DEPLOYED

The backend API deployment to AWS App Runner encountered issues and has been cleaned up. No services are currently running.

## Issues Encountered

During deployment attempts, we resolved multiple issues:

1. ✅ **CORS Configuration** - Fixed pydantic-settings JSON parsing by changing `CORS_ORIGINS` from `list[str]` to `str`
2. ✅ **Email Validator** - Added `email-validator==2.1.0` to requirements.txt
3. ✅ **Docker Architecture** - Built for AMD64/x86_64 platform (App Runner requirement)
4. ✅ **Database Migrations** - Removed from Docker CMD (no database in stateless container)
5. ✅ **SQLAlchemy Model** - Renamed `Signal.metadata` to `Signal.extra_data` (reserved name conflict)

## To Deploy Successfully

### Prerequisites

1. **Production Database** - App Runner needs a real PostgreSQL database:
   ```bash
   # Option A: Use AWS RDS
   aws rds create-db-instance \
     --db-instance-identifier market-intel-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username admin \
     --master-user-password YOUR_SECURE_PASSWORD \
     --allocated-storage 20

   # Option B: Use Neon, Supabase, or other managed PostgreSQL
   ```

2. **Update Environment Variables** - Set proper `DATABASE_URL`:
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   ```

### Deployment Steps

1. **Ensure Latest Image is Built and Pushed**:
   ```bash
   cd /Users/jasonriedel/PyCharmProjects/market-intel-platform/backend

   # Build for AMD64
   docker buildx build --platform linux/amd64 \
     -t 907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest \
     --load .

   # Push to ECR
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin \
     907391580367.dkr.ecr.us-east-1.amazonaws.com

   docker push 907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest
   ```

2. **Create App Runner Service**:
   ```bash
   aws apprunner create-service \
     --service-name market-intel-api \
     --region us-east-1 \
     --source-configuration '{
       "ImageRepository": {
         "ImageIdentifier": "907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest",
         "ImageRepositoryType": "ECR",
         "ImageConfiguration": {
           "Port": "8000",
           "RuntimeEnvironmentVariables": {
             "APP_NAME": "Market Intelligence Platform",
             "ENVIRONMENT": "production",
             "DEBUG": "false",
             "SECRET_KEY": "GENERATE-SECURE-32-CHAR-SECRET",
             "DATABASE_URL": "postgresql://user:pass@YOUR-DB-HOST:5432/market_intel",
             "CORS_ORIGINS": "http://localhost:3000,https://YOUR-FRONTEND-DOMAIN.vercel.app",
             "SMTP_SERVER": "smtp.gmail.com",
             "SMTP_PORT": "587",
             "SMTP_USE_TLS": "true",
             "SMTP_USERNAME": "your-email@gmail.com",
             "SMTP_PASSWORD": "your-app-password"
           }
         }
       },
       "AuthenticationConfiguration": {
         "AccessRoleArn": "arn:aws:iam::907391580367:role/AppRunnerECRAccessRole"
       },
       "AutoDeploymentsEnabled": false
     }' \
     --health-check-configuration '{
       "Protocol": "HTTP",
       "Path": "/health",
       "Interval": 10,
       "Timeout": 5,
       "HealthyThreshold": 1,
       "UnhealthyThreshold": 5
     }' \
     --instance-configuration '{
       "Cpu": "1 vCPU",
       "Memory": "2 GB"
     }'
   ```

3. **Monitor Deployment**:
   ```bash
   # Check status
   aws apprunner list-services --region us-east-1

   # View logs
   aws logs tail /aws/apprunner/market-intel-api/SERVICE_ID/application --follow
   ```

## AWS Resources Created

- **ECR Repository**: `907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend`
- **IAM Role**: `AppRunnerECRAccessRole` (for ECR image access)
- **Docker Image**: Latest AMD64 build with all fixes

## Security Notes

- **GitGuardian Alert**: The `admin123` password in `backend/scripts/init_db.py:27` is a test script default - not a production secret
- **Production Secrets**: Use AWS Secrets Manager or environment variables
- **SECRET_KEY**: Generate a secure 32+ character key for production
- **SMTP Credentials**: Use app-specific passwords, not your main password

## Estimated Costs

- **App Runner**: ~$5-7/month (1 vCPU, 2GB RAM, minimal traffic)
- **RDS db.t3.micro**: ~$15/month
- **ECR Storage**: ~$0.10/month
- **Total**: ~$20-25/month for full production stack

## Next Steps

1. Set up production PostgreSQL database (RDS, Neon, or Supabase)
2. Update environment variables with real database URL
3. Generate secure SECRET_KEY
4. Deploy App Runner service
5. Test at `https://SERVICE-ID.us-east-1.awsapprunner.com`
6. Update frontend `.env.production` with API URL

## Support

- **AWS App Runner Docs**: https://docs.aws.amazon.com/apprunner/
- **ECR Repository**: Check `aws ecr describe-repositories`
- **Logs**: `aws logs tail /aws/apprunner/market-intel-api/SERVICE_ID/application`
