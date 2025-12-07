/**
 * Modern Trading Dashboard - Redesigned
 * Inspired by modern trading apps
 */

import { useQuery } from '@tanstack/react-query';
import { tradesApi } from '../api/trades';
import { stocksApi } from '../api/stocks';
import { TrendingUp, TrendingDown, ArrowRight, Clock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import CompanyLogo from '../components/CompanyLogo';

export default function DashboardNew() {
  const navigate = useNavigate();

  // Fetch recent trades
  const { data: recentTrades, isLoading: loadingTrades } = useQuery({
    queryKey: ['recentTrades'],
    queryFn: () => tradesApi.getRecentTrades(7),
  });

  // Fetch trade statistics
  const { data: tradeStats, isLoading: loadingTradeStats } = useQuery({
    queryKey: ['tradeStats'],
    queryFn: () => tradesApi.getTradeStats(),
  });

  // Get top 5 most active tickers from recent trades for watchlist
  const watchlistTickers = Array.from(
    new Set(recentTrades?.slice(0, 10).map(t => t.company?.ticker).filter(Boolean))
  ).slice(0, 5);

  // Fetch live quotes for watchlist
  const { data: watchlistQuotes, isLoading: loadingWatchlist } = useQuery({
    queryKey: ['watchlist', watchlistTickers],
    queryFn: () => stocksApi.getMultipleQuotes(watchlistTickers as string[]),
    enabled: watchlistTickers.length > 0,
  });

  // Fetch top movers (companies with most insider trading activity)
  const topMoversTickers = Array.from(
    new Set(recentTrades?.slice(0, 15).map(t => t.company?.ticker).filter(Boolean))
  ).slice(0, 3);

  const { data: topMoversQuotes } = useQuery({
    queryKey: ['topMovers', topMoversTickers],
    queryFn: () => stocksApi.getMultipleQuotes(topMoversTickers as string[]),
    enabled: topMoversTickers.length > 0,
  });

  // Latest insider activity (replace "news")
  const latestActivity = recentTrades?.slice(0, 3) || [];

  const formatNumber = (value?: number | null) => {
    if (value === undefined || value === null) return '--';
    return value.toLocaleString();
  };

  const formatCurrency = (value?: number | null) => {
    if (value === undefined || value === null) return '--';
    if (value >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(1)}B`;
    if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
    if (value >= 1_000) return `$${(value / 1_000).toFixed(1)}K`;
    return `$${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
  };

  const metricCards = [
    {
      key: 'totalTrades',
      label: 'Total Trades',
      value: tradeStats?.total_trades,
      icon: ArrowRight,
      accent: 'text-blue-500',
      formatter: formatNumber,
      subtext: tradeStats
        ? `${formatNumber(tradeStats.total_buys)} buys / ${formatNumber(tradeStats.total_sells)} sells`
        : undefined,
    },
    {
      key: 'totalBuyVolume',
      label: 'Buy Volume',
      value: tradeStats?.total_buy_value,
      icon: TrendingUp,
      accent: 'text-emerald-500',
      formatter: formatCurrency,
      subtext: tradeStats ? `${formatNumber(tradeStats.total_buys)} buy orders` : undefined,
    },
    {
      key: 'totalSellVolume',
      label: 'Sell Volume',
      value: tradeStats?.total_sell_value,
      icon: TrendingDown,
      accent: 'text-rose-500',
      formatter: formatCurrency,
      subtext: tradeStats ? `${formatNumber(tradeStats.total_sells)} sell orders` : undefined,
    },
    {
      key: 'averageTrade',
      label: 'Avg Trade Size',
      value: tradeStats?.average_trade_size,
      icon: Clock,
      accent: 'text-amber-500',
      formatter: formatCurrency,
      subtext: tradeStats?.most_active_company ? `Top: ${tradeStats.most_active_company}` : undefined,
    },
  ];

  const MiniChart = ({ color, trending }: { color: string; trending: string }) => (
    <svg width="60" height="24" viewBox="0 0 60 24" className={color}>
      {trending === 'up' ? (
        <polyline
          points="0,20 15,15 30,18 45,8 60,5"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        />
      ) : (
        <polyline
          points="0,5 15,8 30,6 45,15 60,20"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        />
      )}
    </svg>
  );

  return (
    <div className="space-y-6">
      {/* Overview Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Overview</h1>
      </div>

      {/* Trade Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metricCards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.key} className="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-500">{card.label}</p>
                <Icon className={`w-4 h-4 ${card.accent}`} />
              </div>
              <p className="text-2xl font-semibold text-gray-900 mt-2">
                {loadingTradeStats ? '...' : card.formatter(card.value)}
              </p>
              {card.subtext && (
                <p className="text-xs text-gray-500 mt-1">{card.subtext}</p>
              )}
            </div>
          );
        })}
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left Column - My Trades & Watchlist */}
        <div className="col-span-2 space-y-6">
          {/* Recent Insider Trades */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Recent Insider Trades</h2>
              <button
                onClick={() => navigate('/trades')}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center"
              >
                View all <ArrowRight className="w-4 h-4 ml-1" />
              </button>
            </div>

            <div className="space-y-4">
              {loadingTrades ? (
                <div className="text-center py-8 text-gray-500">Loading trades...</div>
              ) : recentTrades && recentTrades.length > 0 ? (
                recentTrades.slice(0, 5).map((trade: any) => (
                  <div
                    key={trade.id}
                    onClick={() => navigate(`/companies/${trade.company?.ticker}`)}
                    className="flex items-center justify-between p-4 hover:bg-gray-50 rounded-xl transition-colors cursor-pointer"
                  >
                    <div className="flex items-center space-x-4">
                      <CompanyLogo
                        ticker={trade.company?.ticker || ''}
                        companyName={trade.company?.name}
                        size="md"
                      />
                      <div>
                        <p className="font-semibold text-gray-900">{trade.company?.ticker || 'Unknown'}</p>
                        <p className="text-sm text-gray-500">{trade.insider?.name?.split(' ')[0] || 'Insider'}</p>
                      </div>
                    </div>
                    <div className="text-center">
                      <MiniChart
                        color={trade.transaction_type === 'BUY' ? 'text-green-500' : 'text-red-500'}
                        trending={trade.transaction_type === 'BUY' ? 'up' : 'down'}
                      />
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900">${trade.total_value?.toLocaleString() || '0'}</p>
                      <p className={`text-sm font-medium ${trade.transaction_type === 'BUY' ? 'text-green-600' : 'text-red-600'}`}>
                        {trade.transaction_type === 'BUY' ? '↑' : '↓'}{parseFloat(trade.shares || '0').toLocaleString()} shares
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-500">{new Date(trade.filing_date).toLocaleDateString()}</p>
                      <p className={`text-xs font-medium ${trade.transaction_type === 'BUY' ? 'text-green-600' : 'text-red-600'}`}>
                        {trade.transaction_type}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">No trades found</div>
              )}
            </div>
          </div>

          {/* Most Active Stocks (Top Insider Trading Activity) */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Most Active Stocks</h2>
              <button
                onClick={() => navigate('/market-overview')}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center"
              >
                View all <ArrowRight className="w-4 h-4 ml-1" />
              </button>
            </div>

            <div className="grid grid-cols-3 gap-4">
              {topMoversQuotes && topMoversQuotes.length > 0 ? (
                topMoversQuotes.map((stock, idx) => (
                  <div
                    key={idx}
                    onClick={() => navigate(`/companies/${stock.ticker}`)}
                    className="bg-gradient-to-br from-gray-50 to-white rounded-xl p-4 border border-gray-100 cursor-pointer hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <CompanyLogo
                          ticker={stock.ticker}
                          companyName={stock.company_name}
                          size="sm"
                        />
                        <div>
                          <p className="font-bold text-gray-900">{stock.ticker}</p>
                          <p className="text-xs text-gray-500">{stock.company_name || 'Company'}</p>
                        </div>
                      </div>
                      <MiniChart
                        color={stock.price_change_percent > 0 ? 'text-green-500' : 'text-red-500'}
                        trending={stock.price_change_percent > 0 ? 'up' : 'down'}
                      />
                    </div>
                    <div className="flex items-end justify-between">
                      <div>
                        <p className="text-lg font-semibold text-gray-900">${stock.current_price.toFixed(2)}</p>
                        <p className={`text-xs font-medium ${stock.price_change_percent > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {stock.price_change_percent > 0 ? '↑' : '↓'}{Math.abs(stock.price_change_percent).toFixed(2)}%
                        </p>
                      </div>
                      <div className="text-xs text-gray-500">
                        {stock.market_state === 'REGULAR' ? '🟢 LIVE' : '⏸️ CLOSED'}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-3 text-center py-8 text-gray-500">Loading market data...</div>
              )}
            </div>
          </div>

          {/* Latest Insider Activity */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Latest Insider Activity</h2>
              <button
                onClick={() => navigate('/trades')}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center"
              >
                View all <ArrowRight className="w-4 h-4 ml-1" />
              </button>
            </div>

            <div className="space-y-4">
              {latestActivity.length > 0 ? (
                latestActivity.map((trade: any, idx) => (
                  <div
                    key={idx}
                    onClick={() => navigate(`/companies/${trade.company?.ticker}`)}
                    className="flex items-start space-x-4 p-4 hover:bg-gray-50 rounded-xl transition-colors cursor-pointer"
                  >
                    <CompanyLogo
                      ticker={trade.company?.ticker || ''}
                      companyName={trade.company?.name}
                      size="xl"
                    />
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 mb-1">
                        {trade.insider?.name || 'Insider'} {trade.transaction_type === 'BUY' ? 'bought' : 'sold'} {trade.company?.ticker || 'stock'}
                      </h3>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span className="font-semibold text-gray-700">{trade.company?.ticker || 'N/A'}</span>
                        <span className={trade.transaction_type === 'BUY' ? 'text-green-600' : 'text-red-600'}>
                          {trade.transaction_type === 'BUY' ? '↑' : '↓'} {parseFloat(trade.shares || '0').toLocaleString()} shares
                        </span>
                        <span>${trade.total_value?.toLocaleString() || '0'}</span>
                        <span className="flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {new Date(trade.filing_date).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">No recent activity</div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column - Active Stocks Watchlist */}
        <div>
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 sticky top-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Active Stocks</h2>
              <button
                onClick={() => navigate('/market-overview')}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center"
              >
                View all <ArrowRight className="w-4 h-4 ml-1" />
              </button>
            </div>

            <div className="space-y-4">
              {loadingWatchlist ? (
                <div className="text-center py-8 text-gray-500">Loading...</div>
              ) : watchlistQuotes && watchlistQuotes.length > 0 ? (
                watchlistQuotes.map((stock, idx) => (
                  <div
                    key={idx}
                    onClick={() => navigate(`/companies/${stock.ticker}`)}
                    className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-xl transition-colors cursor-pointer"
                  >
                    <div className="flex items-center space-x-3">
                      <CompanyLogo
                        ticker={stock.ticker}
                        companyName={stock.company_name}
                        size="md"
                      />
                      <div>
                        <p className="font-semibold text-gray-900 text-sm">{stock.ticker}</p>
                        <p className="text-xs text-gray-500">{stock.company_name || 'Company'}</p>
                      </div>
                    </div>
                    <div className="text-center">
                      <MiniChart
                        color={stock.price_change_percent > 0 ? 'text-green-500' : 'text-red-500'}
                        trending={stock.price_change_percent > 0 ? 'up' : 'down'}
                      />
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900 text-sm">${stock.current_price.toFixed(2)}</p>
                      <p className={`text-xs font-medium ${stock.price_change_percent > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {stock.price_change_percent > 0 ? '↑' : '↓'}{Math.abs(stock.price_change_percent).toFixed(2)}%
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">No stocks available</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
