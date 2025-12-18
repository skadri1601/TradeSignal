/**
 * Upgrade CTA Component
 * Displays upgrade call-to-action banners throughout the app
 */

import { Link } from 'react-router-dom';
import { ArrowRight, Sparkles, TrendingUp } from 'lucide-react';
import { useFeatureAccess } from '../hooks/useFeatureAccess';

interface UpgradeCTAProps {
  variant?: 'banner' | 'card' | 'inline';
  feature?: string;
  requiredTier?: 'plus' | 'pro' | 'enterprise';
  message?: string;
  onDismiss?: () => void;
  className?: string;
}

export function UpgradeCTA({
  variant = 'banner',
  feature,
  requiredTier = 'pro',
  message,
  onDismiss,
  className = '',
}: UpgradeCTAProps) {
  const { userTier, canUpgrade } = useFeatureAccess();

  // Don't show if user already has required tier or can't upgrade
  if (!canUpgrade) {
    return null;
  }

  const tierNames: Record<string, string> = {
    plus: 'Plus',
    pro: 'Pro',
    enterprise: 'Enterprise',
  };

  const defaultMessage = message || `Unlock ${feature || 'premium features'} with ${tierNames[requiredTier]}`;

  if (variant === 'banner') {
    return (
      <div className={`bg-gradient-to-r from-purple-600 to-blue-600 text-white p-4 rounded-lg shadow-lg ${className}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Sparkles className="w-5 h-5" />
            <div>
              <p className="font-semibold">{defaultMessage}</p>
              <p className="text-sm text-purple-100">Upgrade now and get started immediately</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Link
              to="/pricing"
              className="bg-white text-purple-600 px-4 py-2 rounded-lg font-semibold hover:bg-purple-50 transition-colors flex items-center"
            >
              Upgrade
              <ArrowRight className="w-4 h-4 ml-1" />
            </Link>
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="text-white/80 hover:text-white transition-colors"
                aria-label="Dismiss"
              >
                ×
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (variant === 'card') {
    return (
      <div className={`bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-purple-200 rounded-xl p-6 ${className}`}>
        <div className="flex items-start space-x-4">
          <div className="bg-purple-600 rounded-full p-3">
            <TrendingUp className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-gray-900 mb-1">Upgrade to {tierNames[requiredTier]}</h3>
            <p className="text-gray-600 text-sm mb-4">{defaultMessage}</p>
            <Link
              to="/pricing"
              className="inline-flex items-center bg-gradient-to-r from-purple-600 to-blue-600 text-white px-4 py-2 rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all"
            >
              View Plans
              <ArrowRight className="w-4 h-4 ml-2" />
            </Link>
          </div>
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Dismiss"
            >
              ×
            </button>
          )}
        </div>
      </div>
    );
  }

  // Inline variant
  return (
    <div className={`inline-flex items-center space-x-2 text-purple-600 ${className}`}>
      <Sparkles className="w-4 h-4" />
      <Link to="/pricing" className="font-semibold hover:underline">
        {defaultMessage}
      </Link>
    </div>
  );
}

