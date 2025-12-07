# TradeSignal Frontend

React-based frontend application for TradeSignal. Provides a modern, responsive user interface for tracking insider trades, congressional stock transactions, and market intelligence.

## Tech Stack

- **React 18** - Modern UI library with concurrent features
- **TypeScript** - Type-safe JavaScript for better DX
- **Vite** - Fast build tool with hot module replacement
- **React Router 6** - Client-side routing with data loading
- **Tailwind CSS** - Utility-first CSS framework
- **Headless UI** - Unstyled, accessible UI components
- **Recharts** - Composable charting library
- **Axios** - HTTP client for API communication

## Project Structure

```
frontend/
├── src/
│   ├── api/                    # API client functions
│   │   ├── client.ts          # Axios instance with interceptors
│   │   ├── auth.ts            # Authentication API
│   │   ├── billing.ts         # Stripe billing API
│   │   ├── companies.ts       # Companies API
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
│   │   │   └── Layout.tsx
│   │   ├── CompanyLogo.tsx
│   │   ├── CookieConsent.tsx
│   │   ├── FirstTimeDisclaimerModal.tsx
│   │   ├── ProtectedRoute.tsx
│   │   ├── TierRestrictionBanner.tsx
│   │   └── UsageStats.tsx
│   ├── contexts/               # React contexts
│   │   ├── AuthContext.tsx    # Authentication state
│   │   └── NotificationContext.tsx
│   ├── hooks/                  # Custom React hooks
│   │   ├── useCustomAlert.ts
│   │   └── useCustomConfirm.ts
│   ├── pages/                  # Page components
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── ForgotPasswordPage.tsx
│   │   ├── ResetPasswordPage.tsx
│   │   ├── DashboardNew.tsx
│   │   ├── TradesPage.tsx
│   │   ├── CongressionalTradesPage.tsx
│   │   ├── CompanyPage.tsx
│   │   ├── InsiderPage.tsx
│   │   ├── NewsPage.tsx
│   │   ├── FedCalendarPage.tsx
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
│   │   ├── FAQPage.tsx
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
- Insider trading history
- Stock price charts
- News and filings
- Related trades and insiders

### Admin Dashboard
- User management (view, edit, delete users)
- System statistics
- Subscription management
- Support ticket handling
- Analytics and metrics

### Billing & Subscriptions
- Stripe checkout integration
- 3-tier subscription system (Free, Pro, Enterprise)
- Payment history
- Subscription management (upgrade, cancel)
- Feature access control

### Additional Pages
- **News** - Financial news aggregation
- **Fed Calendar** - Economic events and FOMC meetings
- **Lessons** - Educational content for trading
- **Strategies** - Trading strategy guides
- **Support** - Help desk and ticket system
- **FAQ** - Frequently asked questions
- **Contact** - Contact form
- **Careers** - Job listings and applications

## Routing

### Public Routes (no auth required)
- `/about` - About page
- `/pricing` - Pricing tiers
- `/terms` - Terms of service
- `/privacy` - Privacy policy
- `/faq` - FAQ
- `/contact` - Contact form
- `/careers` - Job listings

### Authentication Routes (full-screen, no layout)
- `/login` - Login page
- `/register` - Registration page
- `/forgot-password` - Password reset request
- `/reset-password/:token` - Password reset confirmation

### Protected Routes (auth required)
- `/` - Dashboard
- `/trades` - Insider trades
- `/congressional-trades` - Congressional trades
- `/market-overview` - Market data
- `/companies/:ticker` - Company details
- `/insiders/:id` - Insider profile
- `/news` - News feed
- `/fed-calendar` - Fed calendar
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
- Current user data
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

### API Modules
Each API module exports typed functions:
```typescript
// Example: auth.ts
export const login = async (email: string, password: string): Promise<LoginResponse>
export const register = async (data: RegisterRequest): Promise<User>
export const getCurrentUser = async (): Promise<User>
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
nano .env
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

### Authentication Check
```typescript
const { user, isAuthenticated } = useContext(AuthContext);

if (!isAuthenticated) {
  return <Navigate to="/login" />;
}
```

## Styling

### Tailwind CSS
Utility-first approach with custom configuration:
```typescript
// Example component
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

### Image Optimization
- Use appropriate image formats (WebP, AVIF)
- Lazy load images below the fold
- Responsive images with `srcset`

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
# backend/app/config.py
CORS_ORIGINS = "http://localhost:3000,https://tradesignal.com"
```

### Authentication Not Persisting
Check if `localStorage` is available and not blocked:
```typescript
if (typeof window !== 'undefined' && window.localStorage) {
  // Safe to use localStorage
}
```

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

## Contributing

1. Follow React best practices
2. Use TypeScript for all new code
3. Follow the existing component structure
4. Add prop types for all components
5. Write meaningful commit messages
6. Update this README for significant changes

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
