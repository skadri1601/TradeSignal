import { useCallback, useState } from 'react';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { tradesApi } from '../api/trades';
import { TrendingUp, TrendingDown, Building2, ArrowRight, RefreshCw, AlertCircle } from 'lucide-react';
import { formatNumber, formatCurrencyCompact } from '../utils/formatters';
import LoadingSpinner from '../components/common/LoadingSpinner';
import TradeList from '../components/trades/TradeList';
import TradePieChart from '../components/trades/TradePieChart';
import MarketSummaryCard from '../components/stocks/MarketSummaryCard';
import useTradeStream from '../hooks/useTradeStream';
import type { Trade } from '../types';
import { LegalDisclaimer } from '../components/LegalDisclaimer';

export default function Dashboard() {
  const queryClient = useQueryClient();
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  // Calculate date 7 days ago
  const sevenDaysAgo = new Date();
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
  const dateFrom = sevenDaysAgo.toISOString().split('T')[0];

  // Fetch trade stats (last 7 days)
  const { data: stats, isLoading: statsLoading, error: statsError } = useQuery({
    queryKey: ['tradeStats', 'last7days'],
    queryFn: async () => {
      try {
        const result = await tradesApi.getTradeStats({ transaction_date_from: dateFrom });
        setLastUpdated(new Date());
        return result;
      } catch (error: any) {
        console.error('Error fetching trade stats:', error);
        throw new Error(error?.message || 'Failed to fetch trade statistics');
      }
    },
    retry: (failureCount) => {
      // Retry up to 3 times with exponential backoff
      if (failureCount < 3) {
        return true;
      }
      return false;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    staleTime: 30000, // Consider data stale after 30 seconds
  });

  // Fetch recent trades
  const { data: recentTrades, isLoading: tradesLoading, error: tradesError } = useQuery({
    queryKey: ['recentTrades'],
    queryFn: async () => {
      try {
        return await tradesApi.getRecentTrades(7);
      } catch (error: any) {
        console.error('Error fetching recent trades:', error);
        throw new Error(error?.message || 'Failed to fetch recent trades');
      }
    },
    retry: (failureCount) => {
      // Retry up to 3 times with exponential backoff
      if (failureCount < 3) {
        return true;
      }
      return false;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    staleTime: 30000,
  });

  // Refresh data
  const refreshMutation = useMutation({
    mutationFn: async () => {
      await queryClient.invalidateQueries({ queryKey: ['tradeStats'] });
      await queryClient.invalidateQueries({ queryKey: ['recentTrades'] });
    },
    onSuccess: () => {
      setLastUpdated(new Date());
    },
  });

  const handleStreamMessage = useCallback(
    (payload: { type?: string; trade?: Trade }) => {
      if (!payload || typeof payload !== 'object') return;

      if (payload.type === 'trade_created' || payload.type === 'trade_updated') {
        const trade = payload.trade;
        if (!trade) return;

        queryClient.setQueryData<Trade[] | undefined>(['recentTrades'], (current) => {
          const existing = current ?? [];
          const filtered = existing.filter(item => item.id !== trade.id);
          return [trade, ...filtered].slice(0, 100);
        });

        queryClient.invalidateQueries({ queryKey: ['tradeStats'] });
        queryClient.invalidateQueries({ queryKey: ['trades'] });
      }
    },
    [queryClient]
  );

  useTradeStream(handleStreamMessage);

  if (statsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (statsError) {
    return (
      <div className="space-y-6">
        <LegalDisclaimer />
        <div className="card">
          <div className="text-center py-12">
            <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-3" />
            <p className="text-gray-500 mb-2">Failed to load dashboard data</p>
            <p className="text-sm text-gray-400 mb-4">{statsError instanceof Error ? statsError.message : 'Unknown error'}</p>
            <button
              onClick={() => refreshMutation.mutate()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Format last updated time
  const formatLastUpdated = () => {
    const now = new Date();
    const diff = Math.floor((now.getTime() - lastUpdated.getTime()) / 1000); // seconds

    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return lastUpdated.toLocaleTimeString();
  };

  return (
    <div className="space-y-6">
      <LegalDisclaimer />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">Insider trading activity - Last 7 Days</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <p className="text-xs text-gray-500">Last updated</p>
            <p className="text-sm font-medium text-gray-700">{formatLastUpdated()}</p>
          </div>
          <button
            onClick={() => refreshMutation.mutate()}
            disabled={refreshMutation.isPending}
            className={`flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors ${
              refreshMutation.isPending ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <RefreshCw className={`h-4 w-4 ${refreshMutation.isPending ? 'animate-spin' : ''}`} />
            <span>{refreshMutation.isPending ? 'Refreshing...' : 'Refresh Data'}</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Trades */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Trades (7d)</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatNumber(stats?.total_trades || 0)}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        {/* Buy Trades */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Buy Trades (7d)</p>
              <p className="text-2xl font-bold text-green-600">
                {formatNumber(stats?.total_buys || 0)}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {((stats?.total_buys || 0) / (stats?.total_trades || 1) * 100).toFixed(1)}% of total
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        {/* Sell Trades */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Sell Trades (7d)</p>
              <p className="text-2xl font-bold text-red-600">
                {formatNumber(stats?.total_sells || 0)}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {((stats?.total_sells || 0) / (stats?.total_trades || 1) * 100).toFixed(1)}% of total
              </p>
            </div>
            <div className="p-3 bg-red-100 rounded-lg">
              <TrendingDown className="h-6 w-6 text-red-600" />
            </div>
          </div>
        </div>

        {/* Most Active */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0 pr-2">
              <p className="text-sm font-medium text-gray-600">Most Active</p>
              <p className="text-2xl font-bold text-gray-900 break-words">
                {stats?.most_active_company || 'N/A'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Avg trade: {formatCurrencyCompact(stats?.average_trade_size || 0)}
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg flex-shrink-0">
              <Building2 className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Trade Distribution Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Buy vs Sell Count */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Buy vs Sell (Trade Count)
          </h2>
          <TradePieChart stats={stats} mode="count" />
        </div>

        {/* Buy vs Sell Volume */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Buy vs Sell (Dollar Volume)
          </h2>
          <TradePieChart stats={stats} mode="value" />
        </div>
      </div>

      {/* Market Summary - Top Gainers/Losers */}
      <MarketSummaryCard />

      {/* Recent Trades */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Recent Trades</h2>
          <Link
            to="/trades"
            className="flex items-center text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
          >
            View All
            <ArrowRight className="ml-1 h-4 w-4" />
          </Link>
        </div>
        {tradesLoading ? (
          <div className="flex items-center justify-center h-32">
            <LoadingSpinner />
          </div>
        ) : tradesError ? (
          <div className="text-center py-12">
            <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-3" />
            <p className="text-gray-500 mb-2">Failed to load recent trades</p>
            <p className="text-sm text-gray-400">{tradesError instanceof Error ? tradesError.message : 'Unknown error'}</p>
            <button
              onClick={() => refreshMutation.mutate()}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Retry
            </button>
          </div>
        ) : (recentTrades || []).length === 0 ? (
          <div className="text-center py-12">
            <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-500">No recent trades found</p>
            <p className="text-sm text-gray-400 mt-1">Trades will appear here once data is scraped</p>
          </div>
        ) : (
          <>
            <TradeList trades={(recentTrades || []).slice(0, 5)} />
            {(recentTrades || []).length > 5 && (
              <div className="mt-4 text-center">
                <Link
                  to="/trades"
                  className="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                >
                  View all {(recentTrades || []).length} trades
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
