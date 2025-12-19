# TradeSignal Backend

FastAPI-based backend service for the TradeSignal platform. Provides RESTful APIs for insider trading intelligence, congressional trades, user authentication, billing, research analytics, and real-time notifications.

## Architecture

### Tech Stack
- **FastAPI** - Async web framework with automatic OpenAPI docs
- **SQLAlchemy** - ORM for database interactions
- **PostgreSQL** - Primary relational database (Supabase hosted)
- **Redis** - Caching and rate limiting
- **Celery** - Distributed task queue for background jobs
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
│   │   ├── security.py        # Auth utilities
│   │   └── observability.py   # Metrics and tracing
│   ├── models/                 # SQLAlchemy models (30+)
│   │   ├── user.py            # User and authentication
│   │   ├── trade.py           # Insider trades
│   │   ├── congressional_trade.py
│   │   ├── company.py
│   │   ├── insider.py
│   │   ├── subscription.py    # Billing models
│   │   ├── alert.py
│   │   ├── intrinsic_value.py # IVT research
│   │   ├── tradesignal_score.py # TS Score
│   │   ├── risk_level.py      # Risk assessment
│   │   ├── thesis.py          # Investment thesis
│   │   ├── portfolio.py       # User portfolios
│   │   ├── webhook.py         # Webhook configs
│   │   └── ...
│   ├── routers/                # API endpoints (25+)
│   │   ├── auth.py            # Authentication
│   │   ├── trades.py          # Insider trades
│   │   ├── congressional_trades.py
│   │   ├── companies.py
│   │   ├── insiders.py
│   │   ├── billing.py         # Stripe integration
│   │   ├── research.py        # Research API (PRO)
│   │   ├── ai.py              # AI insights (PRO)
│   │   ├── patterns.py        # Pattern detection
│   │   ├── alerts.py          # User alerts
│   │   ├── news.py
│   │   ├── fed.py             # Federal Reserve
│   │   ├── earnings.py        # Earnings calendar
│   │   ├── stocks.py          # Stock prices
│   │   ├── admin.py
│   │   ├── health.py
│   │   ├── scheduler.py       # Task scheduling
│   │   ├── enterprise_api.py  # Enterprise endpoints
│   │   ├── webhook_api.py     # Webhook management
│   │   └── ...
│   ├── schemas/                # Pydantic schemas
│   │   ├── trade.py
│   │   ├── company.py
│   │   ├── research.py        # Research schemas
│   │   └── ...
│   ├── services/               # Business logic (40+)
│   │   ├── sec_client.py      # SEC EDGAR client
│   │   ├── form4_parser.py    # Form 4 XML parsing
│   │   ├── congressional_scraper.py
│   │   ├── stock_price_service.py
│   │   ├── notification_service.py
│   │   ├── tier_service.py    # Subscription tiers
│   │   ├── ai_service.py      # AI analysis
│   │   ├── dcf_service.py     # DCF calculations
│   │   ├── ts_score_service.py # TradeSignal score
│   │   ├── risk_level_service.py
│   │   ├── thesis_service.py
│   │   ├── cache_service.py
│   │   ├── webhook_service.py
│   │   └── ...
│   ├── tasks/                  # Celery tasks
│   │   ├── sec_tasks.py       # SEC scraping tasks
│   │   ├── analysis_tasks.py
│   │   ├── enrichment_tasks.py
│   │   ├── ai_tasks.py
│   │   ├── ts_score_tasks.py
│   │   └── ...
│   ├── middleware/
│   │   ├── https_redirect.py
│   │   ├── error_handler.py
│   │   └── feature_gating.py
│   ├── config.py               # Settings management
│   ├── database.py             # DB connection
│   └── main.py                 # Application entry
├── tests/                      # Unit tests
├── scripts/                    # Utility scripts
├── docs/                       # API documentation
├── requirements.txt
├── Dockerfile
└── .env.example
```

## API Endpoints (25+ Routers)

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
- `GET /recent` - Get recent trades
- `GET /stats` - Trade statistics

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

### Research API (`/api/v1/research`) - PRO Tier
- `GET /ivt/{ticker}` - Intrinsic Value vs Price
- `GET /ts-score/{ticker}` - TradeSignal Score (1-5)
- `GET /risk-level/{ticker}` - Risk assessment
- `GET /thesis/{ticker}` - Investment thesis
- `GET /summary/{ticker}` - Full research summary
- `GET /competitive-strength/{ticker}` - Competitive analysis
- `GET /management-score/{ticker}` - Management rating

### AI Insights (`/api/v1/ai`) - PRO Tier
- `GET /analysis/{ticker}` - AI-powered analysis
- `GET /summary/{ticker}` - AI summary
- `POST /ask` - Ask AI questions

### Patterns (`/api/v1/patterns`)
- `GET /` - List detected patterns
- `GET /{ticker}` - Patterns for company

### Alerts (`/api/v1/alerts`)
- `GET /` - List user alerts
- `POST /` - Create alert
- `PUT /{id}` - Update alert
- `DELETE /{id}` - Delete alert

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

### Earnings (`/api/v1/earnings`)
- `GET /calendar` - Earnings calendar
- `GET /{ticker}` - Company earnings

### Stocks (`/api/v1/stocks`)
- `GET /{ticker}/price` - Current price
- `GET /{ticker}/history` - Price history

### Admin (`/api/v1/admin`)
- `GET /users` - List all users (superuser only)
- `PUT /users/{id}` - Update user (superuser only)
- `DELETE /users/{id}` - Delete user (superuser only)
- `GET /stats` - System statistics
- `GET /tickets` - Support tickets

### Scheduler (`/api/v1/scheduler`)
- `GET /status` - Scheduler status
- `POST /trigger/{task}` - Trigger task manually

### Enterprise API (`/api/v1/enterprise`)
- High-volume API access for enterprise customers
- Bulk data endpoints
- Custom integrations

### Webhooks (`/api/v1/webhooks`)
- `GET /` - List webhooks
- `POST /` - Create webhook
- `DELETE /{id}` - Delete webhook

### Health & Monitoring
- `GET /api/v1/health` - Health check
- `GET /api/v1/health/detailed` - Detailed health
- `GET /metrics` - Prometheus metrics

## Database Models (30+)

### Core Models
- **User** - User accounts with roles (free, plus, pro, enterprise, admin)
- **Subscription** - Stripe subscription data
- **Payment** - Payment history
- **Trade** - Insider trading transactions
- **CongressionalTrade** - Political stock transactions
- **Company** - Company profiles
- **Insider** - Insider profiles
- **Alert** - User alerts and notifications
- **Ticket** - Support tickets

### Research Models (PRO Features)
- **IntrinsicValue** - IVT calculations
- **TradesignalScore** - TS Score ratings
- **RiskLevel** - Risk assessments
- **Thesis** - Investment theses
- **CompetitiveStrength** - Competitive analysis
- **ManagementScore** - Management ratings

### Enterprise Models
- **Portfolio** - User portfolios
- **Webhook** - Webhook configurations
- **Organization** - Enterprise organizations
- **FeatureUsageLog** - Usage tracking

## Service Layer (40+ Services)

### Data Collection
- **SECClient** - SEC EDGAR API client
- **Form4Parser** - Form 4 XML parsing with robust error handling
- **CongressionalScraper** - Congressional trade scraping

### Research Services
- **DCFService** - Discounted cash flow calculations
- **TSScoreService** - TradeSignal score computation
- **RiskLevelService** - Risk assessment
- **ThesisService** - Investment thesis generation
- **CompetitiveStrengthService** - Competitive analysis

### AI Services
- **AIService** - AI-powered analysis and summaries
- **PredictiveModelingService** - ML predictions

### Infrastructure
- **CacheService** - Redis caching
- **NotificationService** - Multi-channel notifications
- **WebhookService** - Webhook delivery
- **TierService** - Feature access control

## Background Tasks (Celery)

### SEC Tasks (`tasks/sec_tasks.py`)
- `scrape_all_active_companies_form4_filings` - Automated scraping (every 2 hours at 0,4,8,12,16,20)
- `scrape_recent_form4_filings` - Scrape SEC Form 4 filings for specific company
- `process_form4_document` - Parse individual Form 4 with priority routing
- **Priority System**: Recent filings (≤7 days) get priority 9, medium (8-30 days) priority 5, historical priority 0
- **Race Condition Protection**: PostgreSQL INSERT ON CONFLICT prevents duplicates
- **Date Filtering**: Fetches last 30 days of filings
- **Cooldown**: 1-hour cooldown between company scrapes
- Robust XML parsing with null checks
- Correct Form 4 XML file detection

### Analysis Tasks
- `calculate_ts_scores` - Compute TradeSignal scores
- `update_risk_levels` - Update risk assessments
- `generate_theses` - Generate investment theses

### Enrichment Tasks
- `enrich_company_data` - Add company metadata
- `update_stock_prices` - Refresh price data

## Subscription Tiers

| Feature | Free | Plus | PRO | Enterprise |
|---------|------|------|-----|------------|
| API Rate Limit | 100/hr | 500/hr | 2000/hr | Unlimited |
| Insider Trades | Limited | Full | Full | Full |
| Research API | - | - | ✓ | ✓ |
| AI Insights | - | - | ✓ | ✓ |
| Webhooks | - | - | - | ✓ |
| Custom Alerts | 3 | 10 | Unlimited | Unlimited |

## Authentication & Security

### JWT Authentication
- Access tokens with configurable expiry
- Refresh token support
- Password hashing with bcrypt

### Rate Limiting
- Tiered rate limits by subscription
- Redis-backed rate limiter
- Per-endpoint customization

### Security Features
- CORS configuration
- HTTPS redirect middleware (production)
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (Pydantic)
- Secret management via environment variables

## Environment Variables

### Required
```env
# Database (Supabase)
DATABASE_URL=postgresql://user:password@db.supabase.co:5432/postgres

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_PLUS=price_...
STRIPE_PRICE_ID_PRO=price_...
STRIPE_PRICE_ID_ENTERPRISE=price_...

