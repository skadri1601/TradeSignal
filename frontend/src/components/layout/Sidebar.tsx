import { Link, useLocation } from 'react-router-dom';
import {
  TrendingUp,
  Bell,
  Lightbulb,
  BarChart3,
  Newspaper,
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
import { motion } from 'framer-motion';

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

interface NavSection {
  label: string;
  items: NavItem[];
}

const navSections: NavSection[] = [
  {
    label: 'Markets',
    items: [
      { name: 'Market Overview', href: '/market-overview', icon: BarChart3 },
      { name: 'News', href: '/news', icon: Newspaper },
      { name: 'Earnings', href: '/earnings', icon: BarChart3 },
    ],
  },
  {
    label: 'Trading',
    items: [
      { name: 'Insider Trades', href: '/trades', icon: TrendingUp },
      { name: 'Congressional Trades', href: '/congressional-trades', icon: Building2 },
      { name: 'Copy Trading', href: '/copy-trading', icon: RefreshCw, requireTier: 'plus' },
    ],
  },
  {
    label: 'Intelligence',
    items: [
      { name: 'AI Insights', href: '/ai-insights', icon: Lightbulb, requireTier: 'pro' },
      { name: 'Pattern Analysis', href: '/patterns', icon: TrendingUp, requireTier: 'pro' },
      { name: 'Research', href: '/research', icon: FileText, requireTier: 'pro' },
      { name: 'Alerts', href: '/alerts', icon: Bell },
    ],
  },
  {
    label: 'Community',
    items: [
      { name: 'Community', href: '/forum', icon: MessageSquare },
      { name: 'Lessons', href: '/lessons', icon: BookOpen },
      { name: 'Strategies', href: '/strategies', icon: Users },
    ],
  },
  {
    label: 'Settings',
    items: [
      { name: 'Settings', href: '/settings', icon: Settings },
    ],
  },
  {
    label: 'Admin',
    items: [
      { name: 'Admin Panel', href: '/admin', icon: Shield, adminOnly: true },
      { name: 'Support Tickets', href: '/admin/tickets', icon: HelpCircle, adminOnly: true },
      { name: 'Contact Management', href: '/admin/contacts', icon: Mail, adminOnly: true },
    ],
  },
];

const footerNavigation: NavItem[] = [
  { name: 'About Us', href: '/about', icon: Info },
  { name: 'Contact', href: '/contact', icon: Mail },
  { name: 'FAQ', href: '/faq', icon: HelpCircle },
  { name: 'Careers', href: '/careers', icon: Briefcase },
];

const sidebarVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { staggerChildren: 0.03, delayChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, x: -12 },
  visible: { opacity: 1, x: 0 },
};

