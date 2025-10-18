# 🔧 Technical Documentation - Market Intelligence Platform V1.0

**Last Updated**: October 17, 2025
**Version**: 1.0.0

---

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Database Schema](#database-schema)
3. [API Reference](#api-reference)
4. [Authentication Flow](#authentication-flow)
5. [Email System](#email-system)
6. [Frontend Architecture](#frontend-architecture)
7. [Deployment Architecture](#deployment-architecture)
8. [Environment Variables](#environment-variables)
9. [File Structure](#file-structure)
10. [Code Patterns](#code-patterns)

---

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Browser                              │
│  - React Components                                                  │
│  - Next.js App Router                                                │
│  - Axios HTTP Client                                                 │
└──────────────────────┬───────────────────────────────────────────────┘
                       │ HTTPS
                       │
┌──────────────────────▼───────────────────────────────────────────────┐
│                    AWS App Runner (Frontend)                         │
│  - Next.js Production Build                                          │
│  - Static Assets                                                     │
│  - Server-Side Rendering                                             │
└──────────────────────┬───────────────────────────────────────────────┘
                       │ HTTP/REST API
                       │
┌──────────────────────▼───────────────────────────────────────────────┐
│                    AWS App Runner (Backend)                          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  FastAPI Application                                        │    │
│  │  ├── Routers (auth, digest, debug)                         │    │
│  │  ├── Services (AuthService, EmailService)                  │    │
│  │  ├── Models (SQLAlchemy ORM)                               │    │
│  │  ├── Schemas (Pydantic validation)                         │    │
│  │  └── Database Session Management                           │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────┬────────────────────────┬─────────────────────────┘
                   │                        │
                   │                        │
        ┌──────────▼──────────┐  ┌─────────▼──────────┐
        │  Supabase           │  │  SendGrid SMTP     │
        │  PostgreSQL         │  │  Email Service     │
        │  (Database)         │  │                    │
        └─────────────────────┘  └────────────────────┘
```

### Component Interaction

1. **Client → Frontend**
   - User navigates to https://dvnzmpmkt3.us-east-1.awsapprunner.com
   - Next.js serves pre-rendered or client-side rendered pages
   - User interacts with React components

2. **Frontend → Backend**
   - Axios makes HTTP requests to https://4ndyc6baea.us-east-1.awsapprunner.com/api/v1
   - JWT token included in `Authorization` header
   - CORS validation checks origin

3. **Backend → Database**
   - SQLAlchemy async engine connects to PostgreSQL
   - Queries executed via ORM models
   - Connection pooling for performance

4. **Backend → Email**
   - SendGrid SMTP client sends emails
   - Template rendering with Jinja2
   - Async email delivery

---

## 🗄️ Database Schema

### Tables

#### `users`

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription ON users(subscription_tier);
```

**Fields**:
- `id`: Auto-incrementing primary key
- `email`: Unique email address (used for login)
- `hashed_password`: Bcrypt hash of password (72 byte max)
- `full_name`: User's display name
- `is_active`: Account activation status
- `is_verified`: Email verification status
- `subscription_tier`: Subscription level (free, pro, enterprise)
- `created_at`: Timestamp of account creation
- `updated_at`: Timestamp of last update

**Constraints**:
- Email must be unique
- Password hash stored as text (bcrypt generates variable-length hashes)

### Entity Relationships

Currently a single table design. Future expansions:

```
users (1) ──── (N) user_settings
users (1) ──── (N) user_sessions
users (1) ──── (N) email_logs
users (N) ──── (N) organizations (through user_organizations)
```

---

## 🔌 API Reference

### Base URL
**Production**: `https://4ndyc6baea.us-east-1.awsapprunner.com/api/v1`
**Local**: `http://localhost:8000/api/v1`

### Authentication Endpoints

#### POST `/auth/register`
Create a new user account.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "subscription_tier": "free",
  "created_at": "2025-10-17T12:00:00Z"
}
```

**Errors**:
- `400 Bad Request`: Email already registered
- `422 Unprocessable Entity`: Invalid input format

---

#### POST `/auth/login`
Authenticate user and receive JWT tokens.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Token Payload**:
```json
{
  "sub": "1",                    // User ID as string
  "email": "user@example.com",
  "exp": 1697547600,            // Expiration timestamp
  "type": "access"              // Token type
}
```

**Errors**:
- `401 Unauthorized`: Invalid credentials

---

#### GET `/auth/me`
Get current authenticated user information.

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "subscription_tier": "free",
  "created_at": "2025-10-17T12:00:00Z"
}
```

**Errors**:
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Inactive user account

---

#### POST `/auth/refresh`
Refresh access token using refresh token.

**Request**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors**:
- `401 Unauthorized`: Invalid refresh token

---

#### PUT `/auth/me`
Update current user information.

**Headers**:
```
Authorization: Bearer <access_token>
```

**Request**:
```json
{
  "full_name": "Jane Doe"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "is_active": true,
  "is_verified": false,
  "subscription_tier": "free",
  "created_at": "2025-10-17T12:00:00Z"
}
```

---

### Digest Endpoints

#### POST `/digest/send`
Send daily digest email to specified address.

**Headers**:
```
Authorization: Bearer <access_token>
```

**Request**:
```json
{
  "email": "recipient@example.com"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Digest email sent successfully",
  "recipient": "recipient@example.com"
}
```

**Errors**:
- `500 Internal Server Error`: Email sending failed

---

### Debug Endpoints (Development Only)

#### POST `/debug/token`
Validate and inspect JWT token payload.

**Request**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "payload": {
    "sub": "1",
    "email": "user@example.com",
    "exp": 1697547600,
    "type": "access"
  },
  "secret_key_length": 36,
  "algorithm": "HS256"
}
```

---

#### POST `/debug/decode`
Debug full authentication flow (decode token + user lookup).

**Request**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "step": "decode_complete",
  "token_data": {
    "user_id": 1,
    "user_id_type": "int",
    "email": "user@example.com"
  },
  "user_lookup": {
    "id": 1,
    "email": "user@example.com",
    "is_active": true
  }
}
```

---

### Health Check

#### GET `/health`
System health check endpoint.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "app": "Market Intelligence Platform",
  "version": "1.0.0",
  "environment": "production"
}
```

---

## 🔐 Authentication Flow

### Registration Flow

```
┌──────────┐     POST /auth/register      ┌──────────┐
│  Client  │────────────────────────────►│  Backend │
│          │                              │          │
│          │                              │ 1. Validate email format
│          │                              │ 2. Check if email exists
│          │                              │ 3. Hash password (bcrypt)
│          │                              │ 4. Create user in DB
│          │◄────────────────────────────│ 5. Return user object
│          │   201 Created, User Object   │          │
└──────────┘                              └────┬─────┘
                                               │
                                               ▼
                                         ┌──────────┐
                                         │ Database │
                                         │ (users)  │
                                         └──────────┘
```

**Code Flow** (backend/app/api/auth.py):
```python
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. Check if user exists
    existing_user = await AuthService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Create user (password hashed automatically)
    user = await AuthService.create_user(db, user_data)
    return user
```

### Login Flow

```
┌──────────┐     POST /auth/login         ┌──────────┐
│  Client  │────────────────────────────►│  Backend │
│          │                              │          │
│          │                              │ 1. Lookup user by email
│          │                              │ 2. Verify password hash
│          │                              │ 3. Generate JWT tokens
│          │                              │    - Access (30 min)
│          │                              │    - Refresh (7 days)
│          │◄────────────────────────────│ 4. Return tokens
│          │   200 OK, Tokens             │          │
│          │                              └──────────┘
│ 5. Store tokens in memory/localStorage
│
└──────────┘
```

**Password Verification**:
```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')[:72]  # Bcrypt 72-byte limit
    hashed_bytes = hashed_password.encode('utf-8')

    try:
        # Try bcrypt first
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except (ValueError, AttributeError):
        # Fallback to passlib for legacy hashes
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)
```

**JWT Token Generation**:
```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=30))

    to_encode.update({
        "exp": int(expire.timestamp()),  # Unix timestamp
        "type": "access"
    })

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
```

### Protected Endpoint Flow

```
┌──────────┐     GET /auth/me            ┌──────────┐
│  Client  │───────────────────────────►│  Backend │
│          │  Authorization: Bearer <T>  │          │
│          │                             │ 1. Extract token from header
│          │                             │ 2. Decode JWT
│          │                             │ 3. Validate signature
│          │                             │ 4. Check expiration
│          │                             │ 5. Convert sub to int
│          │                             │ 6. Lookup user in DB
│          │                             │ 7. Verify user is active
│          │◄────────────────────────────│ 8. Return user object
│          │   200 OK, User Object       │          │
└──────────┘                             └──────────┘
```

**Token Validation** (backend/app/api/dependencies.py):
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials

    # Decode token
    token_data = AuthService.decode_token(token)
    if token_data is None or token_data.user_id is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    # Lookup user
    user = await AuthService.get_user_by_id(db, token_data.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    # Check if active
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user account")

    return user
```

---

## 📧 Email System

### Architecture

```
┌──────────────────┐
│  Trigger Source  │
│  - API Endpoint  │
│  - Cron Job      │
│  - CLI Script    │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  EmailService                       │
│  ┌──────────────────────────────┐   │
│  │ 1. Load environment config   │   │
│  │ 2. Connect to SendGrid SMTP  │   │
│  │ 3. Render HTML template      │   │
│  │ 4. Construct email message   │   │
│  │ 5. Send via SMTP             │   │
│  └──────────────────────────────┘   │
└─────────────┬───────────────────────┘
              │
              ▼
      ┌──────────────┐
      │  SendGrid    │
      │  SMTP Relay  │
      └──────┬───────┘
             │
             ▼
      ┌──────────────┐
      │  Recipient   │
      │  Inbox       │
      └──────────────┘
```

### Email Template

Located at: `backend/templates/daily_digest_email.html`

**Variables Available**:
- `user_name`: Recipient's name
- `date`: Current date
- `market_snapshot`: Market data object
- `news_articles`: List of article objects
- `unsubscribe_url`: Unsubscribe link

**Sample Rendering**:
```python
from jinja2 import Environment, FileSystemLoader

# Load template
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('daily_digest_email.html')

# Render with data
html_content = template.render(
    user_name="John Doe",
    date="October 17, 2025",
    market_snapshot={"sp500": "+1.2%", "nasdaq": "+0.8%"},
    news_articles=[
        {"title": "Article 1", "url": "https://..."}
    ]
)
```

### Sending Process

**Via API** (backend/app/api/digest.py):
```python
@router.post("/send")
async def send_digest(email: str):
    # 1. Validate email format
    # 2. Fetch market data
    # 3. Render template
    # 4. Send email
    # 5. Log result
    pass
```

**Via CLI** (backend/scripts/send_daily_digest.py):
```bash
cd backend
python scripts/send_daily_digest.py --email recipient@example.com
```

**Environment Requirements**:
```bash
export SMTP_USERNAME="apikey"
export SMTP_PASSWORD="SG.xxxxx"
export DATABASE_URL="postgresql://..."
```

---

## 🎨 Frontend Architecture

### Next.js App Router Structure

```
frontend/app/
├── layout.tsx              # Root layout (global)
├── page.tsx                # Home page (/)
├── login/
│   └── page.tsx            # Login page (/login)
├── register/
│   └── page.tsx            # Register page (/register)
├── dashboard/
│   └── page.tsx            # Dashboard (/dashboard)
└── globals.css             # Global styles
```

### Component Hierarchy

```
Layout (app/layout.tsx)
  ├── Navbar
  ├── {children}            # Page content
  └── Footer

Page (app/page.tsx)
  ├── Hero Section
  ├── Features Grid
  └── CTA Section

Login Page (app/login/page.tsx)
  └── LoginForm
      ├── Email Input
      ├── Password Input
      └── Submit Button

Dashboard (app/dashboard/page.tsx)
  ├── Header
  ├── MarketSnapshot
  │   ├── MetricCard (SP500)
  │   ├── MetricCard (NASDAQ)
  │   └── MetricCard (DOW)
  └── NewsArticles
      └── ArticleCard[]
```

### State Management

**Local State** (React hooks):
```typescript
// Login form state
const [email, setEmail] = useState('');
const [password, setPassword] = useState('');
const [error, setError] = useState('');
const [loading, setLoading] = useState(false);
```

**Authentication State** (localStorage):
```typescript
// Store token after login
localStorage.setItem('access_token', token);

// Retrieve for API calls
const token = localStorage.getItem('access_token');
```

**API Client** (lib/api.ts):
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### Routing

**Public Routes**:
- `/` - Home page
- `/login` - Login page
- `/register` - Registration page

**Protected Routes** (require authentication):
- `/dashboard` - User dashboard

**Route Protection**:
```typescript
// app/dashboard/page.tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Dashboard() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  // ... dashboard content
}
```

---

## 🚀 Deployment Architecture

### AWS Infrastructure

```
┌─────────────────────────────────────────────────────────────┐
│                      AWS Cloud (us-east-1)                  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  ECR (Elastic Container Registry)                      │  │
│  │  ├── market-intel-backend:latest                       │  │
│  │  └── market-intel-frontend:latest                      │  │
│  └──────────────┬──────────────────┬─────────────────────┘  │
│                 │                  │                         │
│  ┌──────────────▼────────┐  ┌──────▼──────────────────┐     │
│  │  App Runner Service   │  │  App Runner Service     │     │
│  │  (Backend)            │  │  (Frontend)             │     │
│  │                       │  │                         │     │
│  │  - Auto-scaling       │  │  - Auto-scaling         │     │
│  │  - Load balancing     │  │  - Load balancing       │     │
│  │  - HTTPS              │  │  - HTTPS                │     │
│  │  - Health checks      │  │  - Health checks        │     │
│  └───────────────────────┘  └─────────────────────────┘     │
│                                                               │
└─────────────────────────────────────────────────────────────┘

External Services:
┌──────────────────┐
│  Supabase        │  PostgreSQL Database
│  (PostgreSQL)    │  - Hosted in cloud
└──────────────────┘  - Connection pooling

┌──────────────────┐
│  SendGrid        │  Email Delivery
│  (SMTP)          │  - Transactional emails
└──────────────────┘  - Analytics
```

### Docker Images

**Backend Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create cache directory
RUN mkdir -p /app/.cache

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile**:
```dockerfile
FROM node:18-alpine AS base

# Dependencies
FROM base AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Builder
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Runner
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

### CI/CD Pipeline

**GitHub Actions Workflow** (.github/workflows/test.yml):
```yaml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          cd backend
          pip install -r requirements.txt
          pytest

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: |
          cd frontend
          npm install
          npm run lint
          npm run build
```

---

## 🔑 Environment Variables

### Backend (.env)

```bash
# Application
APP_NAME="Market Intelligence Platform"
APP_VERSION="1.0.0"
ENVIRONMENT="production"  # or "development"
DEBUG="false"  # "true" for development

# API Configuration
API_V1_PREFIX="/api/v1"

# Security
SECRET_KEY="<32+ character random string>"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES="30"
REFRESH_TOKEN_EXPIRE_DAYS="7"

# CORS
CORS_ORIGINS="https://dvnzmpmkt3.us-east-1.awsapprunner.com,http://localhost:3000"

# Database
DATABASE_URL="postgresql://user:password@host:5432/dbname"

# Email (SendGrid)
SMTP_SERVER="smtp.sendgrid.net"
SMTP_PORT="587"
SMTP_USERNAME="apikey"
SMTP_PASSWORD="SG.xxxxxxxxxxxxxx"
SMTP_FROM_EMAIL="noreply@yourdomain.com"
SMTP_FROM_NAME="Market Intelligence Platform"
```

### Frontend (.env.production)

```bash
# API URL (must be set at build time)
NEXT_PUBLIC_API_URL="https://4ndyc6baea.us-east-1.awsapprunner.com/api/v1"
```

**Important**: Next.js environment variables prefixed with `NEXT_PUBLIC_` are embedded in the frontend bundle at build time.

---

## 📁 File Structure

```
market-intel-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI application entry
│   │   ├── config.py                # Settings/configuration
│   │   ├── database.py              # Database connection
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # Auth endpoints
│   │   │   ├── digest.py            # Email digest endpoints
│   │   │   ├── debug.py             # Debug endpoints
│   │   │   └── dependencies.py      # Shared dependencies
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── user.py              # User model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── user.py              # Pydantic schemas
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── auth.py              # Authentication logic
│   │       └── email.py             # Email sending logic
│   ├── scripts/
│   │   └── send_daily_digest.py     # CLI email script
│   ├── templates/
│   │   └── daily_digest_email.html  # Email template
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_auth.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx               # Root layout
│   │   ├── page.tsx                 # Home page
│   │   ├── globals.css              # Global styles
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   └── dashboard/
│   │       └── page.tsx
│   ├── components/
│   │   └── ...                      # Reusable components
│   ├── lib/
│   │   └── api.ts                   # API client
│   ├── public/
│   │   └── ...                      # Static assets
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.js
│   ├── .env.local                   # Local development
│   └── .env.production              # Production build
│
├── .github/
│   └── workflows/
│       └── test.yml                 # CI/CD pipeline
│
└── Documentation/
    ├── V1.0_RELEASE.md              # Release notes
    ├── TECHNICAL_DOCUMENTATION.md   # This file
    ├── DEPLOYMENT_SUMMARY.md
    └── START_HERE.md
```

---

## 🎯 Code Patterns

### Backend Patterns

**Dependency Injection**:
```python
# Use FastAPI's Depends() for DI
@router.get("/users/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return current_user
```

**Error Handling**:
```python
# Raise HTTPException for errors
if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )
```

**Async/Await**:
```python
# All database operations are async
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
```

**Schema Validation**:
```python
# Pydantic models for request/response
class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    password: str = Field(min_length=8)
    full_name: str
```

### Frontend Patterns

**Client Components** (interactive):
```typescript
'use client';  // Directive for client-side rendering

import { useState } from 'react';

export default function LoginForm() {
  const [email, setEmail] = useState('');
  // ... interactive logic
}
```

**Server Components** (static):
```typescript
// Default for Next.js 14 App Router
export default function Page() {
  // No client-side JS needed
  return <div>Static Content</div>;
}
```

**API Calls**:
```typescript
// Use try/catch for error handling
try {
  const response = await api.post('/auth/login', { email, password });
  const { access_token } = response.data;
  localStorage.setItem('access_token', access_token);
  router.push('/dashboard');
} catch (error) {
  setError('Login failed');
}
```

---

**Last Updated**: October 17, 2025
**Version**: 1.0.0
