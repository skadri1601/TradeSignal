/**
 * Modern Sidebar Navigation Component
 * Inspired by modern trading apps - Dark Mode
 */

import { Link, useLocation } from 'react-router-dom';
import {
  TrendingUp,
  Bell,
  Lightbulb,
  BarChart3,
  Newspaper,
  Calendar,
  BookOpen,
  Users,
  Shield,
  Building2,
  HelpCircle,
  Mail,
  Briefcase,
  Info,
  FileText,
  MessageSquare,
  RefreshCw,
  Settings,
  Lock
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

// Define tier hierarchy
const TIER_LEVELS: Record<string, number> = {
  'free': 0,
  'basic': 1,
  'plus': 2,
  'pro': 3,
  'enterprise': 4
};

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  adminOnly?: boolean;
  requireTier?: string;
}

const navigation: NavItem[] = [
  { name: 'Market Overview', href: '/market-overview', icon: BarChart3 },
  { name: 'Insider Trades', href: '/trades', icon: TrendingUp },
  { name: 'Congressional Trades', href: '/congressional-trades', icon: Building2 },
  { name: 'News', href: '/news', icon: Newspaper },
  { name: 'FED Calendar', href: '/fed-calendar', icon: Calendar },
  { name: 'Earnings', href: '/earnings', icon: BarChart3 },
  { name: 'Pattern Analysis', href: '/patterns', icon: TrendingUp, requireTier: 'pro' },
  { name: 'Research', href: '/research', icon: FileText, requireTier: 'pro' },
  { name: 'Alerts', href: '/alerts', icon: Bell },
  { name: 'AI Insights', href: '/ai-insights', icon: Lightbulb, requireTier: 'pro' },
  { name: 'Community', href: '/forum', icon: MessageSquare },
  { name: 'Copy Trading', href: '/copy-trading', icon: RefreshCw, requireTier: 'plus' }, // Assuming 'premium' means plus/pro/enterprise
  { name: 'Lessons', href: '/lessons', icon: BookOpen },
  { name: 'Strategies', href: '/strategies', icon: Users },
  { name: 'Settings', href: '/settings', icon: Settings },
  { name: 'Admin Panel', href: '/admin', icon: Shield, adminOnly: true },
  { name: 'Support Tickets', href: '/admin/tickets', icon: HelpCircle, adminOnly: true },
  { name: 'Contact Management', href: '/admin/contacts', icon: Mail, adminOnly: true },
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
  const userTier = user?.stripe_subscription_tier || 'free';
  const userLevel = TIER_LEVELS[userTier.toLowerCase()] || 0;

  return (
    <aside className="w-64 bg-black border-r border-white/10 flex flex-col h-screen fixed left-0 top-0 z-50">
      {/* Logo */}
      <div className="p-6 border-b border-white/10">
        <Link to="/" className="flex items-center space-x-2">
          <div className="bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg p-2">
            <TrendingUp className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold text-white tracking-tight">
            TradeSignal
          </span>
        </Link>
      </div>

      {/* Action Buttons - Only show for regular users (not admins) */}
      {user && !isAdmin && (
        <div className="px-4 pt-6 pb-4 space-y-2">
          <Link
            to="/market-overview"
            className="w-full bg-white text-black hover:bg-gray-200 font-semibold py-3 px-4 rounded-lg transition-all flex items-center justify-center space-x-2"
          >
            <span>📊</span>
            <span>View Market</span>
          </Link>
          <Link
            to="/trades"
            className="w-full border border-white/20 text-white hover:bg-white/10 font-semibold py-3 px-4 rounded-lg transition-all flex items-center justify-center space-x-2"
          >
            <span>📈</span>
            <span>View Trades</span>
          </Link>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto custom-scrollbar">
        {navigation
          .filter(item => {
            // Admin check
            if (item.adminOnly && !isAdmin) return false;
            return true;
          })
          .map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href;
            
            // Check tier access
            let hasAccess = true;
            if (item.requireTier && !isAdmin) {
              const requiredLevel = TIER_LEVELS[item.requireTier.toLowerCase()] || 0;
              if (userLevel < requiredLevel) {
                hasAccess = false;
              }
            }

            return (
              <Link
                key={item.name}
                to={hasAccess ? item.href : '/pricing'}
                className={`
                  flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all
                  ${isActive
                    ? 'bg-purple-500/20 text-purple-300 border border-purple-500/20'
                    : hasAccess
                      ? 'text-gray-400 hover:bg-white/5 hover:text-white'
                      : 'text-gray-600 cursor-not-allowed hover:bg-white/5'
                  }
                  ${item.adminOnly ? 'border-t border-white/10 mt-2 pt-2' : ''}
                `}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-purple-400' : hasAccess ? 'text-gray-500 group-hover:text-white' : 'text-gray-600'}`} />
                <span>{item.name}</span>
                {item.adminOnly && <Shield className="w-3 h-3 ml-auto text-purple-500" />}
                {!hasAccess && <Lock className="w-3 h-3 ml-auto text-gray-600" />}
              </Link>
            );
          })}
      </nav>

      {/* Footer Navigation */}
      <div className="p-3 border-t border-white/10 space-y-1">
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
                  ? 'bg-white/10 text-white'
                  : 'text-gray-500 hover:bg-white/5 hover:text-white'
                }
              `}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-gray-500'}`} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </div>

      {/* Bottom Section - Hide upgrade for admins */}
      {!user?.is_superuser && (
        <div className="p-4 border-t border-white/10">
          
          {user?.stripe_subscription_tier && user.stripe_subscription_tier !== 'free' ? (
             <div className="mt-3 bg-gradient-to-r from-purple-900/50 to-blue-900/50 border border-purple-500/30 rounded-lg p-4 text-white shadow-lg">
                <div className="flex items-center space-x-2 mb-2">
                   <div className="p-1.5 bg-purple-500/20 rounded-full">
                      <TrendingUp className="w-4 h-4 text-purple-300" />
                   </div>
                   <span className="font-bold text-xs uppercase tracking-wider text-purple-200">{user.stripe_subscription_tier} PLAN</span>
                </div>
                <p className="text-[10px] text-gray-400">Subscription active</p>
             </div>
          ) : (
            <Link to="/pricing" className="block mt-3">
              <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-4 hover:opacity-90 transition-opacity cursor-pointer shadow-lg">
                <div className="flex items-center justify-center mb-2">
                  <div className="bg-white/20 text-white rounded-full p-2">
                    <TrendingUp className="w-5 h-5" />
                  </div>
                </div>
                <p className="text-xs text-center text-white font-medium">
                  Upgrade to <span className="font-bold">Pro</span>
                </p>
              </div>
            </Link>
          )}
        </div>
      )}
    </aside>
  );
}