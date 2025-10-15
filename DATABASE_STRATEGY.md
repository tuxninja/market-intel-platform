# Database Strategy & Recommendations

## TL;DR: Start with Supabase, Migrate to RDS When Needed

**Recommended Path:**
1. **Now → 1K users**: Supabase (free tier)
2. **1K → 10K users**: Supabase Pro ($25/month)
3. **10K+ users**: AWS RDS (better AWS integration)

---

## Why Supabase for MVP/Launch

### ✅ Pros

1. **Free Tier is Generous**
   - 500 MB database
   - Unlimited API requests
   - 50,000 monthly active users
   - 2 GB bandwidth
   - **Perfect for MVP/launch**

2. **PostgreSQL + Extras**
   - Real PostgreSQL (not a fork)
   - Built-in Auth (could replace your JWT system)
   - Real-time subscriptions (websockets)
   - Auto-generated REST API
   - Storage for user uploads

3. **Developer Experience**
   - SQL editor in dashboard
   - Automatic backups
   - Point-in-time recovery (Pro tier)
   - Easy migrations
   - Great documentation

4. **Fast Setup**
   - 2 minutes to create
   - Connection string immediately available
   - No infrastructure management

5. **AWS-Compatible**
   - Uses standard PostgreSQL
   - Easy migration path to RDS
   - Connection pooling built-in

### ⚠️ Cons

1. **Not in Your AWS Account**
   - Data lives in Supabase infrastructure
   - Slight network latency (but minimal)
   - Less control over backups/security

2. **Scaling Limits**
   - Free tier: 500 MB storage
   - Need to upgrade at scale
   - Not ideal for millions of users

---

## When to Migrate to AWS RDS

### Migrate When You Hit:

1. **Technical Limits**
   - More than 500 MB data (free tier)
   - Need more than 2 GB bandwidth/month
   - Require advanced PostgreSQL extensions
   - Need database in same AWS VPC as App Runner

2. **Business Reasons**
   - Enterprise compliance requirements
   - Need data in specific AWS region
   - Require private networking
   - Want unified AWS billing
   - Need custom backup schedules

3. **Scale Indicators**
   - 10,000+ active users
   - High-frequency data writes
   - Need read replicas
   - Require 99.95%+ uptime SLA

---

## Migration Path: Supabase → RDS

The migration is straightforward because both are PostgreSQL:

### Step 1: Create RDS Instance

```bash
aws rds create-db-instance \
  --db-instance-identifier market-intel-db \
  --db-instance-class db.t3.small \
  --engine postgres \
  --engine-version 15.4 \
  --master-username admin \
  --master-user-password YOUR_SECURE_PASSWORD \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-YOUR_SG \
  --db-subnet-group-name your-subnet-group \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00" \
  --preferred-maintenance-window "mon:04:00-mon:05:00"
```

### Step 2: Export from Supabase

```bash
# From Supabase dashboard, get connection string
# Then dump database
pg_dump "postgresql://user:pass@db.PROJECTID.supabase.co:5432/postgres" \
  --format=custom \
  --file=supabase_backup.dump
```

### Step 3: Import to RDS

```bash
# Restore to RDS
pg_restore \
  --host=market-intel-db.ABC123.us-east-1.rds.amazonaws.com \
  --username=admin \
  --dbname=market_intel \
  --no-owner \
  --no-acl \
  supabase_backup.dump
```

### Step 4: Update Environment Variables

```bash
# Old (Supabase)
DATABASE_URL=postgresql://user:pass@db.PROJECTID.supabase.co:5432/postgres

# New (RDS)
DATABASE_URL=postgresql://admin:pass@market-intel-db.ABC123.us-east-1.rds.amazonaws.com:5432/market_intel
```

### Step 5: Zero-Downtime Cutover

1. Set up RDS replication from Supabase (using logical replication)
2. Let it sync for a few hours
3. Put app in maintenance mode (5 minutes)
4. Do final sync
5. Switch DATABASE_URL to RDS
6. Restart app
7. Monitor for issues

**Total downtime: ~5 minutes**

---

## Cost Comparison

### Supabase

| Tier | Storage | Users | Cost |
|------|---------|-------|------|
| Free | 500 MB | 50K MAU | $0/mo |
| Pro | 8 GB | Unlimited | $25/mo |
| Team | 100 GB | Unlimited | $599/mo |

