import { Link } from 'react-router-dom';
import { CheckCircle2, ArrowRight, User } from 'lucide-react';

export default function BillingSuccessPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0a0a0a] px-4 relative overflow-hidden">
      {/* Background Gradients */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-[128px] pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-[128px] pointer-events-none" />

      <div className="max-w-md w-full text-center bg-gray-900/50 backdrop-blur-xl border border-white/10 p-8 rounded-2xl shadow-2xl relative z-10">
        <div className="flex justify-center mb-6">
          <div className="bg-green-500/20 p-4 rounded-full ring-1 ring-green-500/50 shadow-[0_0_20px_rgba(34,197,94,0.3)]">
            <CheckCircle2 className="h-16 w-16 text-green-400" />
          </div>
        </div>
        
        <h1 className="text-3xl font-bold text-white mb-4 tracking-tight">
          Payment Successful!
        </h1>
        
        <p className="text-gray-400 mb-8 text-lg leading-relaxed">
          Your subscription has been activated. <br/>
          <span className="text-white font-medium">Welcome to the inner circle.</span>
        </p>

        <div className="space-y-4">
          <Link 
            to="/" 
            className="group flex items-center justify-center w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white px-6 py-3.5 rounded-xl font-semibold transition-all hover:scale-[1.02] shadow-lg shadow-purple-500/25"
          >
            Go to Dashboard
            <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
          </Link>
          
          <Link 
            to="/profile" 
            className="flex items-center justify-center w-full bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white border border-white/10 hover:border-white/20 px-6 py-3.5 rounded-xl font-medium transition-colors"
          >
            <User className="w-5 h-5 mr-2" />
            View Subscription
          </Link>
        </div>

        <p className="mt-8 text-xs text-gray-500">
          A receipt has been sent to your email address.
        </p>
      </div>
    </div>
  );
}
