import { useQuery } from '@tanstack/react-query';
import apiClient from '../api/client';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { Receipt, Download, CheckCircle, XCircle, Clock, RefreshCw } from 'lucide-react';

interface Order {
  id: number;
  amount: number;
  currency: string;
  payment_type: string;
  status: string;
  tier: string;
  tier_before?: string;
  description?: string;
  receipt_url?: string;
  invoice_url?: string;
  refunded_amount?: number;
  refunded_at?: string;
  period_start?: string;
  period_end?: string;
  created_at: string;
}

export default function OrderHistoryPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['order-history'],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/billing/orders/', {
        params: { limit: 100 }
      });
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400">Error loading order history</p>
      </div>
    );
  }

  const orders: Order[] = data?.items || [];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'succeeded':
        return <CheckCircle className="h-5 w-5 text-green-400" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-400" />;
      case 'refunded':
        return <RefreshCw className="h-5 w-5 text-orange-400" />;
      default:
        return <Clock className="h-5 w-5 text-yellow-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'succeeded':
        return 'bg-green-500/20 text-green-300 border border-green-500/30';
      case 'failed':
        return 'bg-red-500/20 text-red-300 border border-red-500/30';
      case 'refunded':
        return 'bg-orange-500/20 text-orange-300 border border-orange-500/30';
      default:
        return 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30';
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Order History</h1>
        <p className="mt-2 text-gray-400">
          View all your payment transactions and subscription orders
        </p>
      </div>

      {orders.length === 0 ? (
        <div className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-12 text-center">
          <div className="bg-white/5 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 border border-white/5">
             <Receipt className="h-8 w-8 text-gray-500" />
          </div>
          <p className="text-gray-300 text-lg font-medium">No orders found</p>
          <p className="text-sm text-gray-500 mt-2">
            Your payment history will appear here once you make a purchase
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <div key={order.id} className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-all shadow-lg">
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3">
                    {getStatusIcon(order.status)}
                    <div>
                      <h3 className="font-bold text-white text-lg">
                        {order.payment_type === 'subscription' && 'Subscription'}
                        {order.payment_type === 'upgrade' && 'Upgrade'}
                        {order.payment_type === 'renewal' && 'Renewal'}
                        {order.payment_type === 'one_time' && 'One-time Payment'}
                      </h3>
                      <p className="text-sm text-gray-400">
                        {order.tier_before
                          ? `Upgraded from ${order.tier_before} to ${order.tier}`
                          : `${order.tier.charAt(0).toUpperCase() + order.tier.slice(1)} Tier`}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-2 mt-4 text-sm">
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-500">Amount:</span>
                      <span className="font-mono font-medium text-white">
                        ${order.amount.toFixed(2)} {order.currency.toUpperCase()}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-500">Date:</span>
                      <span className="text-gray-300">
                        {new Date(order.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                        })}
                      </span>
                    </div>

                    {order.period_start && order.period_end && (
                      <div className="flex items-center space-x-2 col-span-1 sm:col-span-2">
                        <span className="text-gray-500">Period:</span>
                        <span className="text-gray-300">
                          {new Date(order.period_start).toLocaleDateString()} -{' '}
                          {new Date(order.period_end).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                    
                    {order.refunded_amount && (
                      <div className="flex items-center space-x-2 text-sm col-span-1 sm:col-span-2 bg-orange-500/10 p-2 rounded-lg border border-orange-500/20 mt-2">
                        <span className="text-orange-400">Refunded:</span>
                        <span className="font-semibold text-orange-300">
                          ${order.refunded_amount.toFixed(2)}
                        </span>
                        {order.refunded_at && (
                          <span className="text-orange-400/70 ml-1">
                            on {new Date(order.refunded_at).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex flex-row md:flex-col items-center md:items-end justify-between gap-4">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${getStatusColor(
                      order.status
                    )}`}
                  >
                    {order.status}
                  </span>
                  <div className="flex space-x-3">
                    {order.receipt_url && (
                      <a
                        href={order.receipt_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white transition-colors text-sm border border-white/5"
                        title="View Receipt"
                      >
                        <Receipt className="h-4 w-4" /> Receipt
                      </a>
                    )}
                    {order.invoice_url && (
                      <a
                        href={order.invoice_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white transition-colors text-sm border border-white/5"
                        title="View Invoice"
                      >
                        <Download className="h-4 w-4" /> Invoice
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}