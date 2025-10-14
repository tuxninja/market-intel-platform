# Quick Start Guide

## 🚀 Get Running in 3 Steps

### Step 1: Install Dependencies
```bash
cd /Users/jasonriedel/PyCharmProjects/market-intel-platform/frontend
npm install
```

### Step 2: Configure Environment
```bash
cp .env.local.example .env.local
```

The default settings work with backend at `http://localhost:8000`

### Step 3: Start Dev Server
```bash
# Terminal 1: Start backend
cd ../backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd ../frontend
npm run dev
```

## ✅ You're Done!

Open http://localhost:3000 in your browser.

## 🔑 Test Account

1. Go to http://localhost:3000
2. Click "Get Started"
3. Register with:
   - Email: `test@example.com`
   - Password: `password123`
   - Name: `Test User`
4. You'll be logged in automatically

## 📋 What You Can Do

- ✅ View landing page with features and pricing
- ✅ Register and login
- ✅ Access dashboard
- ✅ View daily digest (if backend has data)
- ✅ Filter and sort signals
- ✅ Update profile in settings
- ✅ Logout

## 🐛 Common Issues

**Can't connect to backend?**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Should return: {"status":"healthy",...}
```

**Authentication issues?**
```bash
# Clear browser storage
# Open DevTools > Application > Local Storage > Clear
```

**Build issues?**
```bash
rm -rf .next node_modules
npm install
```

## 📚 More Help

- **Detailed Setup**: See `SETUP.md`
- **Full Documentation**: See `README.md`
- **Project Overview**: See `FRONTEND_SUMMARY.md`

## 🎯 URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

## 🔧 Quick Commands

```bash
# Development
npm run dev          # Start dev server
npm run build        # Build for production
npm start            # Start production server
npm run lint         # Run linter

# Check types
npx tsc --noEmit

# Clear cache
rm -rf .next
```

That's it! You're ready to go. 🎉
