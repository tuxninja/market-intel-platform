# SaaS Roadmap: Market Intelligence Platform

**Last Updated**: October 15, 2025
**Current Status**: MVP Email-Only System
**Goal**: Minimum Viable SaaS Product

---

## 🎯 Vision

Transform the current email-only digest system into a subscription-based SaaS platform offering:
- Real-time market intelligence
- AI-powered trading signals
- Multi-user support with tiered pricing
- Web dashboard + daily email delivery
- API access for power users

---

## 📊 Current State vs. MVP SaaS

### What We Have Now (MVP Email System)
✅ Daily email digest automation (6:30 AM Mon-Fri)
✅ Demo signals (AAPL, NVDA, AMD, TSLA, SPY)
✅ Email template with market snapshot (VIX, SPY, DIA, QQQ)
✅ Sentiment categorization (Bullish/Bearish/Neutral)
✅ AWS infrastructure (ECS Fargate + Supabase)
✅ GitHub Actions automation
✅ Cost: ~$1/month

### What We Need for MVP SaaS
❌ Real-time market data integration
❌ Web dashboard (frontend)
❌ User authentication & accounts
❌ Subscription management (Stripe)
❌ Multiple pricing tiers
❌ Custom watchlists per user
❌ API access for programmatic users
❌ Analytics & signal performance tracking

---

## 🗺️ Roadmap Phases

## Phase 1: Real Market Data (Week 1-2)
**Goal**: Replace demo signals with actual market intelligence
**Estimated Time**: 2-3 days of focused work

### Tasks

#### 1.1 Market Data Integration
```bash
# Services to integrate:
- yfinance (real-time stock prices) - FREE
- Alpha Vantage (news sentiment) - FREE tier: 500 calls/day
- NewsAPI (financial news) - FREE tier: 100 calls/day
- Technical indicators (TA-Lib) - FREE/Open source
```

**Files to Create/Modify:**
- `backend/app/services/market_data_service.py` (NEW)
- `backend/app/services/news_service.py` (NEW)
- `backend/app/services/technical_analysis_service.py` (NEW)
- `backend/app/services/digest_service.py` (MODIFY - remove demo signals)

**API Keys Needed:**
- Alpha Vantage: https://www.alphavantage.co/support/#api-key (FREE)
- NewsAPI: https://newsapi.org/register (FREE)

**Implementation Steps:**
```python
# 1. Create market_data_service.py
class MarketDataService:
    async def get_stock_price(self, symbol: str) -> Dict
    async def get_technical_indicators(self, symbol: str) -> Dict
    async def calculate_rsi(self, symbol: str, period: int = 14) -> float
    async def calculate_macd(self, symbol: str) -> Dict

# 2. Create news_service.py
class NewsService:
    async def fetch_market_news(self, hours_lookback: int = 24) -> List[NewsArticle]
    async def analyze_sentiment(self, article: NewsArticle) -> float
    async def filter_relevant_news(self, articles: List) -> List

# 3. Create signal_generator.py
class SignalGenerator:
    async def generate_signals(self, watchlist: List[str]) -> List[Signal]
    async def combine_technical_and_news(self, symbol: str) -> Signal
```

**Testing:**
```bash
# Local test
python scripts/test_market_data.py --symbols AAPL,NVDA,TSLA

# Should output:
# - Real stock prices
# - RSI, MACD values
# - Recent news with sentiment
# - Generated signals with confidence scores
```

**Deliverable**: Real signals based on actual market data instead of hardcoded demos

**Cost**: $0/month (free tier APIs sufficient for MVP)

---

#### 1.2 Database Activation
**Goal**: Store signals, track performance, enable user data

**Files to Modify:**
- `backend/app/services/digest_service.py` (enable database writes)
- `backend/app/models/signal.py` (already exists)
- Add: `backend/app/models/user.py`
- Add: `backend/app/models/subscription.py`
- Add: `backend/app/models/watchlist.py`

