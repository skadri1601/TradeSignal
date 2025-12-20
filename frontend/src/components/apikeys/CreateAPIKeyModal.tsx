import { useState } from 'react';
import { X, Copy, Check, Key, AlertTriangle, Shield } from 'lucide-react';
import toast from 'react-hot-toast';

export interface CreateAPIKeyModalProps {
  onSubmit: (data: {
    name: string;
    description?: string;
    expires_at?: string;
    rate_limit: number;
    permissions: ('read' | 'write' | 'delete')[];
  }) => Promise<{ key: string }>;
  onClose: () => void;
}

export default function CreateAPIKeyModal({ onSubmit, onClose }: CreateAPIKeyModalProps) {
  const [step, setStep] = useState<'form' | 'reveal'>('form');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [expiresAt, setExpiresAt] = useState('');
  const [rateLimit, setRateLimit] = useState(1000);
  const [permissions, setPermissions] = useState<('read' | 'write' | 'delete')[]>(['read']);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [copied, setCopied] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleTogglePermission = (perm: 'read' | 'write' | 'delete') => {
    setPermissions((prev) =>
      prev.includes(perm) ? prev.filter((p) => p !== perm) : [...prev, perm]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: Record<string, string> = {};

    if (!name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (permissions.length === 0) {
      newErrors.permissions = 'At least one permission must be selected';
    }

    if (rateLimit <= 0) {
      newErrors.rate_limit = 'Rate limit must be greater than 0';
    }

    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) return;

    setIsSubmitting(true);
    try {
      const result = await onSubmit({
        name: name.trim(),
        description: description.trim() || undefined,
        expires_at: expiresAt || undefined,
        rate_limit: rateLimit,
        permissions,
      });
      setApiKey(result.key);
      setStep('reveal');
    } catch (error) {
      toast.error('Failed to create API key');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(apiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    toast.success('API key copied to clipboard!');
  };

  const handleClose = () => {
    if (step === 'reveal') {
      toast.success('API key saved! Make sure to store it securely.');
    }
    onClose();
  };

  if (step === 'reveal') {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
        <div className="bg-gray-900 rounded-2xl border border-white/10 w-full max-w-2xl">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                <Check className="w-5 h-5 text-green-400" />
              </div>
              <h2 className="text-2xl font-bold text-white">API Key Created</h2>
            </div>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-white transition-colors"
              aria-label="Close"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Key Display */}
          <div className="p-6 space-y-4">
            <div className="p-4 bg-yellow-900/20 border border-yellow-500/30 rounded-lg flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-yellow-300 mb-1">
                  Save this key - you won't see it again!
                </p>
                <p className="text-xs text-yellow-400/80">
                  Copy and store this API key in a secure location. It cannot be recovered if lost.
                </p>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Your API Key</label>
              <div className="flex items-center gap-2">
                <code className="flex-1 px-4 py-4 bg-black/50 border border-white/10 rounded-lg text-purple-300 font-mono text-sm break-all">
                  {apiKey}
                </code>
                <button
                  onClick={handleCopy}
                  className="px-4 py-4 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors flex items-center gap-2 font-medium flex-shrink-0"
                >
                  {copied ? (
                    <>
                      <Check className="w-5 h-5 text-green-400" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-5 h-5" />
                      Copy
                    </>
                  )}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-end pt-4 border-t border-white/10">
              <button
                onClick={handleClose}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors font-medium"
              >
                I've Saved My Key
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-gray-900 rounded-2xl border border-white/10 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
              <Key className="w-5 h-5 text-purple-400" />
            </div>
            <h2 className="text-2xl font-bold text-white">Create API Key</h2>
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
          {/* Name */}
          <div>
            <label htmlFor="key-name" className="block text-sm font-medium text-gray-300 mb-2">
              Name <span className="text-red-400">*</span>
            </label>
            <input
              id="key-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Production API Key"
              className={`w-full px-4 py-3 bg-black/50 border ${
                errors.name ? 'border-red-500' : 'border-white/10'
              } rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all`}
            />
            {errors.name && <p className="text-sm text-red-400 mt-1">{errors.name}</p>}
          </div>

          {/* Description */}
          <div>
            <label htmlFor="key-description" className="block text-sm font-medium text-gray-300 mb-2">
              Description (Optional)
            </label>
            <textarea
              id="key-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Add a description for this API key..."
              rows={3}
              className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all resize-none"
            />
          </div>

          {/* Expiration Date */}
          <div>
            <label htmlFor="key-expires" className="block text-sm font-medium text-gray-300 mb-2">
              Expiration Date (Optional)
            </label>
            <input
              id="key-expires"
              type="date"
              value={expiresAt}
              onChange={(e) => setExpiresAt(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            />
          </div>

          {/* Rate Limit */}
          <div>
            <label htmlFor="key-rate-limit" className="block text-sm font-medium text-gray-300 mb-2">
              Rate Limit (requests per hour) <span className="text-red-400">*</span>
            </label>
            <input
              id="key-rate-limit"
              type="number"
              value={rateLimit}
              onChange={(e) => setRateLimit(parseInt(e.target.value) || 0)}
              min="1"
              className={`w-full px-4 py-3 bg-black/50 border ${
                errors.rate_limit ? 'border-red-500' : 'border-white/10'
              } rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all`}
            />
            {errors.rate_limit && <p className="text-sm text-red-400 mt-1">{errors.rate_limit}</p>}
          </div>

          {/* Permissions */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Permissions <span className="text-red-400">*</span>
            </label>
            <div className="space-y-2">
              {(['read', 'write', 'delete'] as const).map((perm) => (
                <label
                  key={perm}
                  className="flex items-center gap-3 p-3 bg-black/20 rounded-lg border border-white/5 cursor-pointer hover:bg-black/30 transition-colors"
                >
                  <input
                    type="checkbox"
                    checked={permissions.includes(perm)}
                    onChange={() => handleTogglePermission(perm)}
                    className="w-4 h-4 text-purple-600 bg-black/50 border-white/10 rounded focus:ring-purple-500"
                  />
                  <div className="flex items-center gap-2 text-white">
                    <Shield className="w-4 h-4" />
                    <span className="font-medium capitalize">{perm}</span>
                  </div>
                </label>
              ))}
            </div>
            {errors.permissions && <p className="text-sm text-red-400 mt-1">{errors.permissions}</p>}
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
              {isSubmitting ? 'Creating...' : 'Create API Key'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