# SEC API
SEC_USER_AGENT=TradeSignal/1.0 (your@email.com)

# SEC Scraper Configuration
SCRAPER_SCHEDULE_HOURS=0,4,8,12,16,20  # Run every 2-4 hours
SCRAPER_DAYS_BACK=30                    # Fetch last 30 days
SCRAPER_MAX_FILINGS=50                  # Max filings per company
SCRAPER_COOLDOWN_HOURS=1                # Hours between re-scraping same company
SCRAPER_PRIORITY_RECENT_DAYS=7          # Days for highest priority
SCRAPER_PRIORITY_MEDIUM_DAYS=30         # Days for medium priority
```

### Optional
```env
# Feature Flags
ENABLE_AI_INSIGHTS=true
ENABLE_WEBHOOKS=true
ENABLE_EMAIL_ALERTS=true
SCHEDULER_ENABLED=true

# Logging
LOG_LEVEL=INFO
USE_JSON_LOGGING=false

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Rate Limiting
RATE_LIMIT_FREE_TIER=100
RATE_LIMIT_PLUS_TIER=500
RATE_LIMIT_PRO_TIER=2000
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
```

### Running Locally
```bash
# Run FastAPI server
uvicorn app.main:app --reload --port 8000

# Run Celery worker (REQUIRED - separate terminal)
celery -A app.core.celery_app worker --pool=solo --loglevel=info