**Database Schema:**
```sql
-- Already exists
CREATE TABLE signals (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10),
    title TEXT,
    summary TEXT,
    sentiment_score FLOAT,
    confidence_score FLOAT,
    created_at TIMESTAMP
);

-- NEW: Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    subscription_tier VARCHAR(50) DEFAULT 'free',
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- NEW: User watchlists
CREATE TABLE watchlists (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    symbol VARCHAR(10) NOT NULL,
    added_at TIMESTAMP DEFAULT NOW()
);

-- NEW: Signal performance tracking
CREATE TABLE signal_outcomes (
    id SERIAL PRIMARY KEY,
    signal_id INTEGER REFERENCES signals(id),
    outcome VARCHAR(20), -- 'profitable', 'loss', 'pending'
    profit_loss_percent FLOAT,
    evaluated_at TIMESTAMP
);
```

**Implementation:**
```bash
# Create migration
cd backend
alembic revision --autogenerate -m "Add users and watchlists"
alembic upgrade head

# Test locally
docker-compose exec postgres psql -U marketintel -d market_intelligence
\dt  # Should show new tables
```

**Deliverable**: Database storing all signals and user data

---

## Phase 2: Web Dashboard (Week 2-4)
**Goal**: Build frontend for users to view signals, manage watchlists, and configure settings
**Estimated Time**: 5-7 days

### 2.1 Frontend Setup

**Tech Stack:**
- **Framework**: React + TypeScript + Vite
- **UI Library**: Tailwind CSS + shadcn/ui (pre-built components)
- **State Management**: React Query (server state)
- **Auth**: JWT tokens
- **Hosting**: AWS Amplify (free tier: 1000 build minutes/month)

**Project Structure:**
```bash
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.tsx          # Main dashboard
│   │   ├── SignalCard.tsx         # Individual signal display
│   │   ├── MarketSnapshot.tsx     # VIX, SPY, DIA, QQQ display
│   │   ├── WatchlistManager.tsx   # Add/remove symbols
│   │   └── Settings.tsx           # User preferences
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Signup.tsx
│   │   ├── Dashboard.tsx
│   │   └── Pricing.tsx
│   ├── api/
│   │   └── client.ts              # API client
│   └── App.tsx
└── package.json
```

**Setup Commands:**
```bash
# Create React app
cd /Users/jasonriedel/PyCharmProjects/market-intel-platform
npm create vite@latest frontend -- --template react-ts

cd frontend
npm install

# Install dependencies
npm install @tanstack/react-query axios tailwindcss autoprefixer postcss
npm install -D @shadcn/ui lucide-react

# Initialize Tailwind
npx tailwindcss init -p

# Start dev server
npm run dev  # Runs on http://localhost:5173
```

**Key Features:**
1. **Dashboard Page**
   - List of today's signals (bullish/bearish/neutral sections)
   - Market snapshot at top (VIX, indices)
   - Filter by sentiment, confidence, category
   - Real-time updates

2. **Watchlist Management**
   - Add/remove stock symbols
   - View current watchlist
   - Get alerts only for watchlist stocks (premium feature)

3. **Signal Detail View**
   - Full explanation ("Why This Matters")
   - Trading guidance ("How to Trade")
   - Related news articles
   - Technical chart (optional: integrate TradingView widget)

4. **Settings Page**
   - Email delivery preferences (time, frequency)
   - Notification settings
   - Watchlist management
   - API key generation (for API tier)

**Deliverable**: Functional web dashboard accessible via browser

**Cost**: $0/month (AWS Amplify free tier)

---

### 2.2 Authentication System

**Backend Changes:**
```python
# backend/app/api/v1/endpoints/auth.py
@router.post("/signup")
async def signup(email: str, password: str) -> Token:
    # Hash password with bcrypt
    # Create user in database
    # Return JWT token

@router.post("/login")
async def login(email: str, password: str) -> Token:
    # Verify credentials
    # Return JWT token

@router.post("/refresh")
async def refresh_token(refresh_token: str) -> Token:
    # Validate refresh token
    # Return new access token

@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # Decode JWT
    # Return user info
```

