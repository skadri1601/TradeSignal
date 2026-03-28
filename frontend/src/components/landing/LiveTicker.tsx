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
    <div className="bg-[#111] border-y border-white/[0.06] py-4 overflow-hidden relative">
      <div className="absolute left-4 top-1/2 -translate-y-1/2 flex items-center gap-3 z-20 bg-[#111] pr-6 pl-2 py-1.5 rounded-full border border-white/[0.06]">
        <span className="flex h-2.5 w-2.5 rounded-full bg-amber-400" />
        <span className="text-xs font-semibold uppercase tracking-widest text-amber-400">Demo Trades</span>
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
                className={`ticker-item inline-flex items-center gap-3 px-5 py-2.5 rounded-full mx-2 border ${
                  isBuy
                    ? 'bg-green-500/[0.04] border-green-500/[0.12]'
                    : 'bg-red-500/[0.04] border-red-500/[0.12]'
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
          background: linear-gradient(to right, #111 0%, rgba(17,17,17,0.8) 40%, transparent 100%);
        }

        .ticker-fade-right {
          background: linear-gradient(to left, #111 0%, rgba(17,17,17,0.8) 40%, transparent 100%);
        }
      `}</style>
    </div>
  );
};

export default LiveTicker;
