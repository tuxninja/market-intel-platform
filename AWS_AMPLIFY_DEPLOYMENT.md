# Deploy Frontend to AWS Amplify

## Quick Start (5 Minutes)

### Step 1: Go to AWS Amplify Console
1. Open https://console.aws.amazon.com/amplify
2. Click **"New app"** → **"Host web app"**

### Step 2: Connect GitHub
1. Select **GitHub** as source
2. Click **Authorize AWS Amplify** (if first time)
3. Select repository: **`market-intel-platform`**
4. Select branch: **`main`**
5. Click **Next**

### Step 3: Configure Build Settings
1. **App name**: `market-intel-platform`
2. **Monorepo**: Detected ✓
3. **Root directory**: `frontend`
4. Build settings (auto-detected):
   ```yaml
   version: 1
   applications:
     - frontend:
         phases:
           preBuild:
             commands:
               - npm ci
           build:
             commands:
               - npm run build
         artifacts:
           baseDirectory: .next
           files:
             - '**/*'
         cache:
           paths:
             - node_modules/**/*
         appRoot: frontend
   ```
5. Click **Next**

### Step 4: Add Environment Variables
Click **Advanced settings** → **Add environment variable**

```
NEXT_PUBLIC_API_URL = https://qwdhybryip.us-east-1.awsapprunner.com
```

Click **Next**

### Step 5: Review and Deploy
1. Review settings
2. Click **Save and deploy**
3. Wait 3-5 minutes for deployment

### Step 6: Get Your URL
After deployment completes:
- **URL**: `https://main.XXXXX.amplifyapp.com`
- Custom domain available in settings

---

## Update CORS in App Runner

After frontend deploys, add Amplify URL to CORS:

```bash
# Get your Amplify URL from console
# Then update App Runner environment variable:

aws apprunner update-service \
  --service-arn arn:aws:apprunner:us-east-1:907391580367:service/market-intel-api/b6383d469d8c4844867dcb5f565e9a3d \
  --region us-east-1 \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "CORS_ORIGINS": "http://localhost:3000,https://main.XXXXX.amplifyapp.com"
        }
      }
    }
  }'
```

Or update in AWS Console:
1. Go to App Runner console
2. Select `market-intel-api`
3. Configuration → Edit
4. Update `CORS_ORIGINS` environment variable
5. Save → Deploy

---

## Automatic Deployments

Once connected:
- ✅ Every `git push` to `main` → auto-deploys
- ✅ Every PR → gets preview URL
- ✅ Build logs in Amplify console
- ✅ Rollback available

---

## Costs

**AWS Amplify Pricing**:
- Build time: $0.01/minute (typically 2-3 min/deploy = $0.02-0.03)
- Hosting: $0.15/GB stored + $0.15/GB served
- **Typical monthly cost**: $1-5

**Free Tier** (12 months):
- 1,000 build minutes/month
- 15 GB data served/month
- 5 GB storage

---

## Alternative: AWS CLI Deployment

If you prefer CLI over console:

```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Configure
amplify configure

# Initialize
cd /Users/jasonriedel/PyCharmProjects/market-intel-platform/frontend
amplify init

# Add hosting
amplify add hosting

# Publish
amplify publish
```

---

## Troubleshooting

### Build Fails
- Check build logs in Amplify console
- Verify Node.js version matches local (18.x)
- Check environment variables are set

### CORS Errors
- Ensure Amplify URL is in App Runner CORS_ORIGINS
- Clear browser cache
- Check browser console for exact error

### Can't Find Repository
- Verify GitHub authorization
- Check repository permissions
- Try disconnecting and reconnecting GitHub

---

## Custom Domain (Optional)

To use your own domain:

1. Amplify Console → Domain management
2. Add domain
3. Follow DNS configuration steps
4. Wait for SSL certificate (5-10 minutes)

Example: `app.yourdomain.com` → your Amplify app

---

## Comparison: Amplify vs Others

| Feature | Amplify | App Runner | S3+CloudFront |
|---------|---------|------------|---------------|
| **Setup Time** | 5 min | 15 min | 30 min |
| **Monthly Cost** | $1-5 | $5-10 | $0.50-2 |
| **Auto Deploy** | ✅ Yes | ⚠️ Manual | ❌ No |
| **CDN** | ✅ Built-in | ❌ No | ✅ CloudFront |
| **HTTPS** | ✅ Auto | ✅ Auto | ⚠️ Manual |
| **Best For** | Next.js | APIs | Static sites |

**Recommendation**: Use Amplify for frontend, App Runner for backend.
