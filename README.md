# TradeTheHype

A modern, full-stack SaaS platform delivering AI-enhanced market intelligence and trading insights. Built with FastAPI, React, and PostgreSQL.

## Overview

TradeTheHype provides curated, actionable market intelligence through:

- **Daily Market Digest**: AI-curated trading signals with "WHY THIS MATTERS" and "HOW TO TRADE" guidance
- **Real-time Analysis**: ML-enhanced sentiment analysis and pattern recognition
- **Trade Alerts**: High-confidence trading opportunities with detailed execution strategies
- **Performance Tracking**: Signal performance monitoring and analytics

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   React     │────▶│   FastAPI    │────▶│ PostgreSQL  │
│   Frontend  │     │   Backend    │     │  Database   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ├─────▶ News APIs
                           ├─────▶ Market Data
                           └─────▶ ML Models
```

## Tech Stack

### Backend
- **FastAPI**: Modern, async Python web framework
- **SQLAlchemy**: Async ORM with PostgreSQL
- **Alembic**: Database migrations
- **Pydantic**: Data validation and settings management
- **JWT**: Token-based authentication
- **Bcrypt**: Password hashing

### Database
- **PostgreSQL 16**: Primary database
- **Redis**: Caching layer (optional)

### Intelligence Engine
- **News Collectors**: RSS feeds + NewsAPI integration
- **Sentiment Analysis**: TextBlob + VADER NLP
- **ML Enhancement**: Pattern recognition and confidence scoring
- **Market Context**: VIX regime detection and sector analysis

## Project Structure

```
tradethehype/
├── backend/
│   ├── alembic/                 # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── app/
│   │   ├── api/                 # API endpoints
│   │   │   ├── auth.py          # Authentication routes
│   │   │   ├── digest.py        # Digest routes
│   │   │   └── dependencies.py  # Auth dependencies
│   │   ├── core/                # Core business logic
│   │   │   ├── news_collector.py
│   │   │   ├── sentiment_analyzer.py
│   │   │   ├── ml_digest_enhancer.py
│   │   │   └── digest_generator.py
│   │   ├── models/              # Database models
│   │   │   ├── user.py
│   │   │   ├── subscription.py
│   │   │   ├── signal.py
│   │   │   └── signal_performance.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── user.py
│   │   │   ├── subscription.py
│   │   │   └── digest.py
│   │   ├── services/            # Business logic
│   │   │   ├── auth.py
│   │   │   └── digest_service.py
│   │   ├── config.py            # Settings management
│   │   ├── database.py          # DB configuration
│   │   └── main.py              # Application entry point
│   ├── tests/                   # Test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                    # React frontend (TBD)
├── infrastructure/              # IaC configs (TBD)
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Docker & Docker Compose (optional)

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd tradethehype
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Verify services are running**
```bash
docker-compose ps
```

5. **Access the API**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Option 2: Local Development

1. **Set up PostgreSQL**
```bash
# Install PostgreSQL 16
# Create database
createdb market_intelligence
```

2. **Set up Python environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp ../.env.example ../.env
# Edit .env with your database credentials
```

4. **Run migrations**
```bash
alembic upgrade head
```

5. **Start the backend**
```bash
uvicorn app.main:app --reload
```

6. **Access the API**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password_123",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password_123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>

Response:
{
  "id": 1,
  "email": "user@example.com",
  "subscription_tier": "free",
  "is_active": true,
  "is_verified": false,
  "full_name": "John Doe",
  "created_at": "2025-10-14T11:40:00Z"
}
```

### Digest Endpoints

#### Get Daily Digest
```http
GET /api/v1/digest/daily?max_items=20&hours_lookback=24&enable_ml=true
Authorization: Bearer <access_token>

Response:
{
  "generated_at": "2025-10-14T11:40:00Z",
  "items": [
    {
      "id": 1,
      "symbol": "AAPL",
      "title": "Apple announces new product line",
      "summary": "Strong bullish catalyst for AAPL",
      "explanation": "WHY THIS MATTERS: New product launches historically drive 5-10% gains...",
      "how_to_trade": "HOW TO TRADE: Enter at market open, target $180, stop at $172...",
      "sentiment_score": 0.85,
      "confidence_score": 0.92,
      "priority": "high",
      "category": "trade_alert",
      "source": "NewsAPI",
      "metadata": {},
      "created_at": "2025-10-14T11:30:00Z"
    }
  ],
  "total_items": 15,
  "market_context": {
    "market_trend": "bullish",
    "major_indices": {...}
  },
  "vix_regime": {
    "vix_level": 15.5,
    "regime": "LOW_VOL",
    "description": "Low volatility - favorable for momentum strategies"
  }
}
```

## Database Schema

