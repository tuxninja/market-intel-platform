# Frontend Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/jasonriedel/PyCharmProjects/market-intel-platform/frontend
npm install
```

### 2. Configure Environment

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NODE_ENV=development
```

### 3. Start Backend API

Make sure the backend is running first:

```bash
cd ../backend
source venv/bin/activate  # or activate your virtual environment
uvicorn app.main:app --reload
```

Backend should be accessible at `http://localhost:8000`

### 4. Start Frontend Development Server

```bash
npm run dev
```

Frontend will be available at `http://localhost:3001`

## Testing the Application

### 1. Create an Account

1. Navigate to `http://localhost:3001`
2. Click "Get Started" or "Sign In"
3. Go to Register page
4. Fill in:
   - Email: `test@example.com`
   - Password: `password123` (min 8 chars)
   - Full Name: `Test User` (optional)
5. Click "Create Account"

You'll be automatically logged in and redirected to the dashboard.

### 2. View Dashboard

After login, you'll see:
- Account information (subscription tier, status, verification)
- Quick actions (View Digest, Settings, etc.)
- Feature overview cards

### 3. View Digest

1. Click "View Today's Digest" or navigate to `/digest`
2. You'll see the daily market intelligence feed with:
   - VIX market regime (if available)
   - Statistics (total signals, filtered signals, alerts)
   - Filter sidebar (category, priority, sort)
   - Signal cards with expandable details

### 4. Manage Settings

1. Navigate to `/settings`
2. Update your profile information
3. View account details
4. (Future features like digest preferences and subscription management)

## Features Overview

### Authentication System

- **JWT-based authentication** with access and refresh tokens
- **Auto-refresh** when access token expires
- **Protected routes** redirect to login if not authenticated
- **Token storage** in localStorage
- **Logout** clears tokens and redirects to home

### Landing Page (`/`)

- Hero section with value proposition
- Features showcase
- Pricing tiers (Free, Pro, Premium, Elite)
- Call-to-action buttons

### Dashboard (`/dashboard`)

Protected route showing:
- User profile summary
- Subscription tier badge
- Account status
- Quick action buttons
- Feature overview

### Digest Feed (`/digest`)

Protected route with:
- Daily market intelligence signals
- Three categories:
  - 🔴 **TRADE ALERT** - High-confidence opportunities
  - 🟡 **WATCH LIST** - Emerging opportunities
  - 🟢 **MARKET CONTEXT** - Background information
- **Signal cards** with:
  - Title, summary, symbol
  - Confidence score (0-100%)
  - Sentiment score (-1 to +1)
  - Priority (high, medium, low)
  - Expandable details (WHY THIS MATTERS, HOW TO TRADE)
- **Filters**:
  - Category filter
  - Priority filter
  - Sort by date/confidence/sentiment
- **Refresh button** to reload digest

### Settings (`/settings`)

Protected route for:
- Account information display
- Profile updates (full name)
- Digest preferences (coming soon)
- Subscription management (coming soon)

## API Integration

### Base URL

All API calls go to: `http://localhost:8000/api/v1`

### Authentication Endpoints

```typescript
// Register
POST /auth/register
Body: { email, password, full_name? }
Response: User object

// Login
POST /auth/login
Body: { email, password }
Response: { access_token, refresh_token, token_type }

// Get current user
GET /auth/me
Headers: { Authorization: Bearer <token> }
Response: User object

// Update profile
PUT /auth/me
Headers: { Authorization: Bearer <token> }
Body: { full_name }
Response: Updated user object

// Refresh token
POST /auth/refresh
Body: { token: refresh_token }
Response: { access_token, refresh_token, token_type }
```

### Digest Endpoints

```typescript
// Get daily digest
GET /digest/daily?max_items=20&hours_lookback=24&enable_ml=true
Headers: { Authorization: Bearer <token> }
Response: DigestResponse with items array

// Generate custom digest
POST /digest/generate
Headers: { Authorization: Bearer <token> }
Body: { max_items, hours_lookback, enable_ml, categories? }
Response: DigestResponse with items array
```

## Styling Guide

