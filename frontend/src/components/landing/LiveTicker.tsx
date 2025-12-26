import { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Clock } from 'lucide-react';

interface Trade {
  id: number;
  ticker: string;
  insider_name: string;
  transaction_type: string;
  shares: number;
  value: number;
  filed_at: string;
  company_name?: string;
}

const LiveTicker = () => {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchTrades = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/trades?limit=20&sort=recent`);
        if (response.ok) {
          const data = await response.json();
          // Duplicate the array to ensure smooth infinite scroll
          setTrades([...data, ...data]);
        }
      } catch (error) {
        console.error('Failed to fetch trades:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTrades();
    // Refresh every 30 seconds
    const interval = setInterval(fetchTrades, 30000);
    return () => clearInterval(interval);
  }, []);

  const formatValue = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`;
    }
    return `$${value.toFixed(0)}`;
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  if (isLoading) {
    return (
      <div className="bg-[#0f0f1a] border-y border-white/10 py-3 overflow-hidden">
        <div className="flex items-center gap-2 text-gray-500">
          <Clock className="w-4 h-4 animate-spin" />
          <span className="text-sm">Loading live trades...</span>
        </div>
      </div>
    );
  }

  if (trades.length === 0) {
    return null;
  }

  return (
    <div className="bg-[#0f0f1a] border-y border-white/10 py-3 overflow-hidden relative">
      {/* Live indicator */}
      <div className="absolute left-4 top-1/2 -translate-y-1/2 flex items-center gap-2 z-10 bg-[#0f0f1a] pr-4">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
        </span>
        <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">Live Trades</span>
      </div>

      {/* Scrolling container */}
      <div className="ticker-wrapper">
        <div className="ticker-content">
          {trades.map((trade, index) => {
            const isBuy = trade.transaction_type.toLowerCase().includes('buy') ||
                         trade.transaction_type.toLowerCase().includes('purchase');

            return (
              <div
                key={`${trade.id}-${index}`}
                className="ticker-item inline-flex items-center gap-3 px-6 py-2 bg-black/20 border border-white/5 rounded-full mx-2"
              >
                {/* Transaction Type Indicator */}
                <div className={`flex items-center gap-1 ${isBuy ? 'text-green-400' : 'text-red-400'}`}>
                  {isBuy ? (
                    <TrendingUp className="w-3 h-3" />
                  ) : (
                    <TrendingDown className="w-3 h-3" />
                  )}
                  <span className="text-xs font-bold uppercase">{isBuy ? 'BUY' : 'SELL'}</span>
                </div>

                {/* Ticker */}
                <span className="text-white font-bold text-sm">{trade.ticker}</span>

                {/* Insider */}
                <span className="text-gray-400 text-xs max-w-[150px] truncate">
                  {trade.insider_name}
                </span>

                {/* Value */}
                <span className="text-purple-400 font-semibold text-sm">
                  {formatValue(trade.value)}
                </span>

                {/* Time */}
                <span className="text-gray-500 text-xs flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {formatTime(trade.filed_at)}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <style>{`
        .ticker-wrapper {
          overflow: hidden;
          white-space: nowrap;
        }

        .ticker-content {
          display: inline-block;
          animation: scroll 60s linear infinite;
          padding-left: 180px; /* Offset for "Live Trades" label */
        }

        @keyframes scroll {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-50%);
          }
        }

        .ticker-item {
          display: inline-flex;
        }

        /* Pause animation on hover */
        .ticker-wrapper:hover .ticker-content {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  );
};

export default LiveTicker;
