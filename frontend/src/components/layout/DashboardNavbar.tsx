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

  // Navigation Structure
  // For admin roles, only show Dashboard and Admin
  // For regular users, show Dashboard, Market, Analysis, Signals
  const navLinks = [];
  
  // Always show Dashboard
  navLinks.push({ name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard });
  
  // Only show customer-facing nav items for non-admin users
  if (!isAdminRole) {
    navLinks.push(
      { 
        name: 'Market', 
        path: '/market-overview',
        dropdown: [
          { name: 'Market Overview', path: '/market-overview', icon: LineChart },
          { name: 'News', path: '/news', icon: Newspaper },
          { name: 'Fed Calendar', path: '/fed-calendar', icon: Calendar },
        ]
      },
      { 
        name: 'Analysis', 
        path: '/trades',
        dropdown: [
          { name: 'Congressional Trades', path: '/congressional-trades', icon: Building2 },
          { name: 'Insider Trades', path: '/trades', icon: Users }, // Assuming /trades is insider
          { name: 'Strategies', path: '/strategies', icon: Search },
        ]
      },
      {
        name: 'Signals',
        path: '/ai-insights',
        dropdown: [
          { name: 'AI Insights', path: '/ai-insights', icon: Zap },
          { name: 'Alerts', path: '/alerts', icon: Bell },
        ]
      }
    );
  }

  // Admin Links - only show for admin roles
  if (isAdminRole) {
    navLinks.push({
      name: 'Admin',
      path: '/admin',
      dropdown: [
        { name: 'Dashboard', path: '/admin', icon: Shield },
        { name: 'Contacts', path: '/admin/contacts', icon: Users },
        { name: 'Tickets', path: '/admin/tickets', icon: Ticket },
      ]
    });
  }

  return (
    <nav className="fixed top-6 left-0 right-0 z-50 flex justify-center px-4 w-full pointer-events-none">
      <motion.div 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="pointer-events-auto relative bg-[#0f0f1a]/80 backdrop-blur-xl border border-white/10 rounded-full pl-6 pr-2 py-2 flex items-center justify-between shadow-2xl w-full max-w-6xl"
      >
        {/* Left: Logo */}
        <Link to="/dashboard" className="flex items-center gap-2 text-white font-bold text-lg tracking-tight shrink-0 mr-8">
           <TrendingUp className="w-5 h-5 text-purple-500" />
           <span className="hidden sm:inline font-mono">TradeSignal.</span>
        </Link>

        {/* Center: Navigation */}
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
                className={`flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  location.pathname === link.path || location.pathname.startsWith(link.path + '/')
                    ? 'bg-white/10 text-white' 
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
              >
                {link.icon && !link.dropdown && <link.icon className="w-4 h-4" />}
                {link.name}
                {link.dropdown && <ChevronDown className="w-3 h-3 group-hover:rotate-180 transition-transform" />}
              </Link>

              {/* Dropdown Menu */}
              <AnimatePresence>
                {link.dropdown && activeDropdown === link.name && (
                  <motion.div
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                    className="absolute top-full left-0 pt-4 w-60"
                  >
                    <div className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-2 shadow-xl overflow-hidden ring-1 ring-white/10">
                      <div className="flex flex-col gap-1">
                        {link.dropdown.map((item) => (
                          <Link 
                            key={item.name} 
                            to={item.path}
                            className="flex items-center gap-3 text-gray-400 hover:text-white hover:bg-white/5 px-3 py-2.5 rounded-xl text-sm transition-all"
                          >
                            <div className="bg-white/5 p-1.5 rounded-lg text-purple-400">
                                <item.icon className="w-4 h-4" />
                            </div>
                            {item.name}
                          </Link>
                        ))}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>

        {/* Right: User Cluster */}
        <div className="flex items-center gap-3 ml-auto">
            {/* Notification Bell */}
            <Link to="/alerts" className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-full transition-colors relative">
                <Bell className="w-5 h-5" />
                <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border border-black"></span>
            </Link>

            {/* User Profile (Clerk UserButton) */}
            <UserButton
              appearance={{
                elements: {
                  avatarBox: 'w-8 h-8',
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
