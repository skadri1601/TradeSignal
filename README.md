# TradeSignal

> Real-time insider trading intelligence platform for tracking SEC Form 4 filings, congressional trades, and market-moving transactions with AI-powered insights.

## Overview

TradeSignal is a comprehensive financial intelligence platform that aggregates and analyzes insider trading activity, congressional stock transactions, and market data to help users make informed investment decisions. Built with modern technologies and real-time data processing.

## Tech Stack

### Backend
- **FastAPI** - High-performance async Python web framework
- **PostgreSQL** - Primary database for structured data
- **Redis** - Caching and rate limiting
- **Celery** - Distributed task queue for scheduled scraping
- **SQLAlchemy** - ORM and database management
- **Prometheus** - Metrics and monitoring

### Frontend
- **React 18** - Modern UI library with hooks
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **React Router** - Client-side routing

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy (production)
- **Grafana** - Metrics visualization (optional)

## Key Features

### Backend (14 Core Services)
1. **Authentication** - JWT-based auth with login, register, password reset
2. **Insider Trades** - SEC Form 4 scraping and tracking
3. **Congressional Trades** - Political stock transaction monitoring
4. **Companies & Insiders** - Detailed profiles and historical data
5. **Billing** - Stripe integration with 3-tier subscription system (Free, Plus, Pro, Enterprise)
6. **News** - Financial news aggregation and filtering
7. **Federal Reserve** - Fed calendar and economic event tracking
8. **Jobs** - Career opportunities and applications
9. **Admin Dashboard** - User management and system administration
10. **Contact & Support** - Ticket system for user inquiries
11. **Health Checks** - System monitoring and uptime tracking
12. **Push Notifications** - Real-time alerts for important trades
13. **Stock Prices** - Live market data integration
14. **Scheduler** - Automated scraping with configurable schedules

### Frontend (16 Pages)
1. **Authentication** - Login, Register, Password Reset, Profile
2. **Dashboard** - Overview of recent trades and market activity
3. **Trades** - Insider trading activity with filtering
4. **Congressional Trades** - Political trading transparency
5. **Market Overview** - Live market indices and sector performance
6. **News** - Curated financial news feed
7. **Fed Calendar** - Upcoming economic events
8. **Company Pages** - Detailed company information and insider activity
9. **Insider Pages** - Individual insider profiles and trade history
10. **Admin Dashboard** - System administration interface
11. **Pricing** - Subscription tiers and feature comparison
12. **Support & FAQ** - Help center and documentation
13. **Contact & Careers** - Public pages for inquiries and job listings
14. **Lessons & Strategies** - Educational content for users
15. **Order History** - Billing and subscription management
16. **Terms, Privacy, About** - Legal and informational pages

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/TradeSignal.git
cd TradeSignal
```

2. Create environment files:
```bash
# Backend environment
cp backend/.env.example backend/.env

# Frontend environment
cp frontend/.env.example frontend/.env
```

3. Configure environment variables (see below)

### Docker Deployment (Recommended)

Start all services with Docker Compose:
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

### Backend Key Variables
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/tradesignal

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe Billing
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# SEC API
SEC_API_KEY=your-sec-api-key

# Feature Flags
ENABLE_AI_INSIGHTS=true
ENABLE_WEBHOOKS=true
SCHEDULER_ENABLED=true
```

### Frontend Key Variables
```env
VITE_API_URL=http://localhost:8000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key API Endpoints
- `/api/v1/auth/*` - Authentication
- `/api/v1/trades/*` - Insider trades
- `/api/v1/congressional-trades/*` - Congressional trades
- `/api/v1/companies/*` - Company data
- `/api/v1/insiders/*` - Insider profiles
- `/api/v1/news/*` - Financial news
- `/api/v1/admin/*` - Administration

## Project Structure

```
TradeSignal/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── core/           # Core utilities (security, cache, limiter)
│   │   ├── models/         # SQLAlchemy database models
│   │   ├── routers/        # API endpoint routes
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # Business logic layer
│   │   ├── tasks/          # Celery background tasks
│   │   └── main.py         # Application entry point
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── api/           # API client functions
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts (Auth, Notifications)
│   │   ├── hooks/         # Custom React hooks
│   │   ├── pages/         # Page components
│   │   └── App.tsx        # Application root
│   └── package.json       # Node dependencies
├── docker-compose.yml     # Docker orchestration
└── README.md             # This file
```

## Development Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Run tests: `pytest` (backend) / `npm test` (frontend)
4. Commit changes: `git commit -m "feat: your feature"`
5. Push and create PR: `git push origin feature/your-feature`

## Monitoring

Optional monitoring stack with Prometheus and Grafana:
```bash
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

Access:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

## Testing

### Backend
```bash
cd backend
pytest                          # Run all tests
pytest tests/test_trades_api.py  # Run specific test
pytest --cov=app               # Run with coverage
```

### Frontend
```bash
cd frontend
npm test              # Run tests
npm run test:watch    # Watch mode
```

## Deployment

Production deployment guide:
1. Set production environment variables
2. Configure SSL/TLS certificates
3. Set up production database (PostgreSQL)
4. Configure Redis for production
5. Deploy with Docker Compose or Kubernetes
6. Set up monitoring and logging
7. Configure backup strategy

See [backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md) for detailed deployment instructions.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

Please follow the existing code style and include tests for new features.

## License

This project is proprietary software. All rights reserved.

## Documentation

### User Documentation

- **[Getting Started Guide](docs/GETTING_STARTED.md)** - New user guide and first steps
- **[FAQ](docs/FAQ.md)** - Frequently asked questions
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Release Notes](docs/RELEASE_NOTES_ALPHA_v1.0.0.md)** - Alpha v1.0.0 release notes and data source status
- **[Changelog](CHANGELOG.md)** - Version history and changes

### Feature Guides

- **[Insider Trades Guide](docs/FEATURES/INSIDER_TRADES.md)** - How to use insider trading features
- **[Congressional Trades Guide](docs/FEATURES/CONGRESSIONAL_TRADES.md)** - Congressional trade monitoring (Beta)
- **[AI Insights Guide](docs/FEATURES/AI_INSIGHTS.md)** - AI-powered analysis features (Beta)

### Alerts & Notifications

- **[Alerts Setup Guide](docs/ALERTS_SETUP.md)** - How to create and manage alerts
- **[Discord Webhooks Guide](docs/ALERTS_DISCORD_WEBHOOKS.md)** - Setting up Discord webhook notifications

### Developer Documentation

- **[Backend README](backend/README.md)** - Backend setup and development
- **[Frontend README](frontend/README.md)** - Frontend setup and development
- **API Documentation** - Interactive API docs at `http://localhost:8000/docs` (Swagger UI)

## Support

- **Documentation:** See [docs/](docs/) directory for user guides
- **Email Support:** support@tradesignal.com
- **Issues:** Create a GitHub issue
- **Technical Docs:** [backend/README.md](backend/README.md), [frontend/README.md](frontend/README.md)

## Roadmap

See [TradeSignal.md](TradeSignal.md) for future features and enhancements.
