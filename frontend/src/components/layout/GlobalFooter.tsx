import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Facebook, Instagram, Twitter, Linkedin, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';

const GlobalFooter = () => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  
  // Define public routes that should always show dark footer
  const publicRoutes = ['/', '/about', '/pricing', '/privacy', '/terms', '/faq', '/contact', '/careers'];
  const isPublicRoute = publicRoutes.includes(location.pathname);
  
  // Show light footer only if: authenticated AND on a protected route (not public route)
  // Show dark footer if: on public route OR not authenticated
  const shouldShowLightFooter = isAuthenticated && !isPublicRoute;
  
  // Light footer for logged-in users on protected pages (matches dashboard)
  const lightFooter = (
    <footer className="bg-gradient-to-br from-blue-50 via-white to-indigo-50 text-gray-900 pt-24 overflow-hidden relative font-sans">
       {/* Background Glow - Subtle accent */}
       <div className="absolute top-[-20%] right-[-10%] w-[50%] h-[50%] bg-purple-100/30 blur-[120px] rounded-full -z-10 opacity-50"></div>

      <div className="max-w-7xl mx-auto px-6 mb-20">
        <div className="grid lg:grid-cols-2 gap-16 lg:gap-32">
          
          {/* Left Column: Brand & Newsletter */}
          <div className="space-y-8">
            <Link to="/" className="text-3xl font-bold tracking-tight text-gray-900 block">
              TradeSignal.
            </Link>
            <h2 className="text-3xl lg:text-4xl font-bold leading-tight max-w-md text-gray-900">
              Together, we turn your vision into reality.
            </h2>
            
            {/* Newsletter Form */}
            <form className="max-w-md relative mt-8">
              <div className="relative flex items-center">
                <input 
                  type="email" 
                  placeholder="Your Email" 
                  className="w-full bg-white border border-gray-300 rounded-full py-4 pl-6 pr-32 text-gray-900 placeholder:text-gray-500 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-colors shadow-sm"
                />
                <button 
                  type="button"
                  className="absolute right-2 top-2 bottom-2 bg-[#6766FF] hover:bg-[#5A59E6] text-white font-semibold px-6 rounded-full transition-all hover:scale-105 shadow-md"
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
               <h4 className="font-bold text-gray-900 mb-6">Company</h4>
               <ul className="space-y-3 text-sm text-gray-600">
                 <li><Link to="/" className="hover:text-gray-900 transition-colors">Home</Link></li>
                 <li><Link to="/about" className="hover:text-gray-900 transition-colors">About</Link></li>
                 <li><Link to="/blog" className="hover:text-gray-900 transition-colors">Blog</Link></li>
                 <li><Link to="/work" className="hover:text-gray-900 transition-colors">Work</Link></li>
               </ul>
             </div>

             {/* Resources */}
             <div className="space-y-4">
               <h4 className="font-bold text-gray-900 mb-6">Resources</h4>
               <ul className="space-y-3 text-sm text-gray-600">
                 <li><Link to="/blog" className="hover:text-gray-900 transition-colors">Blog Details</Link></li>
                 <li><Link to="/work" className="hover:text-gray-900 transition-colors">Work Details</Link></li>
                 <li><Link to="/contact" className="hover:text-gray-900 transition-colors">Contact Us</Link></li>
                 {isAuthenticated && (
                   <li><Link to="/support" className="hover:text-gray-900 transition-colors">Help & Support</Link></li>
                 )}
               </ul>
             </div>

             {/* Utility Pages */}
             <div className="space-y-4">
               <h4 className="font-bold text-gray-900 mb-6">Utility Pages</h4>
               <ul className="space-y-3 text-sm text-gray-600">
                 <li><Link to="/privacy" className="hover:text-gray-900 transition-colors">Privacy Policy</Link></li>
                 <li><Link to="/terms" className="hover:text-gray-900 transition-colors">Terms of Service</Link></li>
               </ul>
             </div>
          </div>

        </div>

        {/* Divider */}
        <div className="h-px bg-gray-200 my-12"></div>

        {/* Bottom Bar */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-6 text-sm text-gray-600">
          <div className="flex items-center gap-4">
             <span>Copyrights © TradeSignal</span>
          </div>
          <div className="flex gap-4">
             <a href="#" className="w-10 h-10 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-100 hover:border-gray-400 text-gray-700 transition-all"><Facebook className="w-4 h-4" /></a>
             <a href="#" className="w-10 h-10 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-100 hover:border-gray-400 text-gray-700 transition-all"><Instagram className="w-4 h-4" /></a>
             <a href="#" className="w-10 h-10 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-100 hover:border-gray-400 text-gray-700 transition-all"><Twitter className="w-4 h-4" /></a>
             <a href="#" className="w-10 h-10 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-100 hover:border-gray-400 text-gray-700 transition-all"><Linkedin className="w-4 h-4" /></a>
          </div>
        </div>
      </div>
    </footer>
  );

  // Dark footer for public/visitor pages (matches landing page)
  const darkFooter = (
    <footer className="bg-[#0f0f1a] text-white pt-24 overflow-hidden relative font-sans">
       {/* Background Glow */}
       <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-[#1e1b4b] to-[#0f0f1a] -z-10"></div>
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
                 <li><Link to="/blog" className="hover:text-white transition-colors">Blog</Link></li>
                 <li><Link to="/work" className="hover:text-white transition-colors">Work</Link></li>
               </ul>
             </div>

             {/* Resources */}
             <div className="space-y-4">
               <h4 className="font-bold text-white mb-6">Resources</h4>
               <ul className="space-y-3 text-sm text-gray-400">
                 <li><Link to="/blog" className="hover:text-white transition-colors">Blog Details</Link></li>
                 <li><Link to="/work" className="hover:text-white transition-colors">Work Details</Link></li>
                 <li><Link to="/contact" className="hover:text-white transition-colors">Contact Us</Link></li>
                 {isAuthenticated && (
                   <li><Link to="/support" className="hover:text-white transition-colors">Help & Support</Link></li>
                 )}
               </ul>
             </div>

             {/* Utility Pages */}
             <div className="space-y-4">
               <h4 className="font-bold text-white mb-6">Utility Pages</h4>
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
          <div className="flex items-center gap-4">
             <span>Copyrights © TradeSignal</span>
          </div>
          <div className="flex gap-4">
             <a href="#" className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center hover:bg-white hover:text-black transition-all"><Facebook className="w-4 h-4" /></a>
             <a href="#" className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center hover:bg-white hover:text-black transition-all"><Instagram className="w-4 h-4" /></a>
             <a href="#" className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center hover:bg-white hover:text-black transition-all"><Twitter className="w-4 h-4" /></a>
             <a href="#" className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center hover:bg-white hover:text-black transition-all"><Linkedin className="w-4 h-4" /></a>
          </div>
        </div>
      </div>
    </footer>
  );

  // Return appropriate footer based on route and authentication status
  // Public routes always show dark footer, protected routes show light footer when authenticated
  return shouldShowLightFooter ? lightFooter : darkFooter;
};

export default GlobalFooter;
