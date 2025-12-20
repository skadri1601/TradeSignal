import { useState, useEffect, useRef } from 'react';
import { WebhookDelivery } from '../../types';
import { formatDateTime } from '../../utils/formatters';
import { RefreshCw, Eye, RotateCw, CheckCircle2, XCircle, Clock, AlertCircle } from 'lucide-react';

export interface WebhookDeliveryHistoryProps {
  deliveries: WebhookDelivery[];
  webhookId: number;
  onRetry?: (deliveryId: number) => void;
  onRefresh?: () => void;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export default function WebhookDeliveryHistory({
  deliveries,
  onRetry,
  onRefresh,
  autoRefresh = true,
  refreshInterval = 30000,
}: WebhookDeliveryHistoryProps) {
  const [expandedRow, setExpandedRow] = useState<number | null>(null);
  const [statusFilter, setStatusFilter] = useState<WebhookDelivery['status'] | 'all'>('all');
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Auto-refresh
  useEffect(() => {
    if (autoRefresh && onRefresh) {
      intervalRef.current = setInterval(() => {
        onRefresh();
      }, refreshInterval);

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    }
  }, [autoRefresh, onRefresh, refreshInterval]);

  // Auto-scroll to newest
  const newestRef = useRef<HTMLTableRowElement>(null);
  useEffect(() => {
    if (deliveries.length > 0 && newestRef.current) {
      newestRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [deliveries.length]);

  const filteredDeliveries = deliveries.filter(
    (d) => statusFilter === 'all' || d.status === statusFilter
  );

  const getStatusBadge = (status: WebhookDelivery['status']) => {
    const badges = {
      pending: {
        icon: Clock,
        className: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
        label: 'Pending',
      },
      success: {
        icon: CheckCircle2,
        className: 'bg-green-500/20 text-green-300 border-green-500/30',
        label: 'Success',
      },
      failed: {
        icon: XCircle,
        className: 'bg-red-500/20 text-red-300 border-red-500/30',
        label: 'Failed',
      },
      retrying: {
        icon: RotateCw,
        className: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
        label: 'Retrying',
      },
    };

    const badge = badges[status];
    const Icon = badge.icon;

    return (
      <span
        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${badge.className}`}
      >
        <Icon className="w-3 h-3" />
        {badge.label}
      </span>
    );
  };

  const formatDuration = (createdAt: string, deliveredAt: string | null): string => {
    if (!deliveredAt) return 'N/A';
    const duration = new Date(deliveredAt).getTime() - new Date(createdAt).getTime();
    if (duration < 1000) return `${duration}ms`;
    return `${(duration / 1000).toFixed(2)}s`;
  };

  return (
    <div className="space-y-4">
      {/* Header with Filters */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-white">Delivery History</h3>
        <div className="flex items-center gap-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as WebhookDelivery['status'] | 'all')}
            className="px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="success">Success</option>
            <option value="failed">Failed</option>
            <option value="retrying">Retrying</option>
          </select>
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="p-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
              title="Refresh"
              aria-label="Refresh"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Event</th>
              <th>Status</th>
              <th>Response Code</th>
              <th>Duration</th>
              <th>Attempts</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredDeliveries.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-8 text-gray-500">
                  No deliveries found
                </td>
              </tr>
            ) : (
              filteredDeliveries.map((delivery, index) => (
                <>
                  <tr
                    key={delivery.id}
                    ref={index === 0 ? newestRef : null}
                    className="cursor-pointer hover:bg-white/5 transition-colors"
                    onClick={() => setExpandedRow(expandedRow === delivery.id ? null : delivery.id)}
                  >
                    <td className="text-gray-400">{formatDateTime(delivery.created_at)}</td>
                    <td className="text-white font-medium">
                      {delivery.event_type.replace('_', ' ')}
                    </td>
                    <td>{getStatusBadge(delivery.status)}</td>
                    <td className="text-gray-300 font-mono">
                      {delivery.response_code || 'N/A'}
                    </td>
                    <td className="text-gray-300">
                      {formatDuration(delivery.created_at, delivery.delivered_at)}
                    </td>
                    <td className="text-gray-300">{delivery.attempts}</td>
                    <td>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setExpandedRow(expandedRow === delivery.id ? null : delivery.id);
                          }}
                          className="p-1 text-purple-400 hover:text-purple-300 transition-colors"
                          title="View payload"
                          aria-label="View payload"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        {delivery.status === 'failed' && onRetry && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onRetry(delivery.id);
                            }}
                            className="p-1 text-blue-400 hover:text-blue-300 transition-colors"
                            title="Retry delivery"
                            aria-label="Retry delivery"
                          >
                            <RotateCw className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                  {/* Expanded Row */}
                  {expandedRow === delivery.id && (
                    <tr>
                      <td colSpan={7} className="bg-black/30 p-4">
                        <div className="space-y-3">
                          {/* Payload */}
                          <div>
                            <h4 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
                              <AlertCircle className="w-4 h-4" />
                              Payload
                            </h4>
                            <pre className="bg-black/50 p-4 rounded-lg overflow-x-auto text-xs text-gray-300 font-mono border border-white/10">
                              {JSON.stringify(delivery.payload, null, 2)}
                            </pre>
                          </div>

                          {/* Response Body */}
                          {delivery.response_body && (
                            <div>
                              <h4 className="text-sm font-semibold text-white mb-2">Response Body</h4>
                              <pre className="bg-black/50 p-4 rounded-lg overflow-x-auto text-xs text-gray-300 font-mono border border-white/10">
                                {delivery.response_body}
                              </pre>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

