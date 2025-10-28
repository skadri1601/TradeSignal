import { useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { tradesApi } from '../api/trades';
import { TrendingUp, TrendingDown, Building2 } from 'lucide-react';
import { formatCurrency, formatNumber } from '../utils/formatters';
import LoadingSpinner from '../components/common/LoadingSpinner';
import TradeList from '../components/trades/TradeList';
import useTradeStream from '../hooks/useTradeStream';
import type { Trade } from '../types';

export default function Dashboard() {
  const queryClient = useQueryClient();

  // Calculate date 7 days ago
  const sevenDaysAgo = new Date();
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
  const dateFrom = sevenDaysAgo.toISOString().split('T')[0];

  // Fetch trade stats (last 7 days)
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['tradeStats', 'last7days'],
    queryFn: () => tradesApi.getTradeStats({ transaction_date_from: dateFrom }),
  });

  // Fetch recent trades
  const { data: recentTrades, isLoading: tradesLoading } = useQuery({
    queryKey: ['recentTrades'],
    queryFn: () => tradesApi.getRecentTrades(7),
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Insider trading activity - Last 7 Days</p>
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
              <p className="text-sm font-medium text-gray-600">Buy Volume (7d)</p>
              <p className="text-2xl font-bold text-green-600">
                {formatCurrency(stats?.total_buy_value || 0)}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {formatNumber(stats?.total_buys || 0)} trades
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
              <p className="text-sm font-medium text-gray-600">Sell Volume (7d)</p>
              <p className="text-2xl font-bold text-red-600">
                {formatCurrency(stats?.total_sell_value || 0)}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {formatNumber(stats?.total_sells || 0)} trades
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
                Avg trade: {formatCurrency(stats?.average_trade_size || 0)}
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg flex-shrink-0">
              <Building2 className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Recent Trades */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Trades (Last 7 Days)</h2>
        {tradesLoading ? (
          <div className="flex items-center justify-center h-32">
            <LoadingSpinner />
          </div>
        ) : (
          <TradeList trades={recentTrades || []} />
        )}
      </div>
    </div>
  );
}
