/**
 * Modern Trading Dashboard - Redesigned - Dark Mode
 * Inspired by modern trading apps
 */

import { useQuery } from '@tanstack/react-query';
import { tradesApi } from '../api/trades';
import { stocksApi } from '../api/stocks';
import { marketDataApi } from '../api/marketData';
import { TrendingUp, TrendingDown, ArrowRight, Clock, Calendar } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import CompanyLogo from '../components/CompanyLogo';

export default function DashboardNew() {
  const navigate = useNavigate();

  // Fetch recent trades (increased to 30 days to catch up on missed data)
  const { data: recentTrades, isLoading: loadingTrades } = useQuery({
    queryKey: ['recentTrades'],
    queryFn: () => tradesApi.getRecentTrades(30),
  });

  // Fetch trade statistics
  const { data: tradeStats, isLoading: loadingTradeStats } = useQuery({
    queryKey: ['tradeStats'],
    queryFn: () => tradesApi.getTradeStats(),
    staleTime: 5 * 60 * 1000, // 5 minutes - stats won't refetch on hard refresh for 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes - keep in cache for 10 minutes (React Query v5+)
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

  // Fetch IPO calendar
  const { data: ipoData, isLoading: loadingIpo } = useQuery({
    queryKey: ['ipoCalendar'],
    queryFn: () => marketDataApi.getIpoCalendar(),
    staleTime: 60 * 60 * 1000, // 1 hour - matches backend cache TTL
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
      accent: 'text-blue-400',
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
      accent: 'text-emerald-400',
      formatter: formatCurrency,
      subtext: tradeStats ? `${formatNumber(tradeStats.total_buys)} buy orders` : undefined,
    },
    {
      key: 'totalSellVolume',
      label: 'Sell Volume',
      value: tradeStats?.total_sell_value,
      icon: TrendingDown,
      accent: 'text-rose-400',
      formatter: formatCurrency,
      subtext: tradeStats ? `${formatNumber(tradeStats.total_sells)} sell orders` : undefined,
    },
    {
      key: 'averageTrade',
      label: 'Avg Trade Size',
      value: tradeStats?.average_trade_size,
      icon: Clock,
      accent: 'text-amber-400',
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
        <h1 className="text-3xl font-bold text-white">Overview</h1>
      </div>

      {/* Trade Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metricCards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.key} className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10 p-5 shadow-lg">
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-400">{card.label}</p>
                <Icon className={`w-4 h-4 ${card.accent}`} />
              </div>
              <p className="text-2xl font-semibold text-white mt-2">
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
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - My Trades & Watchlist */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recent Insider Trades */}
          <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-lg border border-white/10 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Recent Insider Trades</h2>
              <button
                onClick={() => navigate('/trades')}
                className="text-sm text-blue-400 hover:text-blue-300 font-medium flex items-center transition-colors"
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
                    className="flex items-center justify-between p-4 hover:bg-white/5 rounded-xl transition-colors cursor-pointer border border-transparent hover:border-white/5"
                  >
                    <div className="flex items-center space-x-4">
                      <CompanyLogo
                        ticker={trade.company?.ticker || ''}
                        companyName={trade.company?.name}
                        size="md"
                      />
                      <div>
                        <p className="font-semibold text-white">{trade.company?.ticker || 'Unknown'}</p>
                        <p className="text-sm text-gray-400">{trade.insider?.name?.split(' ')[0] || 'Insider'}</p>
                      </div>
                    </div>
                    <div className="text-center hidden sm:block">
                      <MiniChart
                        color={trade.transaction_type === 'BUY' ? 'text-green-400' : 'text-red-400'}
                        trending={trade.transaction_type === 'BUY' ? 'up' : 'down'}
                      />
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-white">${trade.total_value?.toLocaleString() || '0'}</p>
                      <p className={`text-sm font-medium ${trade.transaction_type === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                        {trade.transaction_type === 'BUY' ? '↑' : '↓'}{parseFloat(trade.shares || '0').toLocaleString()} shares
                      </p>
                    </div>
                    <div className="text-right hidden sm:block">
                      <p className="text-xs text-gray-500">{new Date(trade.filing_date).toLocaleDateString()}</p>
                      <p className={`text-xs font-medium ${trade.transaction_type === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
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
          <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-lg border border-white/10 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Most Active Stocks</h2>
              <button
                onClick={() => navigate('/market-overview')}
                className="text-sm text-blue-400 hover:text-blue-300 font-medium flex items-center transition-colors"
              >
                View all <ArrowRight className="w-4 h-4 ml-1" />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {topMoversQuotes && topMoversQuotes.length > 0 ? (
                topMoversQuotes.map((stock, idx) => (
                  <div
                    key={idx}
                    onClick={() => navigate(`/companies/${stock.ticker}`)}
                    className="bg-white/5 hover:bg-white/10 rounded-xl p-4 border border-white/10 cursor-pointer transition-colors"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <CompanyLogo
                          ticker={stock.ticker}
                          companyName={stock.company_name}
                          size="sm"
                        />
                        <div className="min-w-0">
                          <p className="font-bold text-white truncate">{stock.ticker}</p>
                          <p className="text-xs text-gray-400 truncate">{stock.company_name || 'Company'}</p>
                        </div>
                      </div>
                      <MiniChart
                        color={stock.price_change_percent > 0 ? 'text-green-400' : 'text-red-400'}
                        trending={stock.price_change_percent > 0 ? 'up' : 'down'}
                      />
                    </div>
                    <div className="flex items-end justify-between">
                      <div>
                        <p className="text-lg font-semibold text-white">${stock.current_price.toFixed(2)}</p>
                        <p className={`text-xs font-medium ${stock.price_change_percent > 0 ? 'text-green-400' : 'text-red-400'}`}>
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
          <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-lg border border-white/10 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Latest Insider Activity</h2>
              <button
                onClick={() => navigate('/trades')}
                className="text-sm text-blue-400 hover:text-blue-300 font-medium flex items-center transition-colors"
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
                    className="flex items-start space-x-4 p-4 hover:bg-white/5 rounded-xl transition-colors cursor-pointer border border-transparent hover:border-white/5"
                  >
                    <CompanyLogo
                      ticker={trade.company?.ticker || ''}
                      companyName={trade.company?.name}
                      size="xl"
                    />
                    <div className="flex-1">
                      <h3 className="font-medium text-white mb-1">
                        {trade.insider?.name || 'Insider'} {trade.transaction_type === 'BUY' ? 'bought' : 'sold'} {trade.company?.ticker || 'stock'}
                      </h3>
                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-400">
                        <span className="font-semibold text-gray-300">{trade.company?.ticker || 'N/A'}</span>
                        <span className={trade.transaction_type === 'BUY' ? 'text-green-400' : 'text-red-400'}>
                          {trade.transaction_type === 'BUY' ? '↑' : '↓'} {parseFloat(trade.shares || '0').toLocaleString()} shares
                        </span>
                        <span>${trade.total_value?.toLocaleString() || '0'}</span>
                        <span className="flex items-center text-gray-500">
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
          <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-lg border border-white/10 p-6 sticky top-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Active Stocks</h2>
              <button
                onClick={() => navigate('/market-overview')}
                className="text-sm text-blue-400 hover:text-blue-300 font-medium flex items-center transition-colors"
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
                    className="flex items-center justify-between p-3 hover:bg-white/5 rounded-xl transition-colors cursor-pointer border border-transparent hover:border-white/5"
                  >
                    <div className="flex items-center space-x-3">
                      <CompanyLogo
                        ticker={stock.ticker}
                        companyName={stock.company_name}
                        size="md"
                      />
                      <div className="min-w-0">
                        <p className="font-semibold text-white text-sm truncate">{stock.ticker}</p>
                        <p className="text-xs text-gray-400 truncate">{stock.company_name || 'Company'}</p>
                      </div>
                    </div>
                    <div className="text-center hidden xl:block">
                      <MiniChart
                        color={stock.price_change_percent > 0 ? 'text-green-400' : 'text-red-400'}
                        trending={stock.price_change_percent > 0 ? 'up' : 'down'}
                      />
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-white text-sm">${stock.current_price.toFixed(2)}</p>
                      <p className={`text-xs font-medium ${stock.price_change_percent > 0 ? 'text-green-400' : 'text-red-400'}`}>
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

          {/* IPO Calendar */}
          <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-lg border border-white/10 p-6 mt-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">IPO Calendar</h2>
              <Calendar className="w-5 h-5 text-blue-400" />
            </div>

            <div className="space-y-3">
              {loadingIpo ? (
                <div className="text-center py-8 text-gray-500">Loading IPOs...</div>
              ) : ipoData?.ipos && ipoData.ipos.length > 0 ? (
                ipoData.ipos.slice(0, 5).map((ipo, idx) => (
                  <div
                    key={idx}
                    className="flex items-start justify-between p-3 hover:bg-white/5 rounded-xl transition-colors border border-transparent hover:border-white/5"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        {ipo.symbol && (
                          <span className="font-semibold text-white text-sm">{ipo.symbol}</span>
                        )}
                        {ipo.status && (
                          <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-400">
                            {ipo.status}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-white font-medium truncate">{ipo.company_name}</p>
                      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-400 mt-1">
                        {ipo.ipo_date && (
                          <span className="flex items-center">
                            <Calendar className="w-3 h-3 mr-1" />
                            {new Date(ipo.ipo_date).toLocaleDateString()}
                          </span>
                        )}
                        {ipo.exchange && <span>{ipo.exchange}</span>}
                        {ipo.price_range && <span>{ipo.price_range}</span>}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">No upcoming IPOs</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}