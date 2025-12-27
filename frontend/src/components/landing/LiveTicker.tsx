import { TrendingUp, TrendingDown } from 'lucide-react';

// CEO name mapping for demo companies
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

// Helper function to get CEO name for a ticker
const getCEOName = (ticker: string): string => {
  return CEO_NAMES[ticker] || 'CEO';
};

// Static demo data for portfolio showcase
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
  // Duplicate for seamless scroll animation
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
    <div className="bg-[#0f0f1a] border-y border-white/10 py-3 overflow-hidden relative">
      {/* Demo indicator */}
      <div className="absolute left-4 top-1/2 -translate-y-1/2 flex items-center gap-2 z-10 bg-[#0f0f1a] pr-4">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
        </span>
        <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">Demo Trades</span>
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
