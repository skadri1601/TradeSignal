# TradeSignal Frontend

React-based frontend application for TradeSignal. Provides a modern, responsive user interface for tracking insider trades, congressional stock transactions, and market intelligence with professional research tools.

## Tech Stack

- **React 18** - Modern UI library with concurrent features
- **TypeScript** - Type-safe JavaScript for better DX
- **Vite** - Fast build tool with hot module replacement
- **React Router 6** - Client-side routing with data loading
- **Tailwind CSS** - Utility-first CSS framework
- **Headless UI** - Unstyled, accessible UI components
- **Recharts** - Composable charting library
- **React Query** - Server state management
- **Axios** - HTTP client for API communication

## Architecture Evolution

TradeSignal is evolving to a **multi-language backend architecture** while maintaining the same React frontend. This follows enterprise patterns used by major technology companies.

### Current State (December 2025)

```
┌─────────────────────────┐
│  Frontend               │
│  React 18 + TypeScript  │
└──────────┬──────────────┘
           │
           ▼
┌──────────────────────────┐
│  Python Backend          │
│  (FastAPI)               │
│  - AI/ML (LUNA Engine)   │
│  - Data pipelines        │
│  - All current features  │
│  Status: MAINTENANCE     │
└──────────────────────────┘
```

### Future State (In Progress)

```
┌─────────────────────────┐
│  Frontend               │
│  React 18 + TypeScript  │
│  (No changes)           │
└──────────┬──────────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
┌────────────┐ ┌────────────────┐
│ TypeScript │ │ Python Backend │
│ Backend    │ │ (FastAPI)      │
│ (Next.js)  │ │                │
│            │ │ - AI/ML only   │
│ NEW        │ │ - Data only    │
│ features   │ │ - Frozen       │
│            │ │                │
│ Status:    │ │ Status:        │
│ ACTIVE     │ │ MAINTENANCE    │
└────────────┘ └────────────────┘
```

**Key Points**:
- **Frontend unchanged** - Same React 18 + TypeScript + Vite stack
- **Python backend frozen** - Maintenance-only, no new features
- **TypeScript backend added** - All NEW features built with Next.js API routes
- **Communication** - REST APIs between services + shared PostgreSQL database

**Rationale**: Optimized for AI-driven development team (Claude Code, Cursor, Gemini, Kilo Code). TypeScript provides compile-time safety, better AI code generation, and faster iteration cycles.

See **[../legacysystem.md](../legacysystem.md)** for detailed architecture documentation.

## Recent Updates (December 2025)

### Dark Theme Consistency Fixes

Fixed visual inconsistencies to match Landing page dark theme aesthetic:

