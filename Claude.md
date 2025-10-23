# Claude Code Session Notes - TradeTheHype

**Last Updated**: October 22, 2025
**Project**: TradeTheHype (AI-Powered Trading Signals SaaS)

---

## 🎯 Project Overview

**Goal**: Build a $1K MRR SaaS product providing AI-powered trading signals
**Timeline**: 16-20 weeks part-time (10 hrs/week)
**Infrastructure**: AWS + Supabase ONLY (no Vercel, Netlify, etc.)
**Cost**: < $20/month total (increased from $10 due to ML)

---

## ✅ Current Progress (65% Complete)

### Phase 0: Pre-Development ✅
- Repository set up
- Development environment configured

### Phase 1: Real Market Data Integration ✅
- **Backend Services Created**:
  - `market_data_service.py` (399 lines) - yfinance, RSI, MACD, EMAs, volume
  - `news_service.py` (428 lines) - 5 RSS feeds, VADER + TextBlob sentiment
  - `signal_generator.py` (541 lines) - 60/40 technical/news scoring
  - Updated `digest_service.py` - real signals instead of demo

- **News Articles Feature**:
  - Signals include `news_articles` field (up to 5 per signal)
  - Email template displays news with sentiment emojis
  - Backend deployed to ECS (Docker image in ECR)

### Phase 2: Web Dashboard ✅
- **Frontend Enhancements**:
  - News articles display in DigestCard component
  - Market Snapshot widget (VIX, SPY, DIA, QQQ)
  - Enhanced signal detail view with expandable sections
  - TypeScript types updated for NewsArticle
  - Dark Robinhood theme, responsive design

- **Deployment Configuration**:
  - App Runner configuration (apprunner.yaml)
  - Docker build script (deploy.sh)
  - Deployment guide (DEPLOYMENT_GUIDE.md)
  - next.config.js updated with standalone output

### Phase 2.5: ML-Powered Signal System ✅ (MAJOR UPGRADE!)
- **Event-Driven Signal Generation**:
  - Replaced watchlist-based with news-driven signals
  - Only generates signals when breaking news occurs (<6 hours old)
  - Eliminates stale price data and repeated recommendations

- **Machine Learning Integration**:
  - FinBERT sentiment analysis (85% accuracy vs 65% VADER)
  - Batch processing for efficiency
  - Confidence scoring for every signal

- **Smart Components**:
  - `ml_sentiment_service.py` - FinBERT ML model
  - `symbol_extractor_service.py` - Advanced ticker extraction (80+ company names)
  - `news_driven_signal_generator.py` - Event-driven engine (472 lines)
  - `signal_history` table - Prevents duplicate signals for 7 days

- **Production Ready**:
  - Async/await throughout (AsyncSession support)
  - Docker image with pre-cached FinBERT model (~1.5GB)
  - Automated deployment script (`deploy_ml_signals.sh`)
  - Graceful fallback: ML → Technical → Demo

- **Documentation**:
  - `ML_SIGNAL_UPGRADE.md` (630 lines) - Technical deep dive
  - `SIGNAL_UPGRADE_SUMMARY.md` - Executive summary
  - `ML_PRODUCTION_DEPLOYMENT.md` - Deployment guide
  - Cost analysis, troubleshooting, monitoring guides

---

## 🚀 Infrastructure Setup

### Backend (Production - LIVE):
- **Service**: AWS ECS Fargate
- **Image**: `907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-backend:latest`
- **Resources**: 0.5 vCPU, 2GB RAM (upgraded for FinBERT)
- **Scheduled Task**: Daily digest at 6:30 AM Arizona Time
- **Features**: ML-powered news-driven signals, real-time price validation
- **Cost**: $15-17/month (increased due to ML model memory requirements)

