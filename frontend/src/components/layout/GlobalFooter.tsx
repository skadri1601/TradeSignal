import { Link } from 'react-router-dom';
import { Twitter, Linkedin, Github, Globe } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const GlobalFooter = () => {
  const { isAuthenticated } = useAuth();
  
  // Dark footer for all pages (matches landing page style)
  return (
    <footer className="bg-black text-white pt-24 overflow-hidden relative font-sans">
       {/* Background Glow */}
       <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-[#1e1b4b] to-black -z-10"></div>
       <div className="absolute top-[-20%] right-[-10%] w-[50%] h-[50%] bg-purple-900/20 blur-[120px] rounded-full -z-10"></div>

      <div className="max-w-7xl mx-auto px-6 mb-20">
        <div className="grid lg:grid-cols-2 gap-16 lg:gap-32">
          
          {/* Left Column: Brand & Newsletter */}
          <div className="space-y-8">
            <Link to="/" className="text-3xl font-bold tracking-tight text-white block">
              TradeSignal.
            </Link>
            <h2 className="text-3xl lg:text-4xl font-bold leading-tight max-w-md text-white">
              Together, we turn your vision into reality.
            </h2>
            
            {/* Newsletter Form */}
            <form className="max-w-md relative mt-8">
              <div className="relative flex items-center">
                <input 
                  type="email" 
                  placeholder="Your Email" 
                  className="w-full bg-white/5 border border-white/10 rounded-full py-4 pl-6 pr-32 text-white placeholder:text-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                />
                <button 
                  type="button"
                  className="absolute right-2 top-2 bottom-2 bg-[#A78BFA] hover:bg-[#8B5CF6] text-black font-semibold px-6 rounded-full transition-all hover:scale-105"
                >
                  Submit
                </button>
              </div>
            </form>
          </div>

          {/* Right Column: Links */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
             {/* Company */}
             <div className="space-y-4">
               <h4 className="font-bold text-white mb-6">Company</h4>
               <ul className="space-y-3 text-sm text-gray-400">
                 <li><Link to="/" className="hover:text-white transition-colors">Home</Link></li>
                 <li><Link to="/about" className="hover:text-white transition-colors">About</Link></li>
                 {/* PORTFOLIO MODE: Removed Use Cases, Testimonials, Careers (business pages) */}
                 <li><Link to="/blog" className="hover:text-white transition-colors">Blog</Link></li>
               </ul>
             </div>

             {/* Resources */}
             <div className="space-y-4">
               <h4 className="font-bold text-white mb-6">Resources</h4>
               <ul className="space-y-3 text-sm text-gray-400">
                 <li><Link to="/docs" className="hover:text-white transition-colors">Documentation</Link></li>
                 <li><Link to="/api-docs" className="hover:text-white transition-colors">API Docs</Link></li>
                 <li><Link to="/public/news" className="hover:text-white transition-colors">News</Link></li>
                 <li><Link to="/public/support" className="hover:text-white transition-colors">Help Center</Link></li>
                 <li><Link to="/roadmap" className="hover:text-white transition-colors">Roadmap</Link></li>
                 <li><Link to="/contact" className="hover:text-white transition-colors">Contact Us</Link></li>
                 <li><Link to="/faq" className="hover:text-white transition-colors">FAQ</Link></li>
                 {isAuthenticated && (
                   <>
                     <li><Link to="/settings" className="hover:text-white transition-colors">Settings</Link></li>
                     <li><Link to="/support" className="hover:text-white transition-colors">Support</Link></li>
                   </>
                 )}
               </ul>
             </div>

             {/* Features */}
             <div className="space-y-4">
               <h4 className="font-bold text-white mb-6">Features</h4>
               <ul className="space-y-3 text-sm text-gray-400">
                 <li><Link to="/features/insider-trades" className="hover:text-white transition-colors">Insider Trades</Link></li>
                 <li><Link to="/features/congress-trading" className="hover:text-white transition-colors">Congressional Trading</Link></li>
                 <li><Link to="/features/ai-insights" className="hover:text-white transition-colors">AI Insights</Link></li>
                 <li><Link to="/features/alerts" className="hover:text-white transition-colors">Alerts</Link></li>
                 {/* PORTFOLIO MODE: Removed Pricing link */}
               </ul>
             </div>

             {/* Legal */}
             <div className="space-y-4">
               <h4 className="font-bold text-white mb-6">Legal</h4>
               <ul className="space-y-3 text-sm text-gray-400">
                 <li><Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
                 <li><Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link></li>
               </ul>
             </div>
          </div>

        </div>

        {/* Divider */}
        <div className="h-px bg-white/10 my-12"></div>

        {/* Bottom Bar */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-6 text-sm text-gray-500">
          <div className="flex flex-col md:flex-row items-center gap-2 md:gap-4">
             <span>Copyrights © TradeSignal</span>
             <span className="hidden md:inline">•</span>
             <span>
               Built by{' '}
               <a
                 href="https://saadkadri.dev/"
                 target="_blank"
                 rel="noopener noreferrer"
                 className="text-purple-400 hover:text-purple-300 transition-colors"
               >
                 Saad Kadri
               </a>
             </span>
          </div>
          <div className="flex gap-4">
             <a href="https://saadkadri.dev/" target="_blank" rel="noopener noreferrer" className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center hover:bg-white hover:text-black transition-all" title="Portfolio"><Globe className="w-4 h-4" /></a>
             <a href="https://github.com/skadri1601" target="_blank" rel="noopener noreferrer" className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center hover:bg-white hover:text-black transition-all" title="GitHub"><Github className="w-4 h-4" /></a>
             <a href="https://www.linkedin.com/in/saad-kadri-58b8bb205/" target="_blank" rel="noopener noreferrer" className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center hover:bg-white hover:text-black transition-all" title="LinkedIn"><Linkedin className="w-4 h-4" /></a>
             <a href="#" className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center hover:bg-white hover:text-black transition-all"><Twitter className="w-4 h-4" /></a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default GlobalFooter;
