/**
 * Tier Comparison Table Component
 * Displays feature comparison across subscription tiers
 */

import { Check, X } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useFeatureAccess } from '../hooks/useFeatureAccess';

interface Feature {
  name: string;
  free: boolean | string;
  plus: boolean | string;
  pro: boolean | string;
  enterprise: boolean | string;
}

interface TierComparisonTableProps {
  features: Feature[];
  showCurrentTier?: boolean;
  onUpgrade?: (tier: string) => void;
}

export function TierComparisonTable({
  features,
  showCurrentTier: _showCurrentTier = true,
  onUpgrade,
}: TierComparisonTableProps) {
  const { userTier } = useFeatureAccess();

  const renderFeature = (value: boolean | string) => {
    if (value === true) {
      return <Check className="w-5 h-5 text-green-600 mx-auto" />;
    }
    if (value === false) {
      return <X className="w-5 h-5 text-gray-300 mx-auto" />;
    }
    return <span className="text-sm text-gray-600">{value}</span>;
  };

  const tiers = [
    { key: 'free', name: 'Free', price: '$0', highlight: false },
    { key: 'plus', name: 'Plus', price: '$9/mo', highlight: userTier === 'plus' },
    { key: 'pro', name: 'Pro', price: '$29/mo', highlight: userTier === 'pro' },
    { key: 'enterprise', name: 'Enterprise', price: '$99/mo', highlight: userTier === 'enterprise' },
  ];

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <th className="text-left p-4 font-semibold text-gray-700">Feature</th>
            {tiers.map((tier) => (
              <th
                key={tier.key}
                className={`p-4 text-center font-semibold ${
                  tier.highlight
                    ? 'bg-purple-50 border-2 border-purple-500 rounded-t-lg'
                    : 'bg-gray-50'
                }`}
              >
                <div className="flex flex-col items-center">
                  <span className="text-lg">{tier.name}</span>
                  <span className="text-sm text-gray-600 mt-1">{tier.price}</span>
                  {tier.highlight && (
                    <span className="text-xs text-purple-600 mt-1 font-medium">Current Plan</span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {features.map((feature, index) => (
            <tr
              key={feature.name}
              className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
            >
              <td className="p-4 font-medium text-gray-900">{feature.name}</td>
              <td className="p-4 text-center">{renderFeature(feature.free)}</td>
              <td className="p-4 text-center">{renderFeature(feature.plus)}</td>
              <td className="p-4 text-center">{renderFeature(feature.pro)}</td>
              <td className="p-4 text-center">{renderFeature(feature.enterprise)}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td></td>
            {tiers.map((tier) => (
              <td key={tier.key} className="p-4">
                {tier.key === 'free' ? (
                  <span className="text-sm text-gray-500">Current plan</span>
                ) : (
                  <Link
                    to="/pricing"
                    onClick={() => onUpgrade?.(tier.key)}
                    className={`block w-full text-center px-4 py-2 rounded-lg font-semibold transition-colors ${
                      tier.highlight
                        ? 'bg-purple-600 text-white cursor-default'
                        : 'bg-purple-600 text-white hover:bg-purple-700'
                    }`}
                  >
                    {tier.highlight ? 'Current Plan' : 'Upgrade'}
                  </Link>
                )}
              </td>
            ))}
          </tr>
        </tfoot>
      </table>
    </div>
  );
}

