/**
 * Modern Sidebar Navigation Component
 * Inspired by modern trading apps
 */

import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  TrendingUp,
  Bell,
  Lightbulb,
  BarChart3,
  CreditCard,
  Newspaper,
  Calendar,
  BookOpen,
  Users,
  Shield,
  Building2,
  HelpCircle,
  Mail,
  Briefcase,
  Info
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import UsageStats from '../UsageStats';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  adminOnly?: boolean;
}

const navigation: NavItem[] = [
  { name: 'Overview', href: '/', icon: LayoutDashboard },
  { name: 'Market Overview', href: '/market-overview', icon: BarChart3 },
  { name: 'Insider Trades', href: '/trades', icon: TrendingUp },
  { name: 'Congressional Trades', href: '/congressional-trades', icon: Building2 },
  { name: 'News', href: '/news', icon: Newspaper },
  { name: 'FED Calendar', href: '/fed-calendar', icon: Calendar },
  { name: 'Earnings', href: '/earnings', icon: BarChart3 },
  { name: 'Pattern Analysis', href: '/patterns', icon: TrendingUp },
  { name: 'Alerts', href: '/alerts', icon: Bell },
  { name: 'AI Insights', href: '/ai-insights', icon: Lightbulb },
  { name: 'Lessons', href: '/lessons', icon: BookOpen },
  { name: 'Strategies', href: '/strategies', icon: Users },
  { name: 'Order History', href: '/orders', icon: CreditCard },
  { name: 'Pricing', href: '/pricing', icon: CreditCard },
  { name: 'Admin Panel', href: '/admin', icon: Shield, adminOnly: true },
];

const footerNavigation: NavItem[] = [
  { name: 'About Us', href: '/about', icon: Info },
  { name: 'Contact', href: '/contact', icon: Mail },
  { name: 'FAQ', href: '/faq', icon: HelpCircle },
  { name: 'Careers', href: '/careers', icon: Briefcase },
];

export default function Sidebar() {
  const location = useLocation();
  const { user } = useAuth();
  const isAdmin = user?.role === 'support' || user?.role === 'super_admin' || user?.is_superuser;

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col h-screen fixed left-0 top-0">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg p-2">
            <TrendingUp className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            TradeSignal
          </span>
          <span className="bg-red-500 text-white text-xs font-semibold px-1.5 py-0.5 rounded">
            LIVE
          </span>
        </div>
      </div>

      {/* Action Buttons - Only show for regular users (not admins) */}
      {user && !isAdmin && (
        <div className="px-4 pt-6 pb-4 space-y-2">
          <Link
            to="/market-overview"
            className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold py-3 px-4 rounded-lg shadow-lg shadow-blue-500/30 transition-all flex items-center justify-center space-x-2"
          >
            <span>📊</span>
            <span>View Market</span>
          </Link>
          <Link
            to="/trades"
            className="w-full border-2 border-blue-600 text-blue-600 hover:bg-blue-50 font-semibold py-3 px-4 rounded-lg transition-all flex items-center justify-center space-x-2"
          >
            <span>📈</span>
            <span>View Trades</span>
          </Link>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navigation
          .filter(item => {
            // If user is admin, only show admin pages
            if (user?.is_superuser) {
              return item.adminOnly === true;
            }
            // If user is not admin, show all non-admin pages
            return !item.adminOnly;
          })
          .map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href;

            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all
                  ${isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                  }
                  ${item.adminOnly ? 'border-t border-gray-200 mt-2 pt-2' : ''}
                `}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-blue-700' : 'text-gray-500'}`} />
                <span>{item.name}</span>
                {item.adminOnly && <Shield className="w-3 h-3 ml-auto text-blue-600" />}
              </Link>
            );
          })}
      </nav>

      {/* Footer Navigation */}
      <div className="p-3 border-t border-gray-200 space-y-1">
        {footerNavigation.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.href;

          return (
            <Link
              key={item.name}
              to={item.href}
              className={`
                flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-all
                ${isActive
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }
              `}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-blue-700' : 'text-gray-500'}`} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </div>

      {/* Bottom Section - Hide upgrade for admins */}
      {!user?.is_superuser && (
        <div className="p-4 border-t border-gray-200">
          <UsageStats />
          <Link to="/pricing" className="block mt-3">
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-center justify-center mb-2">
                <div className="bg-blue-600 text-white rounded-full p-2">
                  <TrendingUp className="w-5 h-5" />
                </div>
              </div>
              <p className="text-xs text-center text-gray-600">
                Upgrade to <span className="font-semibold text-blue-600">Pro</span> for advanced features
              </p>
            </div>
          </Link>
        </div>
      )}
    </aside>
  );
}
