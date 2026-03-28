import { Link } from 'react-router-dom';
import { Twitter, Linkedin, Github, Globe } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const GlobalFooter = () => {
  const { isAuthenticated } = useAuth();

  return (
    <footer className="bg-black text-white pt-24 font-sans">
      <div className="border-t border-white/[0.06]" />

      <div className="max-w-7xl mx-auto px-6 mb-20 pt-16">
        <div className="grid lg:grid-cols-2 gap-16 lg:gap-32">

          <div className="space-y-8">
            <Link to="/" className="text-3xl font-bold tracking-tight text-white block">
              TradeSignal.
            </Link>
            <h2 className="text-3xl lg:text-4xl font-bold leading-tight max-w-md text-white">
              Together, we turn your vision into reality.
            </h2>

            <form className="max-w-md mt-8">
              <div className="relative flex items-center">
                <input
                  type="email"
                  placeholder="Your Email"
                  className="w-full bg-white/[0.06] border border-white/10 rounded-full py-4 pl-6 pr-32 text-white placeholder:text-gray-500 focus:outline-none focus:border-white/20 transition-colors duration-200"
                />
                <button
                  type="button"
                  className="absolute right-2 top-2 bottom-2 bg-purple-500 hover:bg-purple-600 text-white font-semibold px-6 rounded-full transition-colors duration-200"
                >
                  Submit
                </button>
              </div>
            </form>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="space-y-4">
              <h4 className="font-bold text-white mb-6">Company</h4>
              <ul className="space-y-3 text-sm text-gray-400">
                <li><FooterLink to="/">Home</FooterLink></li>
                <li><FooterLink to="/about">About</FooterLink></li>
                <li><FooterLink to="/blog">Blog</FooterLink></li>
              </ul>
            </div>

            <div className="space-y-4">
              <h4 className="font-bold text-white mb-6">Resources</h4>
              <ul className="space-y-3 text-sm text-gray-400">
                <li><FooterLink to="/docs">Documentation</FooterLink></li>
                <li><FooterLink to="/api-docs">API Docs</FooterLink></li>
                <li><FooterLink to="/public/news">News</FooterLink></li>
                <li><FooterLink to="/public/support">Help Center</FooterLink></li>
                <li><FooterLink to="/roadmap">Roadmap</FooterLink></li>
                <li><FooterLink to="/contact">Contact Us</FooterLink></li>
                <li><FooterLink to="/faq">FAQ</FooterLink></li>
                {isAuthenticated && (
                  <>
                    <li><FooterLink to="/settings">Settings</FooterLink></li>
                    <li><FooterLink to="/support">Support</FooterLink></li>
                  </>
                )}
              </ul>
            </div>

            <div className="space-y-4">
              <h4 className="font-bold text-white mb-6">Features</h4>
              <ul className="space-y-3 text-sm text-gray-400">
                <li><FooterLink to="/features/insider-trades">Insider Trades</FooterLink></li>
                <li><FooterLink to="/features/congress-trading">Congressional Trading</FooterLink></li>
                <li><FooterLink to="/features/ai-insights">AI Insights</FooterLink></li>
                <li><FooterLink to="/features/alerts">Alerts</FooterLink></li>
              </ul>
            </div>

            <div className="space-y-4">
              <h4 className="font-bold text-white mb-6">Legal</h4>
              <ul className="space-y-3 text-sm text-gray-400">
                <li><FooterLink to="/privacy">Privacy Policy</FooterLink></li>
                <li><FooterLink to="/terms">Terms of Service</FooterLink></li>
              </ul>
            </div>
          </div>

        </div>

        <div className="border-t border-white/[0.06] my-12" />

        <div className="flex flex-col md:flex-row justify-between items-center gap-6 text-sm text-gray-500">
          <div className="flex flex-col md:flex-row items-center gap-2 md:gap-4">
            <span>Copyrights &copy; TradeSignal</span>
            <span className="hidden md:inline">&bull;</span>
            <span>
              Built by{' '}
              <a
                href="https://saadkadri.dev/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors duration-200"
              >
                Saad Kadri
              </a>
            </span>
          </div>
          <div className="flex gap-4">
            <SocialIcon href="https://saadkadri.dev/" title="Portfolio"><Globe className="w-4 h-4" /></SocialIcon>
            <SocialIcon href="https://github.com/skadri1601" title="GitHub"><Github className="w-4 h-4" /></SocialIcon>
            <SocialIcon href="https://www.linkedin.com/in/saad-kadri-58b8bb205/" title="LinkedIn"><Linkedin className="w-4 h-4" /></SocialIcon>
            <SocialIcon href="#" title="Twitter"><Twitter className="w-4 h-4" /></SocialIcon>
          </div>
        </div>
      </div>
    </footer>
  );
};

const FooterLink = ({ to, children }: { to: string; children: React.ReactNode }) => (
  <Link
    to={to}
    className="hover:text-white transition-colors duration-200"
  >
    {children}
  </Link>
);

const SocialIcon = ({ href, title, children }: { href: string; title: string; children: React.ReactNode }) => (
  <a
    href={href}
    target="_blank"
    rel="noopener noreferrer"
    className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-gray-400 hover:bg-white/10 hover:text-white transition-colors duration-200"
    title={title}
  >
    {children}
  </a>
);

export default GlobalFooter;
