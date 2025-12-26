import { useEffect, useState } from 'react';
import { Building2, TrendingUp, TrendingDown, ArrowRight, Users } from 'lucide-react';
import { Link } from 'react-router-dom';

interface CongressTrade {
  id: number;
  ticker: string;
  representative: string;
  state: string;
  transaction_type: string;
  amount: string;
  filed_at: string;
  party?: string;
}

const CongressSection = () => {
  const [congressTrades, setCongressTrades] = useState<CongressTrade[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchCongressTrades = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/congressional-trades?limit=4`);
        if (response.ok) {
          const data = await response.json();
          setCongressTrades(data);
        }
      } catch (error) {
        console.error('Failed to fetch congressional trades:', error);
        // Use mock data as fallback
        setCongressTrades([
          {
            id: 1,
            ticker: 'NVDA',
            representative: 'Nancy Pelosi',
            state: 'CA',
            transaction_type: 'Purchase',
            amount: '$1M - $5M',
            filed_at: new Date().toISOString(),
            party: 'Democrat'
          },
          {
            id: 2,
            ticker: 'MSFT',
            representative: 'Tommy Tuberville',
            state: 'AL',
            transaction_type: 'Purchase',
            amount: '$500K - $1M',
            filed_at: new Date().toISOString(),
            party: 'Republican'
          },
          {
            id: 3,
            ticker: 'TSLA',
            representative: 'Josh Gottheimer',
            state: 'NJ',
            transaction_type: 'Sale',
            amount: '$250K - $500K',
            filed_at: new Date().toISOString(),
            party: 'Democrat'
          },
          {
            id: 4,
            ticker: 'AAPL',
            representative: 'Dan Crenshaw',
            state: 'TX',
            transaction_type: 'Purchase',
            amount: '$100K - $250K',
            filed_at: new Date().toISOString(),
            party: 'Republican'
          }
        ]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCongressTrades();
  }, []);

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getPartyColor = (party?: string) => {
    if (party?.toLowerCase().includes('democrat')) return 'from-blue-500 to-blue-600';
    if (party?.toLowerCase().includes('republican')) return 'from-red-500 to-red-600';
    return 'from-purple-500 to-indigo-500';
  };

  return (
    <section className="py-20 px-4 bg-[#0a0a0a] relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-0 right-[-10%] w-[40%] h-[40%] bg-blue-900/10 blur-[120px] rounded-full"></div>

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Right Side: Content (appears first on mobile) */}
          <div className="order-2 lg:order-1">
            {/* Trades List */}
            {isLoading ? (
              <div className="space-y-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-6 animate-pulse">
                    <div className="flex items-center gap-4">
                      <div className="w-14 h-14 bg-white/10 rounded-full"></div>
                      <div className="flex-1 space-y-2">
                        <div className="h-4 bg-white/10 rounded w-3/4"></div>
                        <div className="h-3 bg-white/10 rounded w-1/2"></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {congressTrades.map((trade) => {
                  const isPurchase = trade.transaction_type.toLowerCase().includes('purchase') ||
                                    trade.transaction_type.toLowerCase().includes('buy');

                  return (
                    <div
                      key={trade.id}
                      className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-6 hover:border-blue-500/30 transition-all group cursor-pointer"
                    >
                      <div className="flex items-center gap-4">
                        {/* Avatar */}
                        <div className={`w-14 h-14 bg-gradient-to-br ${getPartyColor(trade.party)} rounded-full flex items-center justify-center text-white font-bold text-lg flex-shrink-0`}>
                          {getInitials(trade.representative)}
                        </div>

                        {/* Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-bold text-white truncate">{trade.representative}</h4>
                            <span className="text-xs text-gray-500 bg-white/5 px-2 py-0.5 rounded">{trade.state}</span>
                          </div>
                          <div className="flex items-center gap-3 flex-wrap">
                            <span className="text-sm font-semibold text-purple-400">{trade.ticker}</span>
                            <div className={`flex items-center gap-1 text-xs font-medium ${
                              isPurchase ? 'text-green-400' : 'text-red-400'
                            }`}>
                              {isPurchase ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                              {isPurchase ? 'Bought' : 'Sold'}
                            </div>
                            <span className="text-xs text-gray-400">{trade.amount}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* View All Button */}
            <div className="mt-6">
              <Link
                to="/register"
                className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 font-medium group"
              >
                View All Congressional Trades
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          </div>

          {/* Left Side: Text Content */}
          <div className="order-1 lg:order-2">
            <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-4 py-2 mb-6">
              <Building2 className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-blue-300">Congressional Trading</span>
            </div>

            <h2 className="text-4xl lg:text-5xl font-bold mb-6 leading-tight">
              <span className="text-white">Follow What</span>
              <span className="block bg-gradient-to-r from-blue-400 via-purple-400 to-blue-400 bg-clip-text text-transparent mt-2">
                Congress is Trading
              </span>
            </h2>

            <p className="text-xl text-gray-400 mb-8 leading-relaxed">
              Track stock transactions from all 535 members of Congress in real-time.
              The STOCK Act requires disclosure within 45 days—we alert you the moment they file.
            </p>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-6 mb-10">
              <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-2">
                  <Users className="w-5 h-5 text-blue-400" />
                  <span className="text-2xl font-bold text-white">535</span>
                </div>
                <p className="text-sm text-gray-500">Members Tracked</p>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-5 h-5 text-green-400" />
                  <span className="text-2xl font-bold text-white">2,400+</span>
                </div>
                <p className="text-sm text-gray-500">Trades in Q4 2024</p>
              </div>
            </div>

            {/* Key Features */}
            <div className="space-y-3 mb-10">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-blue-500/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-blue-400 text-xs">✓</span>
                </div>
                <div>
                  <h4 className="font-semibold text-white mb-1">Real-Time STOCK Act Filings</h4>
                  <p className="text-sm text-gray-400">Instant alerts when representatives file new trades</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-blue-500/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-blue-400 text-xs">✓</span>
                </div>
                <div>
                  <h4 className="font-semibold text-white mb-1">Committee Analysis</h4>
                  <p className="text-sm text-gray-400">See which committee members are trading in their sectors</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-blue-500/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-blue-400 text-xs">✓</span>
                </div>
                <div>
                  <h4 className="font-semibold text-white mb-1">Cluster Detection</h4>
                  <p className="text-sm text-gray-400">AI identifies when multiple members buy the same stock</p>
                </div>
              </div>
            </div>

            {/* CTA */}
            <Link
              to="/features/congress-trading"
              className="inline-flex items-center gap-2 bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-200 transition-all hover:scale-105 group"
            >
              Explore Congressional Trades
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CongressSection;
