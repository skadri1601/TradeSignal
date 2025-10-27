# TradeSignal Backend

FastAPI backend service for the TradeSignal insider trading intelligence platform.

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── company.py             # Company model (ticker, CIK, name, sector)
│   │   ├── insider.py             # Insider model (name, title, relationships)
│   │   └── trade.py               # Trade model (transactions with details)
│   │
│   ├── schemas/                   # Pydantic schemas (validation & serialization)
│   │   ├── __init__.py
│   │   ├── common.py              # Shared schemas (pagination, filters)
│   │   ├── company.py             # Company schemas (Create, Read, Update)
│   │   ├── insider.py             # Insider schemas
│   │   └── trade.py               # Trade schemas
│   │
│   ├── routers/                   # API endpoints
│   │   ├── __init__.py
│   │   ├── companies.py           # Company endpoints (/api/v1/companies)
│   │   ├── insiders.py            # Insider endpoints (/api/v1/insiders)
│   │   ├── trades.py              # Trade endpoints (/api/v1/trades)
│   │   └── scraper.py             # Scraper endpoints (/api/v1/scraper)
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── company_service.py     # Company operations
│   │   ├── insider_service.py     # Insider operations
│   │   ├── trade_service.py       # Trade operations
│   │   ├── sec_client.py          # SEC EDGAR API client
│   │   ├── form4_parser.py        # Form 4 XML parser
│   │   └── scraper_service.py     # Scraper orchestration
│   │
│   ├── config.py                  # Settings management (Pydantic BaseSettings)
│   ├── database.py                # Database connection & session factory
│   ├── main.py                    # FastAPI application entry point
│   └── seed_data.py               # Database seed script
│
├── tests/                         # Test data and test cases
│   ├── __init__.py
│   └── seed_trades.json           # Sample trade data
│
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker image definition
└── README.md                      # This file
```

---

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.104+ (async Python web framework)
- **Database**: PostgreSQL 15 with SQLAlchemy 2.0 (async)
- **Validation**: Pydantic v2
- **HTTP Client**: httpx (async)
- **XML Parsing**: lxml, BeautifulSoup4
- **Testing**: pytest (planned)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or use Docker)
- SEC EDGAR user agent (your name + email)

### Installation

**1. Navigate to backend directory**
```bash
cd backend
```

**2. Create virtual environment**
```bash
python -m venv venv
```

**3. Activate virtual environment**

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

**4. Install dependencies**
```bash
pip install -r requirements.txt
```

**5. Set up environment variables**

Create a `.env` file in the backend directory:
```env
# Database
DATABASE_URL=postgresql+asyncpg://tradesignal:tradesignal_dev@localhost:5432/tradesignal

# SEC EDGAR (REQUIRED)
SEC_USER_AGENT=YourName your.email@example.com