export default function Sidebar() {
  const location = useLocation();
  const { user } = useAuth();
  const isAdmin = user?.role === 'support' || user?.role === 'super_admin' || user?.is_superuser;
  const userTier = user?.stripe_subscription_tier || 'free';
  const userLevel = TIER_LEVELS[userTier.toLowerCase()] || 0;

  return (
    <aside className="w-64 flex flex-col h-screen fixed left-0 top-0 z-50 bg-[#0a0a0f]/95 backdrop-blur-xl border-r border-white/[0.06]">
      <style>{`
        @keyframes gradient-spin {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        @keyframes pulse-glow {
          0%, 100% { box-shadow: 0 0 8px rgba(139, 92, 246, 0.3); }
          50% { box-shadow: 0 0 16px rgba(139, 92, 246, 0.6); }
        }
        .upgrade-card-border {
          background: linear-gradient(135deg, #7c3aed, #3b82f6, #7c3aed, #3b82f6);
          background-size: 300% 300%;
          animation: gradient-spin 4s ease infinite;
        }
        .logo-pulse {
          animation: pulse-glow 3s ease-in-out infinite;
        }
        .sidebar-scrollbar::-webkit-scrollbar { width: 4px; }
        .sidebar-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .sidebar-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 4px; }
        .sidebar-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.15); }
      `}</style>

      <div className="p-5 border-b border-white/[0.06]">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="logo-pulse bg-gradient-to-br from-purple-600 to-blue-500 rounded-xl p-2 transition-transform duration-300 group-hover:scale-105">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <span className="text-lg font-bold text-white tracking-tight">
            TradeSignal
          </span>
        </Link>
      </div>

      {user && !isAdmin && (
        <div className="px-4 pt-5 pb-3 space-y-2">
          <Link
            to="/market-overview"
            className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-500 hover:to-blue-500 font-semibold py-2.5 px-4 rounded-xl transition-all duration-300 flex items-center justify-center gap-2 text-sm shadow-lg shadow-purple-500/20"
          >
            <BarChart3 className="w-4 h-4" />
            <span>View Market</span>
          </Link>
          <Link
            to="/trades"
            className="w-full border border-white/10 text-gray-300 hover:bg-white/[0.06] hover:text-white hover:border-white/20 font-medium py-2.5 px-4 rounded-xl transition-all duration-300 flex items-center justify-center gap-2 text-sm"
          >
            <TrendingUp className="w-4 h-4" />
            <span>View Trades</span>
          </Link>
        </div>
      )}

      <motion.nav
        className="flex-1 px-3 pt-3 pb-2 overflow-y-auto sidebar-scrollbar"
        variants={sidebarVariants}
        initial="hidden"
        animate="visible"
      >
        {navSections.map((section) => {
          const visibleItems = section.items.filter(
            (item) => !item.adminOnly || isAdmin
          );
          if (visibleItems.length === 0) return null;

          return (
            <motion.div key={section.label} variants={itemVariants} className="mb-1">
              <div className="px-3 pt-4 pb-2">
                <span className="text-[10px] font-semibold uppercase tracking-[0.12em] text-gray-500">
                  {section.label}
                </span>
              </div>
              <div className="space-y-0.5">
                {visibleItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.href;

                  let hasAccess = true;
                  if (item.requireTier && !isAdmin) {
                    const requiredLevel = TIER_LEVELS[item.requireTier.toLowerCase()] || 0;
                    if (userLevel < requiredLevel) {
                      hasAccess = false;
                    }
                  }

                  return (
                    <motion.div key={item.name} variants={itemVariants}>
                      <Link
                        to={hasAccess ? item.href : '/pricing'}
                        className={`
                          group relative flex items-center gap-3 px-3 py-2 rounded-lg text-[13px] font-medium transition-all duration-200
                          ${isActive
                            ? 'bg-gradient-to-r from-purple-500/20 to-blue-500/20 text-white border-l-2 border-purple-500 ml-0'
                            : hasAccess
                              ? 'text-gray-400 hover:bg-white/[0.04] hover:text-gray-200'
                              : 'text-gray-600 hover:bg-white/[0.03]'
                          }
                        `}
                      >
                        {isActive && (
                          <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-purple-500/10 to-blue-500/10 blur-sm" />
                        )}
                        <Icon
                          className={`w-[18px] h-[18px] relative z-10 transition-colors duration-200 ${
                            isActive
                              ? 'text-purple-400'
                              : hasAccess
                                ? 'text-gray-500 group-hover:text-gray-300'
                                : 'text-gray-600'
                          }`}
                        />
                        <span className="relative z-10 truncate">{item.name}</span>
                        {item.adminOnly && (
                          <Shield className="w-3 h-3 ml-auto text-purple-500/70 relative z-10" />
                        )}
                        {!hasAccess && (
                          <div className="ml-auto relative z-10 group/lock">
                            <Lock className="w-3.5 h-3.5 text-gray-600" />
                            <div className="absolute right-0 -top-8 bg-gray-900 border border-white/10 text-[10px] text-gray-300 px-2 py-1 rounded-md whitespace-nowrap opacity-0 group-hover/lock:opacity-100 transition-opacity duration-200 pointer-events-none">
                              Requires {item.requireTier} plan
                            </div>
                          </div>
                        )}
                      </Link>
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>
          );
        })}
      </motion.nav>

      <div className="px-3 py-2 border-t border-white/[0.06]">
        <div className="space-y-0.5">
          {footerNavigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center gap-3 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200
                  ${isActive
                    ? 'bg-white/[0.08] text-white'
                    : 'text-gray-500 hover:bg-white/[0.04] hover:text-gray-300'
                  }
                `}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-gray-600'}`} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </div>
      </div>

      {!user?.is_superuser && (
        <div className="p-4 border-t border-white/[0.06]">
          {user?.stripe_subscription_tier && user.stripe_subscription_tier !== 'free' ? (
            <div className="relative bg-gradient-to-br from-purple-900/30 to-blue-900/30 border border-purple-500/20 rounded-xl p-3.5 overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-blue-500/5" />
              <div className="relative flex items-center gap-2.5 mb-1.5">
                <div className="p-1.5 bg-purple-500/15 rounded-lg">
                  <TrendingUp className="w-3.5 h-3.5 text-purple-300" />
                </div>
                <span className="font-bold text-[10px] uppercase tracking-widest bg-gradient-to-r from-purple-300 to-blue-300 bg-clip-text text-transparent">
                  {user.stripe_subscription_tier} Plan
                </span>
              </div>
              <p className="relative text-[10px] text-gray-500 pl-0.5">Subscription active</p>
            </div>
          ) : (
            <Link to="/pricing" className="block group">
              <div className="relative rounded-xl p-[1px] upgrade-card-border">
                <div className="bg-[#0d0d14] rounded-[11px] p-4 relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                  <div className="relative flex flex-col items-center gap-2">
                    <div className="bg-gradient-to-br from-purple-500/20 to-blue-500/20 text-white rounded-full p-2.5">
                      <TrendingUp className="w-4 h-4" />
                    </div>
                    <p className="text-xs text-center text-gray-300 font-medium">
                      Upgrade to <span className="font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">Pro</span>
                    </p>
                  </div>
                </div>
              </div>
            </Link>
          )}
        </div>
      )}
    </aside>
  );
}
