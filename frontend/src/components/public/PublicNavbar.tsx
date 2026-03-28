import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, TrendingUp, LayoutDashboard, Menu, X } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const PublicNavbar = () => {
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'About', path: '/about' },
    {
      name: 'Features',
      path: '/features',
      dropdown: [
        { name: 'Insider Trades', path: '/features/insider-trades' },
        { name: 'Congressional Trading', path: '/features/congress-trading' },
        { name: 'AI Insights', path: '/features/ai-insights' },
        { name: 'Alerts & Notifications', path: '/features/alerts' },
      ]
    },
    {
      name: 'Resources',
      path: '/resources',
      dropdown: [
        { name: 'Documentation', path: '/docs' },
        { name: 'API Docs', path: '/api-docs' },
        { name: 'Blog', path: '/blog' },
        { name: 'News', path: '/public/news' },
        { name: 'Help Center', path: '/public/support' },
        { name: 'Roadmap', path: '/roadmap' },
      ]
    },
  ];

  return (
    <nav className="fixed top-6 left-0 right-0 z-50 flex justify-center px-4">
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className={`relative bg-[#0a0a0a]/60 backdrop-blur-2xl border border-white/[0.08] rounded-full px-6 py-3 flex items-center justify-between w-full max-w-4xl transition-shadow duration-500 ${scrolled ? 'shadow-[0_8px_40px_rgba(0,0,0,0.5)]' : 'shadow-2xl'}`}
      >
        <div className="absolute bottom-0 left-[10%] right-[10%] h-px overflow-hidden rounded-full">
          <div className="w-full h-full bg-gradient-to-r from-transparent via-purple-500/60 to-transparent animate-[shimmer_3s_ease-in-out_infinite]" />
        </div>

        <Link to="/" className="flex items-center gap-2 font-bold text-lg tracking-tight shrink-0 group">
          <TrendingUp className="w-5 h-5 text-purple-500 group-hover:text-purple-400 transition-colors duration-300 group-hover:drop-shadow-[0_0_6px_rgba(168,85,247,0.6)]" />
          <span className="bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">TradeSignal.</span>
        </Link>

        <div className="hidden md:flex items-center gap-6">
          {navLinks.map((link) => (
            <div
              key={link.name}
              className="relative group"
              onMouseEnter={() => setActiveDropdown(link.name)}
              onMouseLeave={() => setActiveDropdown(null)}
            >
              <Link
                to={link.path}
                className={`flex items-center gap-1 text-sm font-medium transition-colors duration-300 hover:text-white ${
                  location.pathname === link.path ? 'text-white' : 'text-gray-400'
                }`}
              >
                {link.name}
                {link.dropdown && <ChevronDown className="w-3 h-3 group-hover:rotate-180 transition-transform duration-300" />}
              </Link>

              {location.pathname === link.path && (
                <motion.div
                  layoutId="activeNavDot"
                  className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-gradient-to-r from-purple-400 to-blue-400"
                  transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                />
              )}

              <AnimatePresence>
                {link.dropdown && activeDropdown === link.name && (
                  <motion.div
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                    className="absolute top-full left-0 pt-6 w-56"
                  >
                    <div className="bg-[#0a0a0a]/80 backdrop-blur-2xl border border-white/[0.08] rounded-2xl p-2 shadow-[0_8px_40px_rgba(0,0,0,0.5)] overflow-hidden">
                      <div className="flex flex-col gap-0.5">
                        {link.dropdown.map((item) => (
                          <Link
                            key={item.name}
                            to={item.path}
                            className="text-gray-400 hover:text-white px-3 py-2.5 rounded-xl text-xs transition-all duration-200 block relative group/item hover:bg-gradient-to-r hover:from-purple-500/10 hover:to-transparent"
                          >
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

        <div className="flex items-center gap-3 shrink-0">
          {isAuthenticated ? (
            <Link
              to="/dashboard"
              className="relative group px-5 py-2 rounded-full text-sm font-semibold transition-all duration-300 hover:scale-105 flex items-center gap-2"
            >
              <div className="absolute inset-0 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 p-px">
                <div className="w-full h-full rounded-full bg-[#0a0a0a]/90 group-hover:bg-[#0a0a0a]/70 transition-colors duration-300" />
              </div>
              <LayoutDashboard className="w-4 h-4 relative z-10 text-white" />
              <span className="relative z-10 text-white">Dashboard</span>
            </Link>
          ) : (
            <>
              <Link
                to="/login"
                className="text-sm font-medium transition-all duration-300 bg-gradient-to-r from-gray-300 to-gray-400 bg-clip-text text-transparent hover:from-purple-300 hover:to-white hidden md:block"
              >
                Login
              </Link>
              <Link
                to="/register"
                className="bg-white text-black hover:bg-gray-100 px-5 py-2 rounded-full text-sm font-semibold transition-all duration-300 hover:scale-105 hover:shadow-[0_0_20px_rgba(255,255,255,0.2)]"
              >
                Sign Up
              </Link>
            </>
          )}

          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden w-9 h-9 flex items-center justify-center text-gray-400 hover:text-white transition-colors"
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </motion.div>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.25 }}
            className="absolute top-full left-4 right-4 mt-3 bg-[#0a0a0a]/90 backdrop-blur-2xl border border-white/[0.08] rounded-2xl p-4 shadow-[0_8px_40px_rgba(0,0,0,0.5)] md:hidden"
          >
            <div className="flex flex-col gap-1">
              {navLinks.map((link) => (
                <div key={link.name}>
                  <Link
                    to={link.path}
                    className={`block px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                      location.pathname === link.path
                        ? 'text-white bg-white/5'
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    {link.name}
                  </Link>
                  {link.dropdown && (
                    <div className="ml-4 flex flex-col gap-0.5">
                      {link.dropdown.map((item) => (
                        <Link
                          key={item.name}
                          to={item.path}
                          className="block px-4 py-2 rounded-lg text-xs text-gray-500 hover:text-white hover:bg-white/5 transition-all duration-200"
                        >
                          {item.name}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              {!isAuthenticated && (
                <Link
                  to="/login"
                  className="block px-4 py-3 rounded-xl text-sm font-medium text-gray-400 hover:text-white hover:bg-white/5 transition-all duration-200"
                >
                  Login
                </Link>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`
        @keyframes shimmer {
          0%, 100% { opacity: 0.3; transform: translateX(-30%); }
          50% { opacity: 0.8; transform: translateX(30%); }
        }
      `}</style>
    </nav>
  );
};

export default PublicNavbar;
