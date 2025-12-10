/**
 * Billing and subscription API client
 */

import { getAccessToken } from '../contexts/AuthContext';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Get auth headers with access token
 */
function getAuthHeaders(): HeadersInit {
  const token = getAccessToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
}

export interface CheckoutSessionResponse {
  checkout_url: string;
  session_id: string;
}

export interface UsageStats {
  tier: string;
  limits: {
    ai_requests_per_day: number;
    alerts_max: number;
    real_time_updates: boolean;
    api_access: boolean;
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
  reset_at: string;
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

export interface PauseSubscriptionResponse {
  message: string;
  paused_until: string;
  access_until: string | null;
}

export interface ResumeSubscriptionResponse {
  message: string;
  status: string;
}

export interface SubscriptionResponse {
  tier: string;
  status: string;
  is_active: boolean;
  current_period_start: string | null;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
  billing_period?: 'monthly' | 'yearly';
  price_paid?: number;
  order_number?: string;
  stripe_order_number?: string;
}

/**
 * Create a Stripe checkout session for subscription upgrade
 */
export async function createCheckoutSession(
  tier: 'plus' | 'pro' | 'enterprise',
  billingPeriod: 'monthly' | 'yearly' = 'monthly'
): Promise<CheckoutSessionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/billing/create-checkout-session`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ tier, billing_period: billingPeriod })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create checkout session');
  }

  return response.json();
}

/**
 * Get current user's subscription information
 */
export async function getSubscription(): Promise<SubscriptionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/billing/subscription`, {
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch subscription');
  }

  return response.json();
}

/**
 * Get current user's usage statistics and tier limits
 */
export async function getUsageStats(): Promise<UsageStats> {
  const response = await fetch(`${API_BASE_URL}/api/v1/billing/usage`, {
    headers: getAuthHeaders()
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
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to cancel subscription');
  }

  return response.json();
}

/**
 * Pause user's subscription temporarily
 */
export async function pauseSubscription(): Promise<PauseSubscriptionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/billing/pause-subscription`, {
    method: 'POST',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to pause subscription');
  }

  return response.json();
}

/**
 * Resume a paused subscription
 */
export async function resumeSubscription(): Promise<ResumeSubscriptionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/billing/resume-subscription`, {
    method: 'POST',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to resume subscription');
  }

  return response.json();
}

/**
 * Redirect user to Stripe Checkout
 */
export async function redirectToCheckout(
  tier: 'plus' | 'pro' | 'enterprise',
  billingPeriod: 'monthly' | 'yearly' = 'monthly'
): Promise<void> {
  try {
    const { checkout_url } = await createCheckoutSession(tier, billingPeriod);
    window.location.href = checkout_url;
  } catch (error) {
    console.error('Checkout error:', error);
    throw error;
  }
}
