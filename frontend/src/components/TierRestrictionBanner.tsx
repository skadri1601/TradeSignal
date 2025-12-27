/**
 * Tier Restriction Banner Component
 *
 * PORTFOLIO MODE: Disabled - all features are free for portfolio showcase
 */

import { useQuery } from '@tanstack/react-query';
import { AlertTriangle, ArrowUpCircle, X } from 'lucide-react';
import { useState } from 'react';
import apiClient from '../api/client';
import { Link } from 'react-router-dom';

// PORTFOLIO MODE: Set to true to disable all restriction banners
const PORTFOLIO_MODE = true;

interface UsageStats {
  tier: string;
  limits: {
    ai_requests_per_day: number;
    alerts_max: number;
    companies_tracked: number;
    historical_data_days: number;
  };
  usage: {
    ai_requests: number;
    alerts_triggered: number;
    api_calls: number;
    companies_viewed: number;
  };
  remaining: {
    ai_requests: number;
  };
}

interface TierRestrictionBannerProps {
  feature: string;
  limitType: 'ai_requests' | 'alerts' | 'companies' | 'historical_data';
  currentUsage?: number;
  limit?: number;
  onDismiss?: () => void;
}

export function TierRestrictionBanner({
  feature,
  limitType,
  currentUsage,
  limit,
  onDismiss,
}: TierRestrictionBannerProps) {
  const [dismissed, setDismissed] = useState(false);

  const { data: usageStats } = useQuery<UsageStats>({
    queryKey: ['usage-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/billing/usage');
      return response.data;
    },
    enabled: !PORTFOLIO_MODE && (!currentUsage || !limit),
  });

  // PORTFOLIO MODE: Don't show restriction banners
  if (PORTFOLIO_MODE) {
    return null;
  }

  if (dismissed) return null;

  const stats = usageStats || {
    tier: 'free',
    limits: { ai_requests_per_day: 5, alerts_max: 3, companies_tracked: 10, historical_data_days: 30 },
    usage: { ai_requests: currentUsage || 0, alerts_triggered: 0, api_calls: 0, companies_viewed: 0 },
    remaining: { ai_requests: -1 },
  };

  const actualLimit = limit || (limitType === 'ai_requests' ? stats.limits.ai_requests_per_day : 
                                limitType === 'alerts' ? stats.limits.alerts_max :
                                limitType === 'companies' ? stats.limits.companies_tracked :
                                stats.limits.historical_data_days);
  
  const actualUsage = currentUsage || (limitType === 'ai_requests' ? stats.usage.ai_requests :
                                       limitType === 'alerts' ? stats.usage.alerts_triggered :
                                       limitType === 'companies' ? stats.usage.companies_viewed : 0);

  const isUnlimited = actualLimit === -1;
  const isNearLimit = !isUnlimited && actualUsage >= actualLimit * 0.8;
  const isAtLimit = !isUnlimited && actualUsage >= actualLimit;

  if (isUnlimited) return null;

  const handleDismiss = () => {
    setDismissed(true);
    onDismiss?.();
  };

  return (
    <div className={`rounded-lg border-l-4 p-4 mb-4 ${
      isAtLimit 
        ? 'bg-red-50 border-red-400' 
        : isNearLimit 
        ? 'bg-yellow-50 border-yellow-400'
        : 'bg-blue-50 border-blue-400'
    }`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          <AlertTriangle className={`h-5 w-5 mt-0.5 ${
            isAtLimit ? 'text-red-600' : isNearLimit ? 'text-yellow-600' : 'text-blue-600'
          }`} />
          <div className="flex-1">
            <h3 className={`font-semibold ${
              isAtLimit ? 'text-red-900' : isNearLimit ? 'text-yellow-900' : 'text-blue-900'
            }`}>
              {isAtLimit ? 'Limit Reached' : isNearLimit ? 'Approaching Limit' : 'Upgrade Available'}
            </h3>
            <p className={`text-sm mt-1 ${
              isAtLimit ? 'text-red-700' : isNearLimit ? 'text-yellow-700' : 'text-blue-700'
            }`}>
              {isAtLimit 
                ? `You've reached your ${stats.tier} tier limit for ${feature} (${actualUsage}/${actualLimit}).`
                : isNearLimit
                ? `You're using ${actualUsage} of ${actualLimit} ${feature} on your ${stats.tier} tier.`
                : `Upgrade to unlock more ${feature} and additional features.`
              }
            </p>
            {!isAtLimit && (
              <div className="mt-2">
                <Link
                  to="/pricing"
                  className="inline-flex items-center space-x-1 text-sm font-medium text-blue-600 hover:text-blue-700"
                >
                  <ArrowUpCircle className="h-4 w-4" />
                  <span>Upgrade Now</span>
                </Link>
              </div>
            )}
          </div>
        </div>
        <button
          onClick={handleDismiss}
          className={`ml-4 ${
            isAtLimit ? 'text-red-600 hover:text-red-700' : 
            isNearLimit ? 'text-yellow-600 hover:text-yellow-700' : 
            'text-blue-600 hover:text-blue-700'
          }`}
        >
          <X className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}