**Frontend Integration:**
```typescript
// src/api/auth.ts
export async function login(email: string, password: string) {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const { access_token } = await response.json();
  localStorage.setItem('token', access_token);
}

// Protected route example
function Dashboard() {
  const { data: user } = useQuery('user', getCurrentUser);
  if (!user) return <Navigate to="/login" />;
  return <DashboardContent user={user} />;
}
```

**Deliverable**: Secure login/signup flow with JWT authentication

---

## Phase 3: Subscription & Monetization (Week 4-6)
**Goal**: Implement Stripe payments and tiered pricing
**Estimated Time**: 3-5 days

### 3.1 Pricing Tiers

| Tier | Price | Features | Target User |
|------|-------|----------|------------|
| **Free** | $0/month | - 5 signals/day (top-rated only)<br>- Email delivery only<br>- No watchlist customization<br>- Basic market snapshot | Casual investors |
| **Pro** | $29/month | - Unlimited signals<br>- Web dashboard access<br>- Custom watchlist (up to 25 stocks)<br>- Priority signal generation<br>- Email + dashboard<br>- Technical charts | Active traders |
| **Premium** | $99/month | - Everything in Pro<br>- Real-time alerts (SMS/push)<br>- API access (1000 calls/day)<br>- Advanced analytics<br>- Backtesting tools<br>- Signal performance tracking<br>- Custom alert rules | Professional traders |

### 3.2 Stripe Integration

**Setup:**
```bash
# Install Stripe library
cd backend
echo "stripe==7.0.0" >> requirements.txt
pip install stripe

# Get Stripe keys
# 1. Sign up at https://dashboard.stripe.com/register
# 2. Get test keys: https://dashboard.stripe.com/test/apikeys
# 3. Add to GitHub secrets:
gh secret set STRIPE_API_KEY  # sk_test_...
gh secret set STRIPE_WEBHOOK_SECRET  # whsec_...
```

**Backend Implementation:**
```python
# backend/app/services/subscription_service.py
import stripe

class SubscriptionService:
    async def create_checkout_session(
        self,
        user_id: UUID,
        price_id: str  # Stripe price ID
    ) -> str:
        """Create Stripe checkout session, return checkout URL"""

    async def handle_webhook(self, payload: bytes, sig_header: str):
        """Handle Stripe webhooks (payment success, cancellation, etc.)"""

    async def upgrade_subscription(self, user_id: UUID, tier: str):
        """Upgrade user to Pro/Premium tier"""

    async def cancel_subscription(self, user_id: UUID):
        """Cancel user subscription"""

# backend/app/api/v1/endpoints/subscription.py
@router.post("/checkout")
async def create_checkout(tier: str, user: User = Depends(get_current_user)):
    session_url = await subscription_service.create_checkout_session(
        user.id, tier
    )
    return {"checkout_url": session_url}

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    await subscription_service.handle_webhook(payload, sig_header)
```

**Frontend Integration:**
```typescript
// src/pages/Pricing.tsx
function PricingPage() {
  const handleSubscribe = async (tier: 'pro' | 'premium') => {
    const { checkout_url } = await fetch('/api/v1/subscription/checkout', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ tier })
    }).then(r => r.json());

    window.location.href = checkout_url;  // Redirect to Stripe
  };

  return (
    <PricingCards onSubscribe={handleSubscribe} />
  );
}
```

**Stripe Setup Steps:**
1. Create products in Stripe Dashboard:
   - Pro: $29/month (recurring)
   - Premium: $99/month (recurring)
2. Copy price IDs (e.g., `price_1234567890`)
3. Configure webhook endpoint: `https://your-api.com/api/v1/subscription/webhook`
4. Test with Stripe test cards: `4242 4242 4242 4242`

