import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, TrendingUp, LayoutDashboard } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const PublicNavbar = () => {
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const location = useLocation();
  const { isAuthenticated } = useAuth();

  // PORTFOLIO MODE: Removed Pricing and business pages (Use Cases, Testimonials, Careers)
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
        className="relative bg-black/40 backdrop-blur-xl border border-white/10 rounded-full px-6 py-3 flex items-center justify-between shadow-2xl w-full max-w-4xl"
      >
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 text-white font-bold text-lg tracking-tight shrink-0">
           <TrendingUp className="w-5 h-5 text-purple-500" />
           TradeSignal.
        </Link>

        {/* Links - Centered */}
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
                className={`flex items-center gap-1 text-sm font-medium transition-colors hover:text-white ${
                  location.pathname === link.path ? 'text-white' : 'text-gray-400'
                }`}
              >
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
                    className="absolute top-full left-0 pt-6 w-56"
                  >
                    <div className="bg-black/90 backdrop-blur-2xl border border-white/10 rounded-2xl p-3 shadow-xl overflow-hidden">
                      <div className="flex flex-col gap-1">
                        {link.dropdown.map((item) => (
                          <Link 
                            key={item.name} 
                            to={item.path}
                            className="text-gray-400 hover:text-white hover:bg-white/5 px-3 py-2 rounded-lg text-xs transition-all block"
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

        {/* Right Side (Auth) */}
        <div className="flex items-center gap-4 shrink-0">
           {isAuthenticated ? (
             <Link 
               to="/dashboard" 
               className="bg-white text-black hover:bg-gray-200 px-5 py-2 rounded-full text-sm font-semibold transition-all hover:scale-105 flex items-center gap-2"
             >
               <LayoutDashboard className="w-4 h-4" />
               Dashboard
             </Link>
           ) : (
             <>
               <Link to="/login" className="text-sm font-medium text-white hover:text-purple-400 transition-colors">
                 Login
               </Link>
               <Link 
                 to="/register" 
                 className="bg-white text-black hover:bg-gray-200 px-5 py-2 rounded-full text-sm font-semibold transition-all hover:scale-105"
               >
                 Sign Up
               </Link>
             </>
           )}
        </div>
      </motion.div>
    </nav>
  );
};

export default PublicNavbar;