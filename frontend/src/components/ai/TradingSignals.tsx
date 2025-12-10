import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { aiApi, TradingSignal } from '../../api/ai';
import AISkeleton from '../common/AISkeleton';
import { TrendingUp, TrendingDown, MinusCircle, AlertCircle, RefreshCw } from 'lucide-react';

export default function TradingSignals() {
  const [showAll, setShowAll] = useState(false);
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['tradingSignals'],
    queryFn: () => aiApi.getTradingSignals(),
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  });

  const getSignalColor = (signal: string) => {
    const s = signal.toLowerCase();
    if (s === 'bullish') return 'text-green-400';
    if (s === 'bearish') return 'text-red-400';
    return 'text-gray-400';
  };

  const getSignalBg = (signal: string) => {
    const s = signal.toLowerCase();
    if (s === 'bullish') return 'bg-green-500/10 border-green-500/20';
    if (s === 'bearish') return 'bg-red-500/10 border-red-500/20';
    return 'bg-gray-800/50 border-white/10';
  };

  const getSignalIcon = (signal: string) => {
    const s = signal.toLowerCase();
    if (s === 'bullish') return <TrendingUp className="h-6 w-6" />;
    if (s === 'bearish') return <TrendingDown className="h-6 w-6" />;
    return <MinusCircle className="h-6 w-6" />;
  };

  const getStrengthBadge = (strength: string) => {
    const s = strength.toLowerCase();
    if (s === 'strong') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">
          STRONG
        </span>
      );
    }
    if (s === 'moderate') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-yellow-500/20 text-yellow-300 border border-yellow-500/30">
          MODERATE
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-gray-700 text-gray-400 border border-gray-600">
        WEAK
      </span>
    );
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-bold text-white">AI Trading Signals</h2>
              <div className="mt-4">
                <AISkeleton message="Generating AI trading signals..." />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (isError) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    return (
      <div className="bg-red-900/20 border border-red-500/30 rounded-2xl p-6 flex items-start space-x-4">
        <AlertCircle className="h-6 w-6 text-red-400 flex-shrink-0" />
        <div className="flex-1">
          <h3 className="text-lg font-medium text-red-300">Failed to load signals</h3>
          <p className="text-sm text-red-400/80 mt-1">{errorMessage}</p>
          <button
            onClick={() => refetch()}
            className="mt-4 px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-300 rounded-lg transition-colors text-sm font-medium border border-red-500/30"
          >
            Retry Analysis
          </button>
        </div>
      </div>
    );
  }

  if (!data || data.signals.length === 0) {
    return (
      <div className="bg-gray-900/30 border border-white/10 rounded-2xl p-12 text-center">
        <MinusCircle className="mx-auto h-12 w-12 text-gray-600 mb-4" />
        <h3 className="mt-2 text-lg font-medium text-white">No Signals Available</h3>
        <p className="mt-1 text-sm text-gray-400">
          No significant insider trading activity detected in the last 7 days.
        </p>
        <button
          onClick={() => refetch()}
          className="mt-6 px-6 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-colors border border-white/10"
        >
          Refresh Signals
        </button>
      </div>
    );
  }

  const displayedSignals = showAll ? data.signals : data.signals.slice(0, 6);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10 p-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">AI Trading Signals</h2>
          <p className="text-sm text-gray-400 mt-1">
            Based on {data.days_analyzed} days of activity • {data.signals.length} signals detected
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="p-2 text-gray-400 hover:text-white bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
          title="Refresh Signals"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      {/* Signals Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {displayedSignals.map((signal: TradingSignal, index: number) => (
          <div
            key={index}
            className={`rounded-2xl p-6 border-2 transition-all hover:shadow-lg hover:-translate-y-1 ${getSignalBg(signal.signal)}`}
          >
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-center space-x-4">
                <div className={`p-2 rounded-full bg-black/20 ${getSignalColor(signal.signal)}`}>
                  {getSignalIcon(signal.signal)}
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white tracking-tight">
                    {signal.ticker} <span className="text-gray-400 font-normal text-sm ml-1">- {signal.company_name}</span>
                  </h3>
                  <p className="text-xs text-gray-400 mt-0.5">{signal.total_trades} insider trades</p>
                </div>
              </div>
              {getStrengthBadge(signal.strength)}
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-black/20 rounded-lg p-3">
                <span className="text-xs text-gray-500 uppercase tracking-wide">Buy Ratio</span>
                <p className="text-lg font-mono font-semibold text-white mt-1">{(signal.buy_ratio * 100).toFixed(1)}%</p>
              </div>
              <div className="bg-black/20 rounded-lg p-3">
                <span className="text-xs text-gray-500 uppercase tracking-wide">Total Value</span>
                <p className="text-lg font-mono font-semibold text-white mt-1">${(signal.total_value / 1_000_000).toFixed(2)}M</p>
              </div>
            </div>

            {signal.reasoning && (
              <div className="pt-4 border-t border-black/10">
                <p className="text-sm text-gray-300 italic leading-relaxed">"{signal.reasoning}"</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* See More Button */}
      {data.signals.length > 6 && (
        <div className="text-center pt-4">
          <button
            onClick={() => setShowAll(!showAll)}
            className="px-8 py-3 bg-white/5 hover:bg-white/10 text-white rounded-full font-medium transition-all border border-white/10 hover:border-white/20"
          >
            {showAll ? 'Show Less' : `View All ${data.signals.length} Signals`}
          </button>
        </div>
      )}

      <div className="text-center">
        <p className="text-xs text-gray-600 mt-8">
          Signals generated on {new Date(data.timestamp || data.generated_at).toLocaleString()}
        </p>
      </div>
    </div>
  );
}