/**
 * Pricing Page Component
 * Phase 8: Business Model - Freemium pricing tiers
 */

import { Check } from 'lucide-react';

interface PricingTier {
  name: string;
  price: string;
  period: string;
  features: string[];
  cta: string;
  current?: boolean;
  popular?: boolean;
}

export default function PricingPage() {
  const tiers: PricingTier[] = [
    {
      name: 'Free',
      price: '$0',
      period: '/forever',
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
      name: 'Basic',
      price: '$9',
      period: '/month',
      features: [
        '10 watchlists',
        '20 price alerts',
        '1,000 API calls/day',
        '5-second refresh rate',
        'Real-time market data',
        'Email notifications',
        'Priority email support',
      ],
      cta: 'Coming Soon',
      popular: true,
    },
    {
      name: 'Pro',
      price: '$29',
      period: '/month',
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
      cta: 'Coming Soon',
    },
  ];

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
                <span className="text-5xl font-bold text-gray-900">
                  {tier.price}
                </span>
                <span className="text-gray-600 text-lg">{tier.period}</span>
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
                className={`w-full py-3 px-6 rounded-lg font-semibold transition-all ${
                  tier.current
                    ? 'bg-gray-100 text-gray-600 cursor-not-allowed'
                    : tier.popular
                    ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl'
                    : 'bg-gray-900 text-white hover:bg-gray-800 shadow-md hover:shadow-lg'
                }`}
                disabled={tier.current || tier.cta === 'Coming Soon'}
              >
                {tier.cta}
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
