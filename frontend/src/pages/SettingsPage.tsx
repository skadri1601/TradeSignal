/**
 * Settings Page
 *
 * Comprehensive settings page with tabs for:
 * - Profile: User account settings
 * - Webhooks: Webhook endpoint management
 * - API Keys: API key lifecycle management
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Settings as SettingsIcon,
  Webhook as WebhookIcon,
  Key as KeyIcon,
  User as UserIcon,
  Plus,
  Copy,
  Check,
  Trash2,
  TestTube,
  CheckCircle2,
  XCircle,
  Clock,
  Eye,
  EyeOff,
} from 'lucide-react';
import { webhooksApi, type Webhook, type CreateWebhookRequest } from '../api/webhooks';
import { apiKeysApi, type APIKey, type CreateAPIKeyRequest } from '../api/apiKeys';
import { toast } from 'react-hot-toast';

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<'profile' | 'webhooks' | 'apiKeys'>('profile');

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <SettingsIcon className="w-8 h-8" />
            Settings
          </h1>
          <p className="mt-2 text-gray-400">
            Manage your account, webhooks, and API keys
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-white/10 mb-8">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('profile')}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 transition-colors
                ${
                  activeTab === 'profile'
                    ? 'border-purple-500 text-purple-400'
                    : 'border-transparent text-gray-400 hover:text-white hover:border-white/20'
                }
              `}
            >
              <UserIcon className="w-5 h-5" />
              Profile
            </button>
            <button
              onClick={() => setActiveTab('webhooks')}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 transition-colors
                ${
                  activeTab === 'webhooks'
                    ? 'border-purple-500 text-purple-400'
                    : 'border-transparent text-gray-400 hover:text-white hover:border-white/20'
                }
              `}
            >
              <WebhookIcon className="w-5 h-5" />
              Webhooks
            </button>
            <button
              onClick={() => setActiveTab('apiKeys')}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 transition-colors
                ${
                  activeTab === 'apiKeys'
                    ? 'border-purple-500 text-purple-400'
                    : 'border-transparent text-gray-400 hover:text-white hover:border-white/20'
                }
              `}
            >
              <KeyIcon className="w-5 h-5" />
              API Keys
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'profile' && <ProfileTab />}
        {activeTab === 'webhooks' && <WebhooksTab />}
        {activeTab === 'apiKeys' && <APIKeysTab />}
      </div>
    </div>
  );
}

// ============================================================================
// PROFILE TAB
// ============================================================================

function ProfileTab() {
  return (
    <div className="bg-white/5 border border-white/10 rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-semibold text-white mb-4">
        Account Settings
      </h2>
      <p className="text-gray-400">
        Profile management coming soon. For now, use the user menu to manage your account.
      </p>
    </div>
  );
}

// ============================================================================
// WEBHOOKS TAB
// ============================================================================

function WebhooksTab() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedWebhook, setSelectedWebhook] = useState<Webhook | null>(null);

  const queryClient = useQueryClient();

  // Fetch webhooks
  const { data: webhooks = [], isLoading } = useQuery({
    queryKey: ['webhooks'],
    queryFn: webhooksApi.getWebhooks,
  });

  // Test webhook mutation
  const testMutation = useMutation({
    mutationFn: (webhookId: number) => webhooksApi.testWebhook(webhookId),
    onSuccess: () => {
      toast.success('Test webhook sent successfully!');
    },
    onError: () => {
      toast.error('Failed to send test webhook');
    },
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-semibold text-white">
            Webhooks
          </h2>
          <p className="mt-1 text-sm text-gray-400">
            Receive real-time notifications for events in your account
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Webhook
        </button>
      </div>

      {/* Webhook List */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
        </div>
      ) : (() => {
        if (webhooks.length === 0) {
          return (
            <div className="bg-white/5 border border-white/10 rounded-lg p-12 text-center">
              <WebhookIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white mb-2">
                No webhooks configured
              </h3>
              <p className="text-gray-400 mb-6">
                Get started by creating your first webhook endpoint
              </p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Create Webhook
              </button>
            </div>
          );
        }
        return (
        <div className="space-y-4">
          {webhooks.map((webhook) => (
            <WebhookListItem
              key={webhook.id}
              webhook={webhook}
              onTest={() => testMutation.mutate(webhook.id)}
              onViewDeliveries={() => setSelectedWebhook(webhook)}
            />
          ))}
        </div>
        );
      })()}

      {/* Create Modal */}
      {showCreateModal && (
        <CreateWebhookModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            queryClient.invalidateQueries({ queryKey: ['webhooks'] });
          }}
        />
      )}

      {/* Delivery History Modal */}
      {selectedWebhook && (
        <WebhookDeliveryHistory
          webhook={selectedWebhook}
          onClose={() => setSelectedWebhook(null)}
        />
      )}
    </div>
  );
}

