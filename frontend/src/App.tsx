import { useState, lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import { NotificationProvider } from './contexts/NotificationContext';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { CookieConsent } from './components/CookieConsent';
import { FirstTimeDisclaimerModal } from './components/FirstTimeDisclaimerModal';
import PublicLayout from './components/layout/PublicLayout';
import NotFoundPublic from './pages/public/NotFoundPublic';

// Lazy load pages for code splitting (Phase 4.3)
const Dashboard = lazy(() => import('./pages/DashboardNew'));
const TradesPage = lazy(() => import('./pages/TradesPage'));
const CongressionalTradesPage = lazy(() => import('./pages/CongressionalTradesPage'));
const MarketOverviewPage = lazy(() => import('./pages/MarketOverviewPage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));
const CompanyPage = lazy(() => import('./pages/CompanyPage'));
const InsiderPage = lazy(() => import('./pages/InsiderPage'));
const NewsPage = lazy(() => import('./pages/NewsPage'));
const LessonsPage = lazy(() => import('./pages/LessonsPage'));
const StrategiesPage = lazy(() => import('./pages/StrategiesPage'));
const FedCalendarPage = lazy(() => import('./pages/FedCalendarPage'));
const OrderHistoryPage = lazy(() => import('./pages/OrderHistoryPage'));
const FAQPage = lazy(() => import('./pages/FAQPage'));
const PublicContactPage = lazy(() => import('./pages/PublicContactPage'));
const CareersPage = lazy(() => import('./pages/CareersPage'));
const TermsOfServicePage = lazy(() => import('./pages/TermsOfServicePage'));
const PrivacyPolicyPage = lazy(() => import('./pages/PrivacyPolicyPage'));
const PricingPage = lazy(() => import('./pages/PricingPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const ForgotPasswordPage = lazy(() => import('./pages/ForgotPasswordPage'));
const ResetPasswordPage = lazy(() => import('./pages/ResetPasswordPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const SupportPage = lazy(() => import('./pages/SupportPage'));
const BillingSuccessPage = lazy(() => import('./pages/BillingSuccessPage'));
const BillingCancelPage = lazy(() => import('./pages/BillingCancelPage'));
const LandingPage = lazy(() => import('./pages/LandingPage'));
const BlogPage = lazy(() => import('./pages/BlogPage')); // Added BlogPage
const AdminDashboard = lazy(() => import('./pages/AdminDashboardPage'));
const ContactManagementPage = lazy(() => import('./pages/admin/ContactManagementPage'));
const SupportTicketsPage = lazy(() => import('./pages/admin/SupportTicketsPage')); // New Import
const AIInsightsPage = lazy(() => import('./pages/AIInsightsPage'));
const PatternsPage = lazy(() => import('./pages/PatternsPage'));
const AlertsPage = lazy(() => import('./pages/AlertsPage'));

// Loading skeleton component
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center bg-[#0a0a0a]">
    <div className="space-y-4 w-full max-w-4xl px-4">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="animate-pulse flex space-x-4 p-4 bg-white/5 border border-white/5 rounded-lg">
          <div className="h-4 bg-white/10 rounded w-1/4"></div>
          <div className="h-4 bg-white/10 rounded w-1/2"></div>
          <div className="h-4 bg-white/10 rounded w-1/4"></div>
        </div>
      ))}
    </div>
  </div>
);

function AppContent() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        {/* Auth routes - NO LAYOUT (full screen) */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password/:token" element={<ResetPasswordPage />} />
        
        {/* Public Routes - Wrapped in PublicLayout (Floating Navbar) */}
        <Route element={<PublicLayout />}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/blog" element={<BlogPage />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/privacy" element={<PrivacyPolicyPage />} />
          <Route path="/terms" element={<TermsOfServicePage />} />
          <Route path="/contact" element={<PublicContactPage />} />
          <Route path="/faq" element={<FAQPage />} />
          <Route path="/careers" element={<CareersPage />} />
        </Route>

        {/* All other routes - WITH LAYOUT (Dashboard etc.) */}
        <Route path="/*" element={
          <Layout>
            <Routes>
              {/* Dashboard routes */}
              <Route path="/dashboard" element={<ProtectedRoute redirectAdmin><Dashboard /></ProtectedRoute>} />
              <Route path="/admin" element={<ProtectedRoute requireSuperuser><AdminDashboard /></ProtectedRoute>} />
              <Route path="/admin/contacts" element={<ProtectedRoute requireSuperuser><ContactManagementPage /></ProtectedRoute>} />
              <Route path="/admin/tickets" element={<ProtectedRoute requireSuperuser><SupportTicketsPage /></ProtectedRoute>} /> {/* New Route */}
              <Route path="/trades" element={<ProtectedRoute redirectAdmin><TradesPage /></ProtectedRoute>} />
              <Route path="/congressional-trades" element={<ProtectedRoute redirectAdmin><CongressionalTradesPage /></ProtectedRoute>} />
              <Route path="/market-overview" element={<ProtectedRoute redirectAdmin><MarketOverviewPage /></ProtectedRoute>} />
              <Route path="/news" element={<ProtectedRoute redirectAdmin><NewsPage /></ProtectedRoute>} />
              <Route path="/fed-calendar" element={<ProtectedRoute redirectAdmin><FedCalendarPage /></ProtectedRoute>} />
              <Route path="/lessons" element={<ProtectedRoute redirectAdmin><LessonsPage /></ProtectedRoute>} />
              <Route path="/strategies" element={<ProtectedRoute redirectAdmin><StrategiesPage /></ProtectedRoute>} />
              <Route path="/patterns" element={<ProtectedRoute redirectAdmin requireTier="pro"><PatternsPage /></ProtectedRoute>} />
              <Route path="/ai-insights" element={<ProtectedRoute redirectAdmin requireTier="pro"><AIInsightsPage /></ProtectedRoute>} />
              <Route path="/alerts" element={<ProtectedRoute redirectAdmin><AlertsPage /></ProtectedRoute>} />
              <Route path="/companies/:ticker" element={<ProtectedRoute redirectAdmin><CompanyPage /></ProtectedRoute>} />
              <Route path="/insiders/:id" element={<ProtectedRoute redirectAdmin><InsiderPage /></ProtectedRoute>} />
              <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
              <Route path="/support" element={<ProtectedRoute><SupportPage /></ProtectedRoute>} />
              <Route path="/orders" element={<ProtectedRoute redirectAdmin><OrderHistoryPage /></ProtectedRoute>} />
              <Route path="/billing/success" element={<ProtectedRoute><BillingSuccessPage /></ProtectedRoute>} />
              <Route path="/billing/cancel" element={<ProtectedRoute><BillingCancelPage /></ProtectedRoute>} />
              <Route path="/faq" element={<FAQPage />} />
              <Route path="/careers" element={<CareersPage />} />

              {/* Redirect 404s to global 404 page */}
              <Route path="*" element={<Navigate to="/404" replace />} />
            </Routes>
          </Layout>
        } />
        
        {/* Global 404 Route */}
        <Route path="/404" element={<NotFoundPublic />} />
      </Routes>
    </Suspense>
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
    <AuthProvider>
      <NotificationProvider>
        <AppContent />
        <CookieConsent />
      </NotificationProvider>
    </AuthProvider>
  );
}

export default App;
