# TradeSignal - Quick Start Guide

This guide will help you get the TradeSignal backend up and running in minutes.

## Prerequisites Checklist

- [x] Python 3.11+ installed
- [x] Docker Desktop installed
- [x] Git repository cloned
- [x] .env file created

## Step-by-Step Setup

### 1. Start PostgreSQL Database

```bash
# Navigate to project root
cd trade-signal

# Start only PostgreSQL from docker-compose
docker-compose up postgres -d

# Verify it's running (should show tradesignal-db container)
docker ps

# Expected output:
# CONTAINER ID   IMAGE                  STATUS         PORTS                    NAMES
# xxxxx          postgres:15-alpine     Up X seconds   0.0.0.0:5432->5432/tcp   tradesignal-db
```

### 2. Initialize Database Schema

```bash
# Connect to PostgreSQL and run init script
# Option 1: Using Docker exec
docker exec -i tradesignal-db psql -U tradesignal -d tradesignal < scripts/init_db.sql

# Option 2: Using local psql (if installed)
psql -h localhost -U tradesignal -d tradesignal -f scripts/init_db.sql
# Password: tradesignal_dev

# Verify tables were created
docker exec -it tradesignal-db psql -U tradesignal -d tradesignal -c "\dt"

# Expected output:
#  Schema |   Name    | Type  |   Owner
# --------+-----------+-------+-------------
#  public | companies | table | tradesignal
#  public | insiders  | table | tradesignal
#  public | trades    | table | tradesignal
```

### 3. Set Up Python Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Verify activation (should show (venv) in prompt)
```

### 4. Install Python Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Expected output: Installing packages...
# This may take 2-3 minutes
```

### 5. Verify Environment Configuration

```bash
# Check .env file exists in project root
cd ..
cat .env

# Verify these critical values are set:
# - DATABASE_URL=postgresql://tradesignal:tradesignal_dev@localhost:5432/tradesignal
# - SEC_USER_AGENT=Saad Kadri er.saadk16@gmail.com
# - JWT_SECRET=<some-value>
```

### 6. Start FastAPI Backend

```bash
# From backend directory (with venv activated)
cd backend
uvicorn app.main:app --reload

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process...
# INFO:     Started server process...
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

### 7. Test the API

Open your browser or use curl to test:

**Option 1: Browser**
- Open http://localhost:8000
- Open http://localhost:8000/docs (Swagger UI)
- Open http://localhost:8000/health

**Option 2: Command Line**
```bash
# Root endpoint
curl http://localhost:8000

# Health check (should show database: ok)
curl http://localhost:8000/health

# Expected health check response:
{
  "status": "healthy",
  "timestamp": "2025-10-17T...",
  "version": "1.0.0",
  "environment": "development",
  "checks": {
    "api": "ok",
    "database": "ok"
  }
}
```

## Success Criteria

You should see:

- ✅ PostgreSQL container running (`docker ps` shows tradesignal-db)
- ✅ Database tables created (companies, insiders, trades)
- ✅ FastAPI server running on http://localhost:8000
- ✅ `/health` endpoint returns `"status": "healthy"`
- ✅ `/docs` shows Swagger UI with API documentation
- ✅ Database check shows `"database": "ok"`

## Troubleshooting

### Database Connection Failed

**Problem**: `/health` shows `"database": "error"`

**Solution**:
```bash
# Check if PostgreSQL is running
docker ps

# If not running, start it
docker-compose up postgres -d

# Check logs
docker logs tradesignal-db

# Verify connection manually
docker exec -it tradesignal-db psql -U tradesignal -d tradesignal -c "SELECT 1;"
```

### Import Errors (ModuleNotFoundError)

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Make sure virtual environment is activated
# On Windows:
cd backend
venv\Scripts\activate

# Re-install dependencies
pip install -r requirements.txt
```

### Port 8000 Already in Use

**Problem**: `[ERROR] [Errno 48] Address already in use`

**Solution**:
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000

# macOS/Linux:
lsof -i :8000

# Kill the process or use a different port
uvicorn app.main:app --reload --port 8001
```

### SEC_USER_AGENT Validation Error

**Problem**: `ValueError: SEC_USER_AGENT must include an email address`

**Solution**:
```bash
# Edit .env file
# Change this line:
SEC_USER_AGENT=Saad Kadri er.saadk16@gmail.com

# Format must be: FirstName LastName email@example.com
```

## Next Steps

Now that your backend is running:

1. **Test Database Connectivity**: Use `/docs` to explore API endpoints
2. **Build SEC Scraper**: Start implementing the Form 4 scraper
3. **Create API Endpoints**: Add routes for trades, companies, insiders
4. **Set Up Frontend**: Install and run React frontend
5. **Test Full Stack**: Connect frontend to backend

## Useful Commands

```bash
# Stop PostgreSQL
docker-compose down

# View PostgreSQL logs
docker logs -f tradesignal-db

# Access PostgreSQL shell
docker exec -it tradesignal-db psql -U tradesignal -d tradesignal

# Run backend tests
cd backend
pytest

# Format code
black app/
flake8 app/

# Check FastAPI routes
uvicorn app.main:app --reload --log-level debug
```

## Development Workflow

1. **Start PostgreSQL**: `docker-compose up postgres -d`
2. **Activate venv**: `cd backend && venv\Scripts\activate`
3. **Start backend**: `uvicorn app.main:app --reload`
4. **Code & Test**: Make changes, FastAPI auto-reloads
5. **Stop server**: `Ctrl+C`
6. **Stop database**: `docker-compose down`

---

**Built with ❤️ by Saad Kadri | MS Computer Science @ UT Arlington**
