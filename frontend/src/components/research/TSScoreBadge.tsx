import React from 'react';
import { Star, TrendingUp, Minus, TrendingDown, AlertTriangle } from 'lucide-react';

interface TSScoreBadgeProps {
  score: number; // 1-5 rating
  rating?: string; // "Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"
  priceToIVT?: number;
  riskAdjusted?: boolean;
  loading?: boolean;
}

export const TSScoreBadge: React.FC<TSScoreBadgeProps> = ({
  score,
  rating,
  priceToIVT,
  riskAdjusted = true,
  loading = false
}) => {
  // Default rating text based on score if not provided
  const getRatingText = () => {
    if (rating) return rating;
    if (score >= 4.5) return 'Strong Buy';
    if (score >= 3.5) return 'Buy';
    if (score >= 2.5) return 'Hold';
    if (score >= 1.5) return 'Sell';
    return 'Strong Sell';
  };

  // Color based on score
  const getScoreColor = () => {
    if (score >= 4) return 'bg-green-100 border-green-500 text-green-800';
    if (score >= 3) return 'bg-blue-100 border-blue-500 text-blue-800';
    if (score >= 2) return 'bg-yellow-100 border-yellow-500 text-yellow-800';
    return 'bg-red-100 border-red-500 text-red-800';
  };

  // Icon based on score
  const getIcon = () => {
    if (score >= 4) return <TrendingUp className="w-5 h-5 text-green-600" />;
    if (score >= 3) return <Minus className="w-5 h-5 text-blue-600" />;
    if (score >= 2) return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
    return <TrendingDown className="w-5 h-5 text-red-600" />;
  };

  // Render star rating visualization
  const renderStars = () => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      const isFilled = i <= Math.round(score);
      stars.push(
        <Star
          key={i}
          className={`w-4 h-4 ${
            isFilled
              ? 'fill-yellow-400 text-yellow-400'
              : 'fill-gray-300 text-gray-300'
          }`}
        />
      );
    }
    return stars;
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
    <div className={`border-2 rounded-lg p-4 ${getScoreColor()} transition-all duration-300 hover:shadow-md`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-semibold">TradeSignal Score</span>
        {getIcon()}
      </div>

      {/* Score Display */}
      <div className="mb-2">
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold">{score.toFixed(1)}</span>
          <span className="text-sm text-gray-600">/ 5.0</span>
        </div>
        <div className="flex gap-1 mt-1">
          {renderStars()}
        </div>
      </div>

      {/* Rating Text */}
      <div className="mb-2">
        <span className={`text-lg font-semibold ${
          score >= 4 ? 'text-green-700' :
          score >= 3 ? 'text-blue-700' :
          score >= 2 ? 'text-yellow-700' :
          'text-red-700'
        }`}>
          {getRatingText()}
        </span>
      </div>

      {/* Additional Info */}
      {priceToIVT && (
        <div className="text-xs text-gray-600 mb-1">
          Price/IVT Ratio: {priceToIVT.toFixed(2)}x
        </div>
      )}

      {riskAdjusted && (
        <div className="text-xs text-gray-500">
          <span className="font-semibold">✓ Risk-adjusted</span>
        </div>
      )}

      {/* Explanation */}
      <div className="mt-2 text-xs text-gray-600 border-t border-gray-300 pt-2">
        {score >= 4 && <p>Strong buy signal based on valuation & fundamentals</p>}
        {score >= 3 && score < 4 && <p>Buy signal - stock appears attractive</p>}
        {score >= 2 && score < 3 && <p>Hold - stock fairly valued at current levels</p>}
        {score < 2 && <p>Caution - stock may be overvalued</p>}
      </div>
    </div>
  );
};

export default TSScoreBadge;
