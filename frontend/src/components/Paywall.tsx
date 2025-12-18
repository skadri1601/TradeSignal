/**
 * Paywall Component
 * Displays a paywall overlay when user tries to access premium features
 */

import { Link } from 'react-router-dom';
import { Lock, Sparkles, ArrowRight } from 'lucide-react';
import { useFeatureAccess } from '../hooks/useFeatureAccess';

interface PaywallProps {
  featureName: string;
  requiredTier: 'plus' | 'pro' | 'enterprise';
  description?: string;
  onDismiss?: () => void;
  showComparison?: boolean;
}

export function Paywall({
  featureName,
  requiredTier,
  description,
  onDismiss,
  showComparison = true,
}: PaywallProps) {
  const { userTier, canUpgrade } = useFeatureAccess();

  const tierNames: Record<string, string> = {
    plus: 'Plus',
    pro: 'Pro',
    enterprise: 'Enterprise',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-6 text-white">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-white/20 rounded-full p-3">
              <Lock className="w-8 h-8" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-center mb-2">Premium Feature</h2>
          <p className="text-center text-purple-100">
            {featureName} requires {tierNames[requiredTier]} subscription
          </p>
        </div>

        {/* Content */}
        <div className="p-6">
          {description && (
            <p className="text-gray-600 mb-6 text-center">{description}</p>
          )}

          {showComparison && (
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-gray-900 mb-3">What you'll get:</h3>
              <ul className="space-y-2 text-sm text-gray-700">
                {requiredTier === 'plus' && (
                  <>
                    <li className="flex items-center">
                      <Sparkles className="w-4 h-4 text-purple-600 mr-2" />
                      Unlimited historical data
                    </li>
                    <li className="flex items-center">
                      <Sparkles className="w-4 h-4 text-purple-600 mr-2" />
                      Advanced AI insights
                    </li>
                    <li className="flex items-center">
                      <Sparkles className="w-4 h-4 text-purple-600 mr-2" />
                      Export capabilities
                    </li>
                  </>
                )}
                {requiredTier === 'pro' && (
                  <>
                    <li className="flex items-center">
                      <Sparkles className="w-4 h-4 text-purple-600 mr-2" />
                      Everything in Plus
                    </li>
                    <li className="flex items-center">
                      <Sparkles className="w-4 h-4 text-purple-600 mr-2" />
                      Unlimited API access
                    </li>
                    <li className="flex items-center">
                      <Sparkles className="w-4 h-4 text-purple-600 mr-2" />
                      Priority support
                    </li>
                  </>
                )}
                {requiredTier === 'enterprise' && (
                  <>
                    <li className="flex items-center">
                      <Sparkles className="w-4 h-4 text-purple-600 mr-2" />
                      Everything in Pro
                    </li>
                    <li className="flex items-center">
                      <Sparkles className="w-4 h-4 text-purple-600 mr-2" />
                      Dedicated account manager
                    </li>
                    <li className="flex items-center">
                      <Sparkles className="w-4 h-4 text-purple-600 mr-2" />
                      Custom integrations
                    </li>
                  </>
                )}
              </ul>
            </div>
          )}

          {/* Actions */}
          <div className="space-y-3">
            {canUpgrade ? (
              <Link
                to="/pricing"
                className="block w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all flex items-center justify-center"
              >
                Upgrade to {tierNames[requiredTier]}
                <ArrowRight className="w-5 h-5 ml-2" />
              </Link>
            ) : (
              <div className="text-center text-gray-500 text-sm">
                You're already on the highest tier!
              </div>
            )}
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="block w-full bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
              >
                Maybe Later
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

