# TradeSignal Frontend

React 18 + TypeScript frontend dashboard for the TradeSignal insider trading intelligence platform.

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/                       # API client & HTTP requests
│   │   ├── client.ts              # Axios instance configuration
│   │   ├── companies.ts           # Company API calls
│   │   ├── insiders.ts            # Insider API calls
│   │   └── trades.ts              # Trade API calls
│   │
│   ├── components/                # Reusable UI components
│   │   ├── layout/
│   │   │   ├── Header.tsx         # App header with navigation
│   │   │   ├── Sidebar.tsx        # Filter sidebar
│   │   │   └── Layout.tsx         # Main layout wrapper
│   │   │
│   │   ├── trades/
│   │   │   ├── TradeList.tsx      # Trade table
│   │   │   ├── TradeCard.tsx      # Individual trade card
│   │   │   ├── TradeFilters.tsx   # Filter controls
│   │   │   └── TradeChart.tsx     # Trade visualizations
│   │   │
│   │   ├── companies/
│   │   │   ├── CompanyCard.tsx    # Company overview card
│   │   │   └── CompanyList.tsx    # Company listing
│   │   │
│   │   ├── insiders/
│   │   │   ├── InsiderCard.tsx    # Insider profile card
│   │   │   └── InsiderList.tsx    # Insider listing
│   │   │
│   │   └── common/
│   │       ├── Button.tsx         # Button component
│   │       ├── Card.tsx           # Card wrapper
│   │       ├── LoadingSpinner.tsx # Loading indicator
│   │       └── Pagination.tsx     # Pagination controls
│   │
│   ├── pages/                     # Page components
│   │   ├── Dashboard.tsx          # Home dashboard
│   │   ├── TradesPage.tsx         # All trades view
│   │   ├── CompanyPage.tsx        # Company detail view
│   │   ├── InsiderPage.tsx        # Insider detail view
│   │   └── NotFound.tsx           # 404 page
│   │
│   ├── hooks/                     # Custom React hooks
│   │   ├── useTrades.ts           # React Query hook for trades
│   │   ├── useCompanies.ts        # React Query hook for companies
│   │   └── useInsiders.ts         # React Query hook for insiders
│   │
│   ├── store/                     # State management (Zustand)
│   │   ├── useFilterStore.ts      # Filter state
│   │   └── useThemeStore.ts       # Theme state (dark mode)
│   │
│   ├── types/                     # TypeScript type definitions
│   │   ├── company.ts             # Company types
│   │   ├── insider.ts             # Insider types
│   │   ├── trade.ts               # Trade types
│   │   └── api.ts                 # API response types
│   │
│   ├── utils/                     # Utility functions
│   │   ├── formatters.ts          # Number/date formatters
│   │   ├── validators.ts          # Input validation
│   │   └── constants.ts           # App constants
│   │
│   ├── App.tsx                    # Root app component
│   ├── main.tsx                   # App entry point
│   └── index.css                  # Global styles + Tailwind
│
├── public/                        # Static assets
│   ├── favicon.ico
│   └── logo.svg
│
├── package.json                   # Dependencies & scripts
├── tsconfig.json                  # TypeScript configuration
├── vite.config.ts                 # Vite bundler config
├── tailwind.config.js             # Tailwind CSS config
├── postcss.config.js              # PostCSS config
├── Dockerfile                     # Docker image definition
└── README.md                      # This file
```

**Note:** This is the planned structure for Phase 3. Currently, only basic files exist (`App.tsx`, `main.tsx`).

---

## 🛠️ Tech Stack

- **Framework**: React 18
- **Language**: TypeScript 5
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS 3
- **State Management**: Zustand (global), React Query (server state)
- **HTTP Client**: Axios
- **Routing**: React Router v6
- **Charts**: Recharts
- **Icons**: Lucide React
- **Date Handling**: date-fns
- **Notifications**: react-hot-toast

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running (see [backend/README.md](../backend/README.md))

### Installation

**1. Navigate to frontend directory**
```bash
cd frontend
```

**2. Install dependencies**
```bash
npm install
```

**3. Set up environment variables**

Create a `.env` file in the frontend directory:
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

**4. Start development server**
```bash
npm run dev
```

Frontend will run at: http://localhost:3000

---

## 📜 Available Scripts

### Development
```bash
npm run dev          # Start Vite dev server with hot reload
```

### Production Build
```bash
npm run build        # Build for production (outputs to /dist)
npm run preview      # Preview production build locally
```

### Code Quality
```bash
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript type checking (if configured)
```

---

## 🎨 Styling with Tailwind CSS

This project uses Tailwind CSS for styling. All utility classes are available:

```tsx
// Example component
export function Button() {
  return (
    <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg">
      Click Me
    </button>
  );
}
```

**Tailwind Configuration** (`tailwind.config.js`):
- Custom colors (brand colors)
- Extended spacing
- Custom fonts (optional)
- Dark mode support

---

## 🔌 API Integration

### API Client Setup

The API client is configured in `src/api/client.ts`:

```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (for auth tokens, etc.)
apiClient.interceptors.request.use((config) => {
  // Add auth token if available
  return config;
});

