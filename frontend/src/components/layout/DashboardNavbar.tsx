import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { UserButton } from '@clerk/clerk-react';
import {
  TrendingUp,
  ChevronDown,
  LayoutDashboard,
  Bell,
  Zap,
  LineChart,
  Newspaper,
  Calendar,
  Building2,
  Users,
  Search,
  MessageSquare,
  CreditCard,
  Shield,
  Ticket,
  Activity,
  Settings
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const DashboardNavbar = () => {
  const { user } = useAuth();
  const location = useLocation();

  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);

  const isAdminRole = user?.is_superuser || user?.role === 'super_admin' || user?.role === 'support';

  const navLinks: Array<{
    name: string;
    path: string;
    icon?: React.ComponentType<{ className?: string }>;
    dropdown?: Array<{ name: string; path: string; icon: React.ComponentType<{ className?: string }>; description?: string }>;
  }> = [];

  navLinks.push({ name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard });

  if (!isAdminRole) {
    navLinks.push(
      {
        name: 'Market',
        path: '/market-overview',
        dropdown: [
          { name: 'Market Overview', path: '/market-overview', icon: LineChart, description: 'Real-time market data' },
          { name: 'News', path: '/news', icon: Newspaper, description: 'Latest financial news' },
          { name: 'Fed Calendar', path: '/fed-calendar', icon: Calendar, description: 'Upcoming Fed events' },
        ]
      },
      {
        name: 'Analysis',
        path: '/trades',
        dropdown: [
          { name: 'Congressional Trades', path: '/congressional-trades', icon: Building2, description: 'Track congress activity' },
          { name: 'Insider Trades', path: '/trades', icon: Users, description: 'Corporate insider moves' },
          { name: 'Strategies', path: '/strategies', icon: Search, description: 'Explore strategies' },
        ]
      },
      {
        name: 'Signals',
        path: '/ai-insights',
        dropdown: [
          { name: 'AI Insights', path: '/ai-insights', icon: Zap, description: 'AI-powered analysis' },
          { name: 'Alerts', path: '/alerts', icon: Bell, description: 'Custom price alerts' },
        ]
      }
    );
  }

  if (isAdminRole) {
    navLinks.push({
      name: 'Admin',
      path: '/admin',
      dropdown: [
        { name: 'Dashboard', path: '/admin', icon: Shield, description: 'Admin overview' },
        { name: 'Contacts', path: '/admin/contacts', icon: Users, description: 'Manage contacts' },
        { name: 'Tickets', path: '/admin/tickets', icon: Ticket, description: 'Support tickets' },
      ]
    });
  }

  const isActive = (path: string) =>
    location.pathname === path || location.pathname.startsWith(path + '/');

  const dropdownVariants = {
    hidden: { opacity: 0, y: 8, scale: 0.96 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: { type: 'spring' as const, stiffness: 400, damping: 30, staggerChildren: 0.05 },
    },
    exit: { opacity: 0, y: 8, scale: 0.96, transition: { duration: 0.15 } },
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -8 },
    visible: { opacity: 1, x: 0, transition: { type: 'spring' as const, stiffness: 400, damping: 30 } },
  };

  return (
    <nav className="fixed top-6 left-0 right-0 z-50 flex justify-center px-4 w-full pointer-events-none">
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        className="pointer-events-auto relative bg-[#0f0f1a]/60 backdrop-blur-2xl border border-white/[0.08] rounded-full pl-6 pr-2 py-2 flex items-center justify-between w-full max-w-6xl"
        style={{
          boxShadow: '0 0 0 1px rgba(139, 92, 246, 0.08), 0 8px 40px rgba(0, 0, 0, 0.5), 0 0 80px rgba(139, 92, 246, 0.04)',
        }}
      >
        <div className="absolute inset-0 rounded-full overflow-hidden pointer-events-none">
          <div
            className="absolute bottom-0 left-0 right-0 h-[1px]"
            style={{
              background: 'linear-gradient(90deg, transparent, #8b5cf6, #6366f1, #3b82f6, #8b5cf6, transparent)',
              backgroundSize: '200% 100%',
              animation: 'shimmer 3s linear infinite',
            }}
          />
        </div>

        <style>{`
          @keyframes shimmer {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
          }
          @keyframes bell-glow {
            0%, 100% { box-shadow: 0 0 4px rgba(239, 68, 68, 0.4); }
            50% { box-shadow: 0 0 12px rgba(239, 68, 68, 0.7); }
          }
        `}</style>

        <Link to="/dashboard" className="flex items-center gap-2 text-white font-bold text-lg tracking-tight shrink-0 mr-8 group">
           <TrendingUp className="w-5 h-5 text-purple-500 group-hover:text-purple-400 transition-colors" />
           <span className="hidden sm:inline font-mono bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">TradeSignal.</span>
        </Link>

        <div className="hidden lg:flex items-center gap-1">
          {navLinks.map((link) => (
            <div
              key={link.name}
              className="relative group"
              onMouseEnter={() => setActiveDropdown(link.name)}
              onMouseLeave={() => setActiveDropdown(null)}
            >
              <Link
                to={link.path}
                className={`relative flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                  isActive(link.path)
                    ? 'text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {isActive(link.path) && (
                  <motion.div
                    layoutId="activeNavPill"
                    className="absolute inset-0 rounded-full"
                    style={{
                      background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(99, 102, 241, 0.15))',
                      border: '1px solid rgba(139, 92, 246, 0.15)',
                    }}
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                  />
                )}
                {!isActive(link.path) && (
                  <div className="absolute inset-0 rounded-full bg-white/0 hover:bg-white/5 transition-colors duration-200" />
                )}
                <span className="relative z-10 flex items-center gap-1.5">
                  {link.icon && !link.dropdown && <link.icon className="w-4 h-4" />}
                  {link.name}
                  {link.dropdown && (
                    <ChevronDown className={`w-3 h-3 transition-transform duration-200 ${activeDropdown === link.name ? 'rotate-180' : ''}`} />
                  )}
                </span>
              </Link>

              <AnimatePresence>
                {link.dropdown && activeDropdown === link.name && (
                  <motion.div
                    variants={dropdownVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                    className="absolute top-full left-0 pt-3 w-64"
                  >
                    <div
                      className="bg-[#0f0f1a]/95 backdrop-blur-2xl border border-white/[0.08] rounded-2xl p-1.5 overflow-hidden"
                      style={{
                        boxShadow: '0 0 0 1px rgba(139, 92, 246, 0.06), 0 20px 60px rgba(0, 0, 0, 0.6)',
                      }}
                    >
                      <div className="flex flex-col gap-0.5">
                        {link.dropdown.map((item) => (
                          <motion.div key={item.name} variants={itemVariants}>
                            <Link
                              to={item.path}
                              className="group/item flex items-center gap-3 text-gray-400 hover:text-white px-3 py-2.5 rounded-xl text-sm transition-all duration-200 hover:bg-gradient-to-r hover:from-purple-500/10 hover:to-indigo-500/10"
                            >
                              <div className="p-1.5 rounded-lg bg-white/[0.04] group-hover/item:bg-gradient-to-br group-hover/item:from-purple-500/20 group-hover/item:to-indigo-500/20 transition-all duration-200">
                                  <item.icon className="w-4 h-4 text-purple-400 group-hover/item:text-purple-300 transition-colors" />
                              </div>
                              <div className="flex flex-col">
                                <span className="font-medium">{item.name}</span>
                                {item.description && (
                                  <span className="text-[11px] text-gray-500 group-hover/item:text-gray-400 transition-colors">{item.description}</span>
                                )}
                              </div>
                            </Link>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>

        <div className="flex items-center gap-3 ml-auto">
            <Link to="/alerts" className="relative p-2 text-gray-400 hover:text-white rounded-full transition-all duration-200 hover:bg-white/5">
                <Bell className="w-5 h-5" />
                <span
                  className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"
                  style={{ animation: 'bell-glow 2s ease-in-out infinite' }}
                />
            </Link>

            <UserButton
              appearance={{
                elements: {
                  avatarBox: 'w-8 h-8 ring-2 ring-white/10 hover:ring-purple-500/30 transition-all',
                  userButtonPopoverFooter: 'hidden',
                },
              }}
            >
              {isAdminRole ? (
                <UserButton.MenuItems>
                  <UserButton.Link label="Settings" labelIcon={<Settings className="w-4 h-4" />} href="/settings" />
                </UserButton.MenuItems>
              ) : (
                <UserButton.MenuItems>
                  <UserButton.Link label="Billing & Plans" labelIcon={<CreditCard className="w-4 h-4" />} href="/pricing" />
                  <UserButton.Link label="Order History" labelIcon={<Activity className="w-4 h-4" />} href="/orders" />
                  <UserButton.Link label="Support" labelIcon={<MessageSquare className="w-4 h-4" />} href="/support" />
                  <UserButton.Link label="Settings" labelIcon={<Settings className="w-4 h-4" />} href="/settings" />
                </UserButton.MenuItems>
              )}
            </UserButton>
        </div>
      </motion.div>
    </nav>
  );
};

export default DashboardNavbar;