**Deliverable**: Working subscription flow with Stripe payments

**Cost**: Stripe fees = 2.9% + $0.30 per transaction

---

### 3.3 Feature Gating

**Implement subscription checks:**
```python
# backend/app/core/permissions.py
def require_pro(user: User):
    if user.subscription_tier not in ['pro', 'premium']:
        raise HTTPException(403, "Pro subscription required")

def require_premium(user: User):
    if user.subscription_tier != 'premium':
        raise HTTPException(403, "Premium subscription required")

# Apply to endpoints
@router.get("/signals/all")
async def get_all_signals(user: User = Depends(require_pro)):
    # Only Pro/Premium users can access unlimited signals
    pass

@router.get("/api-key")
async def generate_api_key(user: User = Depends(require_premium)):
    # Only Premium users get API access
    pass
```

**Frontend Feature Gating:**
```typescript
function WatchlistManager({ user }) {
  if (user.subscription_tier === 'free') {
    return <UpgradePrompt message="Upgrade to Pro for custom watchlists" />;
  }
  return <WatchlistEditor />;
}
```

---

## Phase 4: API Access (Week 6-7)
**Goal**: Provide REST API for Premium users
**Estimated Time**: 2-3 days

### 4.1 API Key Management

**Database:**
```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    key_hash VARCHAR(255) NOT NULL,
    key_prefix VARCHAR(10),  -- Show "sk_live_abc..." to user
    name VARCHAR(100),  -- User-given name "My Trading Bot"
    last_used_at TIMESTAMP,
    rate_limit INTEGER DEFAULT 1000,  -- calls per day
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE api_usage (
    id SERIAL PRIMARY KEY,
    api_key_id UUID REFERENCES api_keys(id),
    endpoint VARCHAR(255),
    called_at TIMESTAMP DEFAULT NOW()
);
```

**API Key Generation:**
```python
# backend/app/services/api_key_service.py
import secrets
import hashlib

class APIKeyService:
    def generate_key(self, user_id: UUID, name: str) -> str:
        # Generate secure random key
        key = f"sk_live_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        # Store hash in database
        await self.db.execute(
            "INSERT INTO api_keys (user_id, key_hash, key_prefix, name) VALUES (%s, %s, %s, %s)",
            (user_id, key_hash, key[:15], name)
        )

        # Return plaintext key ONCE (user must save it)
        return key

    async def validate_key(self, key: str) -> Optional[User]:
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        # Look up key, check rate limits, return user
```

**Rate Limiting:**
```python
# backend/app/core/rate_limit.py
from fastapi import HTTPException
from datetime import datetime, timedelta

async def check_rate_limit(api_key_id: UUID, limit: int = 1000):
    today = datetime.now().date()
    count = await db.fetch_val(
        "SELECT COUNT(*) FROM api_usage WHERE api_key_id = %s AND called_at >= %s",
        (api_key_id, today)
    )

    if count >= limit:
        raise HTTPException(429, "Rate limit exceeded")

    # Log usage
    await db.execute(
        "INSERT INTO api_usage (api_key_id, endpoint) VALUES (%s, %s)",
        (api_key_id, request.url.path)
    )
```

### 4.2 API Endpoints

**Public API Endpoints (require API key):**
```python
# GET /api/v1/signals
# Returns list of current signals
# Authentication: API key in header (X-API-Key)

# GET /api/v1/signals/{signal_id}
# Returns specific signal details

# GET /api/v1/market/snapshot
# Returns current market data (VIX, indices)

# GET /api/v1/watchlist
# Returns user's watchlist

# POST /api/v1/watchlist
# Adds symbol to watchlist

# GET /api/v1/technical/{symbol}
# Returns technical indicators for symbol
```

