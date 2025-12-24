import { TrendingUp, Target, AlertCircle, Calendar, DollarSign } from 'lucide-react';

interface PricePrediction {
  timeframe: string;
  target_price: number;
  upside_pct: number;
  probability: number;
}

interface PricePredictionCardProps {
  ticker: string;
  currentPrice?: number;
  predictions: PricePrediction[];
  recommendation?: string;
  riskLevel?: string;
  disclaimer?: string;
}

export default function PricePredictionCard({
  ticker,
  currentPrice,
  predictions,
  recommendation,
  riskLevel,
  disclaimer,
}: PricePredictionCardProps) {
  const getTimeframeLabel = (timeframe: string): string => {
    const labels: Record<string, string> = {
      '1week': '1 Week',
      '1month': '1 Month',
      '3months': '3 Months',
      '6months': '6 Months',
      '1year': '1 Year',
    };
    return labels[timeframe] || timeframe;
  };

  const getRecommendationColor = (rec?: string): string => {
    if (!rec) return 'text-gray-300';
    if (rec.includes('BUY')) return 'text-green-400';
    if (rec.includes('SELL')) return 'text-red-400';
    return 'text-gray-300';
  };

  const getRiskColor = (risk?: string): string => {
    if (!risk) return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
    if (risk === 'HIGH') return 'bg-red-500/20 text-red-300 border-red-500/30';
    if (risk === 'MEDIUM') return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
    return 'bg-green-500/20 text-green-300 border-green-500/30';
  };

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm border border-white/10 rounded-2xl p-6 relative overflow-hidden">
      {/* Gradient Background */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-green-600/10 blur-[60px] rounded-full pointer-events-none -z-10" />

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-green-500/10 p-2.5 rounded-xl border border-green-500/20">
            <Target className="w-5 h-5 text-green-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">LUNA Price Predictions</h3>
            <p className="text-sm text-gray-400">{ticker}</p>
          </div>
        </div>
        {currentPrice && (
          <div className="text-right">
            <p className="text-xs text-gray-500 uppercase font-bold">Current Price</p>
            <p className="text-xl font-mono text-white">${currentPrice.toFixed(2)}</p>
          </div>
        )}
      </div>

      {/* Recommendation & Risk */}
      {(recommendation || riskLevel) && (
        <div className="grid grid-cols-2 gap-4 mb-6">
          {recommendation && (
            <div className="bg-white/5 rounded-xl p-4 border border-white/5">
              <p className="text-xs text-gray-500 uppercase font-bold mb-2">Recommendation</p>
              <p className={`text-lg font-bold ${getRecommendationColor(recommendation)}`}>
                {recommendation.replace('_', ' ')}
              </p>
            </div>
          )}
          {riskLevel && (
            <div className="bg-white/5 rounded-xl p-4 border border-white/5">
              <p className="text-xs text-gray-500 uppercase font-bold mb-2">Risk Level</p>
              <div className={`inline-flex items-center px-2.5 py-1 rounded-md text-sm font-bold border ${getRiskColor(riskLevel)}`}>
                {riskLevel} RISK
              </div>
            </div>
          )}
        </div>
      )}

      {/* Price Predictions Grid */}
      <div className="space-y-3 mb-6">
        <h4 className="text-sm font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
          <Calendar className="w-4 h-4" />
          Price Targets
        </h4>
        {predictions.map((pred, index) => {
          const isPositive = pred.upside_pct >= 0;
          const probabilityPercent = (pred.probability * 100).toFixed(0);

          return (
            <div
              key={pred.timeframe}
              className="bg-black/20 rounded-xl p-4 border border-white/5 hover:border-white/10 transition-all"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className={`w-1.5 h-1.5 rounded-full ${index === 0 ? 'bg-green-400' : index === 1 ? 'bg-blue-400' : index === 2 ? 'bg-purple-400' : 'bg-gray-400'}`} />
                  <span className="text-sm font-semibold text-gray-300">{getTimeframeLabel(pred.timeframe)}</span>
                </div>
                <div className="flex items-center gap-2">
                  <DollarSign className="w-4 h-4 text-gray-500" />
                  <span className="text-lg font-mono font-bold text-white">
                    {pred.target_price.toFixed(2)}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <TrendingUp className={`w-4 h-4 ${isPositive ? 'text-green-400' : 'text-red-400'}`} />
                  <span className={isPositive ? 'text-green-400' : 'text-red-400'}>
                    {isPositive ? '+' : ''}{pred.upside_pct.toFixed(1)}%
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-16 bg-gray-700 h-1.5 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-purple-500 to-blue-500"
                      style={{ width: `${probabilityPercent}%` }}
                    />
                  </div>
                  <span className="text-gray-400 text-xs font-mono">{probabilityPercent}%</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Disclaimer */}
      {disclaimer && (
        <div className="bg-yellow-900/10 border border-yellow-500/20 rounded-xl p-4 flex items-start gap-3">
          <AlertCircle className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
          <p className="text-xs text-yellow-200/80 leading-relaxed">
            {disclaimer}
          </p>
        </div>
      )}

      {!disclaimer && (
        <div className="bg-gray-900/30 border border-white/5 rounded-xl p-4">
          <p className="text-xs text-gray-500 leading-relaxed">
            This analysis is for educational and informational purposes only. It does not constitute investment advice.
            Past performance is not indicative of future results. Always consult with a licensed financial advisor before making investment decisions.
          </p>
        </div>
      )}
    </div>
  );
}
