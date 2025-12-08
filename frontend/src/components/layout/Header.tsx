import { Link, useLocation, useNavigate } from 'react-router-dom';
import { TrendingUp, User, LogOut } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

export default function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();

  const isActive = (path: string) => {
    return location.pathname === path ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600 hover:text-gray-900';
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/dashboard" className="flex items-center space-x-2">
            <TrendingUp className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">TradeSignal</span>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center space-x-8">
            <Link
              to="/dashboard"
              className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/dashboard')}`}
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
              to="/market-overview"
              className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/market-overview')}`}
            >
              Market Overview
            </Link>
            <Link
              to="/ai-insights"
              className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/ai-insights')}`}
            >
              AI Insights
            </Link>
            <Link
              to="/alerts"
              className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/alerts')}`}
            >
              Alerts
            </Link>
            <Link
              to="/pricing"
              className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/pricing')}`}
            >
              Pricing
            </Link>
            <Link
              to="/about"
              className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/about')}`}
            >
              About
            </Link>

            {/* Auth Section */}
            <div className="flex items-center space-x-4 ml-4 pl-4 border-l border-gray-300">
              {isAuthenticated ? (
                <>
                  <Link
                    to="/profile"
                    className="flex items-center space-x-2 text-sm text-gray-700 hover:text-blue-600 transition-colors"
                    title="View Profile"
                  >
                    <User className="h-4 w-4" />
                    <span>{user?.username}</span>
                  </Link>
                  {user?.is_superuser && (
                    <Link
                      to="/admin"
                      className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full font-medium hover:bg-purple-200"
                    >
                      Admin
                    </Link>
                  )}
                  <button
                    onClick={handleLogout}
                    className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                  >
                    <LogOut className="h-4 w-4 mr-1" />
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="inline-flex items-center px-4 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
                  >
                    Sign Up Free
                  </Link>
                </>
              )}
            </div>
          </nav>
        </div>
      </div>
    </header>
  );
}
