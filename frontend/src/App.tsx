import { useState, lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import { NotificationProvider } from './contexts/NotificationContext';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { CookieConsent } from './components/CookieConsent';
import { FirstTimeDisclaimerModal } from './components/FirstTimeDisclaimerModal';

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
const ContactPage = lazy(() => import('./pages/ContactPage'));
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
const AdminDashboard = lazy(() => import('./pages/AdminDashboardPage'));
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

function AppContent() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        {/* Auth routes - NO LAYOUT (full screen) */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password/:token" element={<ResetPasswordPage />} />
        
        {/* Landing Page - Public - NO LAYOUT */}
        <Route path="/" element={<LandingPage />} />

        {/* All other routes - WITH LAYOUT */}
        <Route path="/*" element={
          <Layout>
            <Routes>
              {/* Public routes */}
              <Route path="/about" element={<AboutPage />} />
              <Route path="/pricing" element={<PricingPage />} />
              <Route path="/terms" element={<TermsOfServicePage />} />
              <Route path="/privacy" element={<PrivacyPolicyPage />} />
              <Route path="/faq" element={<FAQPage />} />
              <Route path="/contact" element={<ContactPage />} />
              <Route path="/careers" element={<CareersPage />} />

              {/* Admin routes - redirect non-admins */}
              <Route path="/admin" element={<ProtectedRoute requireSuperuser><AdminDashboard /></ProtectedRoute>} />
              
              {/* User routes - redirect admins to /admin */}
              <Route path="/dashboard" element={<ProtectedRoute redirectAdmin><Dashboard /></ProtectedRoute>} />
              <Route path="/trades" element={<ProtectedRoute redirectAdmin><TradesPage /></ProtectedRoute>} />
              <Route path="/congressional-trades" element={<ProtectedRoute redirectAdmin><CongressionalTradesPage /></ProtectedRoute>} />
              <Route path="/market-overview" element={<ProtectedRoute redirectAdmin><MarketOverviewPage /></ProtectedRoute>} />
              <Route path="/news" element={<ProtectedRoute redirectAdmin><NewsPage /></ProtectedRoute>} />
              <Route path="/fed-calendar" element={<ProtectedRoute redirectAdmin><FedCalendarPage /></ProtectedRoute>} />
              <Route path="/lessons" element={<ProtectedRoute redirectAdmin><LessonsPage /></ProtectedRoute>} />
              <Route path="/strategies" element={<ProtectedRoute redirectAdmin><StrategiesPage /></ProtectedRoute>} />
              <Route path="/companies/:ticker" element={<ProtectedRoute redirectAdmin><CompanyPage /></ProtectedRoute>} />
              <Route path="/insiders/:id" element={<ProtectedRoute redirectAdmin><InsiderPage /></ProtectedRoute>} />
              <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
              <Route path="/support" element={<ProtectedRoute><SupportPage /></ProtectedRoute>} />
              <Route path="/orders" element={<ProtectedRoute redirectAdmin><OrderHistoryPage /></ProtectedRoute>} />
              <Route path="/billing/success" element={<ProtectedRoute><BillingSuccessPage /></ProtectedRoute>} />
              <Route path="/billing/cancel" element={<ProtectedRoute><BillingCancelPage /></ProtectedRoute>} />

              {/* 404 */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Layout>
        } />
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
