import { TrendingUp, TrendingDown } from 'lucide-react';

const CEO_NAMES: Record<string, string> = {
  'NVDA': 'Jensen Huang',
  'TSLA': 'Elon Musk',
  'META': 'Mark Zuckerberg',
  'GOOGL': 'Sundar Pichai',
  'AMZN': 'Andy Jassy',
  'AMD': 'Lisa Su',
  'AAPL': 'Tim Cook',
  'MSFT': 'Satya Nadella',
};

const getCEOName = (ticker: string): string => {
  return CEO_NAMES[ticker] || 'CEO';
};

const staticTrades = [
  { id: 1, ticker: 'NVDA', insider_name: getCEOName('NVDA'), transaction_type: 'Buy', value: 8200000 },
  { id: 2, ticker: 'AAPL', insider_name: getCEOName('AAPL'), transaction_type: 'Buy', value: 3400000 },
  { id: 3, ticker: 'MSFT', insider_name: getCEOName('MSFT'), transaction_type: 'Buy', value: 2100000 },
  { id: 4, ticker: 'GOOGL', insider_name: getCEOName('GOOGL'), transaction_type: 'Sell', value: 5600000 },
  { id: 5, ticker: 'TSLA', insider_name: getCEOName('TSLA'), transaction_type: 'Buy', value: 4200000 },
  { id: 6, ticker: 'META', insider_name: getCEOName('META'), transaction_type: 'Sell', value: 7800000 },
  { id: 7, ticker: 'AMZN', insider_name: getCEOName('AMZN'), transaction_type: 'Buy', value: 1900000 },
  { id: 8, ticker: 'AMD', insider_name: getCEOName('AMD'), transaction_type: 'Buy', value: 3100000 },
];

const LiveTicker = () => {
  const trades = [...staticTrades, ...staticTrades];

  const formatValue = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`;
    }
    return `$${value.toFixed(0)}`;
  };

  return (
    <div className="bg-[#0f0f1a]/80 backdrop-blur-xl border-y border-white/[0.06] py-4 overflow-hidden relative">
      <div className="absolute left-4 top-1/2 -translate-y-1/2 flex items-center gap-3 z-20 bg-[#0f0f1a]/90 backdrop-blur-md pr-6 pl-2 py-1.5 rounded-full border border-white/[0.06]">
        <span className="relative flex h-2.5 w-2.5">
          <span className="ticker-pulse-ring absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.6)]"></span>
        </span>
        <span className="ticker-badge-text text-xs font-semibold uppercase tracking-widest">Demo Trades</span>
      </div>

      <div className="ticker-fade-left absolute left-0 top-0 bottom-0 w-48 z-10 pointer-events-none" />
      <div className="ticker-fade-right absolute right-0 top-0 bottom-0 w-48 z-10 pointer-events-none" />

      <div className="ticker-wrapper">
        <div className="ticker-content">
          {trades.map((trade, index) => {
            const isBuy = trade.transaction_type.toLowerCase().includes('buy') ||
                         trade.transaction_type.toLowerCase().includes('purchase');

            return (
              <div
                key={`${trade.id}-${index}`}
                className={`ticker-item inline-flex items-center gap-3 px-5 py-2.5 rounded-full mx-2 border backdrop-blur-sm transition-all duration-300 ${
                  isBuy
                    ? 'bg-green-500/[0.04] border-green-500/[0.12] hover:border-green-400/30 hover:shadow-[0_0_20px_rgba(34,197,94,0.08)]'
                    : 'bg-red-500/[0.04] border-red-500/[0.12] hover:border-red-400/30 hover:shadow-[0_0_20px_rgba(239,68,68,0.08)]'
                }`}
              >
                <div className={`flex items-center gap-1.5 ${isBuy ? 'text-green-400' : 'text-red-400'}`}>
                  {isBuy ? (
                    <TrendingUp className="w-3.5 h-3.5" />
                  ) : (
                    <TrendingDown className="w-3.5 h-3.5" />
                  )}
                  <span className="text-[11px] font-bold uppercase tracking-wide">{isBuy ? 'BUY' : 'SELL'}</span>
                </div>

                <div className="w-px h-4 bg-white/[0.08]" />

                <span className="text-white font-bold text-sm tracking-wide">{trade.ticker}</span>

                <span className="text-gray-500 text-xs max-w-[130px] truncate">
                  {trade.insider_name}
                </span>

                <span className="text-purple-300 font-semibold text-sm tabular-nums">
                  {formatValue(trade.value)}
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
          animation: ticker-scroll 55s linear infinite;
          padding-left: 200px;
        }

        @keyframes ticker-scroll {
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

        .ticker-wrapper:hover .ticker-content {
          animation-play-state: paused;
        }

        .ticker-fade-left {
          background: linear-gradient(to right, #0f0f1a 0%, #0f0f1acc 40%, transparent 100%);
        }

        .ticker-fade-right {
          background: linear-gradient(to left, #0f0f1a 0%, #0f0f1acc 40%, transparent 100%);
        }

        .ticker-pulse-ring {
          animation: ticker-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }

        @keyframes ticker-pulse {
          0%, 100% {
            transform: scale(1);
            opacity: 0.75;
          }
          50% {
            transform: scale(1.8);
            opacity: 0;
          }
        }

        .ticker-badge-text {
          background: linear-gradient(90deg, #fbbf24, #f59e0b, #fbbf24);
          background-size: 200% 100%;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          animation: ticker-shimmer 3s ease-in-out infinite;
        }

        @keyframes ticker-shimmer {
          0%, 100% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
        }
      `}</style>
    </div>
  );
};

export default LiveTicker;
