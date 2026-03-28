import { useQuery } from '@tanstack/react-query';
import { tradesApi } from '../api/trades';
import { stocksApi } from '../api/stocks';
import { marketDataApi } from '../api/marketData';
import { TrendingUp, TrendingDown, ArrowRight, Clock, Calendar } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import CompanyLogo from '../components/CompanyLogo';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

function AnimatedValue({ value, formatter }: { value?: number | null; formatter: (v?: number | null) => string }) {
  const [display, setDisplay] = useState(0);
  const target = value ?? 0;

  useEffect(() => {
    if (!value) return;
    let start = 0;
    const duration = 800;
    const startTime = performance.now();
    const step = (now: number) => {
      const progress = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      start = target * eased;
      setDisplay(start);
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [value, target]);

  if (!value) return <span>--</span>;
  return <span>{formatter(display)}</span>;
}

function ShimmerBlock({ className }: { className?: string }) {
  return (
    <div className={`relative overflow-hidden rounded-lg bg-white/[0.04] ${className || ''}`}>
      <div className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/[0.06] to-transparent" />
    </div>
  );
}

function ShimmerRows({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-4 py-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 px-2">
          <ShimmerBlock className="w-10 h-10 rounded-full flex-shrink-0" />
          <div className="flex-1 space-y-2">
            <ShimmerBlock className={`h-4 ${i % 2 === 0 ? 'w-3/4' : 'w-1/2'}`} />
            <ShimmerBlock className="h-3 w-1/3" />
          </div>
          <ShimmerBlock className="h-4 w-16" />
        </div>
      ))}
    </div>
  );
}

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] as [number, number, number, number] },
  }),
};

const accentMap: Record<string, { glow: string; gradient: string; bg: string }> = {
  'text-blue-400': {
    glow: 'shadow-blue-500/10 hover:shadow-blue-500/20',
    gradient: 'from-blue-500 to-blue-400',
    bg: 'from-blue-500/20 to-blue-400/10',
  },
  'text-emerald-400': {
    glow: 'shadow-emerald-500/10 hover:shadow-emerald-500/20',
    gradient: 'from-emerald-500 to-emerald-400',
    bg: 'from-emerald-500/20 to-emerald-400/10',
  },
  'text-rose-400': {
    glow: 'shadow-rose-500/10 hover:shadow-rose-500/20',
    gradient: 'from-rose-500 to-rose-400',
    bg: 'from-rose-500/20 to-rose-400/10',
  },
  'text-amber-400': {
    glow: 'shadow-amber-500/10 hover:shadow-amber-500/20',
    gradient: 'from-amber-500 to-amber-400',
    bg: 'from-amber-500/20 to-amber-400/10',
  },
};

