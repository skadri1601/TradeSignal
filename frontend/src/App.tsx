import { useState, lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import { NotificationProvider } from './contexts/NotificationContext';
import { useRealtimeAlerts } from './hooks/useRealtimeAlerts';
import { CookieConsent } from './components/CookieConsent';
import { FirstTimeDisclaimerModal } from './components/FirstTimeDisclaimerModal';

// Lazy load pages for code splitting (Phase 4.3)
const Dashboard = lazy(() => import('./pages/Dashboard'));
const TradesPage = lazy(() => import('./pages/TradesPage'));
const MarketOverviewPage = lazy(() => import('./pages/MarketOverviewPage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));
const CompanyPage = lazy(() => import('./pages/CompanyPage'));
const InsiderPage = lazy(() => import('./pages/InsiderPage'));
const AlertsPage = lazy(() => import('./pages/AlertsPage'));
const AIInsightsPage = lazy(() => import('./pages/AIInsightsPage'));
const TermsOfServicePage = lazy(() => import('./pages/TermsOfServicePage'));
const PrivacyPolicyPage = lazy(() => import('./pages/PrivacyPolicyPage'));
const PricingPage = lazy(() => import('./pages/PricingPage'));
const NotFound = lazy(() => import('./pages/NotFound'));

// Loading skeleton component
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="space-y-4 w-full max-w-4xl px-4">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="animate-pulse flex space-x-4 p-4 bg-white rounded-lg shadow">
          <div className="h-4 bg-gray-300 rounded w-1/4"></div>
          <div className="h-4 bg-gray-300 rounded w-1/2"></div>
          <div className="h-4 bg-gray-300 rounded w-1/4"></div>
        </div>
      ))}
    </div>
  </div>
);

// WebSocket URL for real-time alerts
const ALERTS_WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/alerts/stream';

function AppContent() {
  // Connect to real-time alerts WebSocket
  useRealtimeAlerts({ url: ALERTS_WS_URL, enabled: true });

  return (
    <Layout>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/trades" element={<TradesPage />} />
          <Route path="/market-overview" element={<MarketOverviewPage />} />
          <Route path="/ai-insights" element={<AIInsightsPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/companies/:ticker" element={<CompanyPage />} />
          <Route path="/insiders/:id" element={<InsiderPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/terms" element={<TermsOfServicePage />} />
          <Route path="/privacy" element={<PrivacyPolicyPage />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </Layout>
  );
}

function App() {
  // Track if user has accepted terms on first visit
  const [hasAcceptedTerms, setHasAcceptedTerms] = useState(
    localStorage.getItem('acceptedTerms') === 'true'
  );

  // Show disclaimer modal on first visit
  if (!hasAcceptedTerms) {
    return (
      <FirstTimeDisclaimerModal
        onAccept={() => {
          localStorage.setItem('acceptedTerms', 'true');
          localStorage.setItem('acceptedTermsDate', new Date().toISOString());
          setHasAcceptedTerms(true);
        }}
      />
    );
  }

  return (
    <NotificationProvider>
      <AppContent />
      <CookieConsent />
    </NotificationProvider>
  );
}

export default App;
