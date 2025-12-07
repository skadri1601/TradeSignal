import { Link } from 'react-router-dom';
import { CheckCircle } from 'lucide-react';

export default function BillingSuccessPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full text-center bg-white p-8 rounded-lg shadow-lg">
        <div className="flex justify-center mb-6">
          <CheckCircle className="h-16 w-16 text-green-500" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Payment Successful! 🎉
        </h1>
        <p className="text-gray-600 mb-8">
          Your subscription has been activated. Thank you for supporting TradeSignal!
          You now have access to all premium features.
        </p>
        <div className="space-y-4">
          <Link 
            to="/dashboard" 
            className="block w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Go to Dashboard
          </Link>
          <Link 
            to="/profile" 
            className="block w-full bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
          >
            View Subscription
          </Link>
        </div>
      </div>
    </div>
  );
}