- ✅ **Dashboard page** - Fixed font weights and colors ([Dashboard.tsx:151-241](src/pages/Dashboard.tsx#L151-L241))
  - Changed heading from "Dashboard" to "Overview" with `text-white`
  - Updated stat card labels from `text-gray-600` to `text-gray-400`
  - Changed stat numbers from `text-gray-900` to `text-white`
  - Updated colored numbers to lighter shades (`text-green-400`, `text-red-400`)
  - Changed icon backgrounds from light (`bg-blue-100`) to dark with opacity (`bg-blue-500/20`) with borders

- ✅ **ProtectedRoute dialogs** - All 4 dialog states converted to dark theme ([ProtectedRoute.tsx](src/components/ProtectedRoute.tsx))
  - Loading state: Dark gradient background with purple spinner
  - Premium upgrade dialog: Dark glass-morphism with purple accents
  - Tier restriction dialog: Dark theme with upgrade CTAs
  - Unauthenticated redirect: Consistent dark styling

### Navigation Updates

- ✅ **Removed Chart Patterns** - Link removed from navigation ([DashboardNavbar.tsx:125-132](src/components/layout/DashboardNavbar.tsx#L125-L132))
  - Feature deprecated during LUNA Engine migration
  - Signals dropdown now contains: AI Insights, Alerts

- ✅ **Added Release Notes page** - New page with version history ([ReleaseNotesPage.tsx](src/pages/ReleaseNotesPage.tsx))
  - Detailed changelog for v2.1.0, v2.0.0, v1.5.0, v1.0.0
  - Documents LUNA Engine introduction, Forensic Reports, production fixes
  - Linked from Terms of Service page
  - Route added: `/release-notes`

## Project Structure

```
frontend/
├── src/
│   ├── api/                    # API client functions
│   │   ├── client.ts          # Axios instance with interceptors
│   │   ├── auth.ts            # Authentication API
│   │   ├── billing.ts         # Stripe billing API
│   │   ├── companies.ts       # Companies API
│   │   ├── research.ts        # Research API (PRO features)
│   │   ├── congressionalTrades.ts
│   │   ├── fed.ts
│   │   ├── jobs.ts
│   │   ├── news.ts
│   │   ├── tickets.ts
│   │   └── admin.ts
│   ├── components/             # Reusable components
│   │   ├── common/            # Shared components
│   │   │   ├── CompanyAutocomplete.tsx
│   │   │   ├── CustomAlert.tsx
│   │   │   └── CustomConfirm.tsx
│   │   ├── congressional/     # Congressional trades components
│   │   ├── layout/            # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── TopBar.tsx
│   │   │   ├── DashboardNavbar.tsx
│   │   │   └── Layout.tsx
│   │   ├── research/          # Research badge components (PRO)
│   │   │   ├── IVTBadge.tsx   # Intrinsic Value vs Price
│   │   │   ├── TSScoreBadge.tsx # TradeSignal Score (1-5)
│   │   │   └── RiskLevelBadge.tsx # Risk assessment
│   │   ├── CompanyLogo.tsx
│   │   ├── CookieConsent.tsx
│   │   ├── FirstTimeDisclaimerModal.tsx
│   │   ├── Paywall.tsx
│   │   ├── UpgradeCTA.tsx
│   │   ├── TierComparisonTable.tsx
│   │   ├── ProtectedRoute.tsx
│   │   ├── TierRestrictionBanner.tsx
│   │   └── UsageStats.tsx
│   ├── contexts/               # React contexts
│   │   ├── AuthContext.tsx    # Authentication state
│   │   └── NotificationContext.tsx
│   ├── hooks/                  # Custom React hooks
│   │   ├── useCustomAlert.ts
│   │   ├── useCustomConfirm.ts
│   │   └── useFeatureAccess.ts # Tier-based feature gating
│   ├── pages/                  # Page components (20+)
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── ForgotPasswordPage.tsx
│   │   ├── ResetPasswordPage.tsx
│   │   ├── LandingPage.tsx
│   │   ├── DashboardNew.tsx
│   │   ├── TradesPage.tsx
│   │   ├── CongressionalTradesPage.tsx
│   │   ├── CompanyPage.tsx     # With research badges
│   │   ├── InsiderPage.tsx
│   │   ├── MarketOverviewPage.tsx
│   │   ├── NewsPage.tsx
│   │   ├── FedCalendarPage.tsx
│   │   ├── PatternsPage.tsx
│   │   ├── AIInsightsPage.tsx
│   │   ├── AlertsPage.tsx
│   │   ├── LessonsPage.tsx
│   │   ├── StrategiesPage.tsx
│   │   ├── PricingPage.tsx
│   │   ├── ProfilePage.tsx
│   │   ├── SupportPage.tsx
│   │   ├── AdminDashboardPage.tsx
│   │   ├── OrderHistoryPage.tsx
│   │   ├── BillingSuccessPage.tsx
│   │   ├── BillingCancelPage.tsx
│   │   ├── CareersPage.tsx
│   │   ├── ContactPage.tsx
│   │   ├── BlogPage.tsx
│   │   ├── FAQPage.tsx
│   │   ├── AboutPage.tsx
│   │   ├── TermsOfServicePage.tsx
│   │   ├── PrivacyPolicyPage.tsx
│   │   └── NotFound.tsx
│   ├── types/                  # TypeScript type definitions
│   │   └── index.ts
│   ├── App.tsx                 # Root component with routing
│   ├── main.tsx               # Application entry point
│   └── index.css              # Global styles
├── public/                     # Static assets
├── index.html                  # HTML template
├── package.json               # Dependencies and scripts
├── tsconfig.json              # TypeScript configuration
├── vite.config.ts             # Vite configuration
└── tailwind.config.js         # Tailwind configuration
```

## Key Features

### Authentication Flow
- **Login/Register** - JWT-based authentication
- **Password Reset** - Email-based password recovery
- **Protected Routes** - Route guards with role-based access
- **Session Management** - Auto-refresh tokens, persistent sessions
- **User Profile** - Profile editing and account management

### Dashboard
- Recent insider trades overview
- Congressional trades summary
- Market indices and sector performance
- Quick stats and trending companies
- Real-time data updates

### Trades Pages
- **Insider Trades** - Filterable table with search
- **Congressional Trades** - Political stock transactions
- Advanced filters (date range, transaction type, amount)
- Export functionality
- Detailed trade modals

### Company & Insider Pages
- Company profiles with key metrics
- **Research Badges (PRO)** - IVT, TS Score, Risk Level
- Insider trading history
- Stock price charts
- News and filings
- Related trades and insiders

### Research Components (PRO Features)
- **IVTBadge** - Shows intrinsic value vs current price (undervalued/overvalued)
- **TSScoreBadge** - 1-5 star TradeSignal rating with visual display
- **RiskLevelBadge** - 5-tier risk assessment with descriptions

### Admin Dashboard
- User management (view, edit, delete users)
- System statistics
- Subscription management
- Support ticket handling
- Analytics and metrics

### Billing & Subscriptions
- Stripe checkout integration
- 4-tier subscription system (Free, Plus, Pro, Enterprise)
- Payment history
- Subscription management (upgrade, cancel)
- Feature access control with UpgradeCTA components

### Additional Pages
- **News** - Financial news aggregation
- **Fed Calendar** - Economic events and FOMC meetings
- **Patterns** - Trading pattern analysis
- **AI Insights** - AI-powered analysis (PRO)
- **Lessons** - Educational content for trading
- **Strategies** - Trading strategy guides
- **Support** - Help desk and ticket system
- **FAQ** - Frequently asked questions
- **Blog** - Company blog
- **Contact** - Contact form
- **Careers** - Job listings and applications

## Routing

### Public Routes (no auth required)
- `/` - Landing page
- `/about` - About page
- `/pricing` - Pricing tiers
- `/terms` - Terms of service
- `/privacy` - Privacy policy
- `/faq` - FAQ
- `/contact` - Contact form
- `/careers` - Job listings
- `/blog` - Blog

### Authentication Routes (full-screen, no layout)
- `/login` - Login page
- `/register` - Registration page
- `/forgot-password` - Password reset request
- `/reset-password/:token` - Password reset confirmation

### Protected Routes (auth required)
- `/dashboard` - Dashboard
- `/trades` - Insider trades
- `/congressional-trades` - Congressional trades
- `/market-overview` - Market data
- `/companies/:ticker` - Company details (with research badges)
- `/insiders/:id` - Insider profile
- `/news` - News feed
- `/fed-calendar` - Fed calendar
- `/patterns` - Pattern analysis
- `/ai-insights` - AI insights (PRO)
- `/alerts` - Alerts management
- `/lessons` - Educational content
- `/strategies` - Trading strategies
- `/profile` - User profile
- `/support` - Support center
- `/orders` - Order history
- `/billing/success` - Billing success
- `/billing/cancel` - Billing cancel

### Admin Routes (superuser only)
- `/admin` - Admin dashboard

## State Management

### AuthContext
Manages authentication state globally:
- Current user data with subscription tier
- Login/logout functions
- Token management
- Role-based access control

### NotificationContext
Manages toast notifications:
- Success/error/info/warning messages
- Auto-dismiss timers
- Queue management

## API Integration

### API Client (`src/api/client.ts`)
Centralized Axios instance with:
- Base URL configuration
- Request interceptors (add auth token)
- Response interceptors (handle errors, refresh tokens)
- Error handling and retry logic

### Research API (`src/api/research.ts`)
PRO tier research endpoints:
```typescript
export const getIVTData = async (ticker: string): Promise<IVTData>
export const getTSScore = async (ticker: string): Promise<TSScoreData>
export const getRiskLevel = async (ticker: string): Promise<RiskLevelData>
export const getThesis = async (ticker: string): Promise<ThesisData>
export const getResearchSummary = async (ticker: string): Promise<ResearchSummary>
```

## Environment Variables

Create a `.env` file in the frontend directory:

```env
# Required
VITE_API_URL=http://localhost:8000

# Stripe (for billing)
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...

# Optional
VITE_ENABLE_ANALYTICS=false
```

## Development

### Setup
```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
```

### Run Development Server
```bash
npm run dev
```

Access the app at http://localhost:3000

### Build for Production
```bash
npm run build
```

Output will be in the `dist/` directory.

### Preview Production Build
```bash
npm run preview
```

### Linting
```bash
npm run lint
```

### Type Checking
```bash
npm run type-check
```

## Component Patterns

### Protected Routes
```typescript
<Route path="/admin" element={
  <ProtectedRoute requireSuperuser>
    <AdminDashboard />
  </ProtectedRoute>
} />
```

### Tier-Gated Features
```typescript
import { useFeatureAccess } from '../hooks/useFeatureAccess';

const { hasAccess, tier } = useFeatureAccess();

if (!hasAccess('research')) {
  return <UpgradeCTA feature="Research Badges" requiredTier="PRO" />;
}
```

### Research Badges Usage
```typescript
import { IVTBadge, TSScoreBadge, RiskLevelBadge } from '../components/research';

<IVTBadge ticker={ticker} />
<TSScoreBadge ticker={ticker} />
<RiskLevelBadge ticker={ticker} />
```

### API Calls with Error Handling
```typescript
try {
  const trades = await getTrades({ limit: 50 });
  setTrades(trades);
} catch (error) {
  console.error('Failed to fetch trades:', error);
  showNotification('error', 'Failed to load trades');
}
```

## Styling

### Tailwind CSS
Utility-first approach with custom configuration:
```typescript
<div className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow">
  <h2 className="text-2xl font-bold text-gray-900">Title</h2>
  <p className="text-gray-600 mt-2">Description</p>
</div>
```

### Custom Classes
Defined in `index.css` for reusable styles:
```css
.btn-primary {
  @apply bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700;
}
```

## Performance Optimizations

### Code Splitting
Lazy-loaded routes with React.lazy():
```typescript
const Dashboard = lazy(() => import('./pages/DashboardNew'));
```

### Memoization
Use `useMemo` and `useCallback` for expensive computations:
```typescript
const filteredTrades = useMemo(() =>
  trades.filter(t => t.amount > 100000),
  [trades]
);
```

### React Query
Server state caching and automatic refetching:
```typescript
const { data, isLoading } = useQuery(['research', ticker], () => getResearchSummary(ticker));
```

## Testing

### Unit Tests
```bash
npm test
```

### E2E Tests (if configured)
```bash
npm run test:e2e
```

## Deployment

### Build
```bash
npm run build
```

### Docker
```bash
# Build image
docker build -t tradesignal-frontend .

# Run container
docker run -p 3000:80 tradesignal-frontend
```

### Static Hosting
Deploy the `dist/` folder to:
- Vercel
- Netlify
- AWS S3 + CloudFront
- Nginx

### Environment-Specific Builds
```bash
# Production
VITE_API_URL=https://api.tradesignal.com npm run build

# Staging
VITE_API_URL=https://api-staging.tradesignal.com npm run build
```

## Troubleshooting

### CORS Issues
Ensure backend CORS settings include your frontend URL:
```python
CORS_ORIGINS = "http://localhost:3000,https://tradesignal.com"
```

### Authentication Not Persisting
Check if `localStorage` is available and not blocked.

### API Calls Failing
1. Check `VITE_API_URL` in `.env`
2. Verify backend is running
3. Check browser console for errors
4. Inspect network tab for request details

### Build Errors
```bash
# Clear cache and rebuild
rm -rf node_modules dist .vite
npm install
npm run build
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Accessibility

- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Screen reader friendly
- Color contrast compliance (WCAG AA)

## License

Proprietary - All rights reserved

## Support

For issues and questions:
- GitHub Issues: Create an issue
- Email: dev@tradesignal.com
- Docs: [Main README](../README.md)
