# TradeSignal 📊

> Track insider trades and political stock transactions in real-time. Monitor SEC filings, analyze patterns, and get AI-powered insights on market-moving trades.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/react-18+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5+-blue.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![TradeSignal Demo](docs/demo.gif)
<!-- Add demo screenshot/gif later -->

## 📊 Current Status

**✅ FULLY OPERATIONAL** - All core features implemented and deployed via Docker

- **109+ Companies** actively tracked with hourly automated scraping
- **Real-time Data** via WebSocket connections and 15-second market updates
- **AI Integration** with Google Gemini 2.0 Flash for insights and chatbot
- **Multi-channel Alerts** with webhooks, email, and browser push notifications
- **Live Market Data** from Yahoo Finance with intelligent caching
- **8 Database Models** with full CRUD operations and pagination
- **60+ API Endpoints** documented with interactive Swagger UI
- **Celery Background Tasks** for automated scraping and alerts
- **Docker Deployment** with PostgreSQL, Redis, Celery, Flower, and monitoring

**Access Your TradeSignal Instance:**
- Frontend Dashboard: http://localhost:5174
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Celery Flower: http://localhost:5555

---

## 🚀 Features

- **📡 Real-Time SEC Monitoring**: Track Form 4 insider trading filings within minutes of publication
- **📊 Live Market Overview**: Real-time stock prices for 109+ companies with 15-second auto-refresh
- **🤖 AI-Powered Insights**: Google Gemini 2.0 Flash analysis with daily summaries and trading signals
- **🔔 Smart Alerts**: Multi-channel notifications (webhooks, email, browser push) with custom filters
- **⚡ Real-Time Dashboard**: WebSocket-powered live updates with trade streaming
- **🎯 Advanced Filtering**: Search by ticker, insider role, trade value, transaction type
- **📈 Market Analytics**: Live top gainers/losers, insider activity patterns, buy/sell ratios
- **🔄 Auto-Scraping**: Hourly automated SEC filing scraping for 109+ companies
- **💬 AI Chatbot**: Interactive Q&A about insider trading with real-time data access

## 🎯 Use Cases

- **Retail Investors**: Follow smart money and identify investment opportunities
- **Financial Analysts**: Research insider trading patterns and sentiment
- **Compliance Teams**: Monitor regulatory filings for red flags
- **Academic Research**: Study market efficiency and insider behavior
- **News/Media**: Track and report on significant insider activity

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Data Processing**: Pandas, BeautifulSoup, lxml
- **AI/ML**: Google Gemini 2.0 Flash, OpenAI GPT-4o-mini
- **Market Data**: Yahoo Finance (yfinance), Alpha Vantage (fallback)
- **Task Scheduling**: APScheduler
- **Notifications**: pywebpush, SendGrid, webhooks

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **State Management**: React Query, Zustand
- **Real-Time**: WebSocket API

### DevOps
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Hosting**: Railway / Azure App Service
- **Database**: Supabase (PostgreSQL)

## 📊 Data Sources

- **SEC EDGAR**: Form 4 filings (corporate insiders) - 100% live data
- **Yahoo Finance**: Real-time stock prices (primary, free)
- **Alpha Vantage**: Market data fallback (requires API key)
- **Google Gemini**: AI-powered trade analysis (1500 free requests/day)
- **OpenAI GPT-4**: AI fallback for insights
- **House/Senate Disclosures**: Congressional trades (planned Phase 7)

## 🏗️ Architecture
```
┌─────────────────┐
│   SEC EDGAR     │
│   API Scraper   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│   Data Pipeline │─────▶│   PostgreSQL     │
│   (Python)      │      │   Database       │
└─────────────────┘      └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   FastAPI        │
                         │   Backend        │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
            ┌──────────┐  ┌──────────┐  ┌──────────┐
            │ REST API │  │WebSocket │  │ OpenAI   │
            └─────┬────┘  └─────┬────┘  └──────────┘
                  │             │
                  └──────┬──────┘
                         ▼
                  ┌──────────────┐
                  │    React     │
                  │   Dashboard  │
                  └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (or Supabase account)
- Docker (optional, for containerized setup)

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/trade-signal.git
cd trade-signal
```

**2. Set up environment variables**
```bash
# Copy the example
cp .env.example .env

# Edit .env and add minimum required values:
```

Minimum required configuration:
```env
# Database (use Docker or Supabase)
DATABASE_URL=postgresql://tradesignal:tradesignal_dev@localhost:5432/tradesignal

# SEC EDGAR (REQUIRED - use your info)
SEC_USER_AGENT=Saad Kadri er.saadk16@gmail.com

# Security
JWT_SECRET=your-random-secret-key-change-this
JWT_ALGORITHM=HS256

# Features (disable AI for now)
ENABLE_AI_INSIGHTS=false
ENABLE_WEBHOOKS=false

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

**3. Start PostgreSQL Database**
```bash
# Start only PostgreSQL from docker-compose
docker-compose up postgres -d