export default function DashboardNew() {
  const navigate = useNavigate();

  const { data: recentTrades, isLoading: loadingTrades } = useQuery({
    queryKey: ['recentTrades'],
    queryFn: () => tradesApi.getRecentTrades(30),
  });

  const { data: tradeStats, isLoading: loadingTradeStats } = useQuery({
    queryKey: ['tradeStats'],
    queryFn: () => tradesApi.getTradeStats(),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });

  const watchlistTickers = Array.from(
    new Set(recentTrades?.slice(0, 10).map(t => t.company?.ticker).filter(Boolean))
  ).slice(0, 5);

  const { data: watchlistQuotes, isLoading: loadingWatchlist } = useQuery({
    queryKey: ['watchlist', watchlistTickers],
    queryFn: () => stocksApi.getMultipleQuotes(watchlistTickers as string[]),
    enabled: watchlistTickers.length > 0,
  });

  const topMoversTickers = Array.from(
    new Set(recentTrades?.slice(0, 15).map(t => t.company?.ticker).filter(Boolean))
  ).slice(0, 3);

  const { data: topMoversQuotes } = useQuery({
    queryKey: ['topMovers', topMoversTickers],
    queryFn: () => stocksApi.getMultipleQuotes(topMoversTickers as string[]),
    enabled: topMoversTickers.length > 0,
  });

  const { data: ipoData, isLoading: loadingIpo } = useQuery({
    queryKey: ['ipoCalendar'],
    queryFn: () => marketDataApi.getIpoCalendar(),
    staleTime: 60 * 60 * 1000,
  });

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

  const MiniChart = ({ color, trending }: { color: string; trending: string }) => {
    const id = `gradient-${color}-${trending}`;
    return (
      <svg width="60" height="24" viewBox="0 0 60 24" className={color}>
        <defs>
          <linearGradient id={id} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="currentColor" stopOpacity="0.3" />
            <stop offset="100%" stopColor="currentColor" stopOpacity="1" />
          </linearGradient>
        </defs>
        {trending === 'up' ? (
          <>
            <polyline
              points="0,20 15,15 30,18 45,8 60,5"
              fill="none"
              stroke={`url(#${id})`}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <polyline
              points="0,20 15,15 30,18 45,8 60,5 60,24 0,24"
              fill="currentColor"
              opacity="0.08"
            />
          </>
        ) : (
          <>
            <polyline
              points="0,5 15,8 30,6 45,15 60,20"
              fill="none"
              stroke={`url(#${id})`}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <polyline
              points="0,5 15,8 30,6 45,15 60,20 60,24 0,24"
              fill="currentColor"
              opacity="0.08"
            />
          </>
        )}
      </svg>
    );
  };

  return (
    <div className="space-y-6">
      <style>{`
        @keyframes shimmer {
          100% { transform: translateX(100%); }
        }
      `}</style>

      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h1 className="text-3xl font-bold text-white">Overview</h1>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metricCards.map((card, i) => {
          const Icon = card.icon;
          const accent = accentMap[card.accent];
          return (
            <motion.div
              key={card.key}
              custom={i}
              variants={cardVariants}
              initial="hidden"
              animate="visible"
              className={`relative overflow-hidden bg-white/[0.03] backdrop-blur-md rounded-2xl border border-white/[0.08] p-5 shadow-lg ${accent.glow} transition-all duration-300 hover:-translate-y-1 group`}
            >
              <div className={`absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r ${accent.gradient}`} />
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-400 font-medium">{card.label}</p>
                <div className={`w-8 h-8 rounded-full bg-gradient-to-br ${accent.bg} flex items-center justify-center`}>
                  <Icon className={`w-4 h-4 ${card.accent}`} />
                </div>
              </div>
              <div className="text-2xl font-semibold text-white mt-2">
                {loadingTradeStats ? (
                  <ShimmerBlock className="h-7 w-24 mt-1" />
                ) : (
                  <AnimatedValue value={card.value} formatter={card.formatter} />
                )}
              </div>
              {card.subtext && !loadingTradeStats && (
                <p className="text-xs text-gray-500 mt-1.5">{card.subtext}</p>
              )}
              {loadingTradeStats && <ShimmerBlock className="h-3 w-32 mt-2" />}
            </motion.div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className="bg-white/[0.03] backdrop-blur-md rounded-2xl shadow-lg border border-white/[0.08] p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Recent Insider Trades</h2>
              <button
                onClick={() => navigate('/trades')}
                className="text-sm text-blue-400 hover:text-blue-300 font-medium flex items-center transition-colors group"
              >
                View all <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-0.5 transition-transform" />
              </button>
            </div>

            <div className="space-y-1">
              {loadingTrades ? (
                <ShimmerRows count={5} />
              ) : recentTrades && recentTrades.length > 0 ? (
                recentTrades.slice(0, 5).map((trade: any, idx: number) => (
                  <motion.div
                    key={trade.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.35 + idx * 0.05, duration: 0.4 }}
                    onClick={() => navigate(`/companies/${trade.company?.ticker}`)}
                    className="relative flex items-center justify-between p-4 hover:bg-white/[0.04] rounded-xl transition-all duration-200 cursor-pointer group/row border border-transparent hover:border-white/[0.06]"
                  >
                    <div className={`absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-0 group-hover/row:h-8 rounded-full transition-all duration-200 ${trade.transaction_type === 'BUY' ? 'bg-gradient-to-b from-emerald-400 to-emerald-600' : 'bg-gradient-to-b from-rose-400 to-rose-600'}`} />
                    <div className="flex items-center space-x-4">
                      <div className="ring-2 ring-white/[0.06] rounded-full group-hover/row:ring-white/[0.12] transition-all">
                        <CompanyLogo
                          ticker={trade.company?.ticker || ''}
                          companyName={trade.company?.name}
                          size="md"
                        />
                      </div>
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
                      <span className={`inline-block text-xs font-semibold px-2 py-0.5 rounded-full mt-0.5 ${trade.transaction_type === 'BUY' ? 'bg-emerald-500/15 text-emerald-400' : 'bg-rose-500/15 text-rose-400'}`}>
                        {trade.transaction_type}
                      </span>
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <ArrowRight className="w-8 h-8 mx-auto mb-2 opacity-30" />
                  <p>No trades found</p>
                </div>
              )}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="bg-white/[0.03] backdrop-blur-md rounded-2xl shadow-lg border border-white/[0.08] p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Most Active Stocks</h2>
              <button
                onClick={() => navigate('/market-overview')}
                className="text-sm text-blue-400 hover:text-blue-300 font-medium flex items-center transition-colors group"
              >
                View all <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-0.5 transition-transform" />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {topMoversQuotes && topMoversQuotes.length > 0 ? (
                topMoversQuotes.map((stock, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.45 + idx * 0.08, duration: 0.4 }}
                    onClick={() => navigate(`/companies/${stock.ticker}`)}
                    className="relative overflow-hidden bg-white/[0.04] hover:bg-white/[0.07] rounded-xl p-4 border border-white/[0.08] cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-lg group/card"
                  >
                    <div className={`absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r ${stock.price_change_percent > 0 ? 'from-emerald-500 to-emerald-400' : 'from-rose-500 to-rose-400'}`} />
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <div className="ring-2 ring-white/[0.06] rounded-full">
                          <CompanyLogo
                            ticker={stock.ticker}
                            companyName={stock.company_name}
                            size="sm"
                          />
                        </div>
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
                        <p className={`text-xs font-semibold ${stock.price_change_percent > 0 ? 'text-green-400 drop-shadow-[0_0_6px_rgba(34,197,94,0.3)]' : 'text-red-400 drop-shadow-[0_0_6px_rgba(239,68,68,0.3)]'}`}>
                          {stock.price_change_percent > 0 ? '↑' : '↓'}{Math.abs(stock.price_change_percent).toFixed(2)}%
                        </p>
                      </div>
                      <div className="flex items-center gap-1.5 text-xs text-gray-500">
                        <span className={`inline-block w-2 h-2 rounded-full ${stock.market_state === 'REGULAR' ? 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.5)] animate-pulse' : 'bg-gray-500'}`} />
                        {stock.market_state === 'REGULAR' ? 'LIVE' : 'CLOSED'}
                      </div>
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="col-span-3">
                  <ShimmerRows count={1} />
                </div>
              )}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="bg-white/[0.03] backdrop-blur-md rounded-2xl shadow-lg border border-white/[0.08] p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Latest Insider Activity</h2>
              <button
                onClick={() => navigate('/trades')}
                className="text-sm text-blue-400 hover:text-blue-300 font-medium flex items-center transition-colors group"
              >
                View all <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-0.5 transition-transform" />
              </button>
            </div>

            <div className="space-y-2">
              {latestActivity.length > 0 ? (
                latestActivity.map((trade: any, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.55 + idx * 0.06, duration: 0.4 }}
                    onClick={() => navigate(`/companies/${trade.company?.ticker}`)}
                    className="relative flex items-start space-x-4 p-4 hover:bg-white/[0.04] rounded-xl transition-all duration-200 cursor-pointer group/row border border-transparent hover:border-white/[0.06]"
                  >
                    <div className={`absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-0 group-hover/row:h-10 rounded-full transition-all duration-200 ${trade.transaction_type === 'BUY' ? 'bg-gradient-to-b from-emerald-400 to-emerald-600' : 'bg-gradient-to-b from-rose-400 to-rose-600'}`} />
                    <div className="ring-2 ring-white/[0.06] rounded-xl group-hover/row:ring-white/[0.12] transition-all overflow-hidden">
                      <CompanyLogo
                        ticker={trade.company?.ticker || ''}
                        companyName={trade.company?.name}
                        size="xl"
                      />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-white mb-1">
                        {trade.insider?.name || 'Insider'} {trade.transaction_type === 'BUY' ? 'bought' : 'sold'} {trade.company?.ticker || 'stock'}
                      </h3>
                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-400">
                        <span className="font-semibold text-gray-300">{trade.company?.ticker || 'N/A'}</span>
                        <span className={`font-medium ${trade.transaction_type === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                          {trade.transaction_type === 'BUY' ? '↑' : '↓'} {parseFloat(trade.shares || '0').toLocaleString()} shares
                        </span>
                        <span>${trade.total_value?.toLocaleString() || '0'}</span>
                        <span className="flex items-center text-gray-500">
                          <Clock className="w-3 h-3 mr-1" />
                          {new Date(trade.filing_date).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <Clock className="w-8 h-8 mx-auto mb-2 opacity-30" />
                  <p>No recent activity</p>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.35, duration: 0.5 }}
            className="bg-white/[0.03] backdrop-blur-md rounded-2xl shadow-lg border border-white/[0.08] p-6 sticky top-8"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Active Stocks</h2>
              <button
                onClick={() => navigate('/market-overview')}
                className="text-sm text-blue-400 hover:text-blue-300 font-medium flex items-center transition-colors group"
              >
                View all <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-0.5 transition-transform" />
              </button>
            </div>

            <div className="space-y-1">
              {loadingWatchlist ? (
                <ShimmerRows count={5} />
              ) : watchlistQuotes && watchlistQuotes.length > 0 ? (
                watchlistQuotes.map((stock, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + idx * 0.05, duration: 0.4 }}
                    onClick={() => navigate(`/companies/${stock.ticker}`)}
                    className={`flex items-center justify-between p-3 hover:bg-white/[0.04] rounded-xl transition-all duration-200 cursor-pointer group/item border border-transparent hover:border-white/[0.06] ${idx < watchlistQuotes.length - 1 ? 'border-b border-b-white/[0.04]' : ''}`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="ring-2 ring-white/[0.06] rounded-full group-hover/item:ring-white/[0.12] transition-all">
                        <CompanyLogo
                          ticker={stock.ticker}
                          companyName={stock.company_name}
                          size="md"
                        />
                      </div>
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
                      <p className={`text-xs font-semibold ${stock.price_change_percent > 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {stock.price_change_percent > 0 ? '↑' : '↓'}{Math.abs(stock.price_change_percent).toFixed(2)}%
                      </p>
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <TrendingUp className="w-8 h-8 mx-auto mb-2 opacity-30" />
                  <p>No stocks available</p>
                </div>
              )}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.45, duration: 0.5 }}
            className="bg-white/[0.03] backdrop-blur-md rounded-2xl shadow-lg border border-white/[0.08] p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">IPO Calendar</h2>
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500/20 to-blue-400/10 flex items-center justify-center">
                <Calendar className="w-4 h-4 text-blue-400" />
              </div>
            </div>

            <div className="space-y-2">
              {loadingIpo ? (
                <ShimmerRows count={4} />
              ) : ipoData?.ipos && ipoData.ipos.length > 0 ? (
                ipoData.ipos.slice(0, 5).map((ipo, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 + idx * 0.05, duration: 0.4 }}
                    className="flex items-start justify-between p-3 hover:bg-white/[0.04] rounded-xl transition-all duration-200 border border-transparent hover:border-white/[0.06] group/ipo"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        {ipo.symbol && (
                          <span className="font-semibold text-white text-sm">{ipo.symbol}</span>
                        )}
                        {ipo.status && (
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                            ipo.status.toLowerCase().includes('price')
                              ? 'bg-emerald-500/15 text-emerald-400'
                              : ipo.status.toLowerCase().includes('withdraw')
                                ? 'bg-rose-500/15 text-rose-400'
                                : 'bg-blue-500/15 text-blue-400'
                          }`}>
                            {ipo.status}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-white font-medium truncate">{ipo.company_name}</p>
                      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-400 mt-1">
                        {ipo.ipo_date && (
                          <span className="flex items-center">
                            <Calendar className="w-3 h-3 mr-1 text-blue-400/50" />
                            {new Date(ipo.ipo_date).toLocaleDateString()}
                          </span>
                        )}
                        {ipo.exchange && <span className="text-gray-500">{ipo.exchange}</span>}
                        {ipo.price_range && <span className="text-gray-300 font-medium">{ipo.price_range}</span>}
                      </div>
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <Calendar className="w-8 h-8 mx-auto mb-2 opacity-30" />
                  <p>No upcoming IPOs</p>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
