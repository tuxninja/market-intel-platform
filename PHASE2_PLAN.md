# Phase 2: Web Dashboard - Implementation Plan

**Start Date**: October 16, 2025
**Estimated Duration**: 3-4 weeks (10 hrs/week, part-time)
**Status**: 🚀 STARTING NOW

---

## 🎯 Goals

Build a modern web dashboard that allows users to:
1. **View trading signals** in real-time (not just via email)
2. **Browse signal history** and track performance
3. **Manage account** (profile, preferences, subscription)
4. **Customize watchlist** (add/remove stocks to monitor)
5. **Filter signals** by sentiment, confidence, category

### Success Criteria:
- ✅ Users can log in and view signals
- ✅ Dashboard displays market data (VIX, indices)
- ✅ Signal history with filtering/sorting
- ✅ Responsive design (mobile + desktop)
- ✅ Fast performance (<2s page load)

---

## 📋 Phase 2 Breakdown

### Week 1: Frontend Setup & Authentication (10 hours)
**Goal**: Create React app with login/signup

#### Tasks:
1. **Initialize React Project** (2 hours)
   - Create React + TypeScript + Vite project
   - Set up Tailwind CSS for styling
   - Install shadcn/ui component library
   - Configure routing (React Router)

2. **Authentication Pages** (4 hours)
   - Login page UI
   - Signup page UI
   - Password reset flow
   - JWT token management (localStorage)
   - Protected routes

3. **API Integration Layer** (2 hours)
   - Axios setup for HTTP requests
   - API client with auth interceptors
   - Error handling utilities
   - Environment config

4. **Basic Layout** (2 hours)
   - Header with navigation
   - Sidebar for desktop
   - Mobile menu
   - Footer with links

**Deliverables**:
- ✅ Users can sign up and log in
- ✅ Auth tokens stored securely
- ✅ Protected dashboard route

---

### Week 2: Dashboard Core Features (10 hours)
**Goal**: Display signals and market data

#### Tasks:
1. **Dashboard Homepage** (3 hours)
   - Market snapshot widget (VIX, SPY, DIA, QQQ)
   - Top signals of the day
   - Signal distribution chart (bullish/bearish/neutral)
   - Quick stats (total signals, win rate placeholder)

2. **Signals List View** (4 hours)
   - Table/card view toggle
   - Display all signals with:
     - Symbol, title, summary
     - Sentiment score + emoji
     - Confidence score
     - Category badge
     - Timestamp
   - Click to expand full details

3. **Signal Detail View** (3 hours)
   - Full explanation (WHY THIS MATTERS)
   - Trading guidance (HOW TO TRADE)
   - Related news articles (from Phase 1!)
   - Technical indicators (RSI, MACD, MAs)
   - Share button

**Deliverables**:
- ✅ Dashboard shows market snapshot
- ✅ Users can browse signals
- ✅ Signal details include news articles

---

### Week 3: Filtering & User Preferences (10 hours)
**Goal**: Let users customize their experience

#### Tasks:
1. **Signal Filtering** (3 hours)
   - Filter by sentiment (bullish/bearish/neutral)
   - Filter by confidence (high/medium/low)
   - Filter by category (trade_alert/watch_list/market_context)
   - Filter by symbol (search box)
   - Date range picker

2. **User Settings Page** (3 hours)
   - Profile info (name, email)
   - Email preferences (daily digest on/off)
   - Watchlist customization (add/remove stocks)
   - Timezone selection
   - Theme toggle (dark/light)

3. **API Endpoints for Preferences** (2 hours)
   - Backend: Create user preferences table
   - Backend: CRUD endpoints for preferences
   - Frontend: Save/load preferences

4. **Performance Tracking** (2 hours)
   - Signal history table
   - Win rate calculation (Phase 5 will enhance this)
   - Performance chart placeholder

**Deliverables**:
- ✅ Users can filter signals
- ✅ Users can customize watchlist
- ✅ Preferences saved to database

---

### Week 4: Polish & Deployment (10 hours)
**Goal**: Deploy to production

#### Tasks:
1. **UI Polish** (3 hours)
   - Loading states
   - Empty states
   - Error messages
   - Tooltips & help text
   - Animations (subtle)

2. **Mobile Optimization** (2 hours)
   - Test on iOS Safari
   - Test on Android Chrome
   - Fix any layout issues
   - Optimize touch targets

3. **Build & Deploy** (3 hours)
   - Set up AWS Amplify (or Vercel/Netlify)
   - Configure CI/CD pipeline
   - Set up custom domain
   - SSL certificate

4. **Testing & QA** (2 hours)
   - Test all user flows
   - Check auth edge cases
   - Verify API integration
   - Performance testing

**Deliverables**:
- ✅ Web dashboard live at custom domain
- ✅ Mobile-friendly
- ✅ Fast performance

---

## 🛠️ Tech Stack

### Frontend:
- **React 18** + **TypeScript**: Modern, type-safe UI
- **Vite**: Fast build tool
- **Tailwind CSS**: Utility-first styling
- **shadcn/ui**: Beautiful, accessible components
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **Recharts**: Data visualization
- **date-fns**: Date utilities

### Backend (existing):
- **FastAPI**: Python REST API
- **PostgreSQL**: Database
- **JWT**: Authentication
- **SQLAlchemy**: ORM

### Deployment:
- **AWS Amplify**: Frontend hosting (or Vercel)
- **AWS ECS**: Backend (already running)
- **CloudFront**: CDN for fast global delivery

---