### Users Table
- `id`: Primary key
- `email`: Unique email address
- `hashed_password`: Bcrypt hashed password
- `subscription_tier`: free | pro | premium
- `is_active`: Account active status
- `is_verified`: Email verification status
- `full_name`: User's full name
- `created_at`, `updated_at`: Timestamps

### Subscriptions Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `stripe_subscription_id`: Stripe subscription ID
- `status`: active | canceled | past_due
- `plan`: Subscription plan name
- `current_period_start`, `current_period_end`: Billing period
- `created_at`, `updated_at`: Timestamps

### Signals Table
- `id`: Primary key
- `symbol`: Stock ticker symbol
- `title`: Signal headline
- `summary`: Brief summary
- `explanation`: WHY THIS MATTERS content
- `how_to_trade`: HOW TO TRADE guidance
- `sentiment_score`: -1 to 1
- `confidence_score`: 0 to 1
- `priority`: high | medium | low
- `category`: trade_alert | watch_list | market_context
- `source`: Data source
- `metadata`: JSON metadata
- `created_at`, `expires_at`: Timestamps

### Signal Performance Table
- `id`: Primary key
- `signal_id`: Foreign key to signals
- `entry_price`, `exit_price`: Trade prices
- `entry_time`, `exit_time`: Trade timing
- `pnl`, `pnl_percentage`: Profit/loss metrics
- `outcome`: win | loss | breakeven
- `max_gain`, `max_loss`: Performance metrics
- `notes`: Additional notes
- `created_at`: Timestamp

## Development

### Running Tests
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

### Database Migrations

#### Create a new migration
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

#### Apply migrations
```bash
alembic upgrade head
```

#### Rollback migrations
```bash
alembic downgrade -1
```

### Code Formatting
```bash
cd backend
black app/ tests/
flake8 app/ tests/
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options. Key variables:

**Required:**
- `SECRET_KEY`: JWT secret key (min 32 characters)
- `DATABASE_URL`: PostgreSQL connection string

**Optional:**
- `NEWSAPI_KEY`: NewsAPI.org API key (100 requests/day free)
- `ALPHA_VANTAGE_API_KEY`: Alpha Vantage API key (25 calls/day free)
- `STRIPE_API_KEY`: Stripe API key for subscriptions
- `REDIS_URL`: Redis connection string for caching

### Subscription Tiers

- **Free**: 10 digest items, basic features
- **Pro**: 50 digest items, category filtering, ML enhancement
- **Premium**: Unlimited items, all features, priority support

## Deployment

### Docker Production

1. **Build production image**
```bash
docker build -t tradethehype:latest ./backend
```

2. **Run with production compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Cloud Deployment

The platform is designed for deployment on:
- **AWS**: ECS/Fargate + RDS PostgreSQL
- **Google Cloud**: Cloud Run + Cloud SQL
- **Azure**: Container Apps + PostgreSQL

Infrastructure as Code (IaC) configurations coming soon in `infrastructure/` directory.

## API Rate Limits

| Tier | Requests/Minute | Daily Digest Calls |
|------|----------------|-------------------|
| Free | 10 | 10 |
| Pro | 100 | 100 |
| Premium | 1000 | Unlimited |

## Security

- **Password Hashing**: Bcrypt with salt
- **JWT Tokens**: HS256 algorithm, configurable expiration
- **HTTPS**: Required in production
- **SQL Injection**: Protected via SQLAlchemy ORM
- **CORS**: Configurable origins
- **Input Validation**: Pydantic schemas

## Roadmap

### Phase 1: Backend Foundation ✅
- [x] FastAPI application structure
- [x] Database models and migrations
- [x] Authentication system
- [x] Core intelligence modules
- [x] Digest API endpoints

### Phase 2: Frontend (In Progress)
- [ ] React application setup
- [ ] Authentication UI
- [ ] Dashboard and digest viewer
- [ ] User settings and profile
- [ ] Responsive mobile design

### Phase 3: Intelligence Enhancement
- [ ] Real-time news ingestion
- [ ] Advanced ML models
- [ ] Performance analytics dashboard
- [ ] Alert notifications (email, SMS, push)

### Phase 4: Production Features
- [ ] Stripe subscription integration
- [ ] Webhook handlers
- [ ] Admin dashboard
- [ ] Analytics and monitoring
- [ ] Comprehensive testing

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run tests and linting
5. Submit a pull request

## License

Proprietary - All rights reserved

## Support

For support, please contact:
- Email: support@tradethehype.com
- Documentation: https://docs.tradethehype.com
- Issues: GitHub Issues

## Acknowledgments

Built with:
- FastAPI
- SQLAlchemy
- PostgreSQL
- React (coming soon)
- And many other open-source libraries