// Response interceptor (for error handling)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle errors globally
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Using React Query

React Query manages server state and caching:

```typescript
// src/hooks/useTrades.ts
import { useQuery } from '@tanstack/react-query';
import { fetchTrades } from '@/api/trades';

export function useTrades(filters?: TradeFilters) {
  return useQuery({
    queryKey: ['trades', filters],
    queryFn: () => fetchTrades(filters),
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
  });
}

// Usage in component
function TradesPage() {
  const { data, isLoading, error } = useTrades();

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return <TradeList trades={data.items} />;
}
```

---

## 📊 State Management

### Global State (Zustand)

```typescript
// src/store/useFilterStore.ts
import { create } from 'zustand';

interface FilterState {
  ticker: string | null;
  startDate: Date | null;
  endDate: Date | null;
  transactionType: 'BUY' | 'SELL' | null;
  setTicker: (ticker: string | null) => void;
  setDateRange: (start: Date | null, end: Date | null) => void;
  setTransactionType: (type: 'BUY' | 'SELL' | null) => void;
  reset: () => void;
}

export const useFilterStore = create<FilterState>((set) => ({
  ticker: null,
  startDate: null,
  endDate: null,
  transactionType: null,
  setTicker: (ticker) => set({ ticker }),
  setDateRange: (start, end) => set({ startDate: start, endDate: end }),
  setTransactionType: (type) => set({ transactionType: type }),
  reset: () => set({
    ticker: null,
    startDate: null,
    endDate: null,
    transactionType: null
  }),
}));
```

### Server State (React Query)

React Query handles all server data (trades, companies, insiders) with automatic caching, refetching, and background updates.

---

## 🧩 Key Components (Planned)

### Dashboard
- Overview statistics (total trades, companies, insiders)
- Recent trades list
- Charts (trade volume over time, buy vs sell)
- Top insiders by activity

### Trade List
- Searchable/filterable table
- Pagination
- Sort by date, value, company
- Color coding (green = buy, red = sell)
- Export to CSV (optional)

### Company Page
- Company details (ticker, sector, market cap)
- All insider trades for company
- Insider list
- Trade chart for company

### Insider Page
- Insider details (name, title, relationships)
- All trades by insider
- Win rate / performance metrics
- Timeline of activity

---

## 🎨 Theme & Design

