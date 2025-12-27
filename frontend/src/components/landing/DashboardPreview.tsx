import { TrendingUp, ArrowRight, Zap, Shield, BarChart3 } from 'lucide-react';
import { Link } from 'react-router-dom';

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

const DashboardPreview = () => {
  // PORTFOLIO MODE: Demo data with CEO names
  const mockTrades = [
    { ticker: 'NVDA', insider: getCEOName('NVDA'), type: 'Buy', value: '$8.2M', change: '+12.4%', status: 'High Conviction' },
    { ticker: 'TSLA', insider: getCEOName('TSLA'), type: 'Buy', value: '$5.1M', change: '+8.7%', status: 'Cluster Detected' },
    { ticker: 'META', insider: getCEOName('META'), type: 'Sell', value: '$12.8M', change: '-3.2%', status: 'Normal Pattern' },
    { ticker: 'AAPL', insider: getCEOName('AAPL'), type: 'Buy', value: '$3.4M', change: '+5.1%', status: 'Cluster Detected' },
  ];

  return (
    <section className="py-20 px-4 bg-[#0f0f1a] relative overflow-hidden">
      {/* Background Glow Effects */}
      <div className="absolute top-0 left-[-10%] w-[40%] h-[40%] bg-purple-900/10 blur-[120px] rounded-full"></div>
      <div className="absolute bottom-0 right-[-10%] w-[40%] h-[40%] bg-blue-900/10 blur-[120px] rounded-full"></div>

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Side: Content */}
          <div>
            <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 rounded-full px-4 py-2 mb-6">
              <BarChart3 className="w-4 h-4 text-purple-400" />
              <span className="text-sm text-purple-300">Dashboard Demo</span>
            </div>

            <h2 className="text-4xl lg:text-5xl font-bold mb-6 leading-tight">
              <span className="text-white">Institutional-Grade</span>
              <span className="block bg-gradient-to-r from-purple-400 via-blue-400 to-purple-400 bg-clip-text text-transparent mt-2">
                Trading Intelligence
              </span>
            </h2>

            <p className="text-xl text-gray-400 mb-8 leading-relaxed">
              See exactly what corporate insiders and Congress members are trading in real-time.
              Get the same data that hedge funds pay millions for—delivered instantly to your dashboard.
            </p>

            {/* Feature Pills */}
            <div className="flex flex-wrap gap-3 mb-10">
              <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-full px-4 py-2">
                <Zap className="w-4 h-4 text-yellow-400" />
                <span className="text-sm text-white">AI-Powered Insights</span>
              </div>
              <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-full px-4 py-2">
                <Shield className="w-4 h-4 text-green-400" />
                <span className="text-sm text-white">SEC-Verified Data</span>
              </div>
              <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-full px-4 py-2">
                <TrendingUp className="w-4 h-4 text-blue-400" />
                <span className="text-sm text-white">Real-Time Alerts</span>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-wrap gap-4">
              <Link
                to="/register"
                className="inline-flex items-center gap-2 bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-200 transition-all hover:scale-105 group"
              >
                View Live Dashboard
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              {/* PORTFOLIO MODE: Changed from pricing to about */}
              <Link
                to="/about"
                className="inline-flex items-center gap-2 bg-white/5 border border-white/10 text-white px-8 py-4 rounded-full font-bold hover:bg-white/10 transition-all"
              >
                About the Project
              </Link>
            </div>
          </div>

          {/* Right Side: Dashboard Mockup */}
          <div className="relative">
            {/* Main Dashboard Card */}
            <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl">
              {/* Header */}
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/5">
                <h3 className="text-lg font-bold text-white">Recent Insider Trades</h3>
                <span className="text-xs text-amber-400 bg-amber-500/10 px-3 py-1 rounded-full border border-amber-500/20">Demo Data</span>
              </div>

              {/* Table */}
              <div className="space-y-3">
                {mockTrades.map((trade, index) => (
                  <div
                    key={index}
                    className="bg-white/5 border border-white/5 rounded-xl p-4 hover:bg-white/10 hover:border-purple-500/30 transition-all cursor-pointer group"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
                          <span className="font-bold text-white text-sm">{trade.ticker.slice(0, 2)}</span>
                        </div>
                        <div>
                          <div className="font-bold text-white text-sm">{trade.ticker}</div>
                          <div className="text-xs text-gray-500">{trade.insider}</div>
                        </div>
                      </div>
                      <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                        trade.type === 'Buy'
                          ? 'bg-green-500/20 text-green-400'
                          : 'bg-red-500/20 text-red-400'
                      }`}>
                        {trade.type === 'Buy' ? <TrendingUp className="w-3 h-3" /> : <TrendingUp className="w-3 h-3 rotate-180" />}
                        {trade.type}
                      </div>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-purple-400 font-semibold">{trade.value}</span>
                      <span className={`font-medium ${trade.change.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
                        {trade.change}
                      </span>
                      <span className="text-gray-500 bg-white/5 px-2 py-0.5 rounded">{trade.status}</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Footer */}
              <div className="mt-6 pt-4 border-t border-white/5 flex items-center justify-between">
                <span className="text-xs text-gray-500">Real SEC Form 4 data</span>
                <button className="text-xs text-purple-400 hover:text-purple-300 font-medium flex items-center gap-1 group">
                  View All Trades
                  <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
            </div>

            {/* Floating Stats Cards - PORTFOLIO MODE: Factual info only */}
            <div className="absolute -top-4 -right-4 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl p-4 shadow-xl border border-green-400/20 max-w-[140px]">
              <div className="text-2xl font-bold text-white mb-1">SEC</div>
              <div className="text-xs text-green-100">Form 4 Data</div>
            </div>

            <div className="absolute -bottom-4 -left-4 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl p-4 shadow-xl border border-blue-400/20 max-w-[140px]">
              <div className="text-2xl font-bold text-white mb-1">&lt;2min</div>
              <div className="text-xs text-blue-100">Alert Speed</div>
            </div>
          </div>
        </div>

        {/* Bottom Trust Bar - PORTFOLIO MODE: Factual stats only */}
        <div className="mt-16 pt-12 border-t border-white/5">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-purple-400 mb-2">SEC</div>
              <div className="text-sm text-gray-500">Form 4 Filings</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-400 mb-2">535</div>
              <div className="text-sm text-gray-500">Congress Members</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-green-400 mb-2">Real-Time</div>
              <div className="text-sm text-gray-500">Data Updates</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-orange-400 mb-2">Gemini</div>
              <div className="text-sm text-gray-500">AI Powered</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default DashboardPreview;