# Verify it's running
docker ps
```

**4. Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**5. Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

**6. Initialize Database**
```bash
# Run migrations (details in docs/DEPLOYMENT.md)
```

### Docker Setup (Recommended)
```bash
docker-compose up --build
```

Access:
- Frontend: http://localhost:5174
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📖 Documentation

- [Backend Documentation](backend/README.md) - API endpoints, setup, database schema
- [Frontend Documentation](frontend/README.md) - React components, state management, deployment
- [Project Status](PROJECT_STATUS.md) - Development progress, phase completion, test results
- Interactive API Docs: http://localhost:8000/docs (when backend is running)

## 🔑 Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/tradesignal

# AI Providers (optional)
GEMINI_API_KEY=your-gemini-key  # Free tier: 1500 requests/day
OPENAI_API_KEY=sk-...           # Fallback
AI_PROVIDER=gemini              # gemini or openai

# Market Data (optional)
ALPHA_VANTAGE_API_KEY=...       # Fallback for Yahoo Finance

# Security
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256

# Features
ENABLE_AI_INSIGHTS=true
ENABLE_WEBHOOKS=true
ENABLE_EMAIL_ALERTS=false
ENABLE_PUSH_NOTIFICATIONS=false
```

See `.env.example` for full configuration.

## 🧪 Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📈 Roadmap

### ✅ Phase 1: Backend Core (COMPLETED)
- [x] FastAPI backend with REST API
- [x] PostgreSQL database with SQLAlchemy ORM
- [x] Database models (Companies, Insiders, Trades)
- [x] 21 API endpoints fully tested
- [x] Docker containerization
- [x] Seed data for testing

### ✅ Phase 2: SEC Scraper (COMPLETED)
- [x] SEC EDGAR API client with rate limiting
- [x] Form 4 XML parser (insider trades)
- [x] Real-time scraper service
- [x] Auto-create companies and insiders
- [x] Scraper API endpoints
- [x] Successfully tested with 109+ companies

### ✅ Phase 3: Frontend Dashboard (COMPLETED)
- [x] React 18 dashboard with TypeScript
- [x] Tailwind CSS styling
- [x] Trade listing with advanced filtering
- [x] Company/insider profiles
- [x] Real-time updates (WebSocket)
- [x] Charts and analytics (Recharts)
- [x] Responsive design

### ✅ Phase 4: Scheduled Auto-Scraping (COMPLETED)
- [x] APScheduler integration
- [x] Hourly automated scraping (all 109+ companies)
- [x] Intelligent cooldown (23-hour per company)
- [x] Job management API endpoints
- [x] Error handling and retry logic

### ✅ Phase 5: Notifications & Alerts (COMPLETED)
- [x] Alert rule engine with flexible filters
- [x] Multi-channel notifications (webhooks, email, push)
- [x] Real-time WebSocket alert streaming
- [x] Alert management UI
- [x] Slack/Discord integration tested
- [x] Browser push notifications with VAPID

### ✅ Phase 6: AI-Powered Insights (COMPLETED)
- [x] Google Gemini 2.0 Flash integration (free tier)
- [x] OpenAI GPT-4o-mini fallback
- [x] Daily market summary (news feed style)
- [x] Trading signals (bullish/bearish/neutral)
- [x] Company-specific AI analysis
- [x] Interactive AI chatbot with real data
- [x] AI Insights dashboard page

### ✅ Phase 6.5: Live Market Overview (COMPLETED - Nov 10, 2025)
- [x] Yahoo Finance integration (primary)
- [x] Alpha Vantage fallback
- [x] Real-time prices for 109+ stocks
- [x] 15-second auto-refresh
- [x] Parallel fetching (7-8s for all stocks)
- [x] Market Overview page with search/filter/sort
- [x] Dashboard widget (top gainers/losers)
- [x] Intelligent caching (10s TTL)

### 📋 Future Phases
- [ ] **Phase 7**: Congressional trade tracking (House/Senate)
- [ ] **Phase 8**: Mobile app (React Native, iOS/Android)
- [ ] Machine learning predictions
- [ ] Options flow tracking
- [ ] International market support
- [ ] Advanced portfolio tracking

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This platform is for informational and educational purposes only. It does not constitute financial advice. Always do your own research and consult with a qualified financial advisor before making investment decisions. Insider trading data is publicly available but trading based solely on this information carries risks.

## 🙏 Acknowledgments

- Data sourced from SEC EDGAR (public domain)
- Built with amazing open-source tools
- Inspired by platforms like Capitol Trades and OpenInsider

## 👨‍💻 Author

**Saad Kadri**
- LinkedIn: [linkedin.com/in/yourprofile](https://linkedin.com/in/yourprofile)
- Email: er.saadk16@gmail.com

## ⭐ Show Your Support

If you find this project useful, please give it a star! It helps others discover the project.

---

**Built with ❤️ by Saad Kadri | MS Computer Science @ UT Arlington**
