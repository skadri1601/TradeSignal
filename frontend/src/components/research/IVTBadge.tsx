import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface IVTBadgeProps {
  currentPrice: number;
  intrinsicValue: number;
  discountPct: number;
  calculationDate?: string;
  loading?: boolean;
}

export const IVTBadge: React.FC<IVTBadgeProps> = ({
  currentPrice,
  intrinsicValue,
  discountPct,
  calculationDate,
  loading = false
}) => {
  // Determine if stock is undervalued, overvalued, or fairly valued
  const isUndervalued = discountPct < -5; // More than 5% discount
  const isOvervalued = discountPct > 5; // More than 5% premium
  const isFairlyValued = !isUndervalued && !isOvervalued;

  // Color coding based on valuation
  const getBadgeColor = () => {
    if (isUndervalued) return 'bg-green-100 border-green-500 text-green-800';
    if (isOvervalued) return 'bg-red-100 border-red-500 text-red-800';
    return 'bg-gray-100 border-gray-500 text-gray-800';
  };

  // Icon based on valuation
  const getIcon = () => {
    if (isUndervalued) return <TrendingDown className="w-5 h-5" />;
    if (isOvervalued) return <TrendingUp className="w-5 h-5" />;
    return <Minus className="w-5 h-5" />;
  };

  // Value label
  const getValueLabel = () => {
    if (isUndervalued) return 'Undervalued';
    if (isOvervalued) return 'Overvalued';
    return 'Fairly Valued';
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
        <span className="text-sm font-semibold">Intrinsic Value</span>
        {getIcon()}
      </div>

      {/* Intrinsic Value */}
      <div className="mb-2">
        <div className="text-2xl font-bold">
          ${intrinsicValue.toFixed(2)}
        </div>
        <div className="text-xs text-gray-600">
          Current: ${currentPrice.toFixed(2)}
        </div>
      </div>

      {/* Discount/Premium Percentage */}
      <div className="flex items-center justify-between">
        <span className={`text-sm font-semibold ${
          isUndervalued ? 'text-green-700' :
          isOvervalued ? 'text-red-700' :
          'text-gray-700'
        }`}>
          {getValueLabel()}
        </span>
        <span className={`text-lg font-bold ${
          isUndervalued ? 'text-green-700' :
          isOvervalued ? 'text-red-700' :
          'text-gray-700'
        }`}>
          {discountPct > 0 ? '+' : ''}{discountPct.toFixed(1)}%
        </span>
      </div>

      {/* Calculation Date */}
      {calculationDate && (
        <div className="mt-2 text-xs text-gray-500">
          Updated: {new Date(calculationDate).toLocaleDateString()}
        </div>
      )}

      {/* Tooltip explanation */}
      <div className="mt-2 text-xs text-gray-600 border-t border-gray-300 pt-2">
        {isUndervalued && (
          <p>Stock trading {Math.abs(discountPct).toFixed(1)}% below estimated fair value</p>
        )}
        {isOvervalued && (
          <p>Stock trading {discountPct.toFixed(1)}% above estimated fair value</p>
        )}
        {isFairlyValued && (
          <p>Stock trading near estimated fair value</p>
        )}
      </div>
    </div>
  );
};

export default IVTBadge;