### Color Scheme
- Primary: Blue (#3B82F6)
- Success (Buy): Green (#10B981)
- Danger (Sell): Red (#EF4444)
- Background: Gray (#F9FAFB)
- Dark mode: Coming soon

### Typography
- Font: Inter or system font stack
- Headings: Bold, larger sizes
- Body: Regular, 16px base

### Components
- Cards with subtle shadows
- Rounded corners (8px)
- Hover effects on interactive elements
- Loading skeletons for better UX

---

## 📱 Responsive Design

The dashboard is fully responsive:
- **Desktop** (1024px+): Full layout with sidebar
- **Tablet** (768px-1023px): Collapsible sidebar
- **Mobile** (< 768px): Bottom navigation, stacked layout

Breakpoints (Tailwind):
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px
- `2xl`: 1536px

---

## 🔧 Development Tips

### Hot Module Replacement (HMR)

Vite provides instant HMR. Changes appear immediately without full page reload.

### TypeScript

All components should be typed:
```typescript
interface TradeListProps {
  trades: Trade[];
  onTradeClick?: (trade: Trade) => void;
}

export function TradeList({ trades, onTradeClick }: TradeListProps) {
  // ...
}
```

### Component Organization

- Keep components small and focused
- Extract reusable logic into custom hooks
- Use TypeScript for type safety
- Follow naming conventions:
  - Components: PascalCase (`TradeCard.tsx`)
  - Hooks: camelCase with `use` prefix (`useTrades.ts`)
  - Utils: camelCase (`formatCurrency.ts`)

---

## 🐛 Troubleshooting

### Issue: npm install fails

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Issue: Port 3000 already in use

**Solution:**

Mac/Linux:
```bash
lsof -ti:3000 | xargs kill -9
```

Windows:
```bash
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

Or use different port:
```bash
npm run dev -- --port 3001
```

### Issue: API calls failing (CORS error)

**Cause:** Backend not allowing frontend origin

**Solution:**
1. Ensure backend is running
2. Check CORS configuration in `backend/app/main.py`
3. Verify `VITE_API_URL` in `.env`

### Issue: Build fails with TypeScript errors

**Solution:**
```bash
# Check TypeScript errors
npx tsc --noEmit

# Fix errors, then rebuild
npm run build
```

---

## 📦 Dependencies

### Core Dependencies
- `react` - UI library
- `react-dom` - React DOM renderer
- `react-router-dom` - Client-side routing
- `typescript` - Type safety
- `vite` - Build tool

### UI Libraries
- `tailwindcss` - Utility-first CSS
- `lucide-react` - Icon library
- `recharts` - Charting library
- `react-hot-toast` - Toast notifications

### State & Data
- `@tanstack/react-query` - Server state management
- `zustand` - Global state management
- `axios` - HTTP client
- `date-fns` - Date utilities

---

## 🚀 Production Deployment

### Build for Production
```bash
npm run build
```

Output will be in `/dist` directory.

### Deploy to Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Or connect GitHub repo for automatic deployments
```

### Deploy to Netlify

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
netlify deploy --prod
```

### Environment Variables (Production)

Set these in your hosting platform:
```
VITE_API_URL=https://your-backend-api.com
VITE_WS_URL=wss://your-backend-api.com/ws
```

---

## 🔒 Security

- Environment variables prefixed with `VITE_` (public)
- Sensitive data (API keys) should be in backend only
- HTTPS in production
- Content Security Policy (CSP) headers
- XSS protection via React's built-in escaping

---

## 📊 Performance Optimization

### Code Splitting
Vite automatically code-splits by route:
```typescript
// Lazy load pages
const Dashboard = lazy(() => import('./pages/Dashboard'));
const TradesPage = lazy(() => import('./pages/TradesPage'));
```

### Image Optimization
- Use WebP format when possible
- Lazy load images below fold
- Use proper image sizes (don't load 4K images for thumbnails)

### React Query Caching
- Configure appropriate `staleTime` and `cacheTime`
- Use query key invalidation for real-time updates
- Enable background refetching for live data

---

## 🧪 Testing (Planned)

### Unit Tests (Vitest)
```bash
npm run test
```

### E2E Tests (Playwright)
```bash
npm run test:e2e
```

---

## 📝 Notes

- This frontend is **Phase 3** of the project (not yet implemented)
- Current focus is on backend functionality (Phases 1 & 2)
- Once backend is complete, frontend development will begin
- Design mockups and wireframes coming soon

---

## 📞 Support

For issues or questions:
- Ensure backend API is running and accessible
- Check browser console for errors
- Review React Query DevTools (if enabled)
- Refer to main project [README](../README.md)

---

**Built with React, TypeScript, and Tailwind CSS | Part of TradeSignal Platform**
