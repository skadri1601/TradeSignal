import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
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
  UserCircle,
  LogOut,
  Shield,
  Ticket,
  Activity,
  Settings
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { getUsageStats } from '../../api/billing';
import type { UsageStats } from '../../api/billing';

const DashboardNavbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Dropdown States
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  
  // Data States
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null);
  
  const profileRef = useRef<HTMLDivElement>(null);

  // Close profile dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setIsProfileOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Check if user is an admin role (Super Admin or Support Admin)
  const isAdminRole = user?.is_superuser || user?.role === 'super_admin' || user?.role === 'support';

  // Fetch Stats (Ported from TopBar) - Skip for admin roles as they don't need usage stats
  useEffect(() => {
    const fetchData = async () => {
      if (user && !isAdminRole) {
        try {
          const stats = await getUsageStats().catch(() => null);
          setUsageStats(stats);
        } catch (error) {
           console.error("Failed to fetch dashboard stats");
        }
      }
    };
    fetchData();
  }, [user, isProfileOpen, isAdminRole]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const getUsagePercentage = () => {
    if (!usageStats) return 0;
    const limit = usageStats.limits.ai_requests_per_day;
    if (limit === -1) return 0; 
    return (usageStats.usage.ai_requests / limit) * 100;
  };

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
                    className="absolute top-full left-1/2 -translate-x-1/2 pt-4 w-60"
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

            {/* User Profile Dropdown */}
            <div className="relative" ref={profileRef}>
                <button 
                    onClick={() => setIsProfileOpen(!isProfileOpen)}
                    className="flex items-center gap-2 pl-2 pr-1 py-1 bg-white/5 hover:bg-white/10 rounded-full border border-white/5 transition-all"
                >
                    <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-indigo-500 rounded-full flex items-center justify-center text-xs font-bold text-white shadow-lg">
                        {user?.username?.[0]?.toUpperCase()}
                    </div>
                    <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isProfileOpen ? 'rotate-180' : ''}`} />
                </button>

                <AnimatePresence>
                    {isProfileOpen && (
                        <motion.div
                            initial={{ opacity: 0, y: 10, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: 10, scale: 0.95 }}
                            className="absolute top-full right-0 pt-4 w-72"
                        >
                            <div className="bg-[#0f0f1a] border border-white/10 rounded-2xl shadow-2xl overflow-hidden ring-1 ring-white/10 backdrop-blur-3xl">
                                {/* Header */}
                                <div className="px-5 py-4 bg-white/5 border-b border-white/5">
                                    <p className="text-xs text-purple-400 font-medium mb-0.5">{getGreeting()}</p>
                                    <p className="text-base font-bold text-white truncate">{user?.username}</p>
                                    <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                                </div>

                                {/* AI Usage Stats - Only show for non-admin users */}
                                {!isAdminRole && usageStats && (
                                    <div className="px-5 py-3 border-b border-white/5 bg-black/20">
                                        <div className="flex justify-between items-center mb-2">
                                            <div className="flex items-center space-x-2">
                                                <Zap className="w-3.5 h-3.5 text-yellow-500 fill-yellow-500" />
                                                <span className="text-xs font-medium text-gray-300">Daily AI Usage</span>
                                            </div>
                                            <span className="text-xs font-mono text-gray-400">
                                                <span className="text-white">{usageStats.usage.ai_requests}</span>
                                                <span className="opacity-50">/</span>
                                                {usageStats.limits.ai_requests_per_day === -1 ? '∞' : usageStats.limits.ai_requests_per_day}
                                            </span>
                                        </div>
                                        {usageStats.limits.ai_requests_per_day !== -1 && (
                                            <div className="w-full bg-gray-800 rounded-full h-1.5">
                                                <div
                                                    className={`h-1.5 rounded-full transition-all duration-500 ${
                                                        getUsagePercentage() > 90 ? 'bg-red-500' : 'bg-gradient-to-r from-purple-500 to-blue-500'
                                                    }`}
                                                    style={{ width: `${Math.min(getUsagePercentage(), 100)}%` }}
                                                ></div>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {/* Menu Items */}
                                <div className="p-2">
                                    <button onClick={() => navigate('/profile')} className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-xl transition-colors">
                                        <UserCircle className="w-4 h-4" /> Profile
                                    </button>
                                    {!isAdminRole && (
                                        <>
                                            <button onClick={() => navigate('/pricing')} className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-xl transition-colors">
                                                <CreditCard className="w-4 h-4" /> Billing & Plans
                                            </button>
                                            <button onClick={() => navigate('/orders')} className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-xl transition-colors">
                                                <Activity className="w-4 h-4" /> Order History
                                            </button>
                                            <button onClick={() => navigate('/support')} className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-xl transition-colors">
                                                <MessageSquare className="w-4 h-4" /> Support
                                            </button>
                                        </>
                                    )}

                                    <div className="h-px bg-white/5 my-1 mx-2"></div>

                                    <button onClick={() => navigate('/settings')} className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-xl transition-colors">
                                        <Settings className="w-4 h-4" /> Settings
                                    </button>

                                    <div className="h-px bg-white/5 my-1 mx-2"></div>

                                    <button onClick={handleLogout} className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-red-400 hover:bg-red-500/10 rounded-xl transition-colors">
                                        <LogOut className="w-4 h-4" /> Log Out
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
      </motion.div>
    </nav>
  );
};

export default DashboardNavbar;
