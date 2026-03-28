import { Building2, TrendingUp, TrendingDown, ArrowRight, Users } from 'lucide-react';
import { Link } from 'react-router-dom';

const staticCongressTrades = [
  { id: 1, ticker: 'NVDA', representative: 'Representative A (Demo)', state: 'CA', transaction_type: 'Purchase', amount: '$1M - $5M', party: 'Democrat' },
  { id: 2, ticker: 'MSFT', representative: 'Senator B (Demo)', state: 'TX', transaction_type: 'Purchase', amount: '$500K - $1M', party: 'Republican' },
  { id: 3, ticker: 'TSLA', representative: 'Representative C (Demo)', state: 'NY', transaction_type: 'Sale', amount: '$250K - $500K', party: 'Democrat' },
  { id: 4, ticker: 'AAPL', representative: 'Senator D (Demo)', state: 'FL', transaction_type: 'Purchase', amount: '$100K - $250K', party: 'Republican' },
];

const CongressSection = () => {
  const congressTrades = staticCongressTrades;

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getPartyColor = (party?: string) => {
    if (party?.toLowerCase().includes('democrat')) return 'bg-blue-500';
    if (party?.toLowerCase().includes('republican')) return 'bg-red-500';
    return 'bg-purple-500';
  };

  return (
    <section className="py-24 px-4 bg-[#0a0a0a] border-t border-white/[0.06]">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div className="order-2 lg:order-1">
            <div className="space-y-4">
                {congressTrades.map((trade) => {
                  const isPurchase = trade.transaction_type.toLowerCase().includes('purchase') ||
                                    trade.transaction_type.toLowerCase().includes('buy');

                  return (
                    <div
                      key={trade.id}
                      className="bg-[#111] border border-white/[0.06] rounded-xl p-6 hover:bg-white/[0.04] transition-colors cursor-pointer"
                    >
                      <div className="flex items-center gap-4">
                        <div className={`w-14 h-14 ${getPartyColor(trade.party)} rounded-full flex items-center justify-center text-white font-bold text-lg flex-shrink-0`}>
                          {getInitials(trade.representative)}
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1.5">
                            <h4 className="font-bold text-white truncate">{trade.representative}</h4>
                            <span className="text-[11px] text-gray-500 bg-white/[0.04] border border-white/[0.06] px-2.5 py-0.5 rounded-md font-medium">{trade.state}</span>
                          </div>
                          <div className="flex items-center gap-3 flex-wrap">
                            <span className="text-sm font-semibold text-purple-300">{trade.ticker}</span>
                            <div className={`flex items-center gap-1 text-xs font-semibold ${
                              isPurchase ? 'text-green-400' : 'text-red-400'
                            }`}>
                              {isPurchase ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                              {isPurchase ? 'Bought' : 'Sold'}
                            </div>
                            <span className="text-xs text-gray-500">{trade.amount}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>

            <div className="mt-8">
              <Link
                to="/register"
                className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 font-medium transition-colors"
              >
                View All Congressional Trades
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          <div className="order-1 lg:order-2">
            <div className="inline-flex items-center gap-2.5 bg-[#111] border border-white/[0.06] rounded-full px-5 py-2.5 mb-8">
              <Building2 className="w-4 h-4 text-blue-400" />
              <span className="text-sm font-medium text-gray-300">Congressional Trading</span>
            </div>

            <h2 className="text-4xl lg:text-[3.25rem] font-bold mb-7 leading-[1.15] tracking-tight">
              <span className="text-white">Follow What</span>
              <span className="text-purple-400 block mt-2">
                Congress is Trading
              </span>
            </h2>

            <p className="text-lg text-gray-400 mb-10 leading-relaxed max-w-lg">
              Track stock transactions from all 535 members of Congress in real-time.
              The STOCK Act requires disclosure within 45 days—we alert you the moment they file.
            </p>

            <div className="grid grid-cols-2 gap-5 mb-12">
              <div className="bg-[#111] border border-white/[0.06] rounded-xl p-6">
                <div className="flex items-center gap-2.5 mb-3">
                  <Users className="w-5 h-5 text-blue-400" />
                  <span className="text-3xl font-bold text-white">535</span>
                </div>
                <p className="text-sm text-gray-500">Members Tracked</p>
              </div>
              <div className="bg-[#111] border border-white/[0.06] rounded-xl p-6">
                <div className="flex items-center gap-2.5 mb-3">
                  <TrendingUp className="w-5 h-5 text-green-400" />
                  <span className="text-3xl font-bold text-white">2,400+</span>
                </div>
                <p className="text-sm text-gray-500">Trades in Q4 2024</p>
              </div>
            </div>

            <div className="space-y-4 mb-12">
              {[
                { title: 'Real-Time STOCK Act Filings', desc: 'Instant alerts when representatives file new trades' },
                { title: 'Committee Analysis', desc: 'See which committee members are trading in their sectors' },
                { title: 'Cluster Detection', desc: 'AI identifies when multiple members buy the same stock' },
              ].map((feature) => (
                <div key={feature.title} className="flex items-start gap-3.5">
                  <div className="w-6 h-6 rounded-full bg-purple-500 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-white text-[10px] font-bold">&#10003;</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-white mb-1">{feature.title}</h4>
                    <p className="text-sm text-gray-400 leading-relaxed">{feature.desc}</p>
                  </div>
                </div>
              ))}
            </div>

            <Link
              to="/features/congress-trading"
              className="inline-flex items-center gap-2.5 bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-100 transition-colors"
            >
              Explore Congressional Trades
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CongressSection;
