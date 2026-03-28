import { TrendingUp, ArrowRight, Zap, Shield, BarChart3 } from 'lucide-react';
import { Link } from 'react-router-dom';

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

const DashboardPreview = () => {
  const mockTrades = [
    { ticker: 'NVDA', insider: getCEOName('NVDA'), type: 'Buy', value: '$8.2M', change: '+12.4%', status: 'High Conviction' },
    { ticker: 'TSLA', insider: getCEOName('TSLA'), type: 'Buy', value: '$5.1M', change: '+8.7%', status: 'Cluster Detected' },
    { ticker: 'META', insider: getCEOName('META'), type: 'Sell', value: '$12.8M', change: '-3.2%', status: 'Normal Pattern' },
    { ticker: 'AAPL', insider: getCEOName('AAPL'), type: 'Buy', value: '$3.4M', change: '+5.1%', status: 'Cluster Detected' },
  ];

  return (
    <section className="py-24 px-4 bg-[#0a0a12] relative overflow-hidden">
      <div className="dp-orb-1 absolute top-[-10%] left-[-5%] w-[500px] h-[500px] rounded-full blur-[140px] pointer-events-none" />
      <div className="dp-orb-2 absolute bottom-[-10%] right-[-5%] w-[500px] h-[500px] rounded-full blur-[140px] pointer-events-none" />
      <div className="dp-orb-3 absolute top-[50%] left-[50%] -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full blur-[180px] pointer-events-none" />

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div>
            <div className="inline-flex items-center gap-2.5 bg-purple-500/[0.08] backdrop-blur-sm border border-purple-500/20 rounded-full px-5 py-2.5 mb-8 group">
              <BarChart3 className="w-4 h-4 text-purple-400 drop-shadow-[0_0_6px_rgba(168,85,247,0.4)]" />
              <span className="text-sm font-medium text-purple-300">Dashboard Demo</span>
            </div>

            <h2 className="text-4xl lg:text-[3.25rem] font-bold mb-7 leading-[1.15] tracking-tight">
              <span className="text-white">Institutional-Grade</span>
              <span className="dp-gradient-text block mt-2">
                Trading Intelligence
              </span>
            </h2>

            <p className="text-lg text-gray-400 mb-10 leading-relaxed max-w-lg">
              See exactly what corporate insiders and Congress members are trading in real-time.
              Get the same data that hedge funds pay millions for—delivered instantly to your dashboard.
            </p>

            <div className="flex flex-wrap gap-3 mb-12">
              {[
                { icon: Zap, color: 'yellow', label: 'AI-Powered Insights' },
                { icon: Shield, color: 'green', label: 'SEC-Verified Data' },
                { icon: TrendingUp, color: 'blue', label: 'Real-Time Alerts' },
              ].map((pill) => (
                <div
                  key={pill.label}
                  className="flex items-center gap-2.5 bg-white/[0.04] backdrop-blur-sm border border-white/[0.08] rounded-full px-5 py-2.5 hover:bg-white/[0.07] hover:border-white/[0.15] transition-all duration-300"
                >
                  <pill.icon className={`w-4 h-4 text-${pill.color}-400 drop-shadow-[0_0_6px_rgba(var(--pill-glow),0.4)]`} />
                  <span className="text-sm font-medium text-gray-200">{pill.label}</span>
                </div>
              ))}
            </div>

            <div className="flex flex-wrap gap-4">
              <Link
                to="/register"
                className="dp-cta-primary inline-flex items-center gap-2.5 bg-white text-black px-8 py-4 rounded-full font-bold transition-all duration-300 hover:scale-[1.03] group"
              >
                View Live Dashboard
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
              </Link>
              <Link
                to="/about"
                className="inline-flex items-center gap-2.5 bg-white/[0.04] backdrop-blur-sm border border-white/[0.1] text-white px-8 py-4 rounded-full font-bold hover:bg-white/[0.08] hover:border-white/[0.18] transition-all duration-300"
              >
                About the Project
              </Link>
            </div>
          </div>

          <div className="relative">
            <div className="dp-card-border relative rounded-2xl p-[1px]">
              <div className="bg-[#0f0f1a]/90 backdrop-blur-2xl rounded-2xl p-7 shadow-2xl">
                <div className="flex items-center justify-between mb-7 pb-4 border-b border-white/[0.06]">
                  <h3 className="text-lg font-bold text-white">Recent Insider Trades</h3>
                  <span className="text-[11px] font-medium text-amber-400 bg-amber-500/[0.08] px-3 py-1.5 rounded-full border border-amber-500/20">Demo Data</span>
                </div>

                <div className="space-y-3">
                  {mockTrades.map((trade, index) => (
                    <div
                      key={index}
                      className="dp-trade-row group relative bg-white/[0.03] border border-white/[0.06] rounded-xl p-4 hover:bg-white/[0.06] transition-all duration-300 cursor-pointer overflow-hidden"
                    >
                      <div className={`absolute left-0 top-0 bottom-0 w-[3px] rounded-l-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 ${
                        trade.type === 'Buy' ? 'bg-gradient-to-b from-green-400 to-emerald-500' : 'bg-gradient-to-b from-red-400 to-rose-500'
                      }`} />
                      <div className="flex items-center justify-between mb-2.5">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-purple-500/80 to-blue-500/80 rounded-lg flex items-center justify-center shadow-lg">
                            <span className="font-bold text-white text-sm">{trade.ticker.slice(0, 2)}</span>
                          </div>
                          <div>
                            <div className="font-bold text-white text-sm">{trade.ticker}</div>
                            <div className="text-xs text-gray-500">{trade.insider}</div>
                          </div>
                        </div>
                        <div className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${
                          trade.type === 'Buy'
                            ? 'bg-green-500/[0.12] text-green-400 border border-green-500/[0.15]'
                            : 'bg-red-500/[0.12] text-red-400 border border-red-500/[0.15]'
                        }`}>
                          {trade.type === 'Buy' ? <TrendingUp className="w-3 h-3" /> : <TrendingUp className="w-3 h-3 rotate-180" />}
                          {trade.type}
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-purple-300 font-semibold">{trade.value}</span>
                        <span className={`font-semibold ${trade.change.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
                          {trade.change}
                        </span>
                        <span className="text-gray-500 bg-white/[0.04] px-2.5 py-1 rounded-md text-[11px]">{trade.status}</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-7 pt-4 border-t border-white/[0.06] flex items-center justify-between">
                  <span className="text-xs text-gray-600">Real SEC Form 4 data</span>
                  <button className="text-xs text-purple-400 hover:text-purple-300 font-medium flex items-center gap-1.5 group transition-colors duration-300">
                    View All Trades
                    <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition-transform duration-300" />
                  </button>
                </div>
              </div>
            </div>

            <div className="dp-float-badge absolute -top-5 -right-5 rounded-2xl p-[1px] max-w-[140px]">
              <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl p-4 shadow-[0_8px_32px_rgba(34,197,94,0.25)]">
                <div className="text-2xl font-bold text-white mb-1">SEC</div>
                <div className="text-xs text-green-100/80">Form 4 Data</div>
              </div>
            </div>

            <div className="dp-float-badge-2 absolute -bottom-5 -left-5 rounded-2xl p-[1px] max-w-[140px]">
              <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl p-4 shadow-[0_8px_32px_rgba(59,130,246,0.25)]">
                <div className="text-2xl font-bold text-white mb-1">&lt;2min</div>
                <div className="text-xs text-blue-100/80">Alert Speed</div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-20 pt-14 border-t border-white/[0.05]">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { value: 'SEC', label: 'Form 4 Filings', color: 'purple' },
              { value: '535', label: 'Congress Members', color: 'blue' },
              { value: 'Real-Time', label: 'Data Updates', color: 'green' },
              { value: 'Gemini', label: 'AI Powered', color: 'orange' },
            ].map((stat) => (
              <div
                key={stat.label}
                className="bg-white/[0.03] backdrop-blur-sm border border-white/[0.06] rounded-2xl p-6 text-center hover:bg-white/[0.05] hover:border-white/[0.1] transition-all duration-300"
              >
                <div className={`text-3xl font-bold text-${stat.color}-400 mb-2`}>{stat.value}</div>
                <div className="text-sm text-gray-500">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <style>{`
        .dp-orb-1 {
          background: radial-gradient(circle, rgba(147, 51, 234, 0.12) 0%, transparent 70%);
          animation: dp-orb-drift 12s ease-in-out infinite;
        }

        .dp-orb-2 {
          background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
          animation: dp-orb-drift 15s ease-in-out infinite reverse;
        }

        .dp-orb-3 {
          background: radial-gradient(circle, rgba(139, 92, 246, 0.06) 0%, transparent 70%);
          animation: dp-orb-drift 18s ease-in-out infinite;
        }

        @keyframes dp-orb-drift {
          0%, 100% { transform: translate(-50%, -50%) scale(1); }
          33% { transform: translate(-45%, -55%) scale(1.05); }
          66% { transform: translate(-55%, -45%) scale(0.95); }
        }

        .dp-gradient-text {
          background: linear-gradient(135deg, #a78bfa, #60a5fa, #c084fc, #818cf8);
          background-size: 300% 300%;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          animation: dp-gradient-shift 6s ease-in-out infinite;
        }

        @keyframes dp-gradient-shift {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }

        .dp-card-border {
          background: linear-gradient(135deg, rgba(168, 85, 247, 0.2), rgba(59, 130, 246, 0.1), rgba(168, 85, 247, 0.05), rgba(59, 130, 246, 0.2));
          background-size: 300% 300%;
          animation: dp-border-gradient 8s ease-in-out infinite;
        }

        @keyframes dp-border-gradient {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }

        .dp-cta-primary {
          box-shadow: 0 0 0 0 rgba(255, 255, 255, 0);
          transition: box-shadow 0.3s ease, transform 0.3s ease;
        }

        .dp-cta-primary:hover {
          box-shadow: 0 4px 30px rgba(255, 255, 255, 0.15), 0 0 60px rgba(168, 85, 247, 0.1);
        }

        .dp-float-badge {
          animation: dp-float 5s ease-in-out infinite;
        }

        .dp-float-badge-2 {
          animation: dp-float 5s ease-in-out infinite 1.5s;
        }

        @keyframes dp-float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-8px); }
        }

        .dp-trade-row:hover {
          border-color: rgba(168, 85, 247, 0.15);
        }
      `}</style>
    </section>
  );
};

export default DashboardPreview;
