import { Link, useLocation } from 'react-router-dom';
import { TrendingUp } from 'lucide-react';

export default function Header() {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600 hover:text-gray-900';
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <TrendingUp className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">TradeSignal</span>
          </Link>

          {/* Navigation */}
          <nav className="flex space-x-8">
            <Link
              to="/"
              className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/')}`}
            >
              Dashboard
            </Link>
            <Link
              to="/trades"
              className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/trades')}`}
            >
              Trades
            </Link>
            <Link
              to="/alerts"
              className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/alerts')}`}
            >
              Alerts
            </Link>
            <Link
              to="/about"
              className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/about')}`}
            >
              About
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
