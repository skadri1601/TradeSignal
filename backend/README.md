# TradeSignal Backend

FastAPI-based backend service for the TradeSignal platform. Provides RESTful APIs for insider trading intelligence, congressional trades, user authentication, billing, and real-time notifications.

## Architecture

### Tech Stack
- **FastAPI** - Async web framework with automatic OpenAPI docs
- **SQLAlchemy** - ORM for database interactions
- **PostgreSQL** - Primary relational database
- **Redis** - Caching and rate limiting
- **Celery** - Distributed task queue for background jobs
- **Alembic** - Database migrations (if enabled)
- **Pydantic** - Data validation and serialization
- **Prometheus** - Metrics and monitoring

### Project Structure
```
backend/
├── app/
│   ├── core/                   # Core utilities
│   │   ├── celery_app.py      # Celery configuration
│   │   ├── limiter.py         # Rate limiting
│   │   ├── logging_config.py   # Structured logging
│   │   ├── redis_cache.py     # Redis caching
│   │   └── security.py        # Auth utilities
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py            # User and authentication
│   │   ├── trade.py           # Insider trades
│   │   ├── congressional_trade.py
│   │   ├── company.py
│   │   ├── insider.py
│   │   ├── subscription.py    # Billing models
│   │   ├── alert.py
│   │   ├── payment.py
│   │   ├── ticket.py
│   │   └── ...
│   ├── routers/                # API endpoints
│   │   ├── auth.py            # Authentication
│   │   ├── trades.py          # Insider trades
│   │   ├── congressional_trades.py
│   │   ├── companies.py
│   │   ├── insiders.py
│   │   ├── billing.py         # Stripe integration
│   │   ├── news.py
│   │   ├── fed.py             # Federal Reserve
│   │   ├── admin.py
│   │   ├── health.py
│   │   └── ...
│   ├── schemas/                # Pydantic schemas
│   │   ├── trade.py
│   │   ├── company.py
│   │   ├── insider.py
│   │   └── ...
│   ├── services/               # Business logic
│   │   ├── scraper_service.py
│   │   ├── form4_parser.py
│   │   ├── congressional_scraper.py
│   │   ├── stock_price_service.py
│   │   ├── notification_service.py
│   │   ├── tier_service.py
│   │   └── ...
│   ├── tasks/                  # Celery tasks
│   │   └── stock_tasks.py
│   ├── middleware/
│   │   └── https_redirect.py
│   ├── config.py               # Settings management
│   ├── database.py             # DB connection
│   └── main.py                 # Application entry
├── tests/                      # Unit tests
├── requirements.txt
├── Dockerfile
└── .env.example
```

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register` - Create new user account
- `POST /login` - JWT token authentication
- `POST /forgot-password` - Request password reset
- `POST /reset-password` - Complete password reset
- `GET /me` - Get current user profile
- `PUT /me` - Update user profile

### Insider Trades (`/api/v1/trades`)
- `GET /` - List all insider trades with filters
- `GET /{id}` - Get specific trade details
- `POST /scrape` - Trigger manual scrape (admin)

### Congressional Trades (`/api/v1/congressional-trades`)
- `GET /` - List congressional trades with filters
- `GET /{id}` - Get specific congressional trade
- `GET /congresspeople` - List all congress members

### Companies (`/api/v1/companies`)
- `GET /` - List companies with search
- `GET /{ticker}` - Get company details
- `GET /{ticker}/trades` - Get trades for company
- `GET /{ticker}/insiders` - Get insiders for company

### Insiders (`/api/v1/insiders`)
- `GET /` - List insiders
- `GET /{id}` - Get insider profile
- `GET /{id}/trades` - Get trades by insider

### Billing (`/api/v1/billing`)
- `POST /create-checkout-session` - Create Stripe checkout
- `POST /webhook` - Stripe webhook handler
- `GET /subscription` - Get current subscription
- `POST /cancel-subscription` - Cancel subscription
- `GET /orders` - Get payment history

### News (`/api/v1/news`)
- `GET /` - Get financial news feed
- `GET /{id}` - Get specific news article

### Federal Reserve (`/api/v1/fed`)
- `GET /calendar` - Get Fed economic calendar
- `GET /events` - List upcoming events

### Admin (`/api/v1/admin`)
- `GET /users` - List all users (superuser only)
- `PUT /users/{id}` - Update user (superuser only)
- `DELETE /users/{id}` - Delete user (superuser only)
- `GET /stats` - System statistics

### Health & Monitoring
- `GET /api/v1/health` - Health check
- `GET /metrics` - Prometheus metrics

## Database Models

### Core Models
- **User** - User accounts with roles (free, pro, enterprise, admin)
- **Subscription** - Stripe subscription data
- **Payment** - Payment history
- **Trade** - Insider trading transactions
- **CongressionalTrade** - Political stock transactions
- **Company** - Company profiles
- **Insider** - Insider profiles
- **Alert** - User alerts and notifications
- **Ticket** - Support tickets

## Service Layer

### Scraper Service
- Automated SEC Form 4 scraping
- Scheduled scraping with Celery
- Configurable scrape hours and frequency
- Duplicate detection

### Congressional Scraper
- Political stock transaction scraping
- Congress member profile tracking

### Stock Price Service
- Real-time stock price fetching
- Price history and charts
- Market data integration

### Notification Service
- Multi-channel alerts (email, push)
- Configurable alert rules
- Priority-based notifications

### Tier Service
- Feature access control by subscription tier
- Rate limiting by tier
- Usage tracking

## Authentication & Security

### JWT Authentication
- Access tokens with configurable expiry
- Refresh token support
- Password hashing with bcrypt

### Rate Limiting
- Tiered rate limits (free: 100/hour, pro: 1000/hour, enterprise: unlimited)
- Redis-backed rate limiter
- Per-endpoint customization

### Security Features
- CORS configuration
- HTTPS redirect middleware (production)
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (Pydantic)
- Secret management via environment variables

## Background Tasks

### Celery Workers
- Scheduled scraping (hourly during market hours)
- Stock price updates
- Alert processing
- Email sending

### Task Configuration
```python
# Scraper runs every hour from 9 AM to 4 PM ET
SCRAPER_SCHEDULE_HOURS = "9-16"
SCRAPER_TIMEZONE = "America/New_York"
```

## Environment Variables

### Required
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/tradesignal

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_PRO=price_...
STRIPE_PRICE_ID_ENTERPRISE=price_...

# SEC API
SEC_API_KEY=your-sec-api-key
```

