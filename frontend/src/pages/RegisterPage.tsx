import { SignUp } from '@clerk/clerk-react';
import { Link } from 'react-router-dom';
import { TrendingUp, Check } from 'lucide-react';

export default function RegisterPage() {
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
            Join TradeSignal.<br />
            Start Trading Smarter.
          </h1>
          <p className="text-xl text-blue-100">
            Get access to real-time insider trading data and AI-powered insights
          </p>

          <div className="space-y-4 mt-8">
            {[
              'Free tier with essential features',
              'Real-time SEC filing notifications',
              'Advanced analytics & AI insights',
              'Upgrade anytime to unlock more'
            ].map((benefit, index) => (
              <div key={index} className="flex items-center space-x-3">
                <div className="bg-white/20 backdrop-blur-sm rounded-full p-1">
                  <Check className="w-4 h-4 text-white" />
                </div>
                <span className="text-blue-50">{benefit}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10">
          <p className="text-blue-200 text-sm">
            © 2025 TradeSignal. Built for portfolio demonstration.
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

          <SignUp
            routing="path"
            path="/register"
            signInUrl="/login"
            fallbackRedirectUrl="/dashboard"
            appearance={{
              elements: {
                rootBox: 'w-full',
                card: 'shadow-none bg-transparent w-full',
              },
            }}
          />

          <div className="text-center">
            <Link to="/" className="text-sm font-semibold text-purple-400 hover:text-purple-300">
              ← Back to home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
