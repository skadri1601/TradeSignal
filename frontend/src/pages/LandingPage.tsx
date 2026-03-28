import { Link } from 'react-router-dom';
import { TrendingUp, Zap, ChevronRight, ArrowRight, Globe, Activity, Building2 } from 'lucide-react';
import LiveTicker from '../components/landing/LiveTicker';
import DashboardPreview from '../components/landing/DashboardPreview';
import CongressSection from '../components/landing/CongressSection';
import FeaturesShowcase from '../components/landing/FeaturesShowcase';
import FinalCTA from '../components/landing/FinalCTA';
import { motion } from 'framer-motion';

const fadeIn = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.5 } },
} satisfies import('framer-motion').Variants;

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white selection:bg-purple-500 selection:text-white font-sans overflow-x-hidden">

      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32">
        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="max-w-5xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-8 border border-white/[0.06] bg-[#111]"
            >
              <span className="flex h-2 w-2 rounded-full bg-green-500" />
              <span className="text-xs font-medium text-gray-300 tracking-wide uppercase">Institutional-Grade Intelligence</span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-6xl md:text-8xl lg:text-9xl font-bold leading-[0.95] mb-8 tracking-tight"
            >
              Decode the <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-purple-500">
                Smart Money.
              </span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-xl md:text-2xl text-gray-400 mb-12 max-w-3xl mx-auto leading-relaxed"
            >
              TradeSignal tracks <strong className="text-gray-200">SEC Form 4</strong> insider filings, <strong className="text-gray-200">STOCK Act</strong> congressional disclosures, and institutional flows with <strong className="text-gray-200">LUNA</strong>, our advanced AI engine. See what the market movers are doing before the news breaks.
            </motion.p>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Link
                to="/register"
                className="px-8 py-4 bg-white text-black font-bold rounded-full text-lg hover:bg-gray-100 transition-colors flex items-center justify-center gap-2"
              >
                Start Free Trial <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                to="/login"
                className="px-8 py-4 border border-white/10 text-white font-semibold rounded-full text-lg hover:bg-white/5 transition-colors flex items-center justify-center"
              >
                Live Demo
              </Link>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="mt-16 flex flex-wrap justify-center gap-4 lg:gap-6"
            >
              {['15M+ Filings', 'Real-Time', 'AI-Powered'].map((label) => (
                <div key={label} className="px-4 py-2 rounded-full bg-[#111] border border-white/[0.06] text-sm font-medium text-gray-400">
                  {label}
                </div>
              ))}
            </motion.div>
          </div>
        </div>
      </section>

      <LiveTicker />

      <section className="py-24 bg-[#0a0a0a] border-t border-white/[0.06]" id="features">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl lg:text-6xl font-bold mb-6 tracking-tight">
                Market Intelligence <br />
                <span className="text-purple-400">Without The Noise</span>
              </h2>
              <p className="text-lg text-gray-400 mb-8 leading-relaxed">
                Stop guessing. Start tracking. TradeSignal aggregates millions of data points from regulatory filings, news, and market activity to give you a clear signal.
              </p>
              <Link to="/register" className="px-6 py-3 border border-white/10 hover:bg-white/5 rounded-full text-white font-medium transition-colors inline-flex items-center gap-2">
                Explore Features <ChevronRight className="w-4 h-4" />
              </Link>
            </div>

            <div className="space-y-6">
              {[
                {
                  icon: <Activity className="w-6 h-6" />,
                  title: "Real-Time Insider Flow",
                  desc: "Instant notifications when CEOs and CFOs buy their own stock. Filter by transaction size and significance.",
                },
                {
                  icon: <Building2 className="w-6 h-6" />,
                  title: "Congressional Trading",
                  desc: "Track US Senators and Representatives. See who is beating the market and copy their trades.",
                },
                {
                  icon: <Zap className="w-6 h-6" />,
                  title: "LUNA Advanced AI",
                  desc: "Our proprietary LUNA engine filters out noise to highlight high-conviction trades, sentiment anomalies, and hidden patterns.",
                },
              ].map((feature, i) => (
                <div
                  key={i}
                  className="flex gap-5 p-6 rounded-xl bg-[#111] border border-white/[0.06] hover:bg-white/[0.04] transition-colors"
                >
                  <div className="shrink-0 w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center text-purple-400">
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

      <section className="py-24 bg-[#0a0a0a] border-t border-white/[0.06]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-6">From Data to <span className="text-purple-400">Alpha</span></h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              We process millions of regulatory filings instantly so you don't have to.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12">
            {[
              { step: "01", title: "Ingest", desc: "We monitor SEC EDGAR, Capitol Hill disclosures, and dark pool data feeds in real-time." },
              { step: "02", title: "Analyze", desc: "LUNA, our advanced AI, parses filings, analyzes sentiment, and identifies anomalous transaction patterns in milliseconds." },
              { step: "03", title: "Alert", desc: "You receive instant notifications via SMS, Email, or Discord when a high-conviction trade occurs." },
            ].map((item, i) => (
              <div key={i} className="text-center">
                <div className="w-20 h-20 bg-[#111] border border-white/[0.06] rounded-full flex items-center justify-center mx-auto mb-6">
                  <span className="text-2xl font-bold text-white">{item.step}</span>
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{item.title}</h3>
                <p className="text-gray-400 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <DashboardPreview />

      <CongressSection />

      <section className="py-24 bg-[#0a0a0a] border-t border-white/[0.06]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl md:text-5xl font-bold mb-8">Built for the <br /><span className="text-purple-400">Modern Trader</span></h2>
              <div className="space-y-8">
                {[
                  { color: 'bg-purple-500', label: 'Retail Investors', desc: 'Level the playing field by accessing the same data institutional investors use to make decisions.' },
                  { color: 'bg-blue-500', label: 'Day Traders', desc: 'Catch momentum shifts early by tracking real-time insider buying and selling clusters.' },
                  { color: 'bg-green-500', label: 'Financial Analysts', desc: 'Save hours of research time with automated summaries of Form 4 filings and sentiment analysis.' },
                ].map((item, i) => (
                  <div key={i}>
                    <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-3">
                      <span className={`w-8 h-[2px] ${item.color} rounded-full`} /> {item.label}
                    </h3>
                    <p className="text-gray-400 pl-11">{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { value: '15M+', label: 'Filings Processed', extraClass: 'mt-12' },
                  { value: '24/7', label: 'Market Monitoring', extraClass: '' },
                  { value: '500+', label: 'Congressional Trades', extraClass: '' },
                  { value: '92%', label: 'Sentiment Accuracy', extraClass: 'mt-[-3rem]' },
                ].map((stat, i) => (
                  <div key={i} className={`bg-[#111] p-6 rounded-xl border border-white/[0.06] ${stat.extraClass}`}>
                    <div className="text-4xl font-bold text-white mb-1">{stat.value}</div>
                    <div className="text-sm text-gray-500">{stat.label}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-24 bg-[#0a0a0a] border-t border-white/[0.06]">
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
            {[
              {
                gradient: 'from-blue-900/40 to-black',
                image: 'https://images.unsplash.com/photo-1611974765270-ca1258634369?auto=format&fit=crop&q=80&w=800',
                badgeColor: 'red',
                badgeIcon: <TrendingUp className="w-4 h-4 text-red-400" />,
                badgeText: 'Bearish Signal',
                time: '12m ago',
                title: 'MCD: Insider Selling Spree',
                desc: 'Multiple executives have offloaded significant positions ahead of the earnings report. AI sentiment analysis indicates caution.',
                barWidth: '85%',
                barColor: 'bg-red-500',
                conviction: 'High',
                convictionColor: 'text-red-400',
                colSpan: '',
              },
              {
                gradient: 'from-purple-900/40 to-black',
                image: 'https://images.unsplash.com/photo-1621761191319-c6fb62004040?auto=format&fit=crop&q=80&w=800',
                badgeColor: 'green',
                badgeIcon: <TrendingUp className="w-4 h-4 text-green-400" />,
                badgeText: 'Bullish Flow',
                time: '45m ago',
                title: 'AAPL: Institutional Accumulation',
                desc: 'Unusual options activity detected combined with large block buys on dark pools. Institutions are positioning for a breakout.',
                barWidth: '92%',
                barColor: 'bg-green-500',
                conviction: 'Very High',
                convictionColor: 'text-green-400',
                colSpan: '',
              },
              {
                gradient: 'from-indigo-900/40 to-black',
                image: 'https://images.unsplash.com/photo-1518546305927-5a555bb7020d?auto=format&fit=crop&q=80&w=800',
                badgeColor: 'blue',
                badgeIcon: <Globe className="w-4 h-4 text-blue-400" />,
                badgeText: 'Macro Event',
                time: 'Live',
                title: 'Crypto & Fed Correlation',
                desc: 'Analyzing the decoupling of Bitcoin from traditional equities as Fed rate hike probabilities shift.',
                barWidth: '',
                barColor: '',
                conviction: '',
                convictionColor: '',
                colSpan: 'md:col-span-2 lg:col-span-1',
              },
            ].map((card, i) => (
              <div
                key={i}
                className={`bg-[#111] rounded-2xl overflow-hidden border border-white/[0.06] hover:bg-white/[0.04] transition-colors ${card.colSpan}`}
              >
                <div className={`aspect-video bg-gradient-to-br ${card.gradient} p-6 flex flex-col justify-end relative overflow-hidden`}>
                  <div className={`absolute inset-0 bg-[url('${card.image}')] bg-cover bg-center opacity-20 mix-blend-overlay`} />
                  <div className="relative z-10">
                    <div className="flex items-center gap-2 mb-2">
                      <div className={`bg-${card.badgeColor}-500/20 border border-${card.badgeColor}-500/50 p-1 rounded-full`}>{card.badgeIcon}</div>
                      <span className={`text-sm font-medium text-${card.badgeColor}-200`}>{card.badgeText}</span>
                      <span className="text-xs text-gray-500 ml-auto">{card.time}</span>
                    </div>
                    <h3 className="text-xl font-bold leading-tight">{card.title}</h3>
                  </div>
                </div>
                <div className="p-6">
                  <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                    {card.desc}
                  </p>
                  {card.barWidth ? (
                    <>
                      <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                        <div className={`h-full ${card.barColor} rounded-full`} style={{ width: card.barWidth }} />
                      </div>
                      <div className="flex justify-between mt-2 text-xs text-gray-500">
                        <span>Conviction</span>
                        <span className={`${card.convictionColor} font-bold`}>{card.conviction}</span>
                      </div>
                    </>
                  ) : (
                    <button className="flex items-center gap-2 text-sm font-medium hover:text-purple-400 transition-colors">
                      View Analysis <ChevronRight className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <FeaturesShowcase />

      <FinalCTA />

      <section className="py-32 text-center px-6 bg-[#0a0a0a] border-t border-white/[0.06]">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeIn}
          className="max-w-4xl mx-auto"
        >
          <h2 className="text-4xl lg:text-7xl font-bold mb-6 tracking-tight text-white">
            TradeSignal.
          </h2>
          <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
            Professional grade intelligence for the modern investor. Join thousands of traders tracking the smart money today.
          </p>
          <Link
            to="/register"
            className="px-10 py-4 bg-white text-black font-bold rounded-full text-lg hover:bg-gray-100 transition-colors inline-block"
          >
            Get Started
          </Link>
        </motion.div>
      </section>
    </div>
  );
};

export default LandingPage;
