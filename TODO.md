# TradeSignal - Development TODO List

> **Last Updated**: October 26, 2025
> **Current Branch**: `feature/sec-scraper`
> **Project Stage**: Phase 1 - Backend Infrastructure (70% Complete)

---

## 🎯 Immediate Priorities (Week 1-2)

### Phase 1: Database Models & API Foundation

#### ✅ COMPLETED
- [x] FastAPI backend infrastructure setup
- [x] Database schema design (init_db.sql)
- [x] PostgreSQL Docker container running
- [x] Configuration management (Pydantic Settings)
- [x] Health check endpoint
- [x] Logging and error handling
- [x] CORS middleware setup

#### 🔴 HIGH PRIORITY - Backend Core

- [ ] **Create SQLAlchemy Models** (`backend/app/models/`)
  - [ ] Create `backend/app/models/company.py`
    - [ ] Company model (ticker, name, cik, sector, industry, market_cap)
    - [ ] Add validation for ticker format (uppercase, max 10 chars)
    - [ ] Add validation for CIK format (10 digits)
  - [ ] Create `backend/app/models/insider.py`
    - [ ] Insider model (name, title, relationship, company_id)
    - [ ] Add relationship to Company (many-to-one)
    - [ ] Boolean flags (is_director, is_officer, is_ten_percent_owner)
  - [ ] Create `backend/app/models/trade.py`
    - [ ] Trade model (all fields from schema)
    - [ ] Add relationships to Company and Insider
    - [ ] Add calculated property for total_value
    - [ ] Enum for transaction_type (BUY/SELL)
    - [ ] Enum for transaction_code (P, S, A, M, etc.)
  - [ ] Update `backend/app/models/__init__.py` to export all models

- [ ] **Create Pydantic Schemas** (`backend/app/schemas/`)
  - [ ] Create `backend/app/schemas/company.py`
    - [ ] CompanyBase (shared fields)
    - [ ] CompanyCreate (for POST requests)
    - [ ] CompanyRead (for responses with id, timestamps)
    - [ ] CompanyUpdate (for PATCH requests)
  - [ ] Create `backend/app/schemas/insider.py`
    - [ ] InsiderBase, InsiderCreate, InsiderRead, InsiderUpdate
    - [ ] Include nested company data in InsiderRead
  - [ ] Create `backend/app/schemas/trade.py`
    - [ ] TradeBase, TradeCreate, TradeRead, TradeUpdate
    - [ ] TradeReadDetailed (with company and insider details)
    - [ ] Add computed fields (e.g., transaction_value_formatted)
  - [ ] Create `backend/app/schemas/common.py`
    - [ ] PaginationParams (page, limit, skip)
    - [ ] FilterParams (date_from, date_to, min_value, max_value)
    - [ ] SortParams (sort_by, order)
  - [ ] Update `backend/app/schemas/__init__.py`

- [ ] **Build API Endpoints** (`backend/app/routers/`)
  - [ ] Create `backend/app/routers/trades.py`
    - [ ] GET `/api/v1/trades` - List trades with pagination/filtering
    - [ ] GET `/api/v1/trades/{id}` - Get single trade details
    - [ ] POST `/api/v1/trades` - Create new trade (for scraper)
    - [ ] GET `/api/v1/trades/recent` - Get recent trades (last 7 days)
    - [ ] GET `/api/v1/trades/stats` - Get trade statistics
  - [ ] Create `backend/app/routers/companies.py`
    - [ ] GET `/api/v1/companies` - List companies with search
    - [ ] GET `/api/v1/companies/{ticker}` - Get company by ticker
    - [ ] GET `/api/v1/companies/{ticker}/trades` - Get trades for company
    - [ ] POST `/api/v1/companies` - Create company (for scraper)
  - [ ] Create `backend/app/routers/insiders.py`
    - [ ] GET `/api/v1/insiders` - List insiders
    - [ ] GET `/api/v1/insiders/{id}` - Get insider details
    - [ ] GET `/api/v1/insiders/{id}/trades` - Get trades by insider
  - [ ] Update `backend/app/main.py` to include routers
    - [ ] Import and mount all routers
    - [ ] Add router tags for API documentation

