import { useState, lazy, Suspense, useEffect } from 'react';
import { TrendingUp } from 'lucide-react';
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
const FedCalendarPage = lazy(() => import('./pages/FedCalendarPage'));
const LessonsPage = lazy(() => import('./pages/LessonsPage'));
const StrategiesPage = lazy(() => import('./pages/StrategiesPage'));
const OrderHistoryPage = lazy(() => import('./pages/OrderHistoryPage'));
const FAQPage = lazy(() => import('./pages/FAQPage'));
const PublicContactPage = lazy(() => import('./pages/PublicContactPage'));
// PORTFOLIO MODE: Removed business pages (Careers, Pricing)
const TermsOfServicePage = lazy(() => import('./pages/TermsOfServicePage'));
const PrivacyPolicyPage = lazy(() => import('./pages/PrivacyPolicyPage'));
const ReleaseNotesPage = lazy(() => import('./pages/ReleaseNotesPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
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
// const PatternsPage = lazy(() => import('./pages/PatternsPage')); // TODO: Create this page
const AlertsPage = lazy(() => import('./pages/AlertsPage'));
const ResearchDashboard = lazy(() => import('./pages/ResearchDashboard'));
const ForumPage = lazy(() => import('./pages/ForumPage'));
const ForumPostPage = lazy(() => import('./pages/ForumPostPage'));
const ForumCreatePostPage = lazy(() => import('./pages/ForumCreatePostPage'));
const CopyTradingPage = lazy(() => import('./pages/CopyTradingPage'));
const CopyTradingRulesPage = lazy(() => import('./pages/CopyTradingRulesPage'));
const CopyTradingAccountPage = lazy(() => import('./pages/CopyTradingAccountPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));

// Feature Landing Pages
const InsiderTradesFeature = lazy(() => import('./pages/features/InsiderTradesFeature'));
const CongressTradingFeature = lazy(() => import('./pages/features/CongressTradingFeature'));
const AIInsightsFeature = lazy(() => import('./pages/features/AIInsightsFeature'));
const AlertsFeature = lazy(() => import('./pages/features/AlertsFeature'));

// New Public Pages
const DocumentationPage = lazy(() => import('./pages/DocumentationPage'));
const APIDocsPage = lazy(() => import('./pages/APIDocsPage'));
const RoadmapPage = lazy(() => import('./pages/RoadmapPage'));
// PORTFOLIO MODE: Removed SecurityPage and AccessibilityPage (contained false claims like SOC 2 certification)
const PublicNewsPage = lazy(() => import('./pages/public/PublicNewsPage'));
const PublicSupportPage = lazy(() => import('./pages/public/PublicSupportPage'));

const PageLoader = () => {
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-black relative overflow-hidden">
      <style>{`
        @keyframes pl-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes pl-shimmer { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }
        @keyframes pl-blob1 { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(30px,-20px) scale(1.1); } }
        @keyframes pl-blob2 { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(-20px,30px) scale(1.15); } }
        .pl-ring { animation: pl-spin 2.5s linear infinite; }
        .pl-shimmer::after {
          content: '';
          position: absolute;
          inset: 0;
          background: linear-gradient(90deg, transparent, rgba(139,92,246,0.08), rgba(59,130,246,0.08), transparent);
          animation: pl-shimmer 2s ease-in-out infinite;
        }
        .pl-blob1 { animation: pl-blob1 8s ease-in-out infinite; }
        .pl-blob2 { animation: pl-blob2 10s ease-in-out infinite; }
      `}</style>

      <div className="absolute inset-0 pointer-events-none">
        <div className="pl-blob1 absolute top-1/4 left-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl" />
        <div className="pl-blob2 absolute bottom-1/4 right-1/4 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl" />
      </div>

      <div className={`relative flex flex-col items-center transition-all duration-700 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <div className="relative mb-6">
          <div className="absolute -inset-4 rounded-full bg-gradient-to-r from-purple-500/20 via-blue-500/20 to-purple-500/20 blur-xl animate-pulse" />
          <div className="relative">
            <svg className="pl-ring w-20 h-20" viewBox="0 0 80 80" fill="none">
              <defs>
                <linearGradient id="pl-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#a855f7" />
                  <stop offset="50%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#a855f7" />
                </linearGradient>
              </defs>
              <circle cx="40" cy="40" r="36" stroke="url(#pl-grad)" strokeWidth="2.5" strokeLinecap="round" strokeDasharray="160 66" />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center shadow-lg shadow-purple-500/25">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>

        <span className="text-xl font-bold bg-gradient-to-r from-purple-400 via-blue-400 to-purple-400 bg-clip-text text-transparent mb-10">
          TradeSignal
        </span>

        <div className="w-full max-w-md space-y-3 px-4">
          {[0.7, 1, 0.5, 0.85, 0.6].map((w, i) => (
            <div
              key={i}
              className="pl-shimmer relative overflow-hidden rounded-xl border border-white/5 bg-white/[0.03] backdrop-blur-sm p-4"
              style={{ opacity: 1 - i * 0.12 }}
            >
              <div className="flex items-center gap-3">
                <div className="h-3 rounded-full bg-gradient-to-r from-purple-500/15 to-blue-500/15" style={{ width: `${w * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

function AppContent() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        {/* Auth routes - NO LAYOUT (full screen) */}
        <Route path="/login/*" element={<LoginPage />} />
        <Route path="/register/*" element={<RegisterPage />} />
        {/* Public Routes - Wrapped in PublicLayout (Floating Navbar) */}
        <Route element={<PublicLayout />}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/blog" element={<BlogPage />} />
          {/* PORTFOLIO MODE: Redirect pricing to home */}
          <Route path="/pricing" element={<Navigate to="/" replace />} />
          <Route path="/privacy" element={<PrivacyPolicyPage />} />
          <Route path="/terms" element={<TermsOfServicePage />} />
          <Route path="/release-notes" element={<ReleaseNotesPage />} />
          <Route path="/contact" element={<PublicContactPage />} />
          <Route path="/faq" element={<FAQPage />} />
          {/* PORTFOLIO MODE: Redirect removed business pages to home */}
          <Route path="/careers" element={<Navigate to="/" replace />} />
          <Route path="/use-cases" element={<Navigate to="/" replace />} />
          <Route path="/testimonials" element={<Navigate to="/" replace />} />

          {/* Public Pages */}
          <Route path="/docs" element={<DocumentationPage />} />
          <Route path="/api-docs" element={<APIDocsPage />} />
          <Route path="/roadmap" element={<RoadmapPage />} />
          {/* PORTFOLIO MODE: Redirect security/accessibility (contained false claims) */}
          <Route path="/security" element={<Navigate to="/" replace />} />
          <Route path="/accessibility" element={<Navigate to="/" replace />} />
          <Route path="/public/news" element={<PublicNewsPage />} />
          <Route path="/public/support" element={<PublicSupportPage />} />

          {/* Feature Landing Pages */}
          <Route path="/features/insider-trades" element={<InsiderTradesFeature />} />
          <Route path="/features/congress-trading" element={<CongressTradingFeature />} />
          <Route path="/features/ai-insights" element={<AIInsightsFeature />} />
          <Route path="/features/alerts" element={<AlertsFeature />} />
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
              {/* <Route path="/patterns" element={<ProtectedRoute redirectAdmin requireTier="pro"><PatternsPage /></ProtectedRoute>} /> */} {/* TODO: Create PatternsPage */}
              <Route path="/ai-insights" element={<ProtectedRoute redirectAdmin requireTier="pro"><AIInsightsPage /></ProtectedRoute>} />
              <Route path="/research" element={<ProtectedRoute redirectAdmin requireTier="pro"><ResearchDashboard /></ProtectedRoute>} />
              <Route path="/alerts" element={<ProtectedRoute redirectAdmin><AlertsPage /></ProtectedRoute>} />
              <Route path="/forum" element={<ProtectedRoute redirectAdmin><ForumPage /></ProtectedRoute>} />
              <Route path="/forum/post/:postId" element={<ProtectedRoute redirectAdmin><ForumPostPage /></ProtectedRoute>} />
              <Route path="/forum/create" element={<ProtectedRoute redirectAdmin><ForumCreatePostPage /></ProtectedRoute>} />
              <Route path="/copy-trading" element={<ProtectedRoute redirectAdmin requireTier="plus"><CopyTradingPage /></ProtectedRoute>} />
              <Route path="/copy-trading/rules" element={<ProtectedRoute redirectAdmin requireTier="plus"><CopyTradingRulesPage /></ProtectedRoute>} />
              <Route path="/copy-trading/account" element={<ProtectedRoute redirectAdmin requireTier="plus"><CopyTradingAccountPage /></ProtectedRoute>} />
              <Route path="/companies/:ticker" element={<ProtectedRoute redirectAdmin><CompanyPage /></ProtectedRoute>} />
              <Route path="/insiders/:id" element={<ProtectedRoute redirectAdmin><InsiderPage /></ProtectedRoute>} />
              <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
              <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
              <Route path="/support" element={<ProtectedRoute><SupportPage /></ProtectedRoute>} />
              <Route path="/orders" element={<ProtectedRoute redirectAdmin><OrderHistoryPage /></ProtectedRoute>} />
              <Route path="/billing/success" element={<ProtectedRoute><BillingSuccessPage /></ProtectedRoute>} />
              <Route path="/billing/cancel" element={<ProtectedRoute><BillingCancelPage /></ProtectedRoute>} />
              <Route path="/faq" element={<FAQPage />} />

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
