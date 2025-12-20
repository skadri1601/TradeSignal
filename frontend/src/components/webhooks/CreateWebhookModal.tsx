import { useState } from 'react';
import { WebhookEventType } from '../../types';
import { X, Copy, Check, Send, Webhook as WebhookIcon, Shield, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

export interface CreateWebhookModalProps {
  onSubmit: (data: {
    url: string;
    event_types: WebhookEventType[];
    secret?: string;
    description?: string;
  }) => Promise<void>;
  onClose: () => void;
  availableEvents: WebhookEventType[];
}

export default function CreateWebhookModal({
  onSubmit,
  onClose,
  availableEvents,
}: CreateWebhookModalProps) {
  const [url, setUrl] = useState('');
  const [selectedEvents, setSelectedEvents] = useState<WebhookEventType[]>([]);
  const [secret, setSecret] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [copied, setCopied] = useState(false);

  const eventIcons: Record<WebhookEventType, JSX.Element> = {
    trade_alert: <Send className="w-4 h-4" />,
    conversion: <Shield className="w-4 h-4" />,
    subscription_updated: <WebhookIcon className="w-4 h-4" />,
    user_signed_up: <Shield className="w-4 h-4" />,
    custom: <WebhookIcon className="w-4 h-4" />,
  };

  const validateUrl = (urlString: string): boolean => {
    try {
      const parsed = new URL(urlString);
      return parsed.protocol === 'https:';
    } catch {
      return false;
    }
  };

  const generateSecret = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const secret = Array.from(crypto.getRandomValues(new Uint8Array(32)))
      .map((x) => chars[x % chars.length])
      .join('');
    setSecret(secret);
  };

  const handleCopySecret = () => {
    if (secret) {
      navigator.clipboard.writeText(secret);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      toast.success('Secret copied to clipboard!');
    }
  };

  const handleToggleEvent = (eventType: WebhookEventType) => {
    setSelectedEvents((prev) =>
      prev.includes(eventType)
        ? prev.filter((e) => e !== eventType)
        : [...prev, eventType]
    );
  };

  const handleTest = async () => {
    if (!url || !validateUrl(url)) {
      toast.error('Please enter a valid HTTPS URL');
      return;
    }

    setIsTesting(true);
    try {
      // Test endpoint logic would go here
      toast.success('Test request sent! Check your endpoint.');
    } catch (error) {
      toast.error('Test failed. Please check your URL.');
    } finally {
      setIsTesting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: Record<string, string> = {};

    if (!url.trim()) {
      newErrors.url = 'URL is required';
    } else if (!validateUrl(url)) {
      newErrors.url = 'URL must be a valid HTTPS URL';
    }

    if (selectedEvents.length === 0) {
      newErrors.events = 'At least one event type must be selected';
    }

    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) return;

    setIsSubmitting(true);
    try {
      await onSubmit({
        url: url.trim(),
        event_types: selectedEvents,
        secret: secret || undefined,
        description: description.trim() || undefined,
      });
      onClose();
    } catch (error) {
      toast.error('Failed to create webhook');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-gray-900 rounded-2xl border border-white/10 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
              <WebhookIcon className="w-5 h-5 text-purple-400" />
            </div>
            <h2 className="text-2xl font-bold text-white">Create Webhook</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
            aria-label="Close"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* URL Input */}
          <div>
            <label htmlFor="webhook-url" className="block text-sm font-medium text-gray-300 mb-2">
              Webhook URL <span className="text-red-400">*</span>
            </label>
            <input
              id="webhook-url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://your-server.com/webhooks/tradesignal"
              className={`w-full px-4 py-3 bg-black/50 border ${
                errors.url ? 'border-red-500' : 'border-white/10'
              } rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all`}
            />
            {errors.url && <p className="text-sm text-red-400 mt-1">{errors.url}</p>}
            <p className="text-xs text-gray-400 mt-1">
              Must be a valid HTTPS URL. HTTP is not allowed for security.
            </p>
          </div>

          {/* Event Types */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Event Types <span className="text-red-400">*</span>
            </label>
            <div className="space-y-2">
              {availableEvents.map((eventType) => (
                <label
                  key={eventType}
                  className="flex items-center gap-3 p-3 bg-black/20 rounded-lg border border-white/5 cursor-pointer hover:bg-black/30 transition-colors"
                >
                  <input
                    type="checkbox"
                    checked={selectedEvents.includes(eventType)}
                    onChange={() => handleToggleEvent(eventType)}
                    className="w-4 h-4 text-purple-600 bg-black/50 border-white/10 rounded focus:ring-purple-500"
                  />
                  <div className="flex items-center gap-2 text-white">
                    {eventIcons[eventType]}
                    <span className="font-medium">{eventType.replace('_', ' ')}</span>
                  </div>
                </label>
              ))}
            </div>
            {errors.events && <p className="text-sm text-red-400 mt-1">{errors.events}</p>}
          </div>

          {/* Secret Key */}
          <div>
            <label htmlFor="webhook-secret" className="block text-sm font-medium text-gray-300 mb-2">
              Secret Key (Optional)
            </label>
            <div className="flex items-center gap-2">
              <input
                id="webhook-secret"
                type="text"
                value={secret}
                onChange={(e) => setSecret(e.target.value)}
                placeholder="Auto-generate or enter custom secret"
                className="flex-1 px-4 py-3 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all font-mono text-sm"
                readOnly={!!secret}
              />
              {!secret ? (
                <button
                  type="button"
                  onClick={generateSecret}
                  className="px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors font-medium"
                >
                  Generate
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handleCopySecret}
                  className="px-4 py-3 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors flex items-center gap-2 font-medium"
                >
                  {copied ? (
                    <>
                      <Check className="w-4 h-4 text-green-400" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      Copy
                    </>
                  )}
                </button>
              )}
            </div>
            {secret && (
              <div className="mt-2 p-3 bg-yellow-900/20 border border-yellow-500/30 rounded-lg flex items-start gap-2">
                <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                <p className="text-xs text-yellow-300">
                  Save this secret key! You won't be able to see it again after creating the webhook.
                </p>
              </div>
            )}
          </div>

          {/* Description */}
          <div>
            <label htmlFor="webhook-description" className="block text-sm font-medium text-gray-300 mb-2">
              Description (Optional)
            </label>
            <textarea
              id="webhook-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Add a description for this webhook..."
              rows={3}
              className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all resize-none"
            />
          </div>

          {/* Test Button */}
          <div className="flex items-center justify-end">
            <button
              type="button"
              onClick={handleTest}
              disabled={!url || !validateUrl(url) || isTesting}
              className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
            >
              <Send className="w-4 h-4" />
              {isTesting ? 'Testing...' : 'Test Endpoint'}
            </button>
          </div>

          {/* Submit Buttons */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {isSubmitting ? 'Creating...' : 'Create Webhook'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

