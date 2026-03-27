import { useState, useEffect, ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp } from 'lucide-react';

interface AuthLayoutProps {
  title: string;
  subtitle: string;
  features: string[];
  children: ReactNode;
}

function AuthFormSkeleton() {
  return (
    <div className="w-full space-y-4 animate-pulse">
      <div className="h-8 bg-white/10 rounded w-1/2"></div>
      <div className="h-4 bg-white/5 rounded w-3/4"></div>
      <div className="space-y-3 mt-6">
        <div className="h-10 bg-white/10 rounded"></div>
        <div className="h-10 bg-white/10 rounded"></div>
        <div className="h-10 bg-purple-600/30 rounded"></div>
      </div>
      <div className="h-4 bg-white/5 rounded w-1/2 mx-auto mt-4"></div>
    </div>
  );
}

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
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 p-12 flex-col justify-between relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-96 h-96 bg-white rounded-full -translate-x-1/2 -translate-y-1/2"></div>
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-white rounded-full translate-x-1/2 translate-y-1/2"></div>
        </div>

        <div className="relative z-10">
          <div className="flex items-center space-x-3">
            <div className="bg-white/10 backdrop-blur-sm p-3 rounded-xl">
              <TrendingUp className="w-8 h-8 text-white" />
            </div>
            <span className="text-white text-2xl font-bold">TradeSignal</span>
          </div>
        </div>

        <div className="relative z-10 space-y-6">
          <h1 className="text-5xl font-bold text-white leading-tight">
            {title.split('\n').map((line, i) => (
              <span key={i}>{line}{i < title.split('\n').length - 1 && <br />}</span>
            ))}
          </h1>
          <p className="text-xl text-blue-100">
            {subtitle}
          </p>

          <div className="space-y-4 mt-8">
            {features.map((feature, index) => (
              <div key={index} className="flex items-center space-x-3">
                <div className="bg-white/20 backdrop-blur-sm rounded-full p-1">
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <span className="text-blue-50">{feature}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10">
          <p className="text-blue-200 text-sm">
            &copy; 2025 TradeSignal. Built for portfolio demonstration.
          </p>
        </div>
      </div>

      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-[#0f0f1a]">
        <div className="max-w-md w-full space-y-8">
          <div className="lg:hidden flex justify-center">
            <div className="flex items-center space-x-2">
              <div className="bg-purple-600 p-2 rounded-lg">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold text-white">TradeSignal</span>
            </div>
          </div>

          {!clerkLoaded && <AuthFormSkeleton />}
          <div className={clerkLoaded ? '' : 'sr-only'}>
            {children}
          </div>

          <div className="text-center">
            <Link to="/" className="text-sm font-semibold text-purple-400 hover:text-purple-300">
              &larr; Back to home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