### Frontend (Ready to Deploy):
- **Service**: AWS App Runner (NOT Vercel!)
- **Image**: `907391580367.dkr.ecr.us-east-1.amazonaws.com/market-intel-frontend:latest`
- **Port**: 3000
- **Instance**: 0.25 vCPU, 0.5 GB RAM
- **Cost**: $2-3/month
- **Status**: Docker build failing (ESLint errors - needs fix)

### Database:
- **Service**: Supabase (PostgreSQL)
- **Connection**: Already configured in backend
- **Cost**: $0/month (free tier)

---

## 🛠️ Key Technical Decisions

### 1. Infrastructure: AWS + Supabase ONLY
**Why**: Keep costs down, standardize on fewer providers
**Services**:
- ✅ AWS App Runner for frontend (NOT Vercel)
- ✅ AWS ECS Fargate for backend
- ✅ AWS ECR for Docker images
- ✅ AWS EventBridge for scheduled tasks
- ✅ Supabase for PostgreSQL database
- ❌ NO Vercel, Netlify, or other providers

### 2. Free/Low-Cost Data Sources
**Why**: Minimize ongoing API costs
**Sources**:
- yfinance (stock prices - FREE, no API key)
- Alpha Vantage (backup stock data - FREE, 5 calls/min)
- NewsAPI (breaking news - FREE, 100 calls/day)
- 5 RSS feeds (fallback news - FREE)
- FinBERT ML model (sentiment - FREE, runs locally)
- PyTorch (ML framework - FREE, open source)

### 3. Next.js 14 with App Router
**Why**: Modern, fast, production-ready
**Config**: `output: 'standalone'` required for Docker

### 4. Dark Robinhood Theme
**Colors**:
- Background: `#000000`
- Primary (bullish): `#00ff88` (lime green)
- Negative (bearish): `#ff4444` (red)
- Neutral: `#8e8e93` (gray)

---

## 📝 Important Files

### Backend:
- `backend/app/services/market_data_service.py`
- `backend/app/services/news_service.py`
- `backend/app/services/signal_generator.py`
- `backend/app/services/digest_service.py`
- `backend/app/services/email_service.py`

### Frontend:
- `frontend/components/digest/DigestCard.tsx` (news articles display)
- `frontend/components/dashboard/MarketSnapshot.tsx` (VIX widget)
- `frontend/lib/types.ts` (TypeScript interfaces)
- `frontend/app/digest/page.tsx` (main digest view)
- `frontend/next.config.js` (standalone output)
- `frontend/Dockerfile`
- `frontend/deploy.sh`

### Configuration:
- `backend/.env` (SMTP, DATABASE_URL, JWT_SECRET)
- `frontend/.env.local` (NEXT_PUBLIC_API_URL)
- `frontend/apprunner.yaml`

### Documentation:
- `DEPLOYMENT_GUIDE.md` (AWS App Runner deployment)
- `PHASE1_COMPLETE.md` (real market data)
- `PHASE2_COMPLETE.md` (frontend enhancements)
- `NEWS_ARTICLES_FEATURE.md` (news display)
- `SAAS_ROADMAP.md` (full 5-phase plan)

---

## 🐛 Current Issues

### Frontend Build Failing (ESLint):
**Error**: Apostrophes in JSX need escaping
**Files**:
- `app/dashboard/page.tsx` (lines 54, 78)
- `app/login/page.tsx` (line 24)

**Fix**: Either:
1. Escape apostrophes: `Don&apos;t` or
2. Disable ESLint rule temporarily

**Location**: Build fails during Docker build at `npm run build`

---

## 🔄 Git Workflow

### Commits Made:
1. `190cbdb` - Phase 1 real market data
2. `f529f13` - Phase 1 documentation
3. `0e1bc2a` - Progress summary
4. `d5cead0` - News articles display
5. `a2b7363` - Phase 2 frontend enhancements
6. `70e4c4e` - App Runner deployment config

### Branch: `main`
### Remote: `https://github.com/tuxninja/market-intel-platform`

---

## 💡 Best Practices Learned

