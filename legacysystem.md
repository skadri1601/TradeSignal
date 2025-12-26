# TradeSignal Legacy System Architecture

> **Multi-Language Enterprise Architecture** | Python Legacy + TypeScript New Features

## Table of Contents
- [Overview](#overview)
- [Architecture Decision](#architecture-decision)
- [System Boundaries](#system-boundaries)
- [Communication Layer](#communication-layer)
- [Development Workflow](#development-workflow)
- [Technical Stack Comparison](#technical-stack-comparison)
- [Deployment Architecture](#deployment-architecture)
- [Team Structure](#team-structure)
- [Migration Strategy](#migration-strategy)

---

## Overview

TradeSignal employs a **hybrid multi-language architecture** following enterprise patterns used by major technology companies like Microsoft, Google, and Amazon. This approach allows us to:

- **Preserve existing investments** - 48,184 lines of working Python code remain untouched
- **Optimize for AI-driven development** - New features in TypeScript benefit from compile-time safety
- **Maintain production stability** - No risky rewrites of battle-tested code
- **Leverage language strengths** - Python for AI/ML/data, TypeScript for business logic

```
┌─────────────────────────────────────────────────────────────┐
│                    TradeSignal Platform                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Frontend: React 18 + TypeScript + Vite                     │
│  ┌───────────────────────────────────────────────────┐      │
│  │  User Interface (All Pages & Components)          │      │
│  └───────────────┬───────────────────────────────────┘      │
│                  │                                            │
│       ┌──────────┴──────────┐                               │
│       │                     │                               │
│  ┌────▼────────────┐  ┌────▼──────────────────┐            │
│  │  TypeScript     │  │  Python Backend       │            │
│  │  Backend (NEW)  │  │  (LEGACY - Frozen)    │            │
│  │                 │  │                       │            │
│  │  Next.js API    │  │  FastAPI              │            │
│  │  - New features │  │  - AI/ML (LUNA)       │            │
│  │  - Business     │  │  - Data pipelines     │            │
│  │    logic        │  │  - SEC scraping       │            │
│  │  - REST APIs    │  │  - Form 4 parsing     │            │
│  │                 │  │  - Financial calcs    │            │
│  │  Status: ACTIVE │  │  - Celery tasks       │            │
│  │                 │  │                       │            │
│  │                 │  │  Status: MAINTENANCE  │            │
│  └────┬────────────┘  └────┬──────────────────┘            │
│       │                    │                               │
│       └────────┬───────────┘                               │
│                │                                            │
│       ┌────────▼──────────────┐                            │
│       │  Shared Resources      │                            │
│       │  - PostgreSQL Database │                            │
│       │  - Redis Cache         │                            │
│       │  - Message Queue       │                            │
│       └────────────────────────┘                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture Decision

### Why Hybrid Python + TypeScript?

After analyzing production issues and development velocity, we identified that **the problem wasn't Python itself**, but rather:

1. **AI Development Team Efficiency** - Our team consists of AI coding assistants (Claude Code, Cursor, Gemini, Kilo Code)
2. **Compile-Time Safety** - TypeScript catches 70% of bugs before runtime, reducing testing burden
3. **Faster Iteration** - AI assistants make fewer mistakes with TypeScript due to immediate compiler feedback
4. **Better Code Generation** - Type systems help AI understand intent faster with less back-and-forth

### What We're NOT Doing

- ❌ **Rewriting 48K lines of Python code** - Too risky, too expensive
- ❌ **Replacing what works** - Python services are production-stable
- ❌ **Full migration** - Legacy and new systems coexist indefinitely
- ❌ **Abandoning Python** - It remains critical for AI/ML/data workloads

### What We ARE Doing

- ✅ **Freezing Python at current feature set** - Maintenance-only mode
- ✅ **Building all NEW features in TypeScript** - Active development
- ✅ **Optimizing for AI code generation** - TypeScript's compile-time feedback
- ✅ **Following enterprise patterns** - Like Microsoft's C# legacy + Python services

---

## System Boundaries

### Python Backend (LEGACY - Frozen)

**Status**: 🔒 **MAINTENANCE ONLY** - No new features

#### What Stays in Python

| Category | Components | Reason |
|----------|-----------|---------|
| **AI/ML Services** | LUNA Engine, Gemini 2.5 Flash/Pro, OpenAI integration | Python's AI ecosystem is unmatched |
| **Data Pipelines** | SEC scraping, Congressional trades, Form 4 parsing | Complex XML parsing, recovery mode |
| **Financial Calculations** | Decimal arithmetic, DCF models, IVT calculations | Native Decimal type for precision |
| **Background Tasks** | Celery workers, Beat scheduler, async jobs | Mature task queue ecosystem |
| **Technical Analysis** | numpy/pandas/scikit-learn for predictions | Scientific computing libraries |
| **Data Processing** | Insider pattern analysis, feature extraction | Pandas/numpy optimized workflows |

#### Python Codebase Inventory

- **Total Lines of Code**: 48,184 LOC
- **API Endpoints**: 246 endpoints across 38 routers
- **Database Models**: 40 SQLAlchemy models
- **Services**: 62 business logic services
- **Background Tasks**: 173 Celery task references
- **External APIs**: 10+ integrations (SEC, Finnhub, Alpha Vantage, Gemini, etc.)

#### Python Tech Stack

```python
# Core Framework
FastAPI==0.104.1          # Async web framework
SQLAlchemy==2.0.23        # ORM with type hints
Pydantic==2.5.0           # Data validation

# AI/ML
google-generativeai       # Gemini 2.5 Flash & Pro
openai                    # GPT fallback
numpy==1.26.2             # Numerical computing
pandas==2.1.3             # Data analysis
scikit-learn==1.3.2       # ML models

# Data Processing
lxml                      # Robust XML parsing (Form 4)
ta==0.11.0                # Technical analysis indicators

# Background Jobs
celery==5.3.4             # Distributed task queue
redis==5.0.1              # Message broker & cache

# Database
psycopg2-binary           # PostgreSQL adapter
asyncpg                   # Async PostgreSQL
```

---

### TypeScript Backend (NEW - Active Development)

**Status**: 🚀 **ACTIVE DEVELOPMENT** - All new features here

#### What Goes in TypeScript

| Category | Components | Reason |
|----------|-----------|---------|
| **New API Endpoints** | All future REST APIs | TypeScript compile-time safety |
| **Business Logic** | New feature implementations | Better for AI code generation |
| **User-Facing Features** | Social trading, notifications, etc. | Modern ecosystem |
| **Integrations** | New third-party services | Excellent SDK support |
| **Real-Time Features** | WebSockets, live updates | Native async/await |
| **Authentication Middleware** | Rate limiting, routing, caching | Next.js middleware |

#### TypeScript Tech Stack

```typescript
// Framework
"next": "^14.0.0"              // Full-stack React framework
"@types/node": "^20.0.0"       // Node.js types

// Database ORM (Choose one)
"prisma": "^5.0.0"             // Modern ORM with migrations
// OR
"typeorm": "^0.3.0"            // Alternative ORM

// API & Validation
"zod": "^3.22.0"               // Schema validation
"axios": "^1.6.0"              // HTTP client

// Real-time
"socket.io": "^4.6.0"          // WebSocket support

// Background Jobs (if needed)
"bull": "^4.11.0"              // Redis-backed job queue
"node-cron": "^3.0.0"          // Scheduled tasks
```

#### Communication with Python Backend

TypeScript services will call Python services via REST APIs:

```typescript
// Example: Calling Python AI service from TypeScript
const getAIAnalysis = async (ticker: string) => {
  const response = await axios.get(
    `${PYTHON_BACKEND_URL}/api/v1/ai/analysis/${ticker}`,
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );
  return response.data;
};
```

---

## Communication Layer

### REST APIs Between Services

Both TypeScript and Python backends expose REST APIs that can call each other:

```
┌──────────────────────┐
│  TypeScript Backend  │
│  (Next.js API)       │
│                      │
│  POST /api/social    │◄─── New feature request
│    ├─ Validate data  │
│    ├─ Store in DB    │
│    └─ Call Python ───┼────┐
│                      │    │
└──────────────────────┘    │
                            │
                            ▼
                  ┌─────────────────────┐
                  │  Python Backend     │
                  │  (FastAPI)          │
                  │                     │
                  │  GET /api/v1/ai/    │
                  │    └─ LUNA analysis │
                  │                     │
                  └─────────────────────┘
```

### Shared PostgreSQL Database

Both services connect to the same database:

```
TypeScript (Prisma)  ────┐
                         │
                         ▼
                   ┌──────────┐
                   │PostgreSQL│
                   │(Supabase)│
                   └──────────┘
                         ▲
                         │
Python (SQLAlchemy) ─────┘
```

**Database Access Pattern**:
- **Python**: Owns AI/ML tables, trades, companies, insiders (read/write)
- **TypeScript**: New feature tables (read/write), can read legacy tables

### API Authentication

Shared JWT authentication:

```typescript
// TypeScript validates token
const user = verifyJWT(token);

// Passes token to Python service
const analysis = await pythonAPI.get('/api/v1/ai/analysis', {
  headers: { Authorization: `Bearer ${token}` }
});
```

---

## Development Workflow

### New Feature Checklist

When implementing a new feature, follow this decision tree:

```
┌─────────────────────────┐
│  New Feature Request    │
└────────────┬────────────┘
             │
             ▼
    ┌────────────────────┐
    │ Does it require    │
    │ AI/ML processing,  │
    │ data pipelines, or │
    │ financial calcs?   │
    └────────┬───────────┘
             │
        ┌────┴────┐
        │         │
       YES       NO
        │         │
        ▼         ▼
   ┌────────┐  ┌──────────┐
   │ Python │  │TypeScript│
   │(Extend)│  │  (New)   │
   └────────┘  └──────────┘
```

### When to Use Python vs TypeScript

| Scenario | Language | Rationale |
|----------|----------|-----------|
| New user-facing API endpoint | **TypeScript** | Compile-time safety, AI-friendly |
| Fix bug in existing Python code | **Python** | Don't mix languages for single feature |
| Add new AI model integration | **Python** | Leverage AI/ML ecosystem |
| Create new business logic | **TypeScript** | Modern development, type safety |
| Extend SEC scraping | **Python** | Complex existing pipeline |
| Build social features | **TypeScript** | New feature, user-facing |
| Update financial calculations | **Python** | Requires Decimal precision |
| Add real-time notifications | **TypeScript** | WebSocket support |

### Testing Strategy

**Python (Legacy)**:
- **Unit tests** for critical bug fixes only
- **Integration tests** for existing API endpoints
- **Regression tests** to prevent breaking changes
- **No new feature tests** (maintenance mode)

**TypeScript (New)**:
- **Unit tests** for all new business logic
- **Integration tests** for API endpoints
- **E2E tests** for user flows
- **Type checking** as first line of defense (tsc)

### Git Workflow

```bash
# Python fixes (rare)
git checkout -b fix/python-bug-description
# Make minimal changes
git commit -m "fix(python): description"

# TypeScript features (common)
git checkout -b feature/new-feature-name
# Build new feature
git commit -m "feat(ts): description"
```

---

## Technical Stack Comparison

### Side-by-Side Comparison

| Aspect | Python (Legacy) | TypeScript (New) |
|--------|----------------|------------------|
| **Framework** | FastAPI | Next.js |
| **ORM** | SQLAlchemy 2.0 | Prisma / TypeORM |
| **Validation** | Pydantic | Zod |
| **Background Jobs** | Celery + Redis | Bull / node-cron |
| **Type Safety** | MyPy (85% coverage) | TypeScript (100%) |
| **API Style** | RESTful | RESTful + Server Actions |
| **Authentication** | JWT (custom) | JWT (NextAuth.js) |
| **Database** | PostgreSQL (asyncpg) | PostgreSQL (Prisma) |
| **Caching** | Redis | Redis |
| **Testing** | Pytest | Jest / Vitest |
| **Deployment** | Render.com | Render.com |

### Performance Characteristics

| Metric | Python | TypeScript |
|--------|--------|-----------|
| **Cold Start** | ~2-3s (FastAPI) | ~1-2s (Next.js) |
| **Request Latency** | ~50-100ms | ~30-80ms |
| **Concurrency** | Async (uvicorn workers) | Event loop (Node.js) |
| **Memory Usage** | ~200-400MB | ~100-200MB |
| **AI/ML Tasks** | ✅ Excellent | ❌ Limited |
| **API Throughput** | ✅ High | ✅ Very High |

---

## Deployment Architecture

### Render.com Deployment

Both Python and TypeScript backends deploy to **Render.com** for consistency:

```
┌─────────────────────────────────────────────────┐
│           Render.com Platform                   │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────────┐  ┌─────────────────┐  │
│  │ TypeScript Service  │  │ Python Service  │  │
│  │ (New Features)      │  │ (Legacy AI/ML)  │  │
│  │                     │  │                 │  │
│  │ Port: 3001          │  │ Port: 8000      │  │
│  │ URL: /api/v2/*      │  │ URL: /api/v1/*  │  │
│  └──────────┬──────────┘  └────────┬────────┘  │
│             │                      │           │
│             └──────────┬───────────┘           │
│                        │                       │
│             ┌──────────▼──────────┐            │
│             │  Shared Database    │            │
│             │  PostgreSQL         │            │
│             │  (Supabase)         │            │
│             └─────────────────────┘            │
│                                                 │
│             ┌─────────────────────┐            │
│             │  Redis Cache        │            │
│             └─────────────────────┘            │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Environment Variables

**Python Service** (`.env`):
```bash
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=...
GEMINI_API_KEY=...
SEC_USER_AGENT=...
```

**TypeScript Service** (`.env`):
```bash
DATABASE_URL=postgresql://...          # Same database
REDIS_URL=redis://...                  # Same Redis
PYTHON_API_URL=http://python-service:8000
NEXTAUTH_SECRET=...
```

### Service-to-Service Communication

**Internal network** (same Render account):
```
TypeScript → http://tradesignal-python:8000/api/v1/ai/analysis
```

**Public endpoints** (if different Render accounts):
```
TypeScript → https://api.tradesignal.com/v1/ai/analysis
```

### Load Balancing & Scaling

```
User Request
    ↓
┌───────────────┐
│  Render CDN   │
└───────┬───────┘
        │
        ▼
┌───────────────────┐
│  Request Router   │
└────────┬──────────┘
         │
    ┌────┴─────┐
    ▼          ▼
/api/v2/*  /api/v1/*
    │          │
    ▼          ▼
┌────────┐ ┌────────┐
│  TS    │ │ Python │
│Service │ │Service │
└────────┘ └────────┘
```

---

## Team Structure

### AI-Driven Development Team

Our development team consists primarily of **AI coding assistants**:

| Team Member | Role | Specialization |
|-------------|------|----------------|
| **Claude Code** | Primary developer | Full-stack, architecture, debugging |
| **Cursor** | Code completion | Context-aware suggestions |
| **Gemini** | Research & analysis | API documentation, best practices |
| **Kilo Code** | Code review | Quality assurance |
| **Human (You)** | Testing & QA | Manual testing, user acceptance |

### Why TypeScript Optimizes for AI Agents

1. **Immediate Feedback Loop**
   - AI writes code → TypeScript compiler catches errors → AI fixes immediately
   - Python: AI writes code → User runs code → Finds error → Reports back → AI fixes

2. **Better Code Completion**
   - TypeScript interfaces provide precise type information
   - AI assistants understand intent faster with explicit types

3. **Self-Correction**
   - 70% of bugs caught at compile time
   - AI can iterate without human intervention

4. **Reduced Testing Burden**
   - Type system acts as first line of defense
   - Less manual testing required from you

### Development Workflow

```
┌──────────────┐
│ User Request │
└──────┬───────┘
       │
       ▼
┌─────────────────┐
│ Claude Code     │──► Analyzes requirement
│ (Planning)      │──► Chooses Python or TypeScript
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ AI Team         │──► Implements code
│ (Development)   │──► TypeScript compiler checks
└──────┬──────────┘    (or Python type hints)
       │
       ▼
┌─────────────────┐
│ User            │──► Manual testing
│ (QA)            │──► Acceptance testing
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Deployment      │──► Render.com
└─────────────────┘
```

---

## Migration Strategy

### Gradual Expansion (Not Migration)

This is **NOT a migration**—it's a **gradual expansion**:

```
Year 1 (Current)
┌────────────────────┐
│  Python: 100%      │
│  TypeScript: 0%    │
└────────────────────┘

Year 2 (Target)
┌────────────────────┐
│  Python: 100%      │  (Frozen, no growth)
│  TypeScript: 30%   │  (New features only)
└────────────────────┘

Year 3+
┌────────────────────┐
│  Python: 100%      │  (Stable legacy)
│  TypeScript: 80%+  │  (Majority of new code)
└────────────────────┘
```

### Feature Expansion Plan

**Phase 1: Setup (Current)**
- Set up Next.js TypeScript backend
- Configure Prisma/TypeORM
- Establish communication layer
- Deploy to Render.com

**Phase 2: First Features (Next)**
- Social trading features (new)
- Enhanced notifications (new)
- User preferences API (new)
- All call Python for AI analysis

**Phase 3: Growth**
- Portfolio tracking (new)
- Advanced analytics (new)
- Custom dashboards (new)
- Community features (new)

**Phase 4: Mature**
- TypeScript handles 80% of user requests
- Python focuses on AI/ML/data
- Both systems stable and coexisting

### No Code Rewrite

**Golden Rule**: Never rewrite working Python code unless:
1. ✅ Critical security vulnerability
2. ✅ Unfixable production bug
3. ✅ Performance bottleneck (after profiling)
4. ❌ "It would be cleaner in TypeScript" ← NO

---

## Decision Log

### Why Next.js Over Express/NestJS?

| Framework | Pros | Cons | Decision |
|-----------|------|------|----------|
| **Next.js** | Full-stack, API routes, React integration, Vercel optimization | Heavier than Express | ✅ **CHOSEN** |
| Express | Lightweight, flexible, huge ecosystem | No built-in structure | ❌ |
| NestJS | TypeScript-first, similar to FastAPI, DI | Steeper learning curve | ❌ |
| Fastify | High performance, low overhead | Smaller ecosystem | ❌ |

**Rationale**: Next.js provides the best DX for AI assistants with built-in TypeScript, API routes, and React integration.

### Why REST Over gRPC?

| Protocol | Pros | Cons | Decision |
|----------|------|------|----------|
| **REST** | Simple, familiar, browser-compatible | Slightly slower | ✅ **CHOSEN** |
| gRPC | High performance, streaming | Complex setup, not browser-friendly | ❌ |

**Rationale**: REST APIs are simpler for AI assistants to generate and maintain, with negligible performance difference for our scale.

### Why Shared Database Over Event Sourcing?

| Pattern | Pros | Cons | Decision |
|---------|------|------|----------|
| **Shared DB** | Simple, atomic transactions, no sync issues | Tight coupling | ✅ **CHOSEN** |
| Event Sourcing | Loose coupling, audit trail | Complex, eventual consistency | ❌ |

**Rationale**: Shared database is simpler to reason about and maintain for AI-driven development, with sufficient decoupling via clear service boundaries.

---

## Monitoring & Observability

### Health Checks

**Python Service**:
```
GET /api/v1/health
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "celery": "running"
}
```

**TypeScript Service**:
```
GET /api/v2/health
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "python_service": "reachable"
}
```

### Logging Strategy

Both services use structured JSON logging:

```typescript
// TypeScript
logger.info({
  service: 'typescript',
  endpoint: '/api/v2/social/post',
  user_id: userId,
  duration_ms: 45
});
```

```python
# Python
logger.info({
    "service": "python",
    "endpoint": "/api/v1/ai/analysis",
    "user_id": user_id,
    "duration_ms": 120
})
```

### Metrics

**Prometheus metrics** from both services:
- Request count & latency
- Database query duration
- Cache hit/miss rates
- Error rates by endpoint

---

## FAQ

### Q: Can we ever sunset the Python backend?

**A**: Unlikely. Python's AI/ML ecosystem is too strong, and the financial calculations require Decimal precision. The Python backend will remain indefinitely for these specialized workloads.

### Q: What if we need a new AI feature?

**A**: New AI features go in **Python**. TypeScript calls Python's AI endpoints via REST API.

### Q: Can TypeScript services read Python's database tables?

**A**: Yes, via Prisma/TypeORM schemas. But avoid writing to Python-owned tables to prevent conflicts.

### Q: What about database migrations?

**A**: Coordinate migrations between both services:
1. Python creates migration (Alembic)
2. TypeScript updates schema (Prisma migrate)
3. Test both services work

### Q: How do we handle authentication?

**A**: Shared JWT tokens. Both services validate the same JWT secret. TypeScript can issue tokens for new features.

### Q: What's the performance overhead of REST calls?

**A**: ~10-30ms per call. Negligible compared to AI inference (500ms+) or database queries (50ms+). Can add Redis caching if needed.

---

## Conclusion

TradeSignal's hybrid Python + TypeScript architecture represents a **pragmatic, enterprise-grade approach** to evolution:

- ✅ **Preserves 48K LOC of working Python code**
- ✅ **Optimizes new development for AI coding assistants**
- ✅ **Maintains production stability** (no risky rewrites)
- ✅ **Leverages each language's strengths** (Python for AI/ML, TypeScript for business logic)
- ✅ **Follows patterns used by Fortune 500 companies**

This architecture allows us to move fast with new features while respecting the significant investment in the existing Python codebase.

---

**Last Updated**: December 25, 2025
**Status**: Active Implementation
**Version**: 1.0