# Security
JWT_SECRET=your-random-secret-key-change-this
JWT_ALGORITHM=HS256

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Features
ENABLE_AI_INSIGHTS=false
ENABLE_WEBHOOKS=false
ENABLE_EMAIL_ALERTS=false
```

**6. Start PostgreSQL**

Using Docker:
```bash
# From project root
docker-compose up postgres -d
```

Or use your own PostgreSQL instance.

**7. Seed the database (optional)**
```bash
python -m app.seed_data
```

**8. Start the FastAPI server**
```bash
uvicorn app.main:app --reload
```

Server will run at: http://localhost:8000

---

## 📖 API Documentation

Once the server is running, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🔌 API Endpoints

### Companies

- `GET /api/v1/companies/` - List all companies (with pagination)
- `GET /api/v1/companies/{ticker}` - Get company by ticker
- `GET /api/v1/companies/{ticker}/insiders` - Get company's insiders
- `GET /api/v1/companies/{ticker}/trades` - Get company's trades
- `GET /api/v1/companies/stats` - Get company statistics
- `POST /api/v1/companies/` - Create new company
- `PUT /api/v1/companies/{ticker}` - Update company
- `DELETE /api/v1/companies/{ticker}` - Delete company

### Insiders

- `GET /api/v1/insiders/` - List all insiders (with pagination)
- `GET /api/v1/insiders/{id}` - Get insider by ID
- `GET /api/v1/insiders/{id}/trades` - Get insider's trades
- `GET /api/v1/insiders/{id}/activity` - Get insider's activity summary
- `POST /api/v1/insiders/` - Create new insider
- `PUT /api/v1/insiders/{id}` - Update insider
- `DELETE /api/v1/insiders/{id}` - Delete insider

### Trades

- `GET /api/v1/trades/` - List all trades (with pagination & filters)
- `GET /api/v1/trades/{id}` - Get trade by ID
- `GET /api/v1/trades/recent` - Get recent trades (last 7 days)
- `GET /api/v1/trades/stats` - Get trade statistics
- `POST /api/v1/trades/` - Create new trade
- `PUT /api/v1/trades/{id}` - Update trade
- `DELETE /api/v1/trades/{id}` - Delete trade

**Trade Filters:**
- `ticker` - Filter by company ticker
- `insider_id` - Filter by insider ID
- `transaction_type` - Filter by BUY/SELL
- `min_value` - Minimum transaction value
- `max_value` - Maximum transaction value
- `start_date` - Start date (YYYY-MM-DD)
- `end_date` - End date (YYYY-MM-DD)

### Scraper (Phase 2)

- `GET /api/v1/scraper/test` - Test SEC API connectivity
- `GET /api/v1/scraper/scrape/{ticker}` - Scrape trades by ticker
- `POST /api/v1/scraper/scrape` - Scrape trades (with body params)

**Scraper Parameters:**
- `ticker` - Company ticker symbol (e.g., AAPL, TSLA)
- `cik` - Company CIK number (optional, alternative to ticker)
- `days_back` - Number of days to look back (default: 30)
- `max_filings` - Maximum filings to process (default: 10)

---

## 🧪 Testing API

### Using Swagger UI (Recommended)

1. Open http://localhost:8000/docs
2. Expand any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

### Using cURL

**Get recent trades:**
```bash
curl http://localhost:8000/api/v1/trades/recent
```

**Get company by ticker:**
```bash
curl http://localhost:8000/api/v1/companies/AAPL
```

**Filter trades:**
```bash
curl "http://localhost:8000/api/v1/trades/?ticker=AAPL&transaction_type=BUY"
```

**Scrape Apple trades:**
```bash
curl "http://localhost:8000/api/v1/scraper/scrape/AAPL?days_back=300&max_filings=1"
```

**Get trade statistics:**
```bash
curl http://localhost:8000/api/v1/trades/stats
```

---

## 🗄️ Database

### Schema

**Companies Table:**
- `id` (PK)
- `ticker` (UNIQUE, indexed)
- `name`
- `cik` (UNIQUE, indexed)
- `sector`
- `industry`
- `market_cap`
- `website`
- `created_at`, `updated_at`

**Insiders Table:**
- `id` (PK)
- `name`
- `title`
- `company_id` (FK → companies)
- `is_director`, `is_officer`, `is_ten_percent_owner`, `is_other`
- `created_at`, `updated_at`

**Trades Table:**
- `id` (PK)
- `insider_id` (FK → insiders)
- `company_id` (FK → companies)
- `transaction_date`, `filing_date`
- `transaction_type` (BUY/SELL)
- `transaction_code` (P, S, A, M, etc.)
- `shares`, `price_per_share`, `total_value`
- `shares_owned_after`
- `ownership_type` (Direct/Indirect)
- `derivative_transaction` (boolean)
- `sec_filing_url`, `form_type`
- `created_at`, `updated_at`

### Database Operations

**Connect to PostgreSQL (Docker):**
```bash
docker exec -it tradesignal-db psql -U tradesignal -d tradesignal
```

**Useful SQL queries:**
```sql
-- List tables
\dt

-- Count records
SELECT COUNT(*) FROM companies;
SELECT COUNT(*) FROM insiders;
SELECT COUNT(*) FROM trades;

