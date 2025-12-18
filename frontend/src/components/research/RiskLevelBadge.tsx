import React from 'react';
import { Shield, ShieldAlert, ShieldCheck, AlertCircle, Activity } from 'lucide-react';

interface RiskLevelBadgeProps {
  level: string; // "Conservative", "Moderate", "Aggressive", "Speculative", "High"
  category?: string;
  volatilityScore?: number;
  loading?: boolean;
}

export const RiskLevelBadge: React.FC<RiskLevelBadgeProps> = ({
  level,
  category,
  volatilityScore,
  loading = false
}) => {
  // Normalize level to ensure consistency
  const normalizedLevel = level.toLowerCase();

  // Color coding based on risk level
  const getBadgeColor = () => {
    if (normalizedLevel === 'conservative') return 'bg-blue-100 border-blue-500 text-blue-800';
    if (normalizedLevel === 'moderate') return 'bg-green-100 border-green-500 text-green-800';
    if (normalizedLevel === 'aggressive') return 'bg-yellow-100 border-yellow-500 text-yellow-800';
    if (normalizedLevel === 'speculative') return 'bg-orange-100 border-orange-500 text-orange-800';
    if (normalizedLevel === 'high') return 'bg-red-100 border-red-500 text-red-800';
    return 'bg-gray-100 border-gray-500 text-gray-800';
  };

  // Icon based on risk level
  const getIcon = () => {
    if (normalizedLevel === 'conservative') return <ShieldCheck className="w-5 h-5 text-blue-600" />;
    if (normalizedLevel === 'moderate') return <Shield className="w-5 h-5 text-green-600" />;
    if (normalizedLevel === 'aggressive') return <Activity className="w-5 h-5 text-yellow-600" />;
    if (normalizedLevel === 'speculative') return <ShieldAlert className="w-5 h-5 text-orange-600" />;
    if (normalizedLevel === 'high') return <AlertCircle className="w-5 h-5 text-red-600" />;
    return <Shield className="w-5 h-5 text-gray-600" />;
  };

  // Risk level description
  const getDescription = () => {
    if (normalizedLevel === 'conservative') return 'Low risk, stable cash flows';
    if (normalizedLevel === 'moderate') return 'Moderate risk, balanced growth';
    if (normalizedLevel === 'aggressive') return 'Higher risk, growth-oriented';
    if (normalizedLevel === 'speculative') return 'High risk, unproven model';
    if (normalizedLevel === 'high') return 'Very high risk, binary outcomes';
    return 'Risk level not assessed';
  };

  // Risk bar visualization (1-5 scale)
  const getRiskScore = () => {
    if (normalizedLevel === 'conservative') return 1;
    if (normalizedLevel === 'moderate') return 2;
    if (normalizedLevel === 'aggressive') return 3;
    if (normalizedLevel === 'speculative') return 4;
    if (normalizedLevel === 'high') return 5;
    return 0;
  };

  const renderRiskBar = () => {
    const riskScore = getRiskScore();
    const bars = [];
    for (let i = 1; i <= 5; i++) {
      const isActive = i <= riskScore;
      const barColor =
        i <= 1 ? 'bg-blue-500' :
        i <= 2 ? 'bg-green-500' :
        i <= 3 ? 'bg-yellow-500' :
        i <= 4 ? 'bg-orange-500' :
        'bg-red-500';

      bars.push(
        <div
          key={i}
          className={`h-2 flex-1 rounded ${
            isActive ? barColor : 'bg-gray-300'
          }`}
        />
      );
    }
    return bars;
  };

  if (loading) {
    return (
      <div className="border border-gray-300 rounded-lg p-4 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
        <div className="h-6 bg-gray-200 rounded w-1/2"></div>
      </div>
    );
  }

  return (
    <div className={`border-2 rounded-lg p-4 ${getBadgeColor()} transition-all duration-300 hover:shadow-md`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-semibold">Risk Level</span>
        {getIcon()}
      </div>

      {/* Risk Level Text */}
      <div className="mb-2">
        <div className="text-2xl font-bold capitalize">
          {level}
        </div>
        {category && (
          <div className="text-xs text-gray-600 mt-1">
            Category: {category}
          </div>
        )}
      </div>

      {/* Risk Visualization Bar */}
      <div className="flex gap-1 mb-2">
        {renderRiskBar()}
      </div>

      {/* Risk Score */}
      <div className="text-xs text-gray-600 mb-1">
        Risk Score: {getRiskScore()}/5
      </div>

      {/* Volatility Score (if available) */}
      {volatilityScore !== undefined && (
        <div className="text-xs text-gray-600 mb-2">
          Volatility: {(volatilityScore * 100).toFixed(1)}%
        </div>
      )}

      {/* Description */}
      <div className="mt-2 text-xs text-gray-600 border-t border-gray-300 pt-2">
        <p>{getDescription()}</p>
      </div>
    </div>
  );
};

export default RiskLevelBadge;
