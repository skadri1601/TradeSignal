import { Link } from 'react-router-dom';
import { TrendingUp, Zap, ChevronRight, ArrowRight, Globe, Activity, Building2 } from 'lucide-react';
import LiveTicker from '../components/landing/LiveTicker';
import DashboardPreview from '../components/landing/DashboardPreview';
import CongressSection from '../components/landing/CongressSection';
import FeaturesShowcase from '../components/landing/FeaturesShowcase';
import FinalCTA from '../components/landing/FinalCTA';

const LandingPage = () => {

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white selection:bg-purple-500 selection:text-white font-sans overflow-x-hidden">
      
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
        {/* Abstract Background Elements */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-purple-600/20 rounded-full blur-[120px] -z-10" />
        <div className="absolute bottom-0 right-0 w-[800px] h-[600px] bg-blue-600/10 rounded-full blur-[120px] -z-10" />

        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 mb-6 backdrop-blur-sm">
              <span className="flex h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
              <span className="text-xs font-medium text-gray-300 tracking-wide uppercase">Institutional-Grade Intelligence</span>
            </div>
            
            <h1 className="text-5xl lg:text-8xl font-bold leading-tight mb-6 tracking-tight">
              Decode the <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-blue-400 to-purple-400 animate-gradient-x">
                Smart Money.
              </span>
            </h1>
            <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
              TradeSignal tracks <strong>SEC Form 4</strong> insider filings, <strong>STOCK Act</strong> congressional disclosures, and institutional flows with <strong>LUNA</strong>, our advanced AI engine. See what the market movers are doing before the news breaks.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                to="/register" 
                className="px-8 py-4 bg-white text-black font-bold rounded-full text-lg hover:bg-gray-200 transition-all hover:scale-105 flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(255,255,255,0.3)]"
              >
                Start Free Trial <ArrowRight className="w-5 h-5" />
              </Link>
              <Link 
                to="/login"
                className="px-8 py-4 bg-white/5 backdrop-blur-md border border-white/10 text-white font-semibold rounded-full text-lg hover:bg-white/10 transition-all flex items-center justify-center"
              >
                Live Demo
              </Link>
            </div>
          </div>
        </div>

        {/* Hero Visual / Wave Approximation */}
        <div className="absolute bottom-0 left-0 w-full h-48 sm:h-64 lg:h-96 -z-10 overflow-hidden translate-y-20 opacity-50">
             <svg className="absolute bottom-0 w-full h-full" viewBox="0 0 1440 320" preserveAspectRatio="none">
                <path fill="url(#hero-gradient)" fillOpacity="1" d="M0,160L48,176C96,192,192,224,288,224C384,224,480,192,576,165.3C672,139,768,117,864,128C960,139,1056,181,1152,197.3C1248,213,1344,203,1392,197.3L1440,192L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path>
                <defs>
                  <linearGradient id="hero-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="rgba(124, 58, 237, 0.2)" />
                    <stop offset="100%" stopColor="rgba(59, 130, 246, 0.2)" />
                  </linearGradient>
                </defs>
              </svg>
        </div>
      </section>

      {/* Live Ticker */}
      <LiveTicker />

      {/* Features Grid */}
      <section className="py-24 bg-[#0f0f1a]" id="features">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl lg:text-5xl font-bold mb-6 tracking-tight">
                Market Intelligence <br/> Without The Noise
              </h2>
              <p className="text-lg text-gray-400 mb-8 leading-relaxed">
                Stop guessing. Start tracking. TradeSignal aggregates millions of data points from regulatory filings, news, and market activity to give you a clear signal.
              </p>
              <Link to="/register" className="group px-6 py-3 bg-white/5 border border-white/10 hover:bg-white/10 rounded-full text-white font-medium transition-colors inline-flex items-center gap-2">
                Explore Features <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>

            <div className="space-y-6">
              {[
                {
                  icon: <Activity className="w-6 h-6" />,
                  title: "Real-Time Insider Flow",
                  desc: "Instant notifications when CEOs and CFOs buy their own stock. Filter by transaction size and significance."
                },
                {
                  icon: <Building2 className="w-6 h-6" />,
                  title: "Congressional Trading",
                  desc: "Track US Senators and Representatives. See who is beating the market and copy their trades."
                },
                {
                  icon: <Zap className="w-6 h-6" />,
                  title: "LUNA Advanced AI",
                  desc: "Our proprietary LUNA engine filters out noise to highlight high-conviction trades, sentiment anomalies, and hidden patterns."
                }
              ].map((feature, i) => (
                <div key={i} className="flex gap-5 p-6 rounded-2xl bg-black/40 border border-white/5 hover:border-purple-500/30 transition-all hover:bg-white/[0.02]">
                  <div className="shrink-0 w-12 h-12 bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-xl flex items-center justify-center text-purple-400 border border-white/5">
                    {feature.icon}
                  </div>
                  <div>
                    <h3 className="text-lg font-bold mb-2 text-gray-100">{feature.title}</h3>
                    <p className="text-gray-400 leading-relaxed text-sm">{feature.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 bg-black relative">
        <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent"></div>
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-6">From Data to Alpha</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              We process millions of regulatory filings instantly so you don't have to.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12 relative">
            {/* Connecting Line */}
            <div className="hidden md:block absolute top-12 left-[16%] right-[16%] h-0.5 bg-gradient-to-r from-purple-500/0 via-purple-500/30 to-purple-500/0 z-0"></div>

            {[
              {
                step: "01",
                title: "Ingest",
                desc: "We monitor SEC EDGAR, Capitol Hill disclosures, and dark pool data feeds in real-time."
              },
              {
                step: "02",
                title: "Analyze",
                desc: "LUNA, our advanced AI, parses filings, analyzes sentiment, and identifies anomalous transaction patterns in milliseconds."
              },
              {
                step: "03",
                title: "Alert",
                desc: "You receive instant notifications via SMS, Email, or Discord when a high-conviction trade occurs."
              }
            ].map((item, i) => (
              <div key={i} className="relative z-10 text-center">
                <div className="w-24 h-24 bg-[#0f0f1a] border border-purple-500/30 rounded-full flex items-center justify-center mx-auto mb-6 shadow-[0_0_30px_rgba(168,85,247,0.15)]">
                  <span className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-br from-white to-purple-400">{item.step}</span>
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{item.title}</h3>
                <p className="text-gray-400 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Dashboard Preview */}
      <DashboardPreview />

      {/* Congressional Trading Section */}
      <CongressSection />

      {/* Who Uses TradeSignal */}
      <section className="py-24 bg-[#0f0f1a]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl md:text-5xl font-bold mb-8">Built for the <br/> Modern Trader</h2>
              <div className="space-y-8">
                <div>
                  <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-3">
                    <span className="w-8 h-px bg-purple-500"></span> Retail Investors
                  </h3>
                  <p className="text-gray-400 pl-11">Level the playing field by accessing the same data institutional investors use to make decisions.</p>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-3">
                    <span className="w-8 h-px bg-blue-500"></span> Day Traders
                  </h3>
                  <p className="text-gray-400 pl-11">Catch momentum shifts early by tracking real-time insider buying and selling clusters.</p>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-3">
                    <span className="w-8 h-px bg-green-500"></span> Financial Analysts
                  </h3>
                  <p className="text-gray-400 pl-11">Save hours of research time with automated summaries of Form 4 filings and sentiment analysis.</p>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-blue-500/10 blur-3xl -z-10" />
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-black/50 p-6 rounded-2xl border border-white/5 mt-12">
                  <div className="text-4xl font-bold text-white mb-1">15m+</div>
                  <div className="text-sm text-gray-500">Filings Processed</div>
                </div>
                <div className="bg-black/50 p-6 rounded-2xl border border-white/5">
                  <div className="text-4xl font-bold text-white mb-1">24/7</div>
                  <div className="text-sm text-gray-500">Market Monitoring</div>
                </div>
                <div className="bg-black/50 p-6 rounded-2xl border border-white/5">
                  <div className="text-4xl font-bold text-white mb-1">500+</div>
                  <div className="text-sm text-gray-500">Congressional Trades</div>
                </div>
                <div className="bg-black/50 p-6 rounded-2xl border border-white/5 mt-[-3rem]">
                  <div className="text-4xl font-bold text-white mb-1">92%</div>
                  <div className="text-sm text-gray-500">Sentiment Accuracy</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Dark Cards Section - "Effortless Market Intelligence" */}
      <section className="py-24 bg-black relative">
        <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-purple-500/20 to-transparent"></div>
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-purple-400 font-bold tracking-widest text-xs uppercase mb-3 block">Live Signals</span>
            <h2 className="text-4xl lg:text-6xl font-bold mb-6 tracking-tight">
              See What Others Miss.
            </h2>
            <p className="text-gray-400 text-lg">
              TradeSignal visualizes complex data into actionable insights.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Card 1 */}
            <div className="group relative bg-[#0f0f1a] rounded-3xl overflow-hidden border border-white/10 hover:border-purple-500/50 transition-all duration-300 hover:-translate-y-1">
              <div className="aspect-video bg-gradient-to-br from-blue-900/40 to-black p-6 flex flex-col justify-end relative">
                 <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1611974765270-ca1258634369?auto=format&fit=crop&q=80&w=800')] bg-cover bg-center opacity-20 mix-blend-overlay"></div>
                 <div className="relative z-10">
                   <div className="flex items-center gap-2 mb-2">
                     <div className="bg-red-500/20 border border-red-500/50 p-1 rounded-full"><TrendingUp className="w-4 h-4 text-red-400" /></div>
                     <span className="text-sm font-medium text-red-200">Bearish Signal</span>
                     <span className="text-xs text-gray-500 ml-auto">12m ago</span>
                   </div>
                   <h3 className="text-xl font-bold leading-tight">MCD: Insider Selling Spree</h3>
                 </div>
              </div>
              <div className="p-6">
                <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                  Multiple executives have offloaded significant positions ahead of the earnings report. AI sentiment analysis indicates caution.
                </p>
                <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full w-[85%] bg-red-500"></div>
                </div>
                <div className="flex justify-between mt-2 text-xs text-gray-500">
                    <span>Conviction</span>
                    <span className="text-red-400 font-bold">High</span>
                </div>
              </div>
            </div>

            {/* Card 2 */}
            <div className="group relative bg-[#0f0f1a] rounded-3xl overflow-hidden border border-white/10 hover:border-purple-500/50 transition-all duration-300 hover:-translate-y-1">
               <div className="aspect-video bg-gradient-to-br from-purple-900/40 to-black p-6 flex flex-col justify-end relative">
                 <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1621761191319-c6fb62004040?auto=format&fit=crop&q=80&w=800')] bg-cover bg-center opacity-20 mix-blend-overlay"></div>
                 <div className="relative z-10">
                   <div className="flex items-center gap-2 mb-2">
                     <div className="bg-green-500/20 border border-green-500/50 p-1 rounded-full"><TrendingUp className="w-4 h-4 text-green-400" /></div>
                     <span className="text-sm font-medium text-green-200">Bullish Flow</span>
                     <span className="text-xs text-gray-500 ml-auto">45m ago</span>
                   </div>
                   <h3 className="text-xl font-bold leading-tight">AAPL: Institutional Accumulation</h3>
                 </div>
              </div>
              <div className="p-6">
                <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                  Unusual options activity detected combined with large block buys on dark pools. Institutions are positioning for a breakout.
                </p>
                <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full w-[92%] bg-green-500"></div>
                </div>
                <div className="flex justify-between mt-2 text-xs text-gray-500">
                    <span>Conviction</span>
                    <span className="text-green-400 font-bold">Very High</span>
                </div>
              </div>
            </div>

             {/* Card 3 */}
            <div className="group relative bg-[#0f0f1a] rounded-3xl overflow-hidden border border-white/10 hover:border-purple-500/50 transition-all duration-300 hover:-translate-y-1 md:col-span-2 lg:col-span-1">
               <div className="aspect-video bg-gradient-to-br from-indigo-900/40 to-black p-6 flex flex-col justify-end relative">
                 <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1518546305927-5a555bb7020d?auto=format&fit=crop&q=80&w=800')] bg-cover bg-center opacity-20 mix-blend-overlay"></div>
                 <div className="relative z-10">
                   <div className="flex items-center gap-2 mb-2">
                     <div className="bg-blue-500/20 border border-blue-500/50 p-1 rounded-full"><Globe className="w-4 h-4 text-blue-400" /></div>
                     <span className="text-sm font-medium text-blue-200">Macro Event</span>
                     <span className="text-xs text-gray-500 ml-auto">Live</span>
                   </div>
                   <h3 className="text-xl font-bold leading-tight">Crypto & Fed Correlation</h3>
                 </div>
              </div>
              <div className="p-6">
                <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                   Analyzing the decoupling of Bitcoin from traditional equities as Fed rate hike probabilities shift.
                </p>
                <button className="flex items-center gap-2 text-sm font-medium hover:text-purple-400 transition-colors">
                  View Analysis <div className="bg-white/10 rounded-full p-1"><ChevronRight className="w-3 h-3" /></div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Showcase */}
      <FeaturesShowcase />

      {/* Final CTA */}
      <FinalCTA />

      {/* CTA Footer Section */}
      <section className="py-32 bg-gradient-to-b from-[#0f0f1a] to-black text-center px-6 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-full bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-5"></div>
        <div className="max-w-4xl mx-auto relative z-10">
          <h2 className="text-4xl lg:text-6xl font-bold mb-6 tracking-tight">
            TradeSignal.
          </h2>
          <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
            Professional grade intelligence for the modern investor. Join thousands of traders tracking the smart money today.
          </p>
          <Link 
            to="/register" 
            className="px-10 py-4 bg-white text-black font-bold rounded-full text-lg hover:bg-gray-200 transition-all hover:scale-105 inline-block shadow-lg shadow-white/10"
          >
            Get Started
          </Link>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