function WebhookListItem({
  webhook,
  onTest,
  onViewDeliveries,
}: {
  readonly webhook: Webhook;
  readonly onTest: () => void;
  readonly onViewDeliveries: () => void;
}) {
  const [copied, setCopied] = useState(false);

  const copyUrl = () => {
    navigator.clipboard.writeText(webhook.url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-medium text-white">
              {webhook.url}
            </h3>
            {webhook.is_active ? (
              <span className="px-2 py-1 text-xs font-medium bg-green-500/20 text-green-400 rounded">
                Active
              </span>
            ) : (
              <span className="px-2 py-1 text-xs font-medium bg-gray-500/20 text-gray-400 rounded">
                Inactive
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <span>Events:</span>
            {webhook.event_types.map((event) => (
              <span
                key={event}
                className="px-2 py-0.5 bg-blue-500/20 text-blue-300 rounded text-xs"
              >
                {event}
              </span>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={copyUrl}
            className="p-2 text-gray-400 hover:text-white"
            title="Copy URL"
          >
            {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
          </button>
          <button
            onClick={onTest}
            className="p-2 text-gray-400 hover:text-white"
            title="Send test event"
          >
            <TestTube className="w-4 h-4" />
          </button>
          <button
            onClick={onViewDeliveries}
            className="px-3 py-1 text-sm bg-white/10 text-gray-300 rounded hover:bg-white/20 transition-colors"
          >
            View Deliveries
          </button>
        </div>
      </div>
    </div>
  );
}

function CreateWebhookModal({
  onClose,
  onSuccess,
}: {
  readonly onClose: () => void;
  readonly onSuccess: () => void;
}) {
  const [formData, setFormData] = useState<CreateWebhookRequest>({
    url: '',
    event_types: ['trade_alert'],
    secret: '',
  });

  const createMutation = useMutation({
    mutationFn: webhooksApi.createWebhook,
    onSuccess,
    onError: () => {
      toast.error('Failed to create webhook');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  const eventTypes = ['trade_alert', 'conversion', 'subscription_updated', 'user_signed_up', 'custom'];

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-[#1a1a1a] border border-white/10 rounded-lg shadow-xl max-w-md w-full p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Create Webhook
        </h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="webhook-url" className="block text-sm font-medium text-gray-400 mb-1">
              Endpoint URL
            </label>
            <input
              id="webhook-url"
              type="url"
              value={formData.url}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              className="w-full px-3 py-2 border border-white/10 rounded-lg bg-black/40 text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="https://your-domain.com/webhook"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Event Types
            </label>
            <div className="space-y-2">
              {eventTypes.map((event) => (
                <label key={event} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.event_types?.includes(event)}
                    onChange={(e) => {
                      const types = formData.event_types || [];
                      setFormData({
                        ...formData,
                        event_types: e.target.checked
                          ? [...types, event]
                          : types.filter((t) => t !== event),
                      });
                    }}
                    className="mr-2 rounded border-white/20 bg-black/40 text-purple-600 focus:ring-purple-500"
                  />
                  <span className="text-sm text-gray-300">{event}</span>
                </label>
              ))}
            </div>
          </div>
          <div>
            <label htmlFor="webhook-secret" className="block text-sm font-medium text-gray-400 mb-1">
              Secret (Optional)
            </label>
            <input
              id="webhook-secret"
              type="password"
              value={formData.secret}
              onChange={(e) => setFormData({ ...formData, secret: e.target.value })}
              className="w-full px-3 py-2 border border-white/10 rounded-lg bg-black/40 text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="For HMAC signature verification"
            />
          </div>
          <div className="flex gap-3 justify-end mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
            >
              {createMutation.isPending ? 'Creating...' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function WebhookDeliveryHistory({ webhook, onClose }: { readonly webhook: Webhook; readonly onClose: () => void }) {
  const { data: deliveries = [] } = useQuery({
    queryKey: ['webhook-deliveries', webhook.id],
    queryFn: () => webhooksApi.getDeliveries(webhook.id, { limit: 50 }),
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'delivered':
        return <CheckCircle2 className="w-5 h-5 text-green-400" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-400" />;
      default:
        return <Clock className="w-5 h-5 text-yellow-400" />;
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-[#1a1a1a] border border-white/10 rounded-lg shadow-xl max-w-3xl w-full max-h-[80vh] overflow-hidden">
        <div className="p-6 border-b border-white/10">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-white">
              Delivery History
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white"
            >
              ✕
            </button>
          </div>
          <p className="text-sm text-gray-400 mt-1">{webhook.url}</p>
        </div>
        <div className="overflow-y-auto max-h-[calc(80vh-120px)] p-6">
          {deliveries.length === 0 ? (
            <p className="text-center text-gray-500 py-8">
              No deliveries yet
            </p>
          ) : (
            <div className="space-y-3">
              {deliveries.map((delivery) => (
                <div
                  key={delivery.id}
                  className="flex items-center justify-between p-4 bg-white/5 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    {getStatusIcon(delivery.status)}
                    <div>
                      <div className="font-medium text-white">
                        {delivery.event_type}
                      </div>
                      <div className="text-sm text-gray-400">
                        {new Date(delivery.created_at).toLocaleString()}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    {delivery.response_code && (
                      <div className="text-sm font-medium text-white">
                        HTTP {delivery.response_code}
                      </div>
                    )}
                    <div className="text-sm text-gray-400">
                      {delivery.attempts} attempt{delivery.attempts === 1 ? '' : 's'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// API KEYS TAB
// ============================================================================

function APIKeysTab() {
  const [showCreateModal, setShowCreateModal] = useState(false);

  const queryClient = useQueryClient();

  // Fetch API keys
  const { data: apiKeys = [], isLoading } = useQuery({
    queryKey: ['api-keys'],
    queryFn: apiKeysApi.getKeys,
  });

  // Revoke key mutation
  const revokeMutation = useMutation({
    mutationFn: (keyId: number) => apiKeysApi.revokeKey(keyId),
    onSuccess: () => {
      toast.success('API key revoked');
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
    },
    onError: () => {
      toast.error('Failed to revoke API key');
    },
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-semibold text-white">
            API Keys
          </h2>
          <p className="mt-1 text-sm text-gray-400">
            Manage API keys for programmatic access
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Generate Key
        </button>
      </div>

      {/* API Keys List */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
        </div>
      ) : (() => {
        if (apiKeys.length === 0) {
          return (
            <div className="bg-white/5 border border-white/10 rounded-lg p-12 text-center">
              <KeyIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white mb-2">
                No API keys
              </h3>
              <p className="text-gray-400 mb-6">
                Generate your first API key to access the TradeSignal API
              </p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Generate API Key
              </button>
            </div>
          );
        }
        return (
        <div className="space-y-4">
          {apiKeys.map((apiKey) => (
            <APIKeyListItem
              key={apiKey.id}
              apiKey={apiKey}
              onRevoke={() => revokeMutation.mutate(apiKey.id)}
            />
          ))}
        </div>
        );
      })()}

      {/* Create Modal */}
      {showCreateModal && (
        <CreateAPIKeyModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            queryClient.invalidateQueries({ queryKey: ['api-keys'] });
          }}
        />
      )}
    </div>
  );
}

function APIKeyListItem({
  apiKey,
  onRevoke,
}: {
  readonly apiKey: APIKey;
  readonly onRevoke: () => void;
}) {
  const [showUsage, setShowUsage] = useState(false);

  const { data: usage } = useQuery({
    queryKey: ['api-key-usage', apiKey.id],
    queryFn: () => apiKeysApi.getUsage(apiKey.id, 30),
    enabled: showUsage,
  });

  const permissions = [];
  if (apiKey.can_read) permissions.push('Read');
  if (apiKey.can_write) permissions.push('Write');
  if (apiKey.can_delete) permissions.push('Delete');

  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-colors">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-medium text-white">
              {apiKey.name}
            </h3>
            {apiKey.is_active ? (
              <span className="px-2 py-1 text-xs font-medium bg-green-500/20 text-green-400 rounded">
                Active
              </span>
            ) : (
              <span className="px-2 py-1 text-xs font-medium bg-red-500/20 text-red-400 rounded">
                Revoked
              </span>
            )}
          </div>
          {apiKey.description && (
            <p className="text-sm text-gray-400 mb-2">
              {apiKey.description}
            </p>
          )}
          <div className="flex items-center gap-4 text-sm text-gray-400">
            <span className="font-mono bg-white/10 px-2 py-1 rounded text-gray-300">
              {apiKey.key_prefix}***
            </span>
            <span>Permissions: {permissions.join(', ')}</span>
            <span>Rate Limit: {apiKey.rate_limit_per_hour}/hour</span>
          </div>
          {apiKey.last_used_at && (
            <div className="text-sm text-gray-500 mt-1">
              Last used: {new Date(apiKey.last_used_at).toLocaleString()}
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowUsage(!showUsage)}
            className="p-2 text-gray-400 hover:text-white"
            title="View usage"
          >
            {showUsage ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
          {apiKey.is_active && (
            <button
              onClick={onRevoke}
              className="p-2 text-red-400 hover:text-red-300 transition-colors"
              title="Revoke key"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Usage Stats */}
      {showUsage && usage && (
        <div className="border-t border-white/10 pt-4 grid grid-cols-4 gap-4">
          <div>
            <div className="text-sm text-gray-400">Total Requests</div>
            <div className="text-2xl font-bold text-white">
              {usage.total_requests.toLocaleString()}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Successful</div>
            <div className="text-2xl font-bold text-green-400">
              {usage.successful_requests.toLocaleString()}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Failed</div>
            <div className="text-2xl font-bold text-red-400">
              {usage.failed_requests.toLocaleString()}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Avg Response Time</div>
            <div className="text-2xl font-bold text-blue-400">
              {Math.round(usage.avg_response_time_ms)}ms
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function CreateAPIKeyModal({
  onClose,
  onSuccess,
}: {
  readonly onClose: () => void;
  readonly onSuccess: () => void;
}) {
  const [formData, setFormData] = useState<CreateAPIKeyRequest>({
    name: '',
    description: '',
    rate_limit_per_hour: 1000,
    permissions: {
      read: true,
      write: false,
      delete: false,
    },
    expires_in_days: 365,
  });
  const [createdKey, setCreatedKey] = useState<string | null>(null);

  const createMutation = useMutation({
    mutationFn: apiKeysApi.createKey,
    onSuccess: (data) => {
      setCreatedKey(data.key);
      toast.success('API key created successfully!');
    },
    onError: () => {
      toast.error('Failed to create API key');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  const copyKey = () => {
    if (createdKey) {
      navigator.clipboard.writeText(createdKey);
      toast.success('API key copied to clipboard');
    }
  };

  // Show success screen with the API key
  if (createdKey) {
    return (
      <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 backdrop-blur-sm">
        <div className="bg-[#1a1a1a] border border-white/10 rounded-lg shadow-xl max-w-md w-full p-6">
          <div className="text-center mb-6">
            <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-white mb-2">
              API Key Created
            </h3>
            <p className="text-sm text-red-400 font-medium">
              ⚠️ Save this key now - you won't be able to see it again!
            </p>
          </div>
          <div className="bg-white/5 rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between gap-2">
              <code className="text-sm font-mono text-white break-all flex-1">
                {createdKey}
              </code>
              <button
                onClick={copyKey}
                className="p-2 text-blue-400 hover:text-blue-300 flex-shrink-0"
              >
                <Copy className="w-5 h-5" />
              </button>
            </div>
          </div>
          <button
            onClick={() => {
              setCreatedKey(null);
              onSuccess();
            }}
            className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-[#1a1a1a] border border-white/10 rounded-lg shadow-xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
        <h3 className="text-lg font-semibold text-white mb-4">
          Generate API Key
        </h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="api-key-name" className="block text-sm font-medium text-gray-400 mb-1">
              Name *
            </label>
            <input
              id="api-key-name"
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-white/10 rounded-lg bg-black/40 text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="My API Key"
              required
            />
          </div>
          <div>
            <label htmlFor="api-key-description" className="block text-sm font-medium text-gray-400 mb-1">
              Description
            </label>
            <textarea
              id="api-key-description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-white/10 rounded-lg bg-black/40 text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Used for production API calls"
              rows={2}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Permissions
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.permissions?.read}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      permissions: { ...formData.permissions, read: e.target.checked },
                    })
                  }
                  className="mr-2 rounded border-white/20 bg-black/40 text-purple-600 focus:ring-purple-500"
                />
                <span className="text-sm text-gray-300">Read</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.permissions?.write}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      permissions: { ...formData.permissions, write: e.target.checked },
                    })
                  }
                  className="mr-2 rounded border-white/20 bg-black/40 text-purple-600 focus:ring-purple-500"
                />
                <span className="text-sm text-gray-300">Write</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.permissions?.delete}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      permissions: { ...formData.permissions, delete: e.target.checked },
                    })
                  }
                  className="mr-2 rounded border-white/20 bg-black/40 text-purple-600 focus:ring-purple-500"
                />
                <span className="text-sm text-gray-300">Delete</span>
              </label>
            </div>
          </div>
          <div>
            <label htmlFor="api-key-rate-limit" className="block text-sm font-medium text-gray-400 mb-1">
              Rate Limit (requests/hour)
            </label>
            <input
              id="api-key-rate-limit"
              type="number"
              value={formData.rate_limit_per_hour}
              onChange={(e) =>
                setFormData({ ...formData, rate_limit_per_hour: Number.parseInt(e.target.value, 10) })
              }
              className="w-full px-3 py-2 border border-white/10 rounded-lg bg-black/40 text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              min="1"
              max="10000"
            />
          </div>
          <div>
            <label htmlFor="api-key-expires" className="block text-sm font-medium text-gray-400 mb-1">
              Expires In (days)
            </label>
            <select
              id="api-key-expires"
              value={formData.expires_in_days}
              onChange={(e) =>
                setFormData({ ...formData, expires_in_days: Number.parseInt(e.target.value, 10) })
              }
              className="w-full px-3 py-2 border border-white/10 rounded-lg bg-black/40 text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value={30} className="bg-gray-900">30 days</option>
              <option value={90} className="bg-gray-900">90 days</option>
              <option value={180} className="bg-gray-900">6 months</option>
              <option value={365} className="bg-gray-900">1 year</option>
            </select>
          </div>
          <div className="flex gap-3 justify-end mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
            >
              {createMutation.isPending ? 'Generating...' : 'Generate Key'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}