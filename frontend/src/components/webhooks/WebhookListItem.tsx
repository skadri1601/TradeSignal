import { useState } from 'react';
import { WebhookEndpoint } from '../../types';
import { Copy, Check, Edit2, Trash2, Send, Webhook as WebhookIcon, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export interface WebhookListItemProps {
  webhook: WebhookEndpoint;
  onEdit: () => void;
  onDelete: () => void;
  onTest: () => void;
}

export default function WebhookListItem({
  webhook,
  onEdit,
  onDelete,
  onTest,
}: WebhookListItemProps) {
  const [copied, setCopied] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const truncateUrl = (url: string, maxLength: number = 50) => {
    if (url.length <= maxLength) return url;
    return url.substring(0, maxLength) + '...';
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(webhook.url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getStatusIcon = () => {
    if (!webhook.last_delivery_status) return null;

    switch (webhook.last_delivery_status) {
      case 'success':
        return <CheckCircle2 className="w-4 h-4 text-green-400" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-400" />;
      case 'pending':
      case 'retrying':
        return <Clock className="w-4 h-4 text-yellow-400" />;
      default:
        return null;
    }
  };

  const getStatusColor = () => {
    if (!webhook.last_delivery_status) return 'text-gray-400';
    switch (webhook.last_delivery_status) {
      case 'success':
        return 'text-green-400';
      case 'failed':
        return 'text-red-400';
      case 'pending':
      case 'retrying':
        return 'text-yellow-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div
      className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-white/10 p-6 hover:border-purple-500/30 transition-all"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex items-start justify-between gap-4">
        {/* Main Content */}
        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <WebhookIcon className="w-5 h-5 text-purple-400" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-lg font-bold text-white truncate">{truncateUrl(webhook.url, 60)}</h3>
                <span
                  className={`px-2 py-0.5 text-xs rounded-full font-medium ${
                    webhook.is_active
                      ? 'bg-green-500/20 text-green-300 border border-green-500/30'
                      : 'bg-gray-500/20 text-gray-300 border border-gray-500/30'
                  }`}
                >
                  {webhook.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1 hover:text-purple-400 transition-colors"
                  title="Copy URL"
                >
                  {copied ? (
                    <>
                      <Check className="w-4 h-4 text-green-400" />
                      <span className="text-green-400">Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      <span>Copy URL</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Event Types */}
          <div className="mb-3">
            <p className="text-xs text-gray-400 uppercase font-bold mb-2">Event Types</p>
            <div className="flex items-center gap-2 flex-wrap">
              {webhook.event_types.length > 0 ? (
                webhook.event_types.map((eventType) => (
                  <span
                    key={eventType}
                    className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded-md text-xs font-medium border border-purple-500/30"
                  >
                    {eventType.replace('_', ' ')}
                  </span>
                ))
              ) : (
                <span className="text-xs text-gray-500">No events selected</span>
              )}
            </div>
          </div>

          {/* Status and Success Rate */}
          <div className="grid grid-cols-2 gap-4">
            {/* Last Delivery Status */}
            <div>
              <p className="text-xs text-gray-400 uppercase font-bold mb-1">Last Delivery</p>
              <div className="flex items-center gap-2">
                {getStatusIcon()}
                <span className={`text-sm font-medium ${getStatusColor()}`}>
                  {webhook.last_delivery_status
                    ? webhook.last_delivery_status.charAt(0).toUpperCase() + webhook.last_delivery_status.slice(1)
                    : 'Never'}
                </span>
              </div>
              {webhook.last_delivery_at && (
                <p className="text-xs text-gray-500 mt-1">
                  {formatDistanceToNow(new Date(webhook.last_delivery_at), { addSuffix: true })}
                </p>
              )}
            </div>

            {/* Success Rate */}
            <div>
              <p className="text-xs text-gray-400 uppercase font-bold mb-1">Success Rate</p>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-gray-700 h-2 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all ${
                      (webhook.success_rate || 0) >= 90
                        ? 'bg-green-500'
                        : (webhook.success_rate || 0) >= 70
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                    }`}
                    style={{ width: `${webhook.success_rate || 0}%` }}
                  />
                </div>
                <span className="text-sm font-medium text-white min-w-[3rem] text-right">
                  {webhook.success_rate?.toFixed(1) || '0.0'}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div
          className={`flex items-center gap-2 transition-opacity ${
            isHovered ? 'opacity-100' : 'opacity-0 md:opacity-100'
          }`}
        >
          <button
            onClick={onTest}
            disabled={!webhook.is_active}
            className="p-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Test webhook"
            aria-label="Test webhook"
          >
            <Send className="w-4 h-4" />
          </button>
          <button
            onClick={onEdit}
            className="p-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
            title="Edit webhook"
            aria-label="Edit webhook"
          >
            <Edit2 className="w-4 h-4" />
          </button>
          <button
            onClick={onDelete}
            className="p-2 bg-red-600 text-white rounded-lg hover:bg-red-500 transition-colors"
            title="Delete webhook"
            aria-label="Delete webhook"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