# Run Celery beat scheduler (REQUIRED - separate terminal)
# NOTE: Beat is required for automated scraping every 2 hours
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
├── test_research_api.py
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
- [ ] Configure production database (Supabase)
- [ ] Set up Redis for production
- [ ] Enable HTTPS redirect
- [ ] Configure CORS origins
- [ ] Set up logging aggregation
- [ ] Enable Prometheus monitoring
- [ ] Configure backups
- [ ] Set up health checks

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
- Celery worker status
- API endpoint: `/api/v1/health`

## Troubleshooting

### Database Connection Issues
```bash
# Check DATABASE_URL is correct
echo $DATABASE_URL

# Test connection
python -c "from app.database import engine; print(engine.url)"
```

### Redis Connection Issues
```bash
# Check Redis is running
redis-cli ping
```

### Celery Worker Not Processing
```bash
# Check worker is running
celery -A app.core.celery_app inspect active

# Check for errors in logs
celery -A app.core.celery_app worker --loglevel=debug
```

### Celery Beat Corruption (EOFError)
If Celery Beat fails to start with `EOFError: Ran out of input`, the schedule database is corrupted. This commonly happens on Windows when the process terminates unexpectedly.

**Automatic Recovery:**
The scheduler now automatically detects and recovers from corruption. If it still fails, use manual cleanup:

**Manual Cleanup:**
```bash
# Option 1: Use the cleanup script
python scripts/cleanup_celery_beat.py

# Option 2: Manually delete schedule files
# Windows PowerShell:
Remove-Item celerybeat-schedule* -Force

# Linux/Mac:
rm -f celerybeat-schedule*
```

After cleanup, restart Celery Beat - it will recreate the schedule files automatically.

### SEC Scraper Issues
- Ensure `SEC_USER_AGENT` is set with valid email
- Check rate limiting (10 requests/second max)
- Verify Form 4 XML parsing handles null elements

## Recent Improvements (Dec 2025)

### Priority Queue System
- **Smart Filing Processing**: Recent filings (last 7 days) processed before historical data
- **Priority Levels**: 9 (recent), 5 (medium 8-30 days), 0 (historical)
- **Race Condition Fix**: Atomic INSERT ON CONFLICT prevents duplicate processing
- **Configurable**: Adjust priority thresholds via environment variables

### IVT (Intrinsic Value Target) Integration
- **Real Stock Prices**: Uses Yahoo Finance data via StockPriceService
- **On-Demand Calculation**: Calculates IVT for any ticker on request
- **Accurate Metrics**: Discount/premium percentages reflect real market data
- **PRO Tier Feature**: Fully functional for PRO and Enterprise users

### Automated SEC Scraping
- **Schedule**: Every 2 hours at 0, 4, 8, 12, 16, 20 (configurable)
- **Smart Cooldown**: 1-hour cooldown prevents API rate limiting
- **Date Filtering**: Fetches only last 30 days to reduce load
- **Monitoring**: Flower support for real-time task monitoring

### Performance Optimizations
- **32,000+ Trades**: Successfully processing large-scale historical data
- **151 Companies**: Active monitoring across major tickers
- **Robust Parsing**: Handles malformed XML and null values gracefully

## License

Proprietary - All rights reserved

## Support

For issues and questions:
- GitHub Issues: Create an issue
- Email: dev@tradesignal.com
- Docs: [Main README](../README.md)