-- View recent trades
SELECT * FROM trades ORDER BY transaction_date DESC LIMIT 10;

-- Exit
\q
```

---

## 🔧 Development

### Project Configuration

Configuration is managed via `app/config.py` using Pydantic Settings. All settings can be overridden with environment variables.

**Key settings:**
- `DATABASE_URL` - PostgreSQL connection string
- `SEC_USER_AGENT` - Required by SEC EDGAR API
- `ENABLE_AI_INSIGHTS` - Toggle AI features
- `ENABLE_WEBHOOKS` - Toggle webhook notifications
- `LOG_LEVEL` - Logging verbosity (DEBUG, INFO, WARNING, ERROR)

### Adding New Endpoints

1. Create route function in `app/routers/`
2. Add service logic in `app/services/`
3. Define schemas in `app/schemas/`
4. Register router in `app/main.py`

Example:
```python
# app/routers/example.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/example")
async def get_example():
    return {"message": "Hello World"}

# app/main.py
from app.routers import example
app.include_router(example.router, prefix="/api/v1")
```

### Database Migrations (Future)

Alembic migrations are planned but not yet implemented. Currently using raw SQL schema from project root.

---

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError

**Solution:**
```bash
cd backend
venv\Scripts\activate  # or source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Database connection error

**Solution:**
```bash
# Check if PostgreSQL is running
docker ps

# Start PostgreSQL
docker-compose up postgres -d

# Verify connection string in .env
DATABASE_URL=postgresql+asyncpg://tradesignal:tradesignal_dev@localhost:5432/tradesignal
```

### Issue: Port 8000 already in use

**Solution:**

Windows:
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

Mac/Linux:
```bash
lsof -i :8000
kill -9 <PID>
```

Or use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

### Issue: SEC scraper returns 0 filings

**Possible causes:**
1. Invalid ticker/CIK
2. No recent Form 4 filings for that company
3. SEC API rate limiting (max 10 req/sec)
4. Invalid SEC_USER_AGENT in .env

**Solution:**
```bash
# Test SEC connectivity
curl http://localhost:8000/api/v1/scraper/test

# Check logs for errors
# (logs appear in terminal where uvicorn is running)
```

---

## 📦 Dependencies

Key packages (see `requirements.txt` for full list):

- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server
- `sqlalchemy[asyncio]` - ORM
- `asyncpg` - Async PostgreSQL driver
- `pydantic[email]` - Data validation
- `pydantic-settings` - Settings management
- `httpx` - Async HTTP client
- `lxml` - XML parsing
- `beautifulsoup4` - HTML/XML parsing
- `python-dotenv` - Environment variable management
- `python-multipart` - Form data support

---

## 🔒 Security

- Environment variables stored in `.env` (not committed to git)
- SQL injection protection via SQLAlchemy parameterized queries
- JWT authentication (planned)
- CORS configured for frontend domain
- Rate limiting (planned)

---

## 📊 Logging

Logs are output to stdout in JSON format (in production) or colored format (in development).

Log levels:
- `DEBUG` - Detailed information for debugging
- `INFO` - General informational messages
- `WARNING` - Warning messages
- `ERROR` - Error messages

Configure via `LOG_LEVEL` environment variable.

---

## 🚀 Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t tradesignal-backend .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db \
  -e SEC_USER_AGENT="Name email@example.com" \
  tradesignal-backend
```

Or use docker-compose (recommended):

```bash
# From project root
docker-compose up --build
```

---

## 📝 Notes

- All timestamps stored in UTC
- Database uses async SQLAlchemy 2.0
- SEC EDGAR requires proper User-Agent header
- SEC rate limit: 10 requests/second
- Form 4 filings sometimes have errors - validation is important
- Scraper auto-creates companies and insiders if not found

---

## 📞 Support

For issues or questions:
- Check `/docs` endpoint for API documentation
- Review logs in terminal
- Refer to main project [README](../README.md)

---

**Built with FastAPI and PostgreSQL | Part of TradeSignal Platform**
