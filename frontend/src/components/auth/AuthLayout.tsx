import { useState, useEffect, ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface AuthLayoutProps {
  title: string;
  subtitle: string;
  features: string[];
  children: ReactNode;
}

function AuthFormSkeleton() {
  return (
    <div className="w-full space-y-4">
      <div className="h-8 rounded w-1/2 bg-gradient-to-r from-white/10 via-white/20 to-white/10 bg-[length:200%_100%] animate-[shimmer_1.5s_infinite]"></div>
      <div className="h-4 rounded w-3/4 bg-gradient-to-r from-white/5 via-white/15 to-white/5 bg-[length:200%_100%] animate-[shimmer_1.5s_infinite_0.2s]"></div>
      <div className="space-y-3 mt-6">
        <div className="h-10 rounded bg-gradient-to-r from-white/10 via-white/20 to-white/10 bg-[length:200%_100%] animate-[shimmer_1.5s_infinite_0.4s]"></div>
        <div className="h-10 rounded bg-gradient-to-r from-white/10 via-white/20 to-white/10 bg-[length:200%_100%] animate-[shimmer_1.5s_infinite_0.6s]"></div>
        <div className="h-10 rounded bg-gradient-to-r from-purple-600/20 via-purple-500/40 to-purple-600/20 bg-[length:200%_100%] animate-[shimmer_1.5s_infinite_0.8s]"></div>
      </div>
      <div className="h-4 rounded w-1/2 mx-auto mt-4 bg-gradient-to-r from-white/5 via-white/15 to-white/5 bg-[length:200%_100%] animate-[shimmer_1.5s_infinite_1s]"></div>
    </div>
  );
}

const orbVariants = {
  animate: (i: number) => ({
    x: [0, 30, -20, 10, 0],
    y: [0, -20, 30, -10, 0],
    scale: [1, 1.1, 0.95, 1.05, 1],
    transition: {
      duration: 8 + i * 2,
      repeat: Infinity,
      ease: 'easeInOut' as const,
    },
  }),
};

const featureCardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: 0.3 + i * 0.12,
      duration: 0.5,
      ease: 'easeOut' as const,
    },
  }),
};

const floatVariants = {
  animate: (i: number) => ({
    y: [0, -6, 0],
    transition: {
      duration: 3 + i * 0.5,
      repeat: Infinity,
      ease: 'easeInOut' as const,
    },
  }),
};

export default function AuthLayout({ title, subtitle, features, children }: AuthLayoutProps) {
  const [clerkLoaded, setClerkLoaded] = useState(false);

  useEffect(() => {
    const observer = new MutationObserver(() => {
      if (document.querySelector('.cl-rootBox')) {
        setClerkLoaded(true);
        observer.disconnect();
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    return () => observer.disconnect();
  }, []);

  return (
    <div className="min-h-screen flex">
      <style>{`
        @keyframes shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
        @keyframes gradient-line {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
      `}</style>

      <div className="hidden lg:flex lg:w-1/2 bg-[#0a0a14] p-12 flex-col justify-between relative overflow-hidden">
        <div className="absolute inset-0">
          <motion.div
            custom={0}
            variants={orbVariants}
            animate="animate"
            className="absolute top-[-10%] left-[-5%] w-[500px] h-[500px] rounded-full"
            style={{ background: 'radial-gradient(circle, rgba(139,92,246,0.3) 0%, transparent 70%)' }}
          />
          <motion.div
            custom={1}
            variants={orbVariants}
            animate="animate"
            className="absolute bottom-[-15%] right-[-10%] w-[600px] h-[600px] rounded-full"
            style={{ background: 'radial-gradient(circle, rgba(59,130,246,0.25) 0%, transparent 70%)' }}
          />
          <motion.div
            custom={2}
            variants={orbVariants}
            animate="animate"
            className="absolute top-[40%] left-[30%] w-[400px] h-[400px] rounded-full"
            style={{ background: 'radial-gradient(circle, rgba(99,102,241,0.2) 0%, transparent 70%)' }}
          />
          <motion.div
            custom={3}
            variants={orbVariants}
            animate="animate"
            className="absolute bottom-[20%] left-[-5%] w-[350px] h-[350px] rounded-full"
            style={{ background: 'radial-gradient(circle, rgba(168,85,247,0.15) 0%, transparent 70%)' }}
          />
        </div>

        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.8) 1px, transparent 1px)',
            backgroundSize: '24px 24px',
          }}
        />

        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="relative z-10"
        >
          <div className="flex items-center space-x-3">
            <div className="bg-white/5 backdrop-blur-md border border-white/10 p-3 rounded-xl">
              <TrendingUp className="w-8 h-8 text-purple-400" />
            </div>
            <span className="text-white text-2xl font-bold">TradeSignal</span>
          </div>
        </motion.div>

        <div className="relative z-10 space-y-6">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-5xl font-bold leading-tight"
          >
            {title.split('\n').map((line, i) => (
              <span
                key={i}
                className="bg-gradient-to-r from-white via-purple-200 to-blue-200 bg-clip-text text-transparent"
              >
                {line}{i < title.split('\n').length - 1 && <br />}
              </span>
            ))}
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-lg text-white/60"
          >
            {subtitle}
          </motion.p>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.25 }}
            className="h-px my-6 bg-gradient-to-r from-transparent via-purple-500/40 to-transparent bg-[length:200%_100%]"
            style={{ animation: 'gradient-line 3s ease infinite' }}
          />

          <div className="space-y-3 mt-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                custom={index}
                variants={featureCardVariants}
                initial="hidden"
                animate="visible"
              >
                <motion.div
                  custom={index}
                  variants={floatVariants}
                  animate="animate"
                  className="flex items-center space-x-3 bg-white/[0.04] backdrop-blur-md border border-white/[0.08] rounded-xl px-4 py-3 hover:bg-white/[0.07] hover:border-white/[0.12] transition-all duration-300"
                >
                  <div className="flex-shrink-0 bg-gradient-to-br from-purple-500/30 to-blue-500/30 backdrop-blur-sm rounded-lg p-1.5 border border-white/10">
                    <svg className="w-3.5 h-3.5 text-purple-300" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <span className="text-white/80 text-sm font-medium">{feature}</span>
                </motion.div>
              </motion.div>
            ))}
          </div>
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="relative z-10"
        >
          <p className="text-white/30 text-sm">&copy; 2025 TradeSignal. Built for portfolio demonstration.</p>
        </motion.div>
      </div>

      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-[#0f0f1a] relative overflow-hidden">
        <div
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: 'radial-gradient(circle, rgba(139,92,246,0.8) 1px, transparent 1px)',
            backgroundSize: '32px 32px',
          }}
        />

        <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-purple-500/20 to-transparent lg:hidden" />

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="max-w-md w-full space-y-8 relative z-10"
        >
          <div className="lg:hidden flex justify-center">
            <div className="flex items-center space-x-2">
              <div className="bg-gradient-to-br from-purple-600 to-blue-600 p-2 rounded-lg">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold text-white">TradeSignal</span>
            </div>
          </div>

          <AnimatePresence mode="wait">
            {!clerkLoaded && (
              <motion.div
                key="skeleton"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                transition={{ duration: 0.3 }}
              >
                <AuthFormSkeleton />
              </motion.div>
            )}
          </AnimatePresence>

          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={clerkLoaded ? { opacity: 1, y: 0 } : { opacity: 0, y: 8 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className={clerkLoaded ? '' : 'sr-only'}
          >
            {children}
          </motion.div>

          <div className="text-center">
            <Link
              to="/"
              className="group inline-flex items-center text-sm font-semibold text-purple-400 hover:text-purple-300 transition-colors duration-200"
            >
              <span className="inline-block transition-transform duration-200 group-hover:-translate-x-1">&larr;</span>
              <span className="ml-1">Back to home</span>
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