## 📁 Project Structure

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── SignupForm.tsx
│   │   ├── dashboard/
│   │   │   ├── MarketSnapshot.tsx
│   │   │   ├── SignalsList.tsx
│   │   │   ├── SignalCard.tsx
│   │   │   └── SignalDetail.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   └── ui/
│   │       └── (shadcn components)
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Signup.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Signals.tsx
│   │   ├── SignalDetail.tsx
│   │   └── Settings.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── utils.ts
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useSignals.ts
│   │   └── useMarketData.ts
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

---

## 🎨 Design System

### Colors (Dark Theme):
- **Background**: `#000000` (pure black)
- **Surface**: `#1c1c1e` (dark gray)
- **Primary**: `#00ff88` (neon green - bullish)
- **Secondary**: `#00c6ff` (cyan - info)
- **Danger**: `#ff4444` (red - bearish)
- **Text**: `#ffffff` (white)
- **Text Muted**: `#8e8e93` (gray)

### Typography:
- **Font**: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- **Headings**: 700 weight
- **Body**: 400 weight
- **Small**: 12px, 11px for labels

### Components:
- **Cards**: Dark background, subtle border, rounded corners
- **Buttons**: Solid primary color, hover states
- **Inputs**: Dark with subtle border, focus rings
- **Badges**: Colored backgrounds for categories

---

## 🔌 API Endpoints Needed

### Existing (from Phase 1):
- `POST /auth/login`: User login
- `POST /auth/signup`: User registration
- `GET /digest/daily`: Get today's signals

### New (to build in Phase 2):
- `GET /signals`: List all signals (paginated, filtered)
- `GET /signals/{id}`: Get single signal details
- `GET /market/snapshot`: Current market data (VIX, indices)
- `GET /user/preferences`: Get user preferences
- `PUT /user/preferences`: Update user preferences
- `GET /user/watchlist`: Get custom watchlist
- `POST /user/watchlist`: Add stock to watchlist
- `DELETE /user/watchlist/{symbol}`: Remove from watchlist

---

## 📊 Data Models

### Signal (existing):
```python
class Signal:
    id: int
    symbol: str
    title: str
    summary: str
    explanation: str
    how_to_trade: str
    sentiment_score: float
    confidence_score: float
    priority: str
    category: str
    news_articles: List[Dict]
    created_at: datetime
```

### UserPreferences (new):
```python
class UserPreferences:
    id: int
    user_id: int
    email_digest_enabled: bool
    watchlist: List[str]  # JSON array of symbols
    timezone: str
    theme: str  # "dark" or "light"
    created_at: datetime
    updated_at: datetime
```

---

## 🚀 Week 1 Action Plan (Starting Now!)

### Session 1: Initialize Project (Today - 2 hours)
1. Create React + TypeScript + Vite project
2. Install dependencies (Tailwind, shadcn/ui, React Router, Axios)
3. Set up project structure
4. Configure Tailwind and theme
5. Create basic routing

### Session 2: Authentication UI (Tomorrow - 4 hours)
1. Build login page
2. Build signup page
3. Implement JWT storage
4. Create protected route wrapper
5. Add logout functionality

### Session 3: API Integration (This Week - 4 hours)
1. Set up Axios client
2. Create auth interceptors
3. Build useAuth hook
4. Test login/signup flow
5. Handle errors gracefully

---

## 💰 Cost Estimate

### Development:
- **Week 1-4**: 40 hours × $0/hour (your time)
- **Total Dev Cost**: $0

### Infrastructure:
- **AWS Amplify**: $0-5/month (free tier covers it)
- **Backend (ECS)**: $1-5/month (unchanged from Phase 1)
- **Domain**: $12/year (already have it?)
- **Total Monthly**: ~$1-10/month

**Still incredibly cheap!**

---

## 🎯 Success Metrics

### Technical:
- ✅ Page load time < 2 seconds
- ✅ Lighthouse score > 90
- ✅ Mobile responsive (all viewports)
- ✅ Zero auth bugs

### Product:
- ✅ Users can view signals without email
- ✅ Dashboard is intuitive (no confusion)
- ✅ Filters work correctly
- ✅ Settings save successfully

### Business:
- ✅ Foundation for paid subscriptions (Phase 3)
- ✅ Professional appearance (builds trust)
- ✅ Scalable architecture (can handle growth)

---

## 📝 Notes & Considerations

### Authentication:
- Using existing FastAPI JWT auth (no changes needed)
- Refresh tokens for security
- Remember me option (optional)

### Performance:
- Lazy load signal details (don't fetch everything at once)
- Cache market data (refresh every 5 minutes)
- Infinite scroll for signal history

### Mobile:
- Bottom navigation for mobile
- Swipe gestures for signal cards
- Optimized touch targets (48px minimum)

### Accessibility:
- ARIA labels throughout
- Keyboard navigation
- Screen reader friendly
- High contrast mode

---

## 🔮 Future Enhancements (Post-Phase 2)

These will come in later phases:
- [ ] Real-time signal updates (WebSockets)
- [ ] Push notifications
- [ ] Signal performance tracking with charts
- [ ] Backtesting tool
- [ ] Social features (share signals)
- [ ] Mobile app (React Native)

---

## 🎬 Let's Begin!

**Next Steps**:
1. Create `frontend/` directory
2. Initialize React + Vite project
3. Install dependencies
4. Set up project structure
5. Create first components

**Ready to start building?** Let's create the React app! 🚀

---

**Status**: Phase 2 Planning Complete ✅
**Next**: Initialize React Project 🎯
**Estimated Time to Launch**: 3-4 weeks (part-time)
