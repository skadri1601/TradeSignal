/**
 * Hook for checking feature access based on subscription tier
 *
 * PORTFOLIO MODE: All features unlocked for portfolio showcase
 */

import { useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';

// PORTFOLIO MODE: Set to true to unlock all features
const PORTFOLIO_MODE = true;

// Tier hierarchy for comparison
const TIER_LEVELS: Record<string, number> = {
  'free': 0,
  'basic': 1,
  'plus': 2,
  'pro': 3,
  'enterprise': 4,
};

// Feature to tier mapping
const FEATURE_TIERS: Record<string, string> = {
  'api_access': 'pro',
  'export_enabled': 'plus',
  'real_time_updates': 'plus',
  'advanced_screening': 'plus',
  'unlimited_alerts': 'pro',
  'unlimited_companies': 'pro',
  'unlimited_history': 'pro',
  'priority_support': 'pro',
  'white_label': 'enterprise',
  'custom_integrations': 'enterprise',
};

/**
 * Hook to check if user has access to a feature
 */
export function useFeatureAccess() {
  const { user } = useAuth();

  // PORTFOLIO MODE: Treat all users as enterprise tier
  const userTier = PORTFOLIO_MODE ? 'enterprise' : (user?.stripe_subscription_tier || 'free');
  const userTierLevel = PORTFOLIO_MODE ? 4 : (TIER_LEVELS[userTier.toLowerCase()] || 0);

  const hasFeature = useMemo(() => {
    return (featureKey: string): boolean => {
      // PORTFOLIO MODE: All features available
      if (PORTFOLIO_MODE) {
        return true;
      }

      // Check if feature requires a specific tier
      const requiredTier = FEATURE_TIERS[featureKey];
      if (!requiredTier) {
        // Feature not in mapping, assume free tier
        return true;
      }

      const requiredTierLevel = TIER_LEVELS[requiredTier.toLowerCase()] || 0;
      return userTierLevel >= requiredTierLevel;
    };
  }, [userTierLevel]);

  const hasTier = useMemo(() => {
    return (minTier: string): boolean => {
      // PORTFOLIO MODE: All tiers available
      if (PORTFOLIO_MODE) {
        return true;
      }

      const requiredTierLevel = TIER_LEVELS[minTier.toLowerCase()] || 0;
      return userTierLevel >= requiredTierLevel;
    };
  }, [userTierLevel]);

  const canUpgrade = useMemo(() => {
    // PORTFOLIO MODE: No upgrade prompts needed
    if (PORTFOLIO_MODE) {
      return false;
    }
    return userTier !== 'enterprise';
  }, [userTier]);

  return {
    userTier,
    userTierLevel,
    hasFeature,
    hasTier,
    canUpgrade,
    isFree: !PORTFOLIO_MODE && userTier === 'free',
    isPlus: PORTFOLIO_MODE || userTier === 'plus',
    isPro: PORTFOLIO_MODE || userTier === 'pro',
    isEnterprise: PORTFOLIO_MODE || userTier === 'enterprise',
  };
}