### AWS RDS

| Instance | vCPU | RAM | Storage | Cost |
|----------|------|-----|---------|------|
| db.t3.micro | 2 | 1 GB | 20 GB | ~$15/mo |
| db.t3.small | 2 | 2 GB | 20 GB | ~$30/mo |
| db.t3.medium | 2 | 4 GB | 100 GB | ~$70/mo |
| db.r6g.large | 2 | 16 GB | 100 GB | ~$150/mo |

**Additional AWS RDS Costs:**
- Backup storage: ~$0.095/GB-month
- Data transfer: $0.09/GB (out of AWS)
- Multi-AZ: Double the instance cost

---

## Hybrid Approach (Advanced)

Once you scale, you could use **both**:

```
┌─────────────────┐
│   App Runner    │
│   (Backend)     │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
    ┌────▼────┐      ┌────▼────┐
    │   RDS   │      │Supabase │
    │(Primary)│      │(Analytics)│
    │  Write  │      │   Read   │
    └─────────┘      └──────────┘
```

- **RDS**: Transactional data (users, signals, subscriptions)
- **Supabase**: Analytics, real-time features, public API

---

## My Recommendation

### For Your Current Stage: **Supabase**

**Why:**
1. **Free** - No cost until you have users
2. **Fast** - Deploy in 2 minutes
3. **Full-featured** - PostgreSQL + extras
4. **Easy migration** - Standard PostgreSQL, moves to RDS easily
5. **No lock-in** - You own the data, SQL is portable

### Start with Supabase, Plan Migration at:
- **500 MB storage used** (free tier limit)
- **10K+ active users** (performance needs)
- **Series A funding** (enterprise requirements)

---

## Setup Instructions

### Option 1: Supabase (Recommended for Now)

```bash
# 1. Sign up at https://supabase.com
# 2. Create new project
# 3. Copy connection string from Settings > Database
# 4. Use in your app:

DATABASE_URL=postgresql://postgres.PROJECTID:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:5432/postgres
```

### Option 2: AWS RDS (For Later)

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier market-intel-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YOUR_SECURE_PASSWORD \
  --allocated-storage 20

# Get endpoint
aws rds describe-db-instances \
  --db-instance-identifier market-intel-db \
  --query 'DBInstances[0].Endpoint.Address'

# Use in app
DATABASE_URL=postgresql://admin:pass@market-intel-db.ABC123.us-east-1.rds.amazonaws.com:5432/market_intel
```

---

## Decision Tree

```
Are you launching/MVP?
│
├─ YES → Supabase (Free, Fast)
│
└─ NO → Do you have 10K+ users?
    │
    ├─ YES → AWS RDS (Performance, Control)
    │
    └─ NO → Do you have strict compliance needs?
        │
        ├─ YES → AWS RDS (SOC 2, HIPAA, etc.)
        │
        └─ NO → Supabase (Save money)
```

---

## Next Action

**For immediate deployment:**

1. **Create Supabase project** (2 minutes)
   ```
   https://supabase.com/dashboard/projects
   ```

2. **Get connection string**
   - Settings > Database > Connection String
   - Copy the "Session mode" string

3. **Update App Runner environment**
   ```bash
   DATABASE_URL=postgresql://postgres.PROJECTID:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:5432/postgres
   ```

4. **Deploy and test**

5. **Monitor usage** in Supabase dashboard

6. **Migrate to RDS** when you hit 500 MB or 10K users

---

## Summary

| Feature | Supabase | AWS RDS |
|---------|----------|---------|
| **Setup Time** | 2 minutes | 10-15 minutes |
| **Free Tier** | ✅ Very generous | ❌ No free tier |
| **Min Cost** | $0/mo | ~$15/mo |
| **Max Scale** | ~100K users | Millions+ |
| **AWS Integration** | ⚠️ External | ✅ Native |
| **Migration Difficulty** | N/A | Easy (same PostgreSQL) |
| **Best For** | MVP/Launch | Enterprise/Scale |

**My Advice:** Start with Supabase free tier, migrate to RDS when you have revenue to support it. This gives you fastest time-to-market with lowest risk.
