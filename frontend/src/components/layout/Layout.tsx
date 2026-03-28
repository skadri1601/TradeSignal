import { ReactNode } from 'react';
import { motion } from 'framer-motion';
import DashboardNavbar from './DashboardNavbar';
import GlobalFooter from './GlobalFooter';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-[#050510] text-white selection:bg-purple-500/30 font-sans relative overflow-x-hidden">
      <div className="fixed inset-0 pointer-events-none" aria-hidden="true">
        <div
          className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] rounded-full opacity-[0.07]"
          style={{
            background: 'radial-gradient(circle, #7c3aed 0%, transparent 70%)',
            filter: 'blur(80px)',
          }}
        />
        <div
          className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full opacity-[0.05]"
          style={{
            background: 'radial-gradient(circle, #3b82f6 0%, transparent 70%)',
            filter: 'blur(80px)',
          }}
        />
        <div
          className="absolute top-[40%] right-[20%] w-[30%] h-[30%] rounded-full opacity-[0.04]"
          style={{
            background: 'radial-gradient(circle, #6366f1 0%, transparent 70%)',
            filter: 'blur(60px)',
          }}
        />
      </div>

      <div className="relative z-10">
        <DashboardNavbar />
        <div className="flex flex-col min-h-screen pt-24">
          <motion.main
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
            className="flex-grow px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full"
          >
            {children}
          </motion.main>
          <GlobalFooter />
        </div>
      </div>
    </div>
  );
}