### Optional
```env
# Feature Flags
ENABLE_AI_INSIGHTS=true
ENABLE_WEBHOOKS=true
ENABLE_EMAIL_ALERTS=true
ENABLE_PUSH_NOTIFICATIONS=true
SCHEDULER_ENABLED=true

# Logging
LOG_LEVEL=INFO
USE_JSON_LOGGING=false

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Rate Limiting
RATE_LIMIT_FREE_TIER=100
RATE_LIMIT_PRO_TIER=1000
```

## Development

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### Running Locally
```bash
# Run FastAPI server
uvicorn app.main:app --reload --port 8000

# Run Celery worker (separate terminal)
celery -A app.core.celery_app worker --loglevel=info

# Run Celery beat scheduler (separate terminal)
celery -A app.core.celery_app beat --loglevel=info
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Testing

### Run Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_trades_api.py

# With coverage
pytest --cov=app --cov-report=html

# Verbose output
pytest -v
```

### Test Structure
```
tests/
├── conftest.py           # Fixtures
├── test_trades_api.py
├── test_tier_service.py
├── test_form4_parser.py
└── ...
```

## Deployment

### Docker
```bash
# Build image
docker build -t tradesignal-backend .

# Run container
docker run -p 8000:8000 --env-file .env tradesignal-backend
```

### Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Restart service
docker-compose restart backend
```

### Production Checklist
- [ ] Set `DEBUG=false`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up Redis for production
- [ ] Enable HTTPS redirect
- [ ] Configure CORS origins
- [ ] Set up logging aggregation
- [ ] Enable Prometheus monitoring
- [ ] Configure backups
- [ ] Set up health checks
- [ ] Use environment-specific configs

## Monitoring

### Prometheus Metrics
Available at `/metrics`:
- Request count and latency
- Database connection pool stats
- Celery task metrics
- Custom business metrics

### Logging
- Structured JSON logging in production
- Human-readable logs in development
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Health Checks
- Database connectivity
- Redis connectivity
- Disk space
- Memory usage
- API endpoint: `/api/v1/health`

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check DATABASE_URL is correct
echo $DATABASE_URL
```

### Redis Connection Issues
```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
redis-cli ping
```

### Scraper Not Running
```bash
# Check scheduler is enabled
echo $SCHEDULER_ENABLED  # should be 'true'

# Check Celery beat is running
celery -A app.core.celery_app inspect active
```

## Contributing

1. Follow PEP 8 style guide
2. Add type hints to all functions
3. Write docstrings for public functions
4. Add unit tests for new features
5. Update this README for significant changes

## License

Proprietary - All rights reserved

## Support

For issues and questions:
- GitHub Issues: Create an issue
- Email: dev@tradesignal.com
- Docs: [Main README](../README.md)