- [ ] **Create Service Layer** (`backend/app/services/`)
  - [ ] Create `backend/app/services/trade_service.py`
    - [ ] `get_trades()` - Fetch trades with filters
    - [ ] `get_trade_by_id()` - Fetch single trade
    - [ ] `create_trade()` - Insert new trade
    - [ ] `get_recent_trades()` - Fetch recent trades
    - [ ] `calculate_trade_stats()` - Generate statistics
  - [ ] Create `backend/app/services/company_service.py`
    - [ ] `get_or_create_company()` - Find or create company
    - [ ] `search_companies()` - Search by ticker/name
    - [ ] `enrich_company_data()` - Fetch additional data (yfinance)
  - [ ] Create `backend/app/services/insider_service.py`
    - [ ] `get_or_create_insider()` - Find or create insider
    - [ ] `link_insider_to_company()` - Create relationship

---

## 🟡 MEDIUM PRIORITY - Data Pipeline

### Phase 2: SEC Scraper Implementation

- [ ] **Build SEC EDGAR Scraper** (`data_pipeline/sec_scraper.py`)
  - [ ] Create `SECClient` class
    - [ ] Set up proper user agent (required by SEC)
    - [ ] Add rate limiting (10 requests/second max)
    - [ ] Add retry logic with exponential backoff
    - [ ] Add error handling and logging
  - [ ] Implement `fetch_recent_form4_filings()`
    - [ ] Hit SEC EDGAR RSS feed or search API
    - [ ] Parse filing index to get filing URLs
    - [ ] Filter for Form 4 filings only
    - [ ] Return list of filing URLs and metadata
  - [ ] Implement `download_filing(url)`
    - [ ] Download Form 4 XML/HTML file
    - [ ] Handle different SEC file formats
    - [ ] Cache downloaded files in `data/raw/`
  - [ ] Implement `parse_form4(filing_data)`
    - [ ] Extract company info (ticker, cik, name)
    - [ ] Extract insider info (name, title, relationship)
    - [ ] Extract transaction details (date, type, shares, price)
    - [ ] Handle multiple transactions in one filing
    - [ ] Return structured data (dict or Pydantic model)
  - [ ] Implement `save_to_database(parsed_data)`
    - [ ] Use service layer to insert data
    - [ ] Handle duplicates (check UNIQUE constraints)
    - [ ] Use database transactions for consistency
  - [ ] Create main scraper function `run_scraper()`
    - [ ] Fetch recent filings (last 24 hours)
    - [ ] Parse and save each filing
    - [ ] Log progress and errors
    - [ ] Return summary stats

- [ ] **Create XML/HTML Parsers** (`data_pipeline/parsers/`)
  - [ ] Create `data_pipeline/parsers/form4_parser.py`
    - [ ] `parse_xml()` - Parse SEC XML format
    - [ ] `parse_html()` - Parse HTML format (legacy)
    - [ ] Extract reporting owner info
    - [ ] Extract issuer (company) info
    - [ ] Extract derivative vs non-derivative transactions
    - [ ] Handle edge cases (amendments, multi-page filings)
  - [ ] Create `data_pipeline/parsers/company_enricher.py`
    - [ ] `fetch_company_data(ticker)` - Use yfinance
    - [ ] Get sector, industry, market cap
    - [ ] Get current stock price
    - [ ] Cache results to avoid API limits

- [ ] **Add Scheduler** (`data_pipeline/scheduler.py`)
  - [ ] Set up APScheduler
  - [ ] Schedule scraper to run every hour
  - [ ] Add job for company data enrichment (daily)
  - [ ] Add health check job
  - [ ] Integrate with FastAPI lifespan events

---

## 🔵 MEDIUM PRIORITY - Frontend

### Phase 3: React Dashboard

- [ ] **Set Up Frontend Foundation**
  - [ ] Create proper `frontend/src/App.tsx`
    - [ ] Set up React Router with routes
    - [ ] Add basic layout (header, sidebar, main content)
    - [ ] Set up React Query client
    - [ ] Add toast notifications (react-hot-toast)
  - [ ] Update `frontend/src/main.tsx`
    - [ ] Proper React 18 root rendering
    - [ ] Import Tailwind CSS
    - [ ] Wrap app with providers (QueryClient, Router)
  - [ ] Create `frontend/src/index.css`
    - [ ] Import Tailwind directives
    - [ ] Add custom CSS variables for theme
    - [ ] Dark mode support (optional)

