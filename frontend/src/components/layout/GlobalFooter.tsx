import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Twitter, Linkedin, Github, Globe } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const GlobalFooter = () => {
  const { isAuthenticated } = useAuth();
  const [emailFocused, setEmailFocused] = useState(false);

  return (
    <footer className="relative text-white pt-24 overflow-hidden font-sans">
      <div className="absolute inset-0 bg-black -z-10" />
      <div className="absolute top-[30%] left-[10%] w-[400px] h-[400px] rounded-full bg-purple-900/[0.04] blur-[120px] -z-[5]" />
      <div className="absolute bottom-[20%] right-[15%] w-[350px] h-[350px] rounded-full bg-purple-800/[0.03] blur-[100px] -z-[5]" />
      <div className="absolute top-[60%] left-[50%] w-[500px] h-[500px] rounded-full bg-blue-900/[0.03] blur-[140px] -z-[5]" />

      <div className="h-px w-full bg-gradient-to-r from-transparent via-purple-500/40 to-transparent" />

      <div className="max-w-7xl mx-auto px-6 mb-20 pt-16">
        <div className="grid lg:grid-cols-2 gap-16 lg:gap-32">

          <div className="space-y-8">
            <Link to="/" className="text-3xl font-bold tracking-tight block bg-gradient-to-r from-white via-purple-200 to-purple-400 bg-clip-text text-transparent">
              TradeSignal.
            </Link>
            <h2 className="text-3xl lg:text-4xl font-bold leading-tight max-w-md text-white">
              Together, we turn your vision into reality.
            </h2>

            <form className="max-w-md relative mt-8">
              <div className={`relative flex items-center rounded-full transition-all duration-300 ${emailFocused ? 'shadow-[0_0_20px_rgba(139,92,246,0.25)]' : ''}`}>
                <div className={`absolute -inset-[1px] rounded-full bg-gradient-to-r from-purple-500/50 via-blue-500/50 to-purple-500/50 transition-opacity duration-300 ${emailFocused ? 'opacity-100' : 'opacity-0'}`} />
                <input
                  type="email"
                  placeholder="Your Email"
                  onFocus={() => setEmailFocused(true)}
                  onBlur={() => setEmailFocused(false)}
                  className="relative w-full bg-white/[0.06] backdrop-blur-sm border border-white/10 rounded-full py-4 pl-6 pr-32 text-white placeholder:text-gray-500 focus:outline-none transition-all duration-300 z-[1]"
                />
                <button
                  type="button"
                  className="absolute right-2 top-2 bottom-2 bg-gradient-to-r from-[#A78BFA] to-[#8B5CF6] hover:from-[#8B5CF6] hover:to-[#7C3AED] text-black font-semibold px-6 rounded-full transition-all duration-300 hover:scale-105 hover:shadow-[0_0_20px_rgba(139,92,246,0.4)] z-[2]"
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

        <div className="h-px my-12 bg-gradient-to-r from-transparent via-white/10 to-transparent" />

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
                className="bg-gradient-to-r from-purple-400 to-purple-300 bg-clip-text text-transparent hover:from-purple-300 hover:to-white transition-all duration-300"
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
    className="relative inline-block hover:text-white transition-colors duration-300 group"
  >
    {children}
    <span className="absolute left-0 -bottom-0.5 w-0 h-px bg-gradient-to-r from-purple-400 to-blue-400 transition-all duration-300 group-hover:w-full" />
  </Link>
);

const SocialIcon = ({ href, title, children }: { href: string; title: string; children: React.ReactNode }) => (
  <a
    href={href}
    target="_blank"
    rel="noopener noreferrer"
    className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center transition-all duration-300 hover:scale-110 hover:border-transparent hover:bg-gradient-to-br hover:from-purple-500/80 hover:to-blue-500/80 hover:text-white hover:shadow-[0_0_15px_rgba(139,92,246,0.3)]"
    title={title}
  >
    {children}
  </a>
);

export default GlobalFooter;
