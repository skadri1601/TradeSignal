import { APIKey } from '../../types';
import { formatDate, formatRelativeTime } from '../../utils/formatters';
import { Copy, Check, Edit2, AlertTriangle, Key } from 'lucide-react';
import { useState } from 'react';
import { useCustomConfirm } from '../../hooks/useCustomConfirm';
import CustomConfirm from '../common/CustomConfirm';

export interface APIKeyListItemProps {
  apiKey: APIKey;
  onRevoke: () => void;
  onEdit: () => void;
}

export default function APIKeyListItem({
  apiKey,
  onRevoke,
  onEdit,
}: APIKeyListItemProps) {
  const [copied, setCopied] = useState(false);
  const { confirmState, showConfirm, hideConfirm } = useCustomConfirm();

  const handleCopy = () => {
    navigator.clipboard.writeText(apiKey.key_prefix);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isExpired = apiKey.expires_at ? new Date(apiKey.expires_at) < new Date() : false;
  const isExpiringSoon =
    apiKey.expires_at &&
    !isExpired &&
    new Date(apiKey.expires_at).getTime() - Date.now() < 7 * 24 * 60 * 60 * 1000; // 7 days

  const handleRevoke = () => {
    showConfirm(
      'Are you sure you want to revoke this API key? This action cannot be undone.',
      () => {
        onRevoke();
      },
      {
        type: 'warning',
        title: 'Revoke API Key',
        confirmText: 'Revoke',
        cancelText: 'Cancel',
      }
    );
  };

  return (
    <>
      <div
        className={`bg-gray-900/50 backdrop-blur-sm rounded-xl border border-white/10 p-6 ${
          isExpired ? 'opacity-60' : ''
        }`}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <Key className="w-5 h-5 text-purple-400" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-bold text-white truncate">{apiKey.name}</h3>
                {apiKey.description && (
                  <p className="text-sm text-gray-400 mt-1">{apiKey.description}</p>
                )}
              </div>
            </div>

            {/* Key Prefix */}
            <div className="flex items-center gap-2 mb-3">
              <code className="px-3 py-1.5 bg-black/50 border border-white/10 rounded-lg text-purple-300 font-mono text-sm">
                {apiKey.key_prefix}...
              </code>
              <button
                onClick={handleCopy}
                className="p-1.5 text-gray-400 hover:text-purple-400 transition-colors"
                title="Copy key prefix"
                aria-label="Copy key prefix"
              >
                {copied ? (
                  <Check className="w-4 h-4 text-green-400" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </button>
            </div>

            {/* Status Badges */}
            <div className="flex items-center gap-2 flex-wrap">
              {!apiKey.is_active && (
                <span className="px-2 py-0.5 text-xs rounded-full font-medium bg-red-500/20 text-red-300 border border-red-500/30">
                  Revoked
                </span>
              )}
              {isExpired && (
                <span className="px-2 py-0.5 text-xs rounded-full font-medium bg-gray-500/20 text-gray-300 border border-gray-500/30">
                  Expired
                </span>
              )}
              {isExpiringSoon && !isExpired && (
                <span className="px-2 py-0.5 text-xs rounded-full font-medium bg-yellow-500/20 text-yellow-300 border border-yellow-500/30 flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" />
                  Expiring Soon
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div>
            <p className="text-xs text-gray-400 uppercase font-bold mb-1">Created</p>
            <p className="text-sm text-white">{formatDate(apiKey.created_at)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400 uppercase font-bold mb-1">Last Used</p>
            <p className="text-sm text-white">
              {apiKey.last_used_at ? formatRelativeTime(apiKey.last_used_at) : 'Never'}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-400 uppercase font-bold mb-1">Expires</p>
            <p className="text-sm text-white">
              {apiKey.expires_at ? formatDate(apiKey.expires_at) : 'Never'}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-400 uppercase font-bold mb-1">Usage</p>
            <p className="text-sm text-white">{apiKey.usage_count.toLocaleString()} requests</p>
          </div>
        </div>

        {/* Permissions */}
        <div className="mb-4">
          <p className="text-xs text-gray-400 uppercase font-bold mb-2">Permissions</p>
          <div className="flex items-center gap-2 flex-wrap">
            {apiKey.permissions.map((perm) => (
              <span
                key={perm}
                className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded-md text-xs font-medium border border-purple-500/30"
              >
                {perm}
              </span>
            ))}
          </div>
        </div>

        {/* Rate Limit */}
        <div className="mb-4 p-3 bg-black/20 rounded-lg border border-white/5">
          <p className="text-xs text-gray-400 uppercase font-bold mb-1">Rate Limit</p>
          <p className="text-sm text-white">{apiKey.rate_limit.toLocaleString()} requests/hour</p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3 pt-4 border-t border-white/10">
          <button
            onClick={onEdit}
            className="flex-1 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors flex items-center justify-center gap-2 font-medium"
          >
            <Edit2 className="w-4 h-4" />
            Edit
          </button>
          <button
            onClick={handleRevoke}
            disabled={!apiKey.is_active}
            className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            Revoke
          </button>
        </div>
      </div>

      {/* Confirmation Modal */}
      <CustomConfirm
        show={confirmState.show}
        message={confirmState.message}
        title={confirmState.title || 'TradeSignal'}
        type={confirmState.type}
        confirmText={confirmState.confirmText}
        cancelText={confirmState.cancelText}
        onConfirm={confirmState.onConfirm || (() => {})}
        onCancel={hideConfirm}
      />
    </>
  );
}

