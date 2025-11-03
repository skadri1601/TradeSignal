import { Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import TradesPage from './pages/TradesPage';
import AboutPage from './pages/AboutPage';
import CompanyPage from './pages/CompanyPage';
import InsiderPage from './pages/InsiderPage';
import AlertsPage from './pages/AlertsPage';
import NotFound from './pages/NotFound';
import { NotificationProvider } from './contexts/NotificationContext';
import { useRealtimeAlerts } from './hooks/useRealtimeAlerts';

// WebSocket URL for real-time alerts
const ALERTS_WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/alerts/stream';

function AppContent() {
  // Connect to real-time alerts WebSocket
  useRealtimeAlerts({ url: ALERTS_WS_URL, enabled: true });

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/trades" element={<TradesPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/companies/:ticker" element={<CompanyPage />} />
        <Route path="/insiders/:id" element={<InsiderPage />} />
        <Route path="/alerts" element={<AlertsPage />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Layout>
  );
}

function App() {
  return (
    <NotificationProvider>
      <AppContent />
    </NotificationProvider>
  );
}

export default App;