- [ ] **Create API Client** (`frontend/src/api/`)
  - [ ] Create `frontend/src/api/client.ts`
    - [ ] Axios instance with base URL
    - [ ] Request/response interceptors
    - [ ] Error handling
  - [ ] Create `frontend/src/api/trades.ts`
    - [ ] `fetchTrades()` - GET /api/v1/trades
    - [ ] `fetchTradeById()` - GET /api/v1/trades/:id
    - [ ] `fetchRecentTrades()` - GET /api/v1/trades/recent
  - [ ] Create `frontend/src/api/companies.ts`
    - [ ] `fetchCompanies()` - GET /api/v1/companies
    - [ ] `fetchCompanyByTicker()` - GET /api/v1/companies/:ticker

- [ ] **Build UI Components** (`frontend/src/components/`)
  - [ ] Create `frontend/src/components/TradeList.tsx`
    - [ ] Table view of recent trades
    - [ ] Columns: Date, Company, Insider, Type, Shares, Value
    - [ ] Row highlighting (green for BUY, red for SELL)
    - [ ] Pagination controls
  - [ ] Create `frontend/src/components/TradeFilters.tsx`
    - [ ] Date range picker
    - [ ] Company search/select
    - [ ] Transaction type filter (BUY/SELL)
    - [ ] Min/max value filters
  - [ ] Create `frontend/src/components/CompanyCard.tsx`
    - [ ] Display company info (ticker, name, sector)
    - [ ] Show recent trades count
    - [ ] Link to company detail page
  - [ ] Create `frontend/src/components/TradeChart.tsx`
    - [ ] Use Recharts for visualization
    - [ ] Line chart of trade volume over time
    - [ ] Bar chart of buy vs sell volume
  - [ ] Create `frontend/src/components/Layout.tsx`
    - [ ] Header with logo and navigation
    - [ ] Sidebar with filters
    - [ ] Main content area

- [ ] **Create Pages** (`frontend/src/pages/`)
  - [ ] Create `frontend/src/pages/Dashboard.tsx`
    - [ ] Overview stats (total trades, companies, insiders)
    - [ ] Recent trades list
    - [ ] Charts
  - [ ] Create `frontend/src/pages/TradesPage.tsx`
    - [ ] Full trade list with filters
    - [ ] Search functionality
    - [ ] Export to CSV (optional)
  - [ ] Create `frontend/src/pages/CompanyPage.tsx`
    - [ ] Company details
    - [ ] All trades for company
    - [ ] Insider list for company

- [ ] **Add State Management** (`frontend/src/store/`)
  - [ ] Create `frontend/src/store/useFilterStore.ts` (Zustand)
    - [ ] Filter state (dates, companies, types)
    - [ ] Filter actions (set, reset, clear)
  - [ ] Create `frontend/src/hooks/useTrades.ts`
    - [ ] React Query hook for trades
    - [ ] Handle loading, error, success states
    - [ ] Automatic refetch on interval

---

## 🟢 LOW PRIORITY - Enhancements

### Phase 4: Advanced Features

- [ ] **Fix PostgreSQL Connection Issue**
  - [ ] Try PostgreSQL 14 instead of 15
  - [ ] Test with WSL2 instead of native Windows
  - [ ] Try different libpq version
  - [ ] Or: Deploy to Linux server (Railway/Azure)

- [ ] **Add Database Migrations**
  - [ ] Set up Alembic migrations
  - [ ] Create initial migration from init_db.sql
  - [ ] Add migration for any schema changes

- [ ] **Add Authentication**
  - [ ] Create User model
  - [ ] JWT token generation/validation
  - [ ] Login/register endpoints
  - [ ] Protected routes (admin only)
  - [ ] API key authentication for scraper

- [ ] **Add Testing**
  - [ ] Create `backend/tests/test_models.py`
  - [ ] Create `backend/tests/test_api.py`
  - [ ] Create `backend/tests/test_scraper.py`
  - [ ] Set up pytest fixtures
  - [ ] Add test database setup/teardown
  - [ ] Frontend unit tests (Vitest)

- [ ] **Add AI Insights**
  - [ ] Create `backend/app/services/ai_service.py`
  - [ ] `generate_trade_insight(trade)` - Use OpenAI GPT-4o
  - [ ] Analyze trade significance
  - [ ] Detect patterns (cluster buying, unusual activity)
  - [ ] Add insights to TradeRead schema

- [ ] **Add Alerts/Notifications**
  - [ ] Create watchlist feature
  - [ ] Email alerts for watched companies
  - [ ] Webhook notifications
  - [ ] In-app notifications (WebSocket)