### 1. Always Ask About Infrastructure Preferences
- Don't assume Vercel/Netlify
- User wants AWS-only for cost control
- Confirm provider choice before deployment planning

### 2. Use TodoWrite Tool Consistently
- Track progress in real-time
- Mark tasks complete immediately
- Keep list clean and current

### 3. Commit Messages Format
```
✨ Feature: Brief description

Details:
- Bullet point 1
- Bullet point 2

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### 4. Docker Builds
- Always use `--platform linux/amd64` for AWS
- Test build locally before pushing to ECR
- Use `--no-cache` if dependencies changed
- Enable `output: 'standalone'` in next.config.js

### 5. Environment Variables
- Frontend: `NEXT_PUBLIC_API_URL` (client-side)
- Backend: Database, SMTP, JWT secrets (server-side)
- Never commit `.env` files

---

## 📊 Signal Generation Algorithm

**Scoring**: 60% technical + 40% news
**Technical Indicators** (60%):
- RSI: 30% weight
- MACD: 25% weight
- Moving Averages: 30% weight
- Volume: 15% weight

**News Sentiment** (40%):
- VADER + TextBlob averaged
- Filters: min 0.15 magnitude

**Signal Categories**:
- `trade_alert`: High confidence (> 0.6)
- `watch_list`: Medium confidence (0.4-0.6)
- `market_context`: Low confidence (< 0.4)

**Default Watchlist** (15 stocks):
AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META, AMD, NFLX, DIS, COIN, PLTR, SHOP, SQ, PYPL

---

## 🎯 Next Steps (Immediate)

### 1. Fix Frontend Build (URGENT)
- Fix ESLint errors in dashboard/login pages
- Test Docker build succeeds
- Push to ECR

### 2. Deploy Frontend to App Runner
- Create ECR repository: `market-intel-frontend`
- Run `frontend/deploy.sh`
- Create App Runner service
- Set env var: `NEXT_PUBLIC_API_URL=https://backend-url/api/v1`

### 3. Test Production
- Verify news articles display
- Check Market Snapshot widget
- Test on mobile devices
- Confirm API integration works

---

## 📈 Roadmap Remaining (Weeks 3-16)

### Phase 3: Stripe Subscriptions (Weeks 5-6)
- Payment gateway integration
- Subscription tiers (Free/Pro/Elite)
- User billing dashboard
- Stripe webhook handling

### Phase 4: Launch & Marketing (Week 7+)
- Landing page
- Reddit/Twitter marketing
- First 5-20 beta users
- Collect feedback

### Phase 5: Growth to $1K MRR (Weeks 8-16)
- Target: 35 users × $29/month = $1,015/month
- Performance tracking
- Signal win rate calculation
- Feature improvements based on feedback

---

## 💰 Economics

**Development Cost**: $0 (your time)
**Monthly Infrastructure**: $2.50-8/month
**Target MRR**: $1,000/month
**Target Users**: 35 paying subscribers
**Pricing**: $29/month (Pro tier)
**ROI**: Infinite (built for free)

---

## 🔑 Critical Notes

1. **Backend is LIVE** - Tomorrow's email (Oct 16, 6:30 AM) will have real signals + news
2. **Frontend needs ESLint fix** - Blocking Docker build
3. **Use AWS App Runner** - Not Vercel!
4. **Total monthly cost** - Keep under $10
5. **Git repo** - https://github.com/tuxninja/market-intel-platform

---

## 🚨 Before Reboot Checklist

- [x] Backend deployed to ECS with news articles
- [x] Frontend code complete with news display + Market Snapshot
- [x] Deployment configuration created (App Runner)
- [x] All code committed to git (commit `70e4c4e`)
- [x] Documentation complete
- [ ] Frontend Docker build (blocked by ESLint)
- [ ] Frontend deployed to App Runner
- [ ] Production testing

---

**Status**: Phase 2 complete, pending frontend deployment
**Next Session**: Fix ESLint errors, deploy frontend to App Runner, test production
