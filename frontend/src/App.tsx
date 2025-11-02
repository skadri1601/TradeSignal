import { Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import TradesPage from './pages/TradesPage';
import AboutPage from './pages/AboutPage';
import CompanyPage from './pages/CompanyPage';
import InsiderPage from './pages/InsiderPage';
import AlertsPage from './pages/AlertsPage';
import NotFound from './pages/NotFound';

function App() {
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

export default App;
