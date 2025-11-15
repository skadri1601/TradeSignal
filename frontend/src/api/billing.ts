/**
 * Billing and subscription API client
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface CheckoutSessionResponse {
  checkout_url: string;
  session_id: string;
}

export interface UsageStats {
  tier: string;
  usage: {
    ai_requests_today: number;
    alerts_count: number;
  };
  limits: {
    ai_requests_per_day: number;
    alerts_max: number;
    real_time_updates: boolean;
    api_access: boolean;
    companies_tracked: number;
    historical_data_days: number;
  };
  remaining: {
    ai_requests: number;
    alerts: number;
  };
}

export interface PricingTier {
  name: string;
  price: number;
  features: string[];
}

export interface PricingResponse {
  tiers: {
    free: PricingTier;
    basic: PricingTier;
    pro: PricingTier;
    enterprise: PricingTier;
  };
}

export interface CancelSubscriptionResponse {
  message: string;
  cancel_at: string;
  access_until: string;
}

/**
 * Create a Stripe checkout session for subscription upgrade
 */
export async function createCheckoutSession(tier: 'basic' | 'pro' | 'enterprise'): Promise<CheckoutSessionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/billing/create-checkout-session`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      // TODO: Add authentication token when auth is implemented
      // 'Authorization': `Bearer ${getAuthToken()}`
    },
    body: JSON.stringify({ tier })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create checkout session');
  }

  return response.json();
}

/**
 * Get current user's usage statistics and tier limits
 */
export async function getUsageStats(): Promise<UsageStats> {
  const response = await fetch(`${API_BASE_URL}/api/v1/billing/usage`, {
    headers: {
      // TODO: Add authentication token when auth is implemented
      // 'Authorization': `Bearer ${getAuthToken()}`
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch usage stats');
  }

  return response.json();
}

/**
 * Get pricing information for all subscription tiers
 */
export async function getPricing(): Promise<PricingResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/billing/pricing`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch pricing');
  }

  return response.json();
}

/**
 * Cancel user's subscription at end of billing period
 */
export async function cancelSubscription(): Promise<CancelSubscriptionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/billing/cancel-subscription`, {
    method: 'POST',
    headers: {
      // TODO: Add authentication token when auth is implemented
      // 'Authorization': `Bearer ${getAuthToken()}`
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to cancel subscription');
  }

  return response.json();
}

/**
 * Redirect user to Stripe Checkout
 */
export async function redirectToCheckout(tier: 'basic' | 'pro' | 'enterprise'): Promise<void> {
  try {
    const { checkout_url } = await createCheckoutSession(tier);
    window.location.href = checkout_url;
  } catch (error) {
    console.error('Checkout error:', error);
    throw error;
  }
}
