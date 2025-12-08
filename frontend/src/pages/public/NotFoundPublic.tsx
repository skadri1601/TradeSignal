import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, AlertOctagon } from 'lucide-react';
import PublicNavbar from '../../components/public/PublicNavbar';

const NotFoundPublic = () => {
  return (
    <div className="min-h-screen bg-[#0a0a16] relative overflow-hidden font-sans selection:bg-purple-500/30">
      <PublicNavbar />
      
      {/* Background Gradients */}
      <div className="absolute inset-0 pointer-events-none">
         <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-purple-900/20 blur-[120px] rounded-full"></div>
         <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-900/20 blur-[120px] rounded-full"></div>
         
         {/* Grid Pattern (Subtle) */}
         <div className="absolute inset-0 opacity-[0.03]" 
              style={{ backgroundImage: 'linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)', backgroundSize: '50px 50px' }}>
         </div>
      </div>

      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen text-center px-4">
        
        {/* Floating Icon */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="mb-8 relative"
        >
          <div className="w-20 h-20 bg-gradient-to-tr from-pink-400 to-purple-400 rounded-2xl flex items-center justify-center shadow-[0_0_40px_rgba(168,85,247,0.4)] rotate-3">
            <AlertOctagon className="w-10 h-10 text-white" />
          </div>
          {/* Decorative glow behind */}
          <div className="absolute inset-0 bg-pink-500 blur-2xl opacity-40 -z-10"></div>
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-6xl md:text-7xl font-bold text-white mb-6 tracking-tight"
        >
          Page Not Found! <span className="inline-block animate-pulse">👀</span>
        </motion.h1>

        {/* Subtext */}
        <motion.p
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-gray-400 text-lg md:text-xl max-w-xl mb-10 leading-relaxed"
        >
          Maybe it's hiding in another dimension or someone trained the model wrong.
        </motion.p>

        {/* Button */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Link 
            to="/" 
            className="group relative inline-flex items-center gap-2 px-8 py-3.5 bg-[#8b5cf6] text-white rounded-full font-medium transition-all hover:bg-[#7c3aed] hover:shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:scale-105 active:scale-95"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            Back to Homepage
          </Link>
        </motion.div>

      </div>
    </div>
  );
};

export default NotFoundPublic;
