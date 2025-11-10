import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { aiApi, TradingSignal } from '../../api/ai';
import LoadingSpinner from '../common/LoadingSpinner';

export default function TradingSignals() {
  const [showAll, setShowAll] = useState(false);
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['tradingSignals'],
    queryFn: () => aiApi.getTradingSignals(),
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  });

  const getSignalColor = (signal: string) => {
    const s = signal.toLowerCase();
    if (s === 'bullish') return 'text-green-600';
    if (s === 'bearish') return 'text-red-600';
    return 'text-gray-600';
  };

  const getSignalBg = (signal: string) => {
    const s = signal.toLowerCase();
    if (s === 'bullish') return 'bg-green-100 border-green-200';
    if (s === 'bearish') return 'bg-red-100 border-red-200';
    return 'bg-gray-100 border-gray-200';
  };

  const getSignalIcon = (signal: string) => {
    const s = signal.toLowerCase();
    if (s === 'bullish') {
      return (
        <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z"
            clipRule="evenodd"
          />
        </svg>
      );
    }
    if (s === 'bearish') {
      return (
        <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z"
            clipRule="evenodd"
          />
        </svg>
      );
    }
    return (
      <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z"
          clipRule="evenodd"
        />
      </svg>
    );
  };

  const getStrengthBadge = (strength: string) => {
    const s = strength.toLowerCase();
    if (s === 'strong') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          Strong
        </span>
      );
    }
    if (s === 'moderate') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          Moderate
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
        Weak
      </span>
    );
  };

  if (isLoading) {
    return (
      <div className="card flex items-center justify-center py-12">
        <div className="text-center">
          <LoadingSpinner />
          <p className="text-gray-600 mt-4">Generating trading signals...</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="card bg-red-50 border border-red-200">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3 flex-1">
            <h3 className="text-sm font-medium text-red-800">Failed to Load Signals</h3>
            <p className="text-sm text-red-700 mt-1">
              {error instanceof Error ? error.message : 'An error occurred while loading trading signals.'}
            </p>
            <button
              onClick={() => refetch()}
              className="mt-3 text-sm font-medium text-red-600 hover:text-red-500"
            >
              Try again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!data || data.signals.length === 0) {
    return (
      <div className="card bg-gray-50">
        <div className="text-center py-12">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No Signals Available</h3>
          <p className="mt-1 text-sm text-gray-500">
            No significant insider trading activity detected in the last 7 days.
          </p>
          <button
            onClick={() => refetch()}
            className="mt-4 btn btn-secondary"
          >
            Refresh Signals
          </button>
        </div>
      </div>
    );
  }

  // Filter signals - show top 6 by default, sorted by significance
  const displayedSignals = showAll ? data.signals : data.signals.slice(0, 6);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900">AI Trading Signals</h2>
            <p className="text-sm text-gray-600 mt-1">
              Based on {data.days_analyzed} days of insider trading activity • {data.signals.length} signals detected
            </p>
          </div>
          <button
            onClick={() => refetch()}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Signals Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {displayedSignals.map((signal: TradingSignal, index: number) => (
          <div
            key={index}
            className={`card border-2 ${getSignalBg(signal.signal)}`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className={getSignalColor(signal.signal)}>
                  {getSignalIcon(signal.signal)}
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">
                    {signal.ticker} - {signal.company_name}
                  </h3>
                  <p className="text-sm text-gray-600">{signal.total_trades} trades</p>
                </div>
              </div>
              {getStrengthBadge(signal.strength)}
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Signal:</span>
                <span className={`font-semibold ${getSignalColor(signal.signal)}`}>
                  {signal.signal.toUpperCase()}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Strength:</span>
                <span className="font-medium text-gray-900">{signal.strength}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Buy Ratio:</span>
                <span className="font-medium text-gray-900">
                  {(signal.buy_ratio * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Total Value:</span>
                <span className="font-medium text-gray-900">
                  ${(signal.total_value / 1_000_000).toFixed(2)}M
                </span>
              </div>
            </div>

            {signal.reasoning && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-sm text-gray-700">{signal.reasoning}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* See More Button */}
      {data.signals.length > 6 && (
        <div className="text-center">
          <button
            onClick={() => setShowAll(!showAll)}
            className="btn btn-secondary inline-flex items-center"
          >
            {showAll ? (
              <>
                <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                </svg>
                Show Less
              </>
            ) : (
              <>
                <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
                See More ({data.signals.length - 6} additional signals)
              </>
            )}
          </button>
        </div>
      )}

      {/* Disclaimer */}
      <div className="card bg-yellow-50 border border-yellow-200">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">Disclaimer</h3>
            <p className="text-sm text-yellow-700 mt-1">
              These signals are AI-generated based on insider trading patterns and should not be considered
              financial advice. Always do your own research and consult with a financial advisor before making
              investment decisions.
            </p>
          </div>
        </div>
      </div>

      {/* Timestamp */}
      <div className="text-center">
        <p className="text-xs text-gray-500">
          Signals generated on {new Date(data.timestamp).toLocaleString()}
        </p>
      </div>
    </div>
  );
}
