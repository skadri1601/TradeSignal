import { Link } from 'react-router-dom';
import { XCircle } from 'lucide-react';

export default function BillingCancelPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full text-center bg-white p-8 rounded-lg shadow-lg">
        <div className="flex justify-center mb-6">
          <XCircle className="h-16 w-16 text-gray-400" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Payment Cancelled
        </h1>
        <p className="text-gray-600 mb-8">
          No charges were made. You can try again anytime when you're ready to upgrade.
        </p>
        <Link 
          to="/pricing" 
          className="block w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          Back to Pricing
        </Link>
      </div>
    </div>
  );
}
