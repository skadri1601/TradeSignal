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
    if (party?.toLowerCase().includes('democrat')) return 'from-blue-500 to-blue-600';
    if (party?.toLowerCase().includes('republican')) return 'from-red-500 to-red-600';
    return 'from-purple-500 to-indigo-500';
  };

  const getPartyGlow = (party?: string) => {
    if (party?.toLowerCase().includes('democrat')) return 'group-hover:shadow-[0_0_24px_rgba(59,130,246,0.2)]';
    if (party?.toLowerCase().includes('republican')) return 'group-hover:shadow-[0_0_24px_rgba(239,68,68,0.2)]';
    return 'group-hover:shadow-[0_0_24px_rgba(168,85,247,0.2)]';
  };

  const getPartyBorder = (party?: string) => {
    if (party?.toLowerCase().includes('democrat')) return 'group-hover:border-blue-500/25';
    if (party?.toLowerCase().includes('republican')) return 'group-hover:border-red-500/25';
    return 'group-hover:border-purple-500/25';
  };

  const getAvatarRing = (party?: string) => {
    if (party?.toLowerCase().includes('democrat')) return 'ring-blue-500/30 group-hover:ring-blue-400/50';
    if (party?.toLowerCase().includes('republican')) return 'ring-red-500/30 group-hover:ring-red-400/50';
    return 'ring-purple-500/30 group-hover:ring-purple-400/50';
  };

  return (
    <section className="py-24 px-4 bg-[#0a0a12] relative overflow-hidden">
      <div className="cs-orb-1 absolute top-[-5%] right-[-8%] w-[500px] h-[500px] rounded-full blur-[140px] pointer-events-none" />
      <div className="cs-orb-2 absolute bottom-[-5%] left-[-8%] w-[400px] h-[400px] rounded-full blur-[120px] pointer-events-none" />

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div className="order-2 lg:order-1">
            <div className="space-y-4">
                {congressTrades.map((trade) => {
                  const isPurchase = trade.transaction_type.toLowerCase().includes('purchase') ||
                                    trade.transaction_type.toLowerCase().includes('buy');

                  return (
                    <div
                      key={trade.id}
                      className={`group bg-[#0f0f1a]/80 backdrop-blur-xl border border-white/[0.06] rounded-2xl p-6 transition-all duration-300 cursor-pointer ${getPartyBorder(trade.party)} ${getPartyGlow(trade.party)}`}
                    >
                      <div className="flex items-center gap-4">
                        <div className={`w-14 h-14 bg-gradient-to-br ${getPartyColor(trade.party)} rounded-full flex items-center justify-center text-white font-bold text-lg flex-shrink-0 ring-2 ${getAvatarRing(trade.party)} transition-all duration-300 shadow-lg`}>
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
                className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 font-medium group transition-colors duration-300"
              >
                View All Congressional Trades
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-300" />
              </Link>
            </div>
          </div>

          <div className="order-1 lg:order-2">
            <div className="cs-section-badge inline-flex items-center gap-2.5 bg-blue-500/[0.08] backdrop-blur-sm border border-blue-500/20 rounded-full px-5 py-2.5 mb-8">
              <Building2 className="w-4 h-4 text-blue-400 drop-shadow-[0_0_6px_rgba(59,130,246,0.4)]" />
              <span className="cs-badge-text text-sm font-medium">Congressional Trading</span>
            </div>

            <h2 className="text-4xl lg:text-[3.25rem] font-bold mb-7 leading-[1.15] tracking-tight">
              <span className="text-white">Follow What</span>
              <span className="cs-gradient-text block mt-2">
                Congress is Trading
              </span>
            </h2>

            <p className="text-lg text-gray-400 mb-10 leading-relaxed max-w-lg">
              Track stock transactions from all 535 members of Congress in real-time.
              The STOCK Act requires disclosure within 45 days—we alert you the moment they file.
            </p>

            <div className="grid grid-cols-2 gap-5 mb-12">
              <div className="bg-white/[0.03] backdrop-blur-sm border border-white/[0.06] rounded-2xl p-6 hover:bg-white/[0.05] hover:border-white/[0.1] transition-all duration-300">
                <div className="flex items-center gap-2.5 mb-3">
                  <Users className="w-5 h-5 text-blue-400 drop-shadow-[0_0_6px_rgba(59,130,246,0.3)]" />
                  <span className="text-3xl font-bold text-white">535</span>
                </div>
                <p className="text-sm text-gray-500">Members Tracked</p>
              </div>
              <div className="bg-white/[0.03] backdrop-blur-sm border border-white/[0.06] rounded-2xl p-6 hover:bg-white/[0.05] hover:border-white/[0.1] transition-all duration-300">
                <div className="flex items-center gap-2.5 mb-3">
                  <TrendingUp className="w-5 h-5 text-green-400 drop-shadow-[0_0_6px_rgba(34,197,94,0.3)]" />
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
                  <div className="cs-check-circle w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
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
              className="cs-cta-btn inline-flex items-center gap-2.5 bg-white text-black px-8 py-4 rounded-full font-bold transition-all duration-300 hover:scale-[1.03] group"
            >
              Explore Congressional Trades
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
            </Link>
          </div>
        </div>
      </div>

      <style>{`
        .cs-orb-1 {
          background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
          animation: cs-orb-drift 14s ease-in-out infinite;
        }

        .cs-orb-2 {
          background: radial-gradient(circle, rgba(139, 92, 246, 0.08) 0%, transparent 70%);
          animation: cs-orb-drift 17s ease-in-out infinite reverse;
        }

        @keyframes cs-orb-drift {
          0%, 100% { transform: scale(1) translate(0, 0); }
          33% { transform: scale(1.05) translate(10px, -10px); }
          66% { transform: scale(0.95) translate(-10px, 10px); }
        }

        .cs-gradient-text {
          background: linear-gradient(135deg, #60a5fa, #a78bfa, #818cf8, #60a5fa);
          background-size: 300% 300%;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          animation: cs-gradient-shift 6s ease-in-out infinite;
        }

        @keyframes cs-gradient-shift {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }

        .cs-badge-text {
          background: linear-gradient(90deg, #93c5fd, #60a5fa, #93c5fd);
          background-size: 200% 100%;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          animation: cs-shimmer 3s ease-in-out infinite;
        }

        @keyframes cs-shimmer {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }

        .cs-check-circle {
          background: linear-gradient(135deg, #3b82f6, #8b5cf6);
          box-shadow: 0 0 12px rgba(59, 130, 246, 0.25);
        }

        .cs-cta-btn {
          box-shadow: 0 0 0 0 rgba(255, 255, 255, 0);
          transition: box-shadow 0.3s ease, transform 0.3s ease;
        }

        .cs-cta-btn:hover {
          box-shadow: 0 4px 30px rgba(255, 255, 255, 0.15), 0 0 60px rgba(59, 130, 246, 0.1);
        }
      `}</style>
    </section>
  );
};

export default CongressSection;