**Example API Call:**
```bash
curl -H "X-API-Key: sk_live_abc123..." \
  https://api.marketintel.com/api/v1/signals

# Response:
{
  "generated_at": "2025-10-15T13:30:00Z",
  "total_items": 15,
  "items": [
    {
      "id": 123,
      "symbol": "AAPL",
      "title": "Apple Shows Strong Momentum",
      "sentiment_score": 0.75,
      "confidence_score": 0.85,
      "category": "trade_alert"
    },
    ...
  ]
}
```

**API Documentation:**
- Auto-generated with FastAPI: `https://api.marketintel.com/docs`
- Custom docs page on frontend: `https://marketintel.com/api-docs`

**Deliverable**: REST API with authentication, rate limiting, and documentation

---

## Phase 5: Analytics & Performance (Week 7-8)
**Goal**: Track signal performance, show users which signals were profitable
**Estimated Time**: 3-4 days

### 5.1 Signal Performance Tracking

**Implementation:**
```python
# backend/app/services/performance_tracker.py
class PerformanceTracker:
    async def evaluate_signal(self, signal: Signal):
        """
        Check signal outcome after 1 day, 3 days, 1 week
        """
        # Get signal entry price (when signal was created)
        entry_price = signal.extra_data.get('entry_price')

        # Get current price
        current_price = await market_data.get_price(signal.symbol)

        # Calculate profit/loss
        if signal.sentiment_score > 0:  # Bullish signal
            profit_pct = ((current_price - entry_price) / entry_price) * 100
        else:  # Bearish signal
            profit_pct = ((entry_price - current_price) / entry_price) * 100

        # Store outcome
        await db.execute(
            "INSERT INTO signal_outcomes (signal_id, outcome, profit_loss_percent) VALUES (%s, %s, %s)",
            (signal.id, 'profitable' if profit_pct > 0 else 'loss', profit_pct)
        )

    async def get_performance_stats(self) -> Dict:
        """
        Return overall performance statistics
        """
        return {
            "total_signals": 1250,
            "profitable_signals": 780,
            "win_rate": 62.4,
            "avg_profit": 3.2,
            "best_performer": "NVDA (+15.8%)",
            "worst_performer": "TSLA (-8.3%)"
        }
```

**Dashboard Display:**
```typescript
// src/components/PerformanceStats.tsx
function PerformanceStats() {
  const { data: stats } = useQuery('performance', getPerformanceStats);

  return (
    <div className="stats-grid">
      <StatCard title="Win Rate" value={`${stats.win_rate}%`} />
      <StatCard title="Avg Profit" value={`${stats.avg_profit}%`} />
      <StatCard title="Total Signals" value={stats.total_signals} />
      <StatCard title="Best Trade" value={stats.best_performer} />
    </div>
  );
}
```

**Scheduled Job (Daily):**
```bash
# .github/workflows/evaluate-signals.yml
name: Evaluate Signal Performance
on:
  schedule:
    - cron: '0 22 * * 1-5'  # 3 PM Arizona Time (after market close)

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - name: Run evaluation
        run: |
          aws ecs run-task \
            --cluster market-intel-cluster \
            --task-definition evaluate-signals \
            --region us-east-1
```

**Deliverable**: Performance tracking with win rate, avg profit, and signal history

---

## 📈 Launch Checklist

### Pre-Launch (1 week before)

- [ ] **Security Audit**
  - [ ] All secrets in environment variables (not code)
  - [ ] Rate limiting on all endpoints
  - [ ] SQL injection prevention (use parameterized queries)
  - [ ] XSS protection on frontend
  - [ ] HTTPS only (SSL certificate)

- [ ] **Testing**
  - [ ] Full end-to-end test: signup → subscribe → receive email + dashboard access
  - [ ] Test all three subscription tiers
  - [ ] Test Stripe webhooks (payment success, failure, cancellation)
  - [ ] Load testing (simulate 100 concurrent users)
  - [ ] Mobile responsiveness

- [ ] **Legal & Compliance**
  - [ ] Terms of Service page
  - [ ] Privacy Policy page
  - [ ] Disclaimer (not investment advice)
  - [ ] GDPR compliance (data export, deletion)
  - [ ] CAN-SPAM compliance (unsubscribe link)

