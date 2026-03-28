import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
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
      <div
        className={`bg-black/80 backdrop-blur-xl border border-white/[0.06] rounded-full px-6 py-3 flex items-center justify-between w-full max-w-4xl transition-shadow duration-300 ${scrolled ? 'shadow-lg shadow-black/50' : 'shadow-xl shadow-black/30'}`}
      >
        <Link to="/" className="flex items-center gap-2 font-bold text-lg tracking-tight shrink-0">
          <TrendingUp className="w-5 h-5 text-purple-500" />
          <span className="text-white">TradeSignal.</span>
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
                className={`flex items-center gap-1 text-sm font-medium transition-colors duration-200 hover:text-white ${
                  location.pathname === link.path ? 'text-white' : 'text-gray-400'
                }`}
              >
                {link.name}
                {link.dropdown && <ChevronDown className="w-3 h-3 group-hover:rotate-180 transition-transform duration-200" />}
              </Link>

              {link.dropdown && activeDropdown === link.name && (
                <div className="absolute top-full left-0 pt-4 w-56">
                  <div className="bg-[#111] border border-white/[0.06] rounded-xl p-2">
                    <div className="flex flex-col gap-0.5">
                      {link.dropdown.map((item) => (
                        <Link
                          key={item.name}
                          to={item.path}
                          className="text-gray-400 hover:text-white px-3 py-2.5 rounded-lg text-xs transition-colors duration-150 block hover:bg-white/5"
                        >
                          {item.name}
                        </Link>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="flex items-center gap-3 shrink-0">
          {isAuthenticated ? (
            <Link
              to="/dashboard"
              className="px-5 py-2 rounded-full text-sm font-semibold bg-white text-black hover:bg-gray-100 transition-colors duration-200 flex items-center gap-2"
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>Dashboard</span>
            </Link>
          ) : (
            <>
              <Link
                to="/login"
                className="text-sm font-medium text-gray-400 hover:text-white transition-colors duration-200 hidden md:block"
              >
                Login
              </Link>
              <Link
                to="/register"
                className="bg-white text-black hover:bg-gray-100 px-5 py-2 rounded-full text-sm font-semibold transition-colors duration-200"
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
      </div>

      {mobileOpen && (
        <div className="absolute top-full left-4 right-4 mt-3 bg-[#111] border border-white/[0.06] rounded-xl p-4 md:hidden">
          <div className="flex flex-col gap-1">
            {navLinks.map((link) => (
              <div key={link.name}>
                <Link
                  to={link.path}
                  className={`block px-4 py-3 rounded-lg text-sm font-medium transition-colors duration-150 ${
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
                        className="block px-4 py-2 rounded-lg text-xs text-gray-500 hover:text-white hover:bg-white/5 transition-colors duration-150"
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
                className="block px-4 py-3 rounded-lg text-sm font-medium text-gray-400 hover:text-white hover:bg-white/5 transition-colors duration-150"
              >
                Login
              </Link>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default PublicNavbar;
