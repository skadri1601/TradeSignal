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
        <p className="text-red-600">Error loading order history</p>
      </div>
    );
  }

  const orders: Order[] = data?.items || [];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'succeeded':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'refunded':
        return <RefreshCw className="h-5 w-5 text-orange-600" />;
      default:
        return <Clock className="h-5 w-5 text-yellow-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'succeeded':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'refunded':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Order History</h1>
        <p className="mt-2 text-gray-600">
          View all your payment transactions and subscription orders
        </p>
      </div>

      {orders.length === 0 ? (
        <div className="card text-center py-12">
          <Receipt className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No orders found</p>
          <p className="text-sm text-gray-500 mt-2">
            Your payment history will appear here once you make a purchase
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <div key={order.id} className="card">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    {getStatusIcon(order.status)}
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {order.payment_type === 'subscription' && 'Subscription'}
                        {order.payment_type === 'upgrade' && 'Upgrade'}
                        {order.payment_type === 'renewal' && 'Renewal'}
                        {order.payment_type === 'one_time' && 'One-time Payment'}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {order.tier_before
                          ? `Upgraded from ${order.tier_before} to ${order.tier}`
                          : `${order.tier.charAt(0).toUpperCase() + order.tier.slice(1)} Tier`}
                      </p>
                    </div>
                  </div>

                  <div className="mt-3 space-y-1">
                    <div className="flex items-center space-x-2 text-sm">
                      <span className="text-gray-600">Amount:</span>
                      <span className="font-semibold text-gray-900">
                        ${order.amount.toFixed(2)} {order.currency}
                      </span>
                    </div>
                    {order.period_start && order.period_end && (
                      <div className="flex items-center space-x-2 text-sm">
                        <span className="text-gray-600">Period:</span>
                        <span className="text-gray-900">
                          {new Date(order.period_start).toLocaleDateString()} -{' '}
                          {new Date(order.period_end).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                    <div className="flex items-center space-x-2 text-sm">
                      <span className="text-gray-600">Date:</span>
                      <span className="text-gray-900">
                        {new Date(order.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                    </div>
                    {order.refunded_amount && (
                      <div className="flex items-center space-x-2 text-sm">
                        <span className="text-orange-600">Refunded:</span>
                        <span className="font-semibold text-orange-600">
                          ${order.refunded_amount.toFixed(2)}
                        </span>
                        {order.refunded_at && (
                          <span className="text-gray-500">
                            on {new Date(order.refunded_at).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                <div className="ml-4 flex flex-col items-end space-y-2">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(
                      order.status
                    )}`}
                  >
                    {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                  </span>
                  <div className="flex space-x-2">
                    {order.receipt_url && (
                      <a
                        href={order.receipt_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-gray-600 hover:text-blue-600 transition-colors"
                        title="View Receipt"
                      >
                        <Receipt className="h-5 w-5" />
                      </a>
                    )}
                    {order.invoice_url && (
                      <a
                        href={order.invoice_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-gray-600 hover:text-blue-600 transition-colors"
                        title="View Invoice"
                      >
                        <Download className="h-5 w-5" />
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