- [ ] **Monitoring**
  - [ ] CloudWatch alarms (high error rate, high latency)
  - [ ] Stripe webhook monitoring
  - [ ] Database backup strategy
  - [ ] Uptime monitoring (e.g., UptimeRobot)

### Launch Day

- [ ] Announce on social media (Twitter, LinkedIn)
- [ ] Post on Reddit (r/StockMarket, r/algotrading)
- [ ] Email existing users (jasonnetbiz@gmail.com) with launch announcement
- [ ] Monitor error logs closely
- [ ] Have rollback plan ready

### Post-Launch (First Week)

- [ ] Daily check of user signups, conversions, churn
- [ ] Monitor Stripe dashboard for payment issues
- [ ] Respond to user feedback within 24 hours
- [ ] Fix critical bugs immediately
- [ ] Iterate on features based on user requests

---

## 💰 Cost Projections

### MVP SaaS Costs (Monthly)

| Service | Cost | Notes |
|---------|------|-------|
| **AWS ECS Fargate** | $1-5 | 0.25 vCPU, 0.5 GB RAM, runs 1 hour/day |
| **Supabase (Database)** | $0 | Free tier: 500 MB storage, 2 GB bandwidth |
| **AWS Amplify (Frontend)** | $0 | Free tier: 1000 build minutes |
| **GitHub Actions** | $0 | Free for public repos, 2000 min/month private |
| **Stripe** | 2.9% + $0.30 | Per transaction (only when you make money!) |
| **Domain (marketintel.com)** | $12/year | One-time annual cost |
| **SSL Certificate** | $0 | Free with AWS or Let's Encrypt |
| **API Keys (Alpha Vantage, NewsAPI)** | $0 | Free tiers sufficient for MVP |

**Total Fixed Costs**: ~$2-7/month

**Variable Costs**: Stripe fees (only on successful subscriptions)

### Revenue Projections (Conservative)

| Month | Users | Free | Pro ($29) | Premium ($99) | MRR | Costs | Profit |
|-------|-------|------|-----------|---------------|-----|-------|--------|
| 1 | 10 | 8 | 2 | 0 | $58 | $5 | $53 |
| 3 | 50 | 40 | 8 | 2 | $430 | $10 | $420 |
| 6 | 150 | 120 | 25 | 5 | $1,220 | $20 | $1,200 |
| 12 | 500 | 400 | 80 | 20 | $4,300 | $50 | $4,250 |

**Break-even**: Month 1 (first paying customer covers costs)

**Target**: 100 paying users by Month 6 = $2,000+ MRR

---

## 🚀 Go-To-Market Strategy

### Target Audience

**Primary**: Retail investors/traders who:
- Trade actively (3+ times per week)
- Follow market news daily
- Use multiple tools (TradingView, Seeking Alpha, FinViz)
- Age 25-45, income $50k-150k
- Want actionable signals, not just raw data

**Secondary**: Professional traders who:
- Need API access for algorithmic trading
- Manage portfolios $100k+
- Willing to pay premium for edge

### Marketing Channels

1. **Content Marketing** (Organic)
   - Blog: "How to Trade Earnings Reports" (SEO)
   - YouTube: "Daily Market Breakdown" videos
   - Twitter: Share daily top signal with screenshot
   - Reddit: Post in r/StockMarket with value (not spam)

2. **Paid Ads** (Later, when profitable)
   - Google Ads: "stock trading signals" keywords
   - Twitter Ads: Target finance/investing accounts
   - Budget: $500/month → expect 50-100 signups

3. **Partnerships**
   - Discord communities (trading servers)
   - Finance YouTubers (affiliate program: 20% commission)
   - Stock market podcasts (sponsorships)

4. **Referral Program**
   - Give users unique referral link
   - Reward: 1 month free Pro for each friend who subscribes
   - Track in database with referral codes

### Positioning

**Tagline**: "AI-Powered Trading Signals, Delivered Daily"

**Elevator Pitch**:
> "Market Intelligence Platform combines real-time market data, AI sentiment analysis, and technical indicators to generate high-probability trading signals. Get actionable insights delivered to your inbox every morning before market open—so you know exactly what to trade and why."

**Differentiation**:
- **vs. FinViz**: More actionable (we tell you how to trade, not just show data)
- **vs. Seeking Alpha**: Faster (real-time signals, not hours-old articles)
- **vs. Bloomberg Terminal**: Affordable ($29 vs. $24,000/year)
- **vs. Reddit WallStreetBets**: Data-driven, not hype-driven

---

## 📊 Success Metrics

### Key Performance Indicators (KPIs)

| Metric | Target | How to Track |
|--------|--------|--------------|
| **Signup Conversion Rate** | 5% of visitors | Google Analytics + Database |
| **Free → Pro Conversion** | 10% within 30 days | Stripe + Database |
| **Pro → Premium Upgrade** | 5% | Stripe + Database |
| **Churn Rate** | < 5%/month | Stripe cancellations |
| **Daily Active Users (DAU)** | 60% of subscribers | Dashboard login tracking |
| **Email Open Rate** | > 40% | Email service analytics |
| **Signal Win Rate** | > 55% | Performance tracker |
| **Customer Lifetime Value (LTV)** | > $200 | Avg subscription length × MRR |
| **Customer Acquisition Cost (CAC)** | < $20 | Marketing spend / new users |

**Goal**: LTV/CAC ratio > 3:1 (healthy SaaS business)

---

## ⏱️ Timeline Summary

| Phase | Duration | Key Deliverables | Ready to Launch? |
|-------|----------|------------------|------------------|
| Phase 1: Real Market Data | 1-2 weeks | Real signals, database storage | ❌ No (email-only) |
| Phase 2: Web Dashboard | 2-4 weeks | Frontend, authentication | ❌ No (no payments) |
| Phase 3: Subscriptions | 1-2 weeks | Stripe integration, pricing tiers | ✅ **MVP LAUNCH** |
| Phase 4: API Access | 1 week | REST API, rate limiting | ✅ Full Feature Set |
| Phase 5: Analytics | 1 week | Performance tracking, stats | ✅ Mature Product |

**Total Time to MVP Launch**: 6-8 weeks of focused development

**Total Time to Full Feature Set**: 8-10 weeks

---

## 🎯 Immediate Next Steps (This Week)

### Priority 1: Real Market Data (Start Today)

```bash
# 1. Sign up for free API keys
# - Alpha Vantage: https://www.alphavantage.co/support/#api-key
# - NewsAPI: https://newsapi.org/register

# 2. Install dependencies
cd backend
echo "yfinance==0.2.31" >> requirements.txt
echo "alpha-vantage==2.3.1" >> requirements.txt
echo "newsapi-python==0.2.7" >> requirements.txt
pip install -r requirements.txt

# 3. Create market data service
touch app/services/market_data_service.py
# Implement get_stock_price(), get_technical_indicators()

# 4. Test locally
python scripts/test_market_data.py

# 5. Replace demo signals
# Modify app/services/digest_service.py
# Remove _generate_demo_signals(), use real data

# 6. Test end-to-end
docker-compose up -d
curl http://localhost:8000/api/v1/digest/generate
python scripts/send_daily_digest.py --email jasonnetbiz@gmail.com

# 7. Deploy to production
git add .
git commit -m "Add real market data integration"
git push origin main
```

### Priority 2: Set Up Frontend (Next 2-3 Days)

```bash
# 1. Create React app
cd /Users/jasonriedel/PyCharmProjects/market-intel-platform
npm create vite@latest frontend -- --template react-ts

# 2. Install dependencies
cd frontend
npm install @tanstack/react-query axios tailwindcss

# 3. Build basic dashboard
# - Login page
# - Dashboard page (display signals from API)
# - Settings page

# 4. Deploy to AWS Amplify
# Connect GitHub repo, auto-deploy on push
```

