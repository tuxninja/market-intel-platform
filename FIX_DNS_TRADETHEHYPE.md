# Fix tradethehype.com DNS Issue

**Problem**: tradethehype.com shows "webpage not found" even though DNS A record points to App Runner URL

**Cause**: App Runner requires explicit custom domain configuration in AWS, not just DNS records.

---

## Solution: Configure Custom Domain in AWS App Runner

### Step 1: Add Custom Domain in App Runner Console

1. Go to AWS App Runner console: https://console.aws.amazon.com/apprunner/
2. Click on your frontend service
3. Go to **Custom domains** tab
4. Click **Link domain**
5. Enter: `tradethehype.com` and `www.tradethehype.com`
6. AWS will provide validation records

### Step 2: Add Validation Records to DNS

App Runner will show something like:

```
_app-runner-challenge.tradethehype.com  CNAME  xyz123.awsapprunner.com
```

Add this to your DNS provider.

### Step 3: Wait for Validation

- Can take 5-15 minutes
- App Runner will show "Pending" then "Active"

### Step 4: Update DNS to App Runner Domain

Instead of A record alias, use **CNAME** record:

```
tradethehype.com  →  dvnzmpmkt3.us-east-1.awsapprunner.com
www               →  dvnzmpmkt3.us-east-1.awsapprunner.com
```

**Important**: Some DNS providers don't allow CNAME on root domain. Solutions:

1. **ALIAS record** (if provider supports it - Route 53, Cloudflare)
2. **ANAME record** (if provider supports it)
3. **Redirect www to non-www** and use CNAME for www only

---

## Alternative: Use CloudFlare (Recommended)

CloudFlare allows CNAME flattening for root domains.

### Steps:

1. Sign up at cloudflare.com (free)
2. Add `tradethehype.com` as a site
3. Update nameservers at your registrar to CloudFlare's
4. Add CNAME record in CloudFlare:
   ```
   tradethehype.com  →  dvnzmpmkt3.us-east-1.awsapprunner.com
   ```
5. CloudFlare automatically handles CNAME flattening

---

## Quick Check

```bash
# Check DNS propagation
dig tradethehype.com

# Check if App Runner is accessible
curl -I https://dvnzmpmkt3.us-east-1.awsapprunner.com

# Check custom domain once configured
curl -I https://tradethehype.com
```

---

## Current Status

Your frontend App Runner service is accessible at:
**https://dvnzmpmkt3.us-east-1.awsapprunner.com**

Once custom domain is linked in App Runner console, tradethehype.com will work.

---

*Note: This is separate from the ML backend deployment which is in progress.*