### Theme Colors

```css
--background: #000000         /* Black background */
--card: #0f1419              /* Dark card background */
--card-secondary: #1a1f29    /* Slightly lighter card */
--primary: #00ff88           /* Lime green (Robinhood style) */
--primary-dark: #00cc6a      /* Darker green */
--primary-light: #33ffaa     /* Lighter green */
--negative: #ff4444          /* Red for errors/negative */
--neutral: #6b7280           /* Gray for neutral */
```

### Component Usage

```tsx
// Button
<Button variant="primary" size="md">Click Me</Button>
<Button variant="secondary" loading>Loading...</Button>
<Button variant="ghost" fullWidth>Full Width</Button>

// Card
<Card hover>Hoverable card</Card>
<Card className="custom-class">Custom styled</Card>

// Badge
<Badge variant="success">Active</Badge>
<Badge variant="error">Inactive</Badge>
<Badge variant="warning">Pending</Badge>

// Input
<Input
  label="Email"
  type="email"
  error="Invalid email"
  helperText="Enter your email address"
/>
```

## Troubleshooting

### Problem: Can't connect to backend

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `.env.local` has correct API URL
3. Ensure no CORS issues (backend should allow `http://localhost:3001`)

### Problem: Authentication not working

**Solution:**
1. Clear browser localStorage: DevTools > Application > Local Storage > Clear
2. Check backend JWT configuration
3. Try registering a new account

### Problem: Build fails

**Solution:**
```bash
rm -rf .next node_modules
npm install
npm run build
```

### Problem: Type errors

**Solution:**
```bash
npx tsc --noEmit
```

Check TypeScript errors and fix them.

### Problem: Digest not loading

**Solution:**
1. Check if backend has digest data
2. Verify user is authenticated (check localStorage for tokens)
3. Check browser console for API errors
4. Try refreshing the page

## Development Workflow

### 1. Making Changes

```bash
# Edit files in app/, components/, or lib/
# Changes hot-reload automatically

# If hot reload breaks:
rm -rf .next
npm run dev
```

### 2. Adding New Components

```bash
# Create component file
touch components/ui/NewComponent.tsx

# Use TypeScript and follow existing patterns
# Export as default
```

### 3. Adding New Pages

```bash
# Create page directory
mkdir app/new-page

# Create page.tsx
touch app/new-page/page.tsx

# Follow App Router conventions
```

### 4. Testing

```bash
# Manual testing:
npm run dev
# Test in browser at http://localhost:3001

# Build test:
npm run build
npm start
```

### 5. Code Quality

```bash
# Linting
npm run lint

# Type checking
npx tsc --noEmit

# Format code (if prettier is added)
npx prettier --write .
```

## Production Deployment

### Option 1: Vercel (Recommended)

1. Push code to GitHub
2. Connect repo to Vercel
3. Set environment variables
4. Deploy automatically

### Option 2: Docker

```bash
# Build image
docker build -t market-intel-frontend .

# Run container
docker run -p 3001:3000 \
  -e NEXT_PUBLIC_API_URL=https://api.example.com/api/v1 \
  market-intel-frontend
```

### Option 3: Manual

```bash
# Build
npm run build

# Start
npm start
```

## Next Steps

### Recommended Features to Add

1. **Email Verification Flow**
   - Add verification page
   - Handle verification tokens
   - Show verification status

2. **Password Reset**
   - Forgot password page
   - Reset token handling
   - Password update form

3. **Subscription Management**
   - Stripe integration
   - Plan selection
   - Payment processing

4. **Advanced Filters**
   - Date range picker
   - Symbol search
   - Custom watchlists

5. **Performance Tracking**
   - Historical digest view
   - Signal performance metrics
   - Trade history

6. **Real-time Updates**
   - WebSocket integration
   - Live signal notifications
   - Push notifications

7. **Mobile App**
   - React Native version
   - Native notifications
   - Offline support

## Support

For issues or questions:
- Check this guide first
- Review README.md
- Check browser console for errors
- Review backend logs
- GitHub Issues

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [React Documentation](https://react.dev/)