### Priority 3: Stripe Integration (Following Week)

```bash
# 1. Create Stripe account
# https://dashboard.stripe.com/register

# 2. Create products
# - Pro: $29/month
# - Premium: $99/month

# 3. Implement backend
# Add app/services/subscription_service.py
# Add app/api/v1/endpoints/subscription.py

# 4. Add pricing page to frontend
# src/pages/Pricing.tsx

# 5. Test with Stripe test cards
# 4242 4242 4242 4242 (success)
```

---

## 📞 Support & Maintenance Plan

### Customer Support

**Tier 1: Self-Service** (Free/Pro)
- FAQ page on website
- Documentation (/docs)
- Email support: support@marketintel.com (48-hour response)

**Tier 2: Priority Support** (Premium)
- Email support (24-hour response)
- Live chat during market hours (9:30 AM - 4 PM ET)
- Dedicated Slack channel (if >100 premium users)

### Maintenance Windows

- **Database backups**: Daily at 2 AM ET (automated)
- **Dependency updates**: Monthly (security patches immediately)
- **Feature releases**: Every 2 weeks (sprint cycle)
- **Downtime**: Target 99.9% uptime (< 45 minutes/month)

---

## 🔮 Future Features (Post-MVP)

**6-12 Months After Launch:**

1. **Mobile Apps** (iOS + Android)
   - React Native app
   - Push notifications for real-time alerts
   - Cost: $99/year Apple Developer + $25 Google Play

2. **Social Features**
   - Share signals with friends
   - Public leaderboard (top-performing users)
   - Community discussion per signal

3. **Backtesting Tools**
   - Test signal strategies on historical data
   - "What if I had followed all signals last year?"
   - Show hypothetical P&L

4. **Advanced Alerts**
   - SMS alerts (Twilio integration)
   - Custom alert rules: "Alert me when AAPL breaks $180"
   - Webhook support (integrate with user's own tools)

5. **Portfolio Tracking**
   - Connect brokerage accounts (Plaid API)
   - Show actual P&L from signals
   - Tax loss harvesting suggestions

6. **AI Chat Assistant**
   - "Why is NVDA bullish today?"
   - "What's the risk of shorting TSLA?"
   - Powered by GPT-4 + real market data

---

## ✅ Decision Points

Before proceeding with full SaaS buildout, decide:

### Question 1: Do you want to build the full SaaS or stay email-only?

**Option A: Full SaaS (Recommended)**
- Pros: Higher revenue potential ($29-99/user vs. $0), scalable, VC fundable
- Cons: More complexity, 6-8 weeks development, requires ongoing support
- Best for: Building a business, aiming for $10k+ MRR

**Option B: Email-Only (Current MVP)**
- Pros: Simple, low maintenance, already working
- Cons: Limited revenue (ads or sponsorships only), not scalable
- Best for: Personal use, small audience, side project

### Question 2: Do you want to code this yourself or hire help?

**Option A: Solo Development (You + Claude Code)**
- Pros: No cost, full control, learn new skills
- Cons: Slower (6-8 weeks), limited by your availability
- Timeline: 2-3 months to MVP launch

**Option B: Hire Contractor**
- Pros: Faster (4-6 weeks), professional quality
- Cons: Cost ($5k-15k for MVP), less control
- Timeline: 1-2 months to MVP launch

### Question 3: What's your revenue goal?

**Goal: $1,000/month** → Focus on Pro tier, organic growth
**Goal: $10,000/month** → Need 100+ Pro users or 25+ Premium users, paid ads
**Goal: $100,000/month** → Need 1000+ Pro users or institutional sales, VC funding

---

**Ready to start?** Let me know which phase you want to tackle first, and I'll provide detailed implementation steps!
