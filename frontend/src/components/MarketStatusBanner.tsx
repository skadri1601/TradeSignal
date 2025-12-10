/**
 * Market Status Banner Component
 *
 * Displays current US stock market status (open/closed) with animated indicator.
 * Based on TRUTH_FREE.md Phase 3.4 specifications.
 */

import { useQuery } from '@tanstack/react-query';

interface MarketStatus {
  is_open: boolean;
  status: string;
  reason: string;
  next_open?: string;
  closes_at?: string;
  time_until_close?: string;
  current_time_et: string;
  fallback_mode?: boolean;
}

const MarketStatusBanner = () => {
  const { data: marketStatus, isLoading } = useQuery<MarketStatus>({
    queryKey: ['market-status'],
    queryFn: async () => {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/stocks/market/status`);
      if (!response.ok) throw new Error('Failed to fetch market status');
      return response.json();
    },
    refetchInterval: 60000, // Check every minute
    staleTime: 50000,
    retry: 3,
  });

  if (isLoading || !marketStatus) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6 animate-pulse">
        <div className="h-4 bg-gray-300 rounded w-1/3"></div>
      </div>
    );
  }

  const isOpen = marketStatus.is_open;

  return (
    <div
      className={`rounded-lg p-4 mb-6 border ${
        isOpen
          ? 'bg-green-900/20 border-green-500/30'
          : 'bg-gray-900/50 border-white/10'
      }`}
    >
      <div className="flex items-center justify-between flex-wrap gap-3">
        {/* Status Indicator & Info */}
        <div className="flex items-center space-x-3">
          {/* Animated dot when open */}
          <div
            className={`w-3 h-3 rounded-full ${
              isOpen
                ? 'bg-green-500 animate-pulse'
                : 'bg-gray-400'
            }`}
          />

          <div>
            <h3 className="font-semibold text-white flex items-center gap-2">
              {isOpen ? (
                <>
                  <span className="text-green-400">🟢</span> Market is OPEN
                </>
              ) : (
                <>
                  <span className="text-gray-400">⚪</span> Market is CLOSED
                </>
              )}
              {marketStatus.fallback_mode && (
                <span className="text-xs bg-yellow-900/20 text-yellow-300 px-2 py-0.5 rounded">
                  Fallback Mode
                </span>
              )}
            </h3>
            <p className="text-sm text-gray-400">{marketStatus.reason}</p>
          </div>
        </div>

        {/* Timing Information */}
        <div className="text-sm text-gray-400">
          {isOpen ? (
            <div className="text-right">
              <div className="font-medium text-white">Closes at {marketStatus.closes_at}</div>
              <div className="text-xs text-gray-500">
                ({marketStatus.time_until_close} remaining)
              </div>
            </div>
          ) : (
            <div className="text-right">
              <div className="font-medium text-white">Next open:</div>
              <div className="text-xs text-gray-500">{marketStatus.next_open}</div>
            </div>
          )}
        </div>
      </div>

      {/* Warning when market is closed */}
      {!isOpen && (
        <div className="mt-3 text-xs text-yellow-300 bg-yellow-900/20 border border-yellow-500/30 rounded p-2 flex items-start gap-2">
          <span className="flex-shrink-0">⚠️</span>
          <div>
            <strong className="text-white">Market is closed.</strong> Prices shown are from last market close.
            Data is not updating in real-time.
          </div>
        </div>
      )}

      {/* Current ET Time */}
      <div className="mt-2 text-xs text-gray-500">
        Current time (ET): {marketStatus.current_time_et}
      </div>
    </div>
  );
};

export default MarketStatusBanner;
