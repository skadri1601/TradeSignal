# TradeSignal

> Real-time insider trading intelligence platform for tracking SEC Form 4 filings, congressional trades, and market-moving transactions with AI-powered insights and professional research tools.

## Overview

TradeSignal is a comprehensive financial intelligence platform that aggregates and analyzes insider trading activity, congressional stock transactions, and market data to help users make informed investment decisions. Built with modern technologies and real-time data processing.

## Tech Stack

### Backend
- **FastAPI** - High-performance async Python web framework
- **PostgreSQL** - Primary database (Supabase hosted)
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
- **React Query** - Server state management

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy (production)
- **Supabase** - Managed PostgreSQL database
- **Grafana** - Metrics visualization (optional)

## Key Features

### Backend Services (25+ API Routers)

#### Core Services
1. **Authentication** - JWT-based auth with login, register, password reset
2. **Insider Trades** - SEC Form 4 scraping and tracking
3. **Congressional Trades** - Political stock transaction monitoring
4. **Companies & Insiders** - Detailed profiles and historical data
5. **Billing** - Stripe integration with 4-tier subscription system

#### Research & Analytics (PRO Features)
6. **Research API** - IVT, TS Score, Risk Level, Thesis data
7. **AI Insights** - AI-powered trade analysis and summaries
8. **Patterns Detection** - Insider trading pattern recognition
9. **Enterprise Research** - Advanced research endpoints

#### Data & Monitoring
10. **News** - Financial news aggregation and filtering
11. **Federal Reserve** - Fed calendar and economic event tracking
12. **Earnings** - Earnings calendar and reports
13. **Stock Prices** - Live market data integration
14. **Data Health** - Data quality monitoring

#### Administration
15. **Admin Dashboard** - User management and system administration
16. **Scheduler** - Automated scraping with configurable schedules
17. **Tasks** - Background task management
18. **Health Checks** - System monitoring and uptime tracking

#### User Features
19. **Alerts** - Custom trade alerts and notifications
20. **Push Notifications** - Real-time alerts for important trades
21. **Contact & Support** - Ticket system for user inquiries
22. **Jobs** - Career opportunities and applications

#### Enterprise Features
23. **Webhooks** - Custom webhook integrations
24. **Enterprise API** - High-volume API access
25. **Marketing API** - Campaign management

### Frontend Pages (20+)

#### Authentication
- Login, Register, Password Reset, Profile

#### Dashboard & Trading
- **Dashboard** - Overview of recent trades and market activity
- **Trades** - Insider trading activity with filtering
- **Congressional Trades** - Political trading transparency
- **Market Overview** - Live market indices and sector performance
- **Patterns** - Trading pattern analysis

#### Company & Insider Research
- **Company Pages** - Detailed company info with research badges (IVT, TS Score, Risk Level)
- **Insider Pages** - Individual insider profiles and trade history

#### News & Events
- **News** - Curated financial news feed
- **Fed Calendar** - Upcoming economic events

#### AI & Research (PRO)
- **AI Insights** - AI-powered analysis

#### Education
- **Lessons** - Educational content for users
- **Strategies** - Trading strategy guides

#### Account & Billing
- **Pricing** - Subscription tiers and feature comparison
- **Order History** - Billing and subscription management
- **Profile** - User settings

#### Support & Info
- **Support & FAQ** - Help center and documentation
- **Contact & Careers** - Public pages for inquiries and job listings
- **Blog** - Company blog
- **About, Terms, Privacy** - Legal and informational pages

## Subscription Tiers

| Feature | Free | Plus | PRO | Enterprise |
|---------|------|------|-----|------------|
| Insider Trades | Limited | Full | Full | Full |
| Congressional Trades | View | Full | Full | Full |
| Research Badges (IVT, TS Score, Risk) | - | - | ✓ | ✓ |
| AI Insights | - | - | ✓ | ✓ |
| Pattern Detection | - | - | ✓ | ✓ |
| Custom Alerts | 3 | 10 | Unlimited | Unlimited |
| API Access | - | - | Limited | Full |
| Webhooks | - | - | - | ✓ |
| Priority Support | - | - | ✓ | ✓ |

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

#### Celery Worker (for background tasks)
```bash
cd backend
celery -A app.core.celery_app worker --loglevel=info --pool=solo
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
# Database (Supabase)
DATABASE_URL=postgresql://user:pass@db.supabase.co:5432/postgres

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe Billing
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# SEC API
SEC_USER_AGENT=YourApp/1.0 (your@email.com)

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
- `/api/v1/research/*` - Research data (PRO)
- `/api/v1/ai/*` - AI insights (PRO)
- `/api/v1/news/*` - Financial news
- `/api/v1/admin/*` - Administration

## Project Structure

```
TradeSignal/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── core/           # Core utilities (security, cache, celery)
│   │   ├── models/         # SQLAlchemy database models
│   │   ├── routers/        # API endpoint routes (25+)
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # Business logic layer
│   │   ├── tasks/          # Celery background tasks
│   │   ├── middleware/     # Custom middleware
│   │   └── main.py         # Application entry point
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── api/           # API client functions
│   │   ├── components/    # React components
│   │   │   ├── research/  # Research badges (IVT, TS Score, Risk)
│   │   │   ├── layout/    # Layout components
│   │   │   └── ...
│   │   ├── contexts/      # React contexts (Auth, Notifications)
│   │   ├── hooks/         # Custom React hooks
│   │   ├── pages/         # Page components (20+)
│   │   └── App.tsx        # Application root
│   └── package.json       # Node dependencies
├── Docs/                   # Documentation
├── docker-compose.yml     # Docker orchestration
└── README.md             # This file
```

## Development Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Run tests: `pytest` (backend) / `npm test` (frontend)
4. Commit changes: `git commit -m "feat: your feature"`
5. Push and create PR: `git push origin feature/your-feature`

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
3. Set up production database (Supabase recommended)
4. Configure Redis for production
5. Deploy with Docker Compose or Kubernetes
6. Set up monitoring and logging
7. Configure backup strategy

See [backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md) for detailed deployment instructions.

## Documentation

- **[Backend README](backend/README.md)** - Backend setup and development
- **[Frontend README](frontend/README.md)** - Frontend setup and development
- **[Docs/](Docs/)** - Additional documentation
- **API Documentation** - Interactive API docs at `http://localhost:8000/docs`

## Support

- **Documentation:** See [Docs/](Docs/) directory
- **Email Support:** support@tradesignal.com
- **Issues:** Create a GitHub issue

## License

This project is proprietary software. All rights reserved.
