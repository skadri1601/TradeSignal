/**
 * Pricing Page Component
 * Phase 8: Business Model - Freemium pricing tiers
 * Updated to match Landing Page Dark Theme
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check, Loader2, AlertCircle, Zap, Shield, Search } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { redirectToCheckout, getSubscription } from '../api/billing';
import type { SubscriptionResponse } from '../api/billing';

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
  description: string;
  icon?: React.ReactNode;
}

export default function PricingPage() {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const [loadingTier, setLoadingTier] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');
  const [subscription, setSubscription] = useState<SubscriptionResponse | null>(null);
  const [, setSubscriptionLoading] = useState(true);

  // Fetch user's current subscription
  useEffect(() => {
    const fetchSubscription = async () => {
      if (!isAuthenticated || !user) {
        setSubscriptionLoading(false);
        return;
      }

      try {
        setSubscriptionLoading(true);
        const sub = await getSubscription();
        setSubscription(sub);
      } catch (error) {
        console.error('Failed to load subscription data');
        // Default to free tier on error
        setSubscription({
          tier: 'free',
          status: 'inactive',
          is_active: false,
          current_period_start: null,
          current_period_end: null,
          cancel_at_period_end: false,
        });
      } finally {
        setSubscriptionLoading(false);
      }
    };

    fetchSubscription();
  }, [isAuthenticated, user]);

  // Determine current tier and billing period from subscription
  const currentTier = (subscription?.is_active && subscription?.tier) ? subscription.tier : 'free';
  const currentBillingPeriod = subscription?.billing_period || null;
  const isCurrentTierActive = subscription?.is_active || false;

  // Helper function to determine if a tier is the current plan
  const isCurrentPlan = (tierName: string, period: 'monthly' | 'yearly') => {
    if (!isAuthenticated || !isCurrentTierActive) {
      return false;
    }
    // Check both tier and billing period match
    const tierMatch = currentTier === tierName.toLowerCase();
    const billingMatch = currentBillingPeriod === period;
    return tierMatch && billingMatch;
  };

  // Helper function to determine if a tier should show "Most Popular" badge
  const shouldShowPopular = (tierName: string, period: 'monthly' | 'yearly') => {
    if (!isAuthenticated) {
      // For logged-out users: Always show "Most Popular" on Plus (both monthly and yearly)
      return tierName === 'Plus';
    }

    // For logged-in users:
    // - Never show "Most Popular" on user's current plan (check both tier AND billing period)
    if (isCurrentPlan(tierName, period)) {
      return false;
    }

    // - Never show "Most Popular" on user's current tier (regardless of billing period)
    if (currentTier === tierName.toLowerCase()) {
      return false;
    }

    // - If user is on Pro tier → Don't show "Most Popular" badge at all
    if (currentTier === 'pro') {
      return false;
    }

    // - If user is on Free or Plus tier → Show "Most Popular" on Pro plan (both monthly and yearly)
    if (currentTier === 'free' || currentTier === 'plus' || currentTier === 'basic') {
      return tierName === 'Pro';
    }

    return false;
  };

  const tiers: PricingTier[] = [
    {
      name: 'Free',
      description: 'Perfect for beginners exploring the market.',
      price_monthly: 0,
      price_yearly: 0,
      icon: <Search className="w-6 h-6" />,
      features: [
        '3 watchlists',
        '5 price alerts',
        '100 API calls/day',
        '15-second refresh rate',
        'Educational data only',
        'Community support',
      ],
      cta: isCurrentPlan('free', billingPeriod) ? 'Current Plan' : 'Get Started',
      current: isCurrentPlan('free', billingPeriod),
      popular: shouldShowPopular('Free', billingPeriod),
    },
    {
      name: 'Plus',
      description: 'For serious traders who need real-time data.',
      price_monthly: 9.99,
      price_yearly: 90,
      yearly_savings: 29.88,
      tier: 'plus',
      icon: <Zap className="w-6 h-6" />,
      features: [
        '10 watchlists',
        '20 price alerts',
        '1,000 API calls/day',
        '5-second refresh rate',
        'Real-time market data',
        'Email notifications',
        'Priority email support',
      ],
      cta: isCurrentPlan('plus', billingPeriod) ? 'Current Plan' : 'Upgrade to Plus',
      current: isCurrentPlan('plus', billingPeriod),
      popular: shouldShowPopular('Plus', billingPeriod),
    },
    {
      name: 'Pro',
      description: 'Advanced tools and AI insights for pros.',
      price_monthly: 29.99,
      price_yearly: 300,
      yearly_savings: 59.88,
      tier: 'pro',
      icon: <Shield className="w-6 h-6" />,
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
      cta: isCurrentPlan('pro', billingPeriod) ? 'Current Plan' : (currentTier === 'free' || currentTier === 'plus' || currentTier === 'basic' ? 'Upgrade to Pro' : 'Upgrade to Pro'),
      current: isCurrentPlan('pro', billingPeriod),
      popular: shouldShowPopular('Pro', billingPeriod),
    },
    {
      name: 'Enterprise',
      description: 'Custom solutions for institutions.',
      price_monthly: 99.99,
      price_yearly: 1000,
      yearly_savings: 199.88,
      tier: 'enterprise',
      icon: <Check className="w-6 h-6" />,
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
      cta: isCurrentPlan('enterprise', billingPeriod) ? 'Current Plan' : 'Contact Sales',
      current: isCurrentPlan('enterprise', billingPeriod),
      popular: shouldShowPopular('Enterprise', billingPeriod),
    },
  ];

  const handleUpgrade = async (tier: PricingTier) => {
    // Don't allow upgrade if this is already the current plan
    if (tier.current) {
      return;
    }

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
    <div className="min-h-screen bg-black text-white font-sans selection:bg-purple-500/30 overflow-x-hidden">
      
      {/* Background Ambience */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px]" />
      </div>

      <div className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          
          {/* Header */}
          <div className="text-center mb-16 relative z-10">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Simple, Transparent <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
                Pricing
              </span>
            </h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-8">
              Choose the perfect plan for your trading journey. Start free, upgrade as you grow.
            </p>

            {/* Billing Period Toggle */}
            <div className="inline-flex items-center p-1 bg-white/5 border border-white/10 rounded-xl backdrop-blur-sm">
              <button
                onClick={() => setBillingPeriod('monthly')}
                className={`px-6 py-2.5 rounded-lg font-medium transition-all duration-300 ${
                  billingPeriod === 'monthly'
                    ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/25'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingPeriod('yearly')}
                className={`px-6 py-2.5 rounded-lg font-medium transition-all duration-300 relative ${
                  billingPeriod === 'yearly'
                    ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/25'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Yearly
                <span className="absolute -top-3 -right-3 bg-[#10B981] text-black text-[10px] font-bold px-2 py-0.5 rounded-full shadow-lg">
                  SAVE 17%
                </span>
              </button>
            </div>
            
            {/* Error Message */}
            {error && (
              <div className="mt-8 max-w-lg mx-auto">
                <div className="bg-red-900/20 border border-red-500/50 p-4 rounded-xl flex items-start text-left">
                  <AlertCircle className="h-5 w-5 text-red-400 mt-0.5 mr-3 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm text-red-200">{error}</p>
                    {error.includes('blocked') && (
                      <div className="mt-2 text-xs text-red-300/70">
                        <p className="font-medium">Try disabling ad blockers or using a different browser.</p>
                      </div>
                    )}
                  </div>
                  <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300 ml-4">×</button>
                </div>
              </div>
            )}
          </div>

          {/* Platform Value Proposition */}
          <section className="py-12 px-6 max-w-4xl mx-auto text-center mb-12 relative z-10">
            <p className="text-gray-400 leading-relaxed mb-6">
              TradeSignal provides real-time insider trading intelligence by tracking SEC Form 4 filings,
              congressional trades, and market-moving transactions. Choose the plan that fits your trading style.
            </p>
            <div className="flex flex-wrap justify-center gap-4 text-sm">
              <div className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-full">
                <span className="text-blue-400">✓</span>
                <span className="text-gray-300">15M+ Filings Processed</span>
              </div>
              <div className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-full">
                <span className="text-purple-400">✓</span>
                <span className="text-gray-300">92% AI Accuracy</span>
              </div>
              <div className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-full">
                <span className="text-green-400">✓</span>
                <span className="text-gray-300">10K+ Active Traders</span>
              </div>
            </div>
          </section>

          {/* Pricing Cards */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 relative z-10">
            {tiers.map((tier) => (
              <div
                key={tier.name}
                className={`relative rounded-3xl p-6 flex flex-col h-full transition-all duration-300 ${
                  tier.popular
                    ? 'bg-gradient-to-b from-gray-800 to-gray-900 border-2 border-purple-500/50 shadow-2xl shadow-purple-500/10 scale-105 z-10'
                    : 'bg-gray-900/50 border border-white/10 hover:border-white/20 hover:bg-gray-900/80'
                }`}
              >
                {/* Popular Badge */}
                {tier.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-purple-600 text-white text-xs font-bold uppercase tracking-wider px-4 py-1.5 rounded-full shadow-lg border border-purple-400/30">
                      Most Popular
                    </span>
                  </div>
                )}

                <div className="mb-6">
                  <div className="w-12 h-12 bg-white/5 rounded-xl flex items-center justify-center text-purple-400 mb-4 border border-white/5">
                    {tier.icon}
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">{tier.name}</h3>
                  <p className="text-sm text-gray-400 min-h-[40px]">{tier.description}</p>
                </div>

                <div className="mb-6">
                  <div className="flex items-baseline">
                    <span className="text-4xl font-bold text-white">
                      ${billingPeriod === 'monthly' ? tier.price_monthly : tier.price_yearly}
                    </span>
                    <span className="text-gray-500 ml-2">
                      /{billingPeriod === 'monthly' ? 'mo' : 'yr'}
                    </span>
                  </div>
                  {billingPeriod === 'yearly' && tier.yearly_savings && (
                    <p className="text-xs text-green-400 mt-2 font-medium">
                      Save ${tier.yearly_savings} per year
                    </p>
                  )}
                </div>

                <ul className="space-y-3 mb-8 flex-1">
                  {tier.features.map((feature, i) => (
                    <li key={i} className="flex items-start text-sm">
                      <Check className="w-4 h-4 text-purple-500 mr-3 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => handleUpgrade(tier)}
                  disabled={tier.current || loadingTier === tier.name}
                  className={`w-full py-3 px-6 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center ${
                    tier.current
                      ? 'bg-white/5 text-gray-400 cursor-not-allowed border border-white/5'
                      : tier.popular
                      ? 'bg-purple-600 text-white hover:bg-purple-500 shadow-lg shadow-purple-500/25'
                      : 'bg-white text-black hover:bg-gray-200'
                  }`}
                >
                  {loadingTier === tier.name ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
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
          <div className="mt-24 max-w-3xl mx-auto relative z-10">
            <h2 className="text-3xl font-bold text-white mb-10 text-center">
              Frequently Asked Questions
            </h2>

            <div className="space-y-4">
              {[
                { q: "Can I cancel anytime?", a: "Yes! You can cancel your subscription at any time from your profile. You'll keep access until the end of your billing period." },
                { q: "Do you offer refunds?", a: "We offer a 30-day money-back guarantee for all paid plans. If you're not satisfied, just let us know." },
                { q: "What payment methods do you accept?", a: "We accept all major credit cards (Visa, Mastercard, Amex) securely processed via Stripe." },
                { q: "Can I switch plans later?", a: "Absolutely. You can upgrade or downgrade your plan at any time. Changes take effect immediately." }
              ].map((faq, i) => (
                <div key={i} className="bg-gray-900/50 border border-white/10 rounded-2xl p-6 hover:bg-gray-900/80 transition-colors">
                  <h3 className="font-semibold text-white mb-2">{faq.q}</h3>
                  <p className="text-gray-400 text-sm leading-relaxed">{faq.a}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Disclaimer */}
          <div className="text-center mt-16 text-xs text-gray-600 max-w-2xl mx-auto">
            <p>
              All prices in USD. Market data provided by TradeSignal is for educational purposes only.
              We are not financial advisors. Past performance is not indicative of future results.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}