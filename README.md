# TradeSignal 📊

> Track insider trades and political stock transactions in real-time. Monitor SEC filings, analyze patterns, and get AI-powered insights on market-moving trades.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/react-18+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5+-blue.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![TradeSignal Demo](docs/demo.gif)
<!-- Add demo screenshot/gif later -->

## 🚀 Features

- **📡 Real-Time SEC Monitoring**: Track Form 4 insider trading filings within minutes of publication
- **🏛️ Congressional Trade Tracking**: Monitor U.S. politician stock transactions (STOCK Act disclosures)
- **📊 Live Market Data**: Real-time stock and crypto price integration
- **🤖 AI-Powered Insights**: GPT-4o-generated analysis of trading patterns and significance
- **🔔 Smart Alerts**: Custom watchlists with email/webhook notifications
- **📈 Performance Analytics**: Historical win rates and pattern detection
- **⚡ Real-Time Dashboard**: WebSocket-powered live updates
- **🎯 Advanced Filtering**: Search by insider, company, trade size, date range

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
- **AI/ML**: OpenAI GPT-4o, scikit-learn
- **Task Scheduling**: APScheduler

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

- **SEC EDGAR**: Form 4 filings (corporate insiders)
- **House Financial Disclosures**: Congressional trades
- **Senate Financial Disclosures**: Senate trades
- **Yahoo Finance**: Stock prices (via yfinance)
- **CoinGecko API**: Cryptocurrency prices
- **Alpha Vantage**: Alternative market data

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
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📖 Documentation

- [API Documentation](docs/API.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Contributing Guide](CONTRIBUTING.md)

## 🔑 Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/tradesignal

# APIs
OPENAI_API_KEY=sk-...
ALPHA_VANTAGE_API_KEY=...

# Security
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256

# Features
ENABLE_AI_INSIGHTS=true
ENABLE_WEBHOOKS=true
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

- [x] SEC Form 4 scraper
- [x] FastAPI backend with REST API
- [x] React dashboard
- [x] Real-time WebSocket updates
- [ ] Congressional trade tracking
- [ ] AI-powered insights (GPT-4o)
- [ ] Email/webhook alerts
- [ ] Mobile app (React Native)
- [ ] Machine learning predictions
- [ ] Options flow tracking
- [ ] International market support

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
