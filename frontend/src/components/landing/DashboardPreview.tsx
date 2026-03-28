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
    <section className="py-24 px-4 bg-[#0a0a0a] border-t border-white/[0.06]">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div>
            <div className="inline-flex items-center gap-2.5 bg-[#111] border border-white/[0.06] rounded-full px-5 py-2.5 mb-8">
              <BarChart3 className="w-4 h-4 text-purple-400" />
              <span className="text-sm font-medium text-gray-300">Dashboard Demo</span>
            </div>

            <h2 className="text-4xl lg:text-[3.25rem] font-bold mb-7 leading-[1.15] tracking-tight">
              <span className="text-white">Institutional-Grade</span>
              <span className="text-purple-400 block mt-2">
                Trading Intelligence
              </span>
            </h2>

            <p className="text-lg text-gray-400 mb-10 leading-relaxed max-w-lg">
              See exactly what corporate insiders and Congress members are trading in real-time.
              Get the same data that hedge funds pay millions for—delivered instantly to your dashboard.
            </p>

            <div className="flex flex-wrap gap-3 mb-12">
              {[
                { icon: Zap, label: 'AI-Powered Insights' },
                { icon: Shield, label: 'SEC-Verified Data' },
                { icon: TrendingUp, label: 'Real-Time Alerts' },
              ].map((pill) => (
                <div
                  key={pill.label}
                  className="flex items-center gap-2.5 bg-[#111] border border-white/[0.06] rounded-full px-5 py-2.5"
                >
                  <pill.icon className="w-4 h-4 text-gray-400" />
                  <span className="text-sm font-medium text-gray-300">{pill.label}</span>
                </div>
              ))}
            </div>

            <div className="flex flex-wrap gap-4">
              <Link
                to="/register"
                className="inline-flex items-center gap-2.5 bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-100 transition-colors"
              >
                View Live Dashboard
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                to="/about"
                className="inline-flex items-center gap-2.5 border border-white/10 text-white px-8 py-4 rounded-full font-bold hover:bg-white/5 transition-colors"
              >
                About the Project
              </Link>
            </div>
          </div>

          <div>
            <div className="bg-[#111] border border-white/[0.06] rounded-2xl p-7">
              <div className="flex items-center justify-between mb-7 pb-4 border-b border-white/[0.06]">
                <h3 className="text-lg font-bold text-white">Recent Insider Trades</h3>
                <span className="text-[11px] font-medium text-amber-400 bg-amber-500/[0.08] px-3 py-1.5 rounded-full border border-amber-500/20">Demo Data</span>
              </div>

              <div className="space-y-3">
                {mockTrades.map((trade, index) => (
                  <div
                    key={index}
                    className="bg-white/[0.02] border border-white/[0.06] rounded-xl p-4 hover:bg-white/[0.04] transition-colors cursor-pointer"
                  >
                    <div className="flex items-center justify-between mb-2.5">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-purple-500/10 rounded-lg flex items-center justify-center">
                          <span className="font-bold text-purple-400 text-sm">{trade.ticker.slice(0, 2)}</span>
                        </div>
                        <div>
                          <div className="font-bold text-white text-sm">{trade.ticker}</div>
                          <div className="text-xs text-gray-500">{trade.insider}</div>
                        </div>
                      </div>
                      <div className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${
                        trade.type === 'Buy'
                          ? 'bg-green-500/[0.1] text-green-400'
                          : 'bg-red-500/[0.1] text-red-400'
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
                <button className="text-xs text-purple-400 hover:text-purple-300 font-medium flex items-center gap-1.5 transition-colors">
                  View All Trades
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-20 pt-14 border-t border-white/[0.06]">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { value: 'SEC', label: 'Form 4 Filings', color: 'text-purple-400' },
              { value: '535', label: 'Congress Members', color: 'text-blue-400' },
              { value: 'Real-Time', label: 'Data Updates', color: 'text-green-400' },
              { value: 'Gemini', label: 'AI Powered', color: 'text-orange-400' },
            ].map((stat) => (
              <div
                key={stat.label}
                className="bg-[#111] border border-white/[0.06] rounded-xl p-6 text-center"
              >
                <div className={`text-3xl font-bold ${stat.color} mb-2`}>{stat.value}</div>
                <div className="text-sm text-gray-500">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default DashboardPreview;
