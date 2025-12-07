/**
 * Pricing Page Component
 * Phase 8: Business Model - Freemium pricing tiers
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check, Loader2, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { redirectToCheckout } from '../api/billing';

interface PricingTier {
  name: string;
  price_monthly: number;
  price_yearly: number;
  yearly_savings?: number;
  features: string[];
  cta: string;
  current?: boolean;
  popular?: boolean;
  tier?: 'plus' | 'pro' | 'enterprise';
}

export default function PricingPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [loadingTier, setLoadingTier] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');
  const tiers: PricingTier[] = [
    {
      name: 'Free',
      price_monthly: 0,
      price_yearly: 0,
      features: [
        '3 watchlists',
        '5 price alerts',
        '100 API calls/day',
        '15-second refresh rate',
        'Educational data only',
        'Community support',
      ],
      cta: 'Current Plan',
      current: true,
    },
    {
      name: 'Plus',
      price_monthly: 9.99,
      price_yearly: 90,
      yearly_savings: 29.88,
      tier: 'plus',
      features: [
        '10 watchlists',
        '20 price alerts',
        '1,000 API calls/day',
        '5-second refresh rate',
        'Real-time market data',
        'Email notifications',
        'Priority email support',
      ],
      cta: 'Upgrade to Plus',
      popular: true,
    },
    {
      name: 'Pro',
      price_monthly: 29.99,
      price_yearly: 300,
      yearly_savings: 59.88,
      tier: 'pro',
      features: [
        '50 watchlists',
        '100 price alerts',
        '10,000 API calls/day',
        '1-second refresh rate',
        'Real-time market data',
        'Email + SMS notifications',
        'Advanced AI insights',
        'API access',
        'Priority support',
      ],
      cta: 'Upgrade to Pro',
    },
    {
      name: 'Enterprise',
      price_monthly: 99.99,
      price_yearly: 1000,
      yearly_savings: 199.88,
      tier: 'enterprise',
      features: [
        'Unlimited watchlists',
        'Unlimited price alerts',
        'Unlimited API calls',
        'Real-time data feeds',
        'Dedicated account manager',
        'Custom integrations',
        'White-label options',
        'SLA guarantee',
        '24/7 phone support',
        'Custom AI models',
        'Data export & APIs',
      ],
      cta: 'Contact Sales',
    },
  ];

  const handleUpgrade = async (tier: PricingTier) => {
    // Handle "Contact Sales" for Enterprise tier
    if (tier.name === 'Enterprise' && tier.cta === 'Contact Sales') {
      window.location.href = 'mailto:sales@tradesignal.com?subject=Enterprise Plan Inquiry&body=Hello, I am interested in learning more about the Enterprise plan.';
      return;
    }

    // Check if user is authenticated
    if (!isAuthenticated) {
      // Save intended tier in sessionStorage and redirect to login
      if (tier.tier) {
        sessionStorage.setItem('intended_tier', tier.tier);
      }
      navigate('/login');
      return;
    }

    // Proceed with checkout
    if (tier.tier) {
      setLoadingTier(tier.name);
      setError(null);
      try {
        await redirectToCheckout(tier.tier, billingPeriod);
      } catch (error: any) {
        console.error('Checkout failed:', error);
        
        // Check for Stripe blocking errors
        const errorMessage = error?.message || String(error);
        if (errorMessage.includes('ERR_BLOCKED_BY_CLIENT') || 
            errorMessage.includes('blocked') ||
            errorMessage.includes('CORS') ||
            errorMessage.includes('Failed to fetch')) {
          setError('Stripe payment processing is being blocked. Please disable ad blockers or browser extensions and try again.');
        } else if (errorMessage.includes('503') || errorMessage.includes('not configured') || errorMessage.includes('configuration')) {
          setError('Payment processing is not fully configured. Please contact support or try again later.');
        } else if (errorMessage.includes('401') || errorMessage.includes('Unauthorized')) {
          setError('Please log in to continue with checkout.');
          navigate('/login');
        } else {
          setError(errorMessage || 'Failed to start checkout. Please try again.');
        }
        setLoadingTier(null);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Choose Your Plan
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            Start free. Upgrade when you're ready.
          </p>
          <p className="text-sm text-gray-500">
            All plans include 30-day money-back guarantee
          </p>

          {/* Billing Period Toggle */}
          <div className="mt-6 flex items-center justify-center">
            <div className="bg-white rounded-lg p-1 border border-gray-200 inline-flex shadow-sm">
              <button
                onClick={() => setBillingPeriod('monthly')}
                className={`px-6 py-2 rounded-md font-medium transition-all ${
                  billingPeriod === 'monthly'
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingPeriod('yearly')}
                className={`px-6 py-2 rounded-md font-medium transition-all relative ${
                  billingPeriod === 'yearly'
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Yearly
                <span className="absolute -top-2 -right-2 bg-green-500 text-white text-xs font-bold px-1.5 py-0.5 rounded-full">
                  Save 17%
                </span>
              </button>
            </div>
          </div>
          
          {/* Error Message */}
          {error && (
            <div className="mt-4 max-w-2xl mx-auto">
              <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                <div className="flex items-start">
                  <AlertCircle className="h-5 w-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm text-red-700 font-medium">Payment Error</p>
                    <p className="text-sm text-red-600 mt-1">{error}</p>
                    {error.includes('blocked') && (
                      <div className="mt-2 text-xs text-red-600">
                        <p className="font-medium">To fix this:</p>
                        <ul className="list-disc list-inside mt-1 space-y-1">
                          <li>Disable ad blockers (uBlock Origin, AdBlock Plus, etc.)</li>
                          <li>Disable privacy extensions temporarily</li>
                          <li>Try using a different browser</li>
                          <li>Check if your firewall is blocking Stripe</li>
                        </ul>
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => setError(null)}
                    className="text-red-500 hover:text-red-700 ml-4"
                  >
                    ×
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {tiers.map((tier) => (
            <div
              key={tier.name}
              className={`rounded-2xl p-8 relative ${
                tier.popular
                  ? 'border-2 border-blue-500 shadow-2xl scale-105'
                  : 'border border-gray-200 shadow-lg'
              } bg-white`}
            >
              {/* Popular Badge */}
              {tier.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-blue-500 text-white text-xs font-bold uppercase px-4 py-1 rounded-full shadow-lg">
                    Most Popular
                  </span>
                </div>
              )}

              {/* Tier Name */}
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                {tier.name}
              </h3>

              {/* Price */}
              <div className="mb-6">
                <div className="flex items-baseline">
                  <span className="text-5xl font-bold text-gray-900">
                    ${billingPeriod === 'monthly' ? tier.price_monthly : tier.price_yearly}
                  </span>
                  <span className="text-gray-600 text-lg ml-2">
                    /{billingPeriod === 'monthly' ? 'month' : 'year'}
                  </span>
                </div>
                {billingPeriod === 'yearly' && tier.yearly_savings && (
                  <div className="mt-2">
                    <span className="text-sm text-green-600 font-semibold">
                      Save ${tier.yearly_savings}/year
                    </span>
                    <span className="text-xs text-gray-500 ml-2">
                      (${tier.price_monthly}/month billed annually)
                    </span>
                  </div>
                )}
                {billingPeriod === 'monthly' && tier.yearly_savings && (
                  <div className="mt-2">
                    <span className="text-xs text-gray-500">
                      ${tier.price_yearly}/year if paid annually (save ${tier.yearly_savings})
                    </span>
                  </div>
                )}
              </div>

              {/* Features */}
              <ul className="space-y-4 mb-8">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-start">
                    <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>

              {/* CTA Button */}
              <button
                onClick={() => handleUpgrade(tier)}
                className={`w-full py-3 px-6 rounded-lg font-semibold transition-all flex items-center justify-center ${
                  tier.current
                    ? 'bg-gray-100 text-gray-600 cursor-not-allowed'
                    : tier.popular
                    ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl disabled:bg-blue-400'
                    : 'bg-gray-900 text-white hover:bg-gray-800 shadow-md hover:shadow-lg disabled:bg-gray-600'
                }`}
                disabled={tier.current || loadingTier === tier.name}
              >
                {loadingTier === tier.name ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  tier.cta
                )}
              </button>
            </div>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Frequently Asked Questions
          </h2>

          <div className="space-y-6">
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2">
                Can I upgrade or downgrade anytime?
              </h3>
              <p className="text-gray-600">
                Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately,
                and we'll prorate any charges.
              </p>
            </div>

            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2">
                What payment methods do you accept?
              </h3>
              <p className="text-gray-600">
                We accept all major credit cards (Visa, MasterCard, American Express) via Stripe.
                All payments are secure and encrypted.
              </p>
            </div>

            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2">
                Is there a free trial for paid plans?
              </h3>
              <p className="text-gray-600">
                The Free plan is available forever with no credit card required. Paid plans come with
                a 30-day money-back guarantee, so you can try risk-free.
              </p>
            </div>

            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2">
                Do you offer discounts for annual plans?
              </h3>
              <p className="text-gray-600">
                Yes! Annual plans save you 20% compared to monthly billing. Contact us for details.
              </p>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="text-center mt-12 text-sm text-gray-500">
          <p>
            All prices in USD. Market data is for educational purposes only.
            Not financial advice.
          </p>
        </div>
      </div>
    </div>
  );
}