- [ ] **Add WebSocket Support**
  - [ ] Real-time trade updates
  - [ ] Live dashboard updates
  - [ ] Connection status indicator

---

## 🚀 Deployment Checklist

### Phase 5: Production Deployment

- [ ] **Backend Deployment**
  - [ ] Set up Railway/Azure App Service
  - [ ] Configure environment variables
  - [ ] Set up PostgreSQL (Supabase or managed instance)
  - [ ] Enable HTTPS
  - [ ] Set up monitoring (logs, errors)

- [ ] **Frontend Deployment**
  - [ ] Build production bundle (`npm run build`)
  - [ ] Deploy to Vercel/Netlify
  - [ ] Configure API_URL environment variable
  - [ ] Set up CDN for assets

- [ ] **CI/CD Pipeline**
  - [ ] GitHub Actions workflow
  - [ ] Automated testing on PR
  - [ ] Automated deployment on merge to main
  - [ ] Docker image building and pushing

- [ ] **Documentation**
  - [ ] API documentation (Swagger is auto-generated ✅)
  - [ ] Update README with deployment instructions
  - [ ] Add CONTRIBUTING.md with development guidelines
  - [ ] Add ARCHITECTURE.md with system design details

- [ ] **Security**
  - [ ] Rotate JWT_SECRET
  - [ ] Set up rate limiting
  - [ ] Add input validation/sanitization
  - [ ] Security headers (helmet.js equivalent)
  - [ ] SQL injection protection (SQLAlchemy handles this ✅)

---

## 📊 Progress Tracking

### Overall Completion: ~30%

| Phase | Status | Completion |
|-------|--------|------------|
| Phase 1: Backend Infrastructure | 🟡 In Progress | 70% |
| Phase 2: SEC Scraper | 🔴 Not Started | 0% |
| Phase 3: Frontend Dashboard | 🔴 Not Started | 5% |
| Phase 4: Advanced Features | 🔴 Not Started | 0% |
| Phase 5: Deployment | 🔴 Not Started | 0% |

### Weekly Goals

**Week 1-2**: Complete Phase 1 (Backend Core)
- SQLAlchemy models
- Pydantic schemas
- API endpoints
- Service layer

**Week 3-4**: Complete Phase 2 (SEC Scraper)
- SEC client implementation
- Form 4 parser
- Scheduler setup
- First data ingestion

**Week 5-6**: Complete Phase 3 (Frontend)
- React components
- API integration
- Dashboard UI
- Charts and filters

**Week 7-8**: Phase 4 (Enhancements) + Phase 5 (Deployment)
- Testing
- AI insights (optional)
- Production deployment
- Documentation

---

## 🐛 Known Issues to Address

1. **PostgreSQL Connection from Windows** (DEFERRED)
   - Impact: `/health` endpoint shows database error
   - Workaround: Deploy to Linux or use WSL2
   - Priority: Low (not blocking development)

2. **Frontend Files are Empty**
   - Impact: Cannot run frontend yet
   - Priority: High (Phase 3)

3. **No Sample Data**
   - Impact: Cannot test API without data
   - Solution: Add seed data script or run scraper
   - Priority: Medium

---

## 💡 Nice-to-Have Features (Future)

- [ ] Congressional trade tracking (House/Senate disclosures)
- [ ] Options flow tracking
- [ ] Dark pool activity detection
- [ ] Mobile app (React Native)
- [ ] Machine learning predictions
- [ ] International market support (UK, EU)
- [ ] Social sentiment analysis (Twitter/Reddit)
- [ ] Portfolio tracking (personal watchlist)
- [ ] Email digest (weekly summary)
- [ ] Public API with rate limiting
- [ ] Premium features (advanced alerts, AI insights)

---

## 📝 Notes

- **SEC User Agent**: Must use your real name and email (required by SEC)
- **Rate Limits**: SEC allows 10 requests/second - don't exceed this
- **Data Quality**: Form 4 filings can have errors - add validation
- **Timezone**: All timestamps should be UTC
- **Database**: Use transactions for multi-table inserts
- **API Design**: Follow REST conventions (GET for reads, POST for creates)
- **Error Handling**: Always return proper HTTP status codes
- **Logging**: Log all scraper runs, API errors, and database operations

---

**Last Updated**: October 26, 2025
**Maintained By**: Saad Kadri (er.saadk16@gmail.com)
**Repository**: https://github.com/yourusername/trade-signal
