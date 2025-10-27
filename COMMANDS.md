# Quick Command Reference

## 🚀 Start the Backend

```bash
# 1. Navigate to backend
cd backend

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Seed the database (first time only)
python -m app.seed_data

# 4. Start FastAPI server
uvicorn app.main:app --reload
```

**Server will run at**: http://localhost:8000
**Swagger UI**: http://localhost:8000/docs

---

## 🗄️ Database Commands

```bash
# Check PostgreSQL is running
docker ps

# Start PostgreSQL (if not running)
docker-compose up postgres -d

# Connect to database
docker exec -it tradesignal-db psql -U tradesignal -d tradesignal

# Inside psql:
\dt                    # List tables
SELECT COUNT(*) FROM companies;
SELECT COUNT(*) FROM insiders;
SELECT COUNT(*) FROM trades;
\q                     # Exit
```

---

## 🧪 Testing API

### Option 1: Swagger UI (Recommended)
Open browser: http://localhost:8000/docs

### Option 2: cURL Commands

```bash
# Get recent trades
curl http://localhost:8000/api/v1/trades/recent

# Get company by ticker
curl http://localhost:8000/api/v1/companies/AAPL

# Search companies
curl "http://localhost:8000/api/v1/companies/search?q=apple"

# Get trade statistics
curl http://localhost:8000/api/v1/trades/stats

# Get trades with filters
curl "http://localhost:8000/api/v1/trades?ticker=AAPL&transaction_type=BUY"
```

---

## 📦 Package Management

```bash
# Install dependencies
pip install -r requirements.txt

# Add new package
pip install package-name
pip freeze > requirements.txt
```

---

## 🔄 Database Reset (if needed)

```bash
# Stop and remove PostgreSQL container
docker-compose down

# Remove volume (deletes all data)
docker volume rm tradesignal_postgres_data

# Start fresh
docker-compose up postgres -d

# Re-run init script
docker exec -i tradesignal-db psql -U tradesignal -d tradesignal < scripts/init_db.sql

# Re-seed data
python -m app.seed_data
```

---

## Git Operations (You Handle These)

```bash
# Check status
git status

# Stage changes
git add .

# Commit
git commit -m "feat: implement backend core (models, schemas, services, API endpoints)"

# Push to remote
git push origin feature/sec-scraper

# Or push to main
git checkout main
git merge feature/sec-scraper
git push origin main
```

---

## 🐍 Python Environment

```bash
# Create venv (if needed)
python -m venv venv

# Activate
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Deactivate
deactivate

# Check Python version
python --version

# Check installed packages
pip list
```

---

## 🔍 Debugging

```bash
# Check FastAPI logs
# (Server logs appear in terminal where uvicorn is running)

# Check PostgreSQL logs
docker logs tradesignal-db

# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process on port 8000 (if needed)
# Find PID from netstat output
taskkill /PID <PID> /F
```

---

## 📊 Verify Installation

```bash
# Check all services
docker ps                        # PostgreSQL should be running
python --version                 # Should be 3.11+
pip show fastapi                 # Should be installed
curl http://localhost:8000       # Server should respond
```

---

## Common Issues

### Issue: ModuleNotFoundError
**Solution**:
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Database connection error
**Solution**:
```bash
docker ps                    # Check if PostgreSQL is running
docker-compose up postgres -d
```

### Issue: Port 8000 in use
**Solution**:
```bash
netstat -ano | findstr :8000    # Find PID
taskkill /PID <PID> /F          # Kill process
# Or use different port:
uvicorn app.main:app --reload --port 8001
```

---

## Next Steps

1. ✅ Run `docker ps` - verify PostgreSQL is running
2. ✅ Run `python -m app.seed_data` - populate database
3. ✅ Run `uvicorn app.main:app --reload` - start server
4. ✅ Open http://localhost:8000/docs - test API
5. ⏭️ Build SEC scraper (Phase 2)
