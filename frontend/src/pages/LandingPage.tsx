import { Link } from 'react-router-dom';
import { TrendingUp, Zap, ChevronRight, ArrowRight, Globe, Activity, Building2 } from 'lucide-react';
import LiveTicker from '../components/landing/LiveTicker';
import DashboardPreview from '../components/landing/DashboardPreview';
import CongressSection from '../components/landing/CongressSection';
import FeaturesShowcase from '../components/landing/FeaturesShowcase';
import FinalCTA from '../components/landing/FinalCTA';
import { motion, useInView, useMotionValue, useTransform, animate } from 'framer-motion';
import { useRef, useEffect, useState } from 'react';

const AnimatedCounter = ({ target, suffix = '' }: { target: number; suffix?: string }) => {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });
  const count = useMotionValue(0);
  const rounded = useTransform(count, (v) => `${Math.round(v)}${suffix}`);
  const [display, setDisplay] = useState(`0${suffix}`);

  useEffect(() => {
    if (isInView) {
      const controls = animate(count, target, { duration: 2, ease: 'easeOut' });
      const unsub = rounded.on('change', (v) => setDisplay(v));
      return () => { controls.stop(); unsub(); };
    }
  }, [isInView, target, count, rounded]);

  return <div ref={ref}>{display}</div>;
};

const fadeUp = {
  hidden: { opacity: 0, y: 40 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay: i * 0.15, ease: [0.22, 1, 0.36, 1] as const },
  }),
} satisfies import('framer-motion').Variants;

const LandingPage = () => {
  const featuresRef = useRef(null);
  const howRef = useRef(null);
  const usersRef = useRef(null);
  const cardsRef = useRef(null);
  const featuresInView = useInView(featuresRef, { once: true, margin: '-80px' });
  const howInView = useInView(howRef, { once: true, margin: '-80px' });
  const usersInView = useInView(usersRef, { once: true, margin: '-80px' });
  const cardsInView = useInView(cardsRef, { once: true, margin: '-80px' });

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white selection:bg-purple-500 selection:text-white font-sans overflow-x-hidden">

      <style>{`
        @keyframes mesh-rotate-1 { 0% { transform: translate(-50%, -50%) scale(1); } 33% { transform: translate(-30%, -60%) scale(1.2); } 66% { transform: translate(-70%, -40%) scale(0.9); } 100% { transform: translate(-50%, -50%) scale(1); } }
        @keyframes mesh-rotate-2 { 0% { transform: translate(-50%, -50%) scale(1.1); } 33% { transform: translate(-60%, -30%) scale(0.8); } 66% { transform: translate(-40%, -70%) scale(1.3); } 100% { transform: translate(-50%, -50%) scale(1.1); } }
        @keyframes mesh-rotate-3 { 0% { transform: translate(-50%, -50%) scale(0.9); } 33% { transform: translate(-70%, -60%) scale(1.1); } 66% { transform: translate(-30%, -30%) scale(1); } 100% { transform: translate(-50%, -50%) scale(0.9); } }
        @keyframes mesh-rotate-4 { 0% { transform: translate(-50%, -50%) scale(1); } 50% { transform: translate(-40%, -55%) scale(1.15); } 100% { transform: translate(-50%, -50%) scale(1); } }
        @keyframes shimmer { 0% { background-position: -200% center; } 100% { background-position: 200% center; } }
        @keyframes shimmer-border { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        @keyframes gradient-text { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        @keyframes line-shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
        @keyframes float-badge { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-8px); } }
        .animate-mesh-1 { animation: mesh-rotate-1 20s ease-in-out infinite; }
        .animate-mesh-2 { animation: mesh-rotate-2 25s ease-in-out infinite; }
        .animate-mesh-3 { animation: mesh-rotate-3 18s ease-in-out infinite; }
        .animate-mesh-4 { animation: mesh-rotate-4 22s ease-in-out infinite; }
        .animate-shimmer { animation: shimmer 3s linear infinite; background-size: 200% auto; }
        .animate-shimmer-border { animation: shimmer-border 3s ease infinite; background-size: 300% 300%; }
        .animate-gradient-text { animation: gradient-text 4s ease infinite; background-size: 300% 300%; }
        .animate-line-shimmer { animation: line-shimmer 3s linear infinite; background-size: 200% 100%; }
        .animate-float { animation: float-badge 3s ease-in-out infinite; }
        .animate-float-delay { animation: float-badge 3.5s ease-in-out 0.5s infinite; }
        .animate-float-delay-2 { animation: float-badge 4s ease-in-out 1s infinite; }
      `}</style>

      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
        <div className="absolute inset-0 -z-10" style={{ backgroundImage: 'radial-gradient(rgba(255,255,255,0.03) 1px, transparent 1px)', backgroundSize: '32px 32px' }} />

        <div className="absolute top-1/2 left-1/2 w-[700px] h-[700px] rounded-full blur-[140px] -z-10 bg-purple-600/25 animate-mesh-1" />
        <div className="absolute top-1/2 left-1/2 w-[600px] h-[600px] rounded-full blur-[120px] -z-10 bg-blue-600/20 animate-mesh-2" />
        <div className="absolute top-1/2 left-1/2 w-[500px] h-[500px] rounded-full blur-[100px] -z-10 bg-indigo-500/15 animate-mesh-3" />
        <div className="absolute top-1/2 left-1/2 w-[400px] h-[400px] rounded-full blur-[80px] -z-10 bg-violet-500/10 animate-mesh-4" />

        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="max-w-5xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-8 relative overflow-hidden"
            >
              <div className="absolute inset-0 rounded-full p-[1px]">
                <div className="absolute inset-0 rounded-full animate-shimmer-border bg-gradient-to-r from-purple-500/40 via-blue-400/40 to-purple-500/40" />
              </div>
              <div className="absolute inset-[1px] rounded-full bg-[#0a0a0a]/90 backdrop-blur-sm" />
              <span className="relative flex h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              <span className="relative text-xs font-medium text-gray-300 tracking-wide uppercase">Institutional-Grade Intelligence</span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.15 }}
              className="text-6xl md:text-8xl lg:text-9xl font-bold leading-[0.95] mb-8 tracking-tight"
            >
              Decode the <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-blue-400 to-purple-400 animate-gradient-text">
                Smart Money.
              </span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="text-xl md:text-2xl text-gray-400 mb-12 max-w-3xl mx-auto leading-relaxed"
            >
              TradeSignal tracks <strong className="text-gray-200">SEC Form 4</strong> insider filings, <strong className="text-gray-200">STOCK Act</strong> congressional disclosures, and institutional flows with <strong className="text-gray-200">LUNA</strong>, our advanced AI engine. See what the market movers are doing before the news breaks.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.45 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Link
                to="/register"
                className="group px-8 py-4 bg-white text-black font-bold rounded-full text-lg hover:bg-gray-100 transition-all hover:scale-105 flex items-center justify-center gap-2 shadow-[0_0_30px_rgba(255,255,255,0.25)] hover:shadow-[0_0_50px_rgba(255,255,255,0.4)]"
              >
                Start Free Trial <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                to="/login"
                className="px-8 py-4 bg-white/5 backdrop-blur-md border border-white/10 text-white font-semibold rounded-full text-lg hover:bg-white/10 hover:border-white/20 transition-all flex items-center justify-center"
              >
                Live Demo
              </Link>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.7 }}
              className="mt-16 flex flex-wrap justify-center gap-4 lg:gap-6"
            >
              {[
                { label: '15M+ Filings', color: 'from-purple-500/20 to-purple-500/5 border-purple-500/20', anim: 'animate-float' },
                { label: 'Real-Time', color: 'from-blue-500/20 to-blue-500/5 border-blue-500/20', anim: 'animate-float-delay' },
                { label: 'AI-Powered', color: 'from-indigo-500/20 to-indigo-500/5 border-indigo-500/20', anim: 'animate-float-delay-2' },
              ].map((badge) => (
                <div key={badge.label} className={`${badge.anim} px-4 py-2 rounded-full bg-gradient-to-r ${badge.color} border backdrop-blur-sm text-sm font-medium text-gray-300`}>
                  {badge.label}
                </div>
              ))}
            </motion.div>
          </div>
        </div>

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

      <LiveTicker />

      <section className="py-24 bg-[#0f0f1a] relative" id="features" ref={featuresRef}>
        <div className="absolute inset-0" style={{ backgroundImage: 'radial-gradient(rgba(255,255,255,0.02) 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
        <div className="max-w-7xl mx-auto px-6 relative">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <motion.div
              initial="hidden"
              animate={featuresInView ? 'visible' : 'hidden'}
              variants={fadeUp}
              custom={0}
            >
              <h2 className="text-4xl lg:text-6xl font-bold mb-6 tracking-tight">
                Market Intelligence <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">Without The Noise</span>
              </h2>
              <p className="text-lg text-gray-400 mb-8 leading-relaxed">
                Stop guessing. Start tracking. TradeSignal aggregates millions of data points from regulatory filings, news, and market activity to give you a clear signal.
              </p>
              <Link to="/register" className="group px-6 py-3 bg-white/5 border border-white/10 hover:bg-white/10 hover:border-purple-500/30 rounded-full text-white font-medium transition-all inline-flex items-center gap-2 hover:shadow-[0_0_20px_rgba(168,85,247,0.15)]">
                Explore Features <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </motion.div>

            <div className="space-y-6">
              {[
                {
                  icon: <Activity className="w-6 h-6" />,
                  title: "Real-Time Insider Flow",
                  desc: "Instant notifications when CEOs and CFOs buy their own stock. Filter by transaction size and significance.",
                  gradient: 'from-purple-500 to-blue-500',
                },
                {
                  icon: <Building2 className="w-6 h-6" />,
                  title: "Congressional Trading",
                  desc: "Track US Senators and Representatives. See who is beating the market and copy their trades.",
                  gradient: 'from-blue-500 to-cyan-500',
                },
                {
                  icon: <Zap className="w-6 h-6" />,
                  title: "LUNA Advanced AI",
                  desc: "Our proprietary LUNA engine filters out noise to highlight high-conviction trades, sentiment anomalies, and hidden patterns.",
                  gradient: 'from-violet-500 to-purple-500',
                },
              ].map((feature, i) => (
                <motion.div
                  key={i}
                  initial="hidden"
                  animate={featuresInView ? 'visible' : 'hidden'}
                  variants={fadeUp}
                  custom={i + 1}
                  className="group flex gap-5 p-6 rounded-2xl bg-white/[0.03] backdrop-blur-sm border border-white/[0.06] hover:border-purple-500/30 transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgba(168,85,247,0.08)] relative overflow-hidden"
                >
                  <div className={`absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r ${feature.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />
                  <div className={`shrink-0 w-12 h-12 bg-gradient-to-br ${feature.gradient} rounded-xl flex items-center justify-center text-white shadow-lg`}>
                    {feature.icon}
                  </div>
                  <div>
                    <h3 className="text-lg font-bold mb-2 text-gray-100">{feature.title}</h3>
                    <p className="text-gray-400 leading-relaxed text-sm">{feature.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="py-24 bg-black relative" ref={howRef}>
        <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        <div className="max-w-7xl mx-auto px-6">
          <motion.div
            initial="hidden"
            animate={howInView ? 'visible' : 'hidden'}
            variants={fadeUp}
            custom={0}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-5xl font-bold mb-6">From Data to <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">Alpha</span></h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              We process millions of regulatory filings instantly so you don't have to.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-12 relative">
            <div className="hidden md:block absolute top-12 left-[16%] right-[16%] h-[2px] z-0 bg-gradient-to-r from-purple-500/0 via-purple-500/50 to-blue-500/0 animate-line-shimmer" style={{ backgroundImage: 'linear-gradient(90deg, transparent 0%, rgba(168,85,247,0) 10%, rgba(168,85,247,0.5) 30%, rgba(59,130,246,0.5) 50%, rgba(168,85,247,0.5) 70%, rgba(168,85,247,0) 90%, transparent 100%)', backgroundSize: '200% 100%' }} />

            {[
              { step: "01", title: "Ingest", desc: "We monitor SEC EDGAR, Capitol Hill disclosures, and dark pool data feeds in real-time." },
              { step: "02", title: "Analyze", desc: "LUNA, our advanced AI, parses filings, analyzes sentiment, and identifies anomalous transaction patterns in milliseconds." },
              { step: "03", title: "Alert", desc: "You receive instant notifications via SMS, Email, or Discord when a high-conviction trade occurs." },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial="hidden"
                animate={howInView ? 'visible' : 'hidden'}
                variants={fadeUp}
                custom={i + 1}
                className="relative z-10 text-center"
              >
                <div className="w-24 h-24 bg-[#0f0f1a] rounded-full flex items-center justify-center mx-auto mb-6 relative">
                  <div className="absolute inset-0 rounded-full bg-gradient-to-br from-purple-500/30 to-blue-500/30 animate-pulse" style={{ filter: 'blur(12px)' }} />
                  <div className="absolute inset-0 rounded-full border-2 border-transparent" style={{ background: 'linear-gradient(#0f0f1a, #0f0f1a) padding-box, linear-gradient(135deg, rgba(168,85,247,0.6), rgba(59,130,246,0.6)) border-box' }} />
                  <span className="relative text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-br from-white to-purple-400">{item.step}</span>
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{item.title}</h3>
                <p className="text-gray-400 leading-relaxed">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <DashboardPreview />

      <CongressSection />

      <section className="py-24 bg-[#0f0f1a] relative" ref={usersRef}>
        <div className="absolute inset-0" style={{ backgroundImage: 'radial-gradient(rgba(255,255,255,0.015) 1px, transparent 1px)', backgroundSize: '36px 36px' }} />
        <div className="max-w-7xl mx-auto px-6 relative">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <motion.div
              initial="hidden"
              animate={usersInView ? 'visible' : 'hidden'}
              variants={fadeUp}
              custom={0}
            >
              <h2 className="text-3xl md:text-5xl font-bold mb-8">Built for the <br /><span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">Modern Trader</span></h2>
              <div className="space-y-8">
                {[
                  { color: 'bg-purple-500', hoverGlow: 'group-hover:shadow-[0_0_12px_rgba(168,85,247,0.4)]', label: 'Retail Investors', desc: 'Level the playing field by accessing the same data institutional investors use to make decisions.' },
                  { color: 'bg-blue-500', hoverGlow: 'group-hover:shadow-[0_0_12px_rgba(59,130,246,0.4)]', label: 'Day Traders', desc: 'Catch momentum shifts early by tracking real-time insider buying and selling clusters.' },
                  { color: 'bg-green-500', hoverGlow: 'group-hover:shadow-[0_0_12px_rgba(34,197,94,0.4)]', label: 'Financial Analysts', desc: 'Save hours of research time with automated summaries of Form 4 filings and sentiment analysis.' },
                ].map((item, i) => (
                  <motion.div
                    key={i}
                    initial="hidden"
                    animate={usersInView ? 'visible' : 'hidden'}
                    variants={fadeUp}
                    custom={i + 1}
                    className="group"
                  >
                    <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-3">
                      <span className={`w-8 h-[2px] ${item.color} rounded-full transition-all ${item.hoverGlow}`} /> {item.label}
                    </h3>
                    <p className="text-gray-400 pl-11">{item.desc}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
            <motion.div
              initial="hidden"
              animate={usersInView ? 'visible' : 'hidden'}
              variants={fadeUp}
              custom={2}
              className="relative"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-blue-500/10 blur-3xl -z-10" />
              <div className="grid grid-cols-2 gap-4">
                {[
                  { value: 15, suffix: 'M+', label: 'Filings Processed', extraClass: 'mt-12' },
                  { value: 24, suffix: '/7', label: 'Market Monitoring', extraClass: '' },
                  { value: 500, suffix: '+', label: 'Congressional Trades', extraClass: '' },
                  { value: 92, suffix: '%', label: 'Sentiment Accuracy', extraClass: 'mt-[-3rem]' },
                ].map((stat, i) => (
                  <div key={i} className={`group bg-black/50 backdrop-blur-sm p-6 rounded-2xl border border-white/5 hover:border-purple-500/20 transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgba(168,85,247,0.06)] ${stat.extraClass}`}>
                    <div className="text-4xl font-bold text-white mb-1">
                      <AnimatedCounter target={stat.value} suffix={stat.suffix} />
                    </div>
                    <div className="text-sm text-gray-500">{stat.label}</div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      <section className="py-24 bg-black relative" ref={cardsRef}>
        <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-purple-500/20 to-transparent" />
        <div className="max-w-7xl mx-auto px-6">
          <motion.div
            initial="hidden"
            animate={cardsInView ? 'visible' : 'hidden'}
            variants={fadeUp}
            custom={0}
            className="text-center max-w-3xl mx-auto mb-16"
          >
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400 font-bold tracking-widest text-xs uppercase mb-3 block">Live Signals</span>
            <h2 className="text-4xl lg:text-6xl font-bold mb-6 tracking-tight">
              See What Others <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-blue-400 to-purple-400 animate-gradient-text">Miss.</span>
            </h2>
            <p className="text-gray-400 text-lg">
              TradeSignal visualizes complex data into actionable insights.
            </p>
          </motion.div>

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
                barColor: 'bg-gradient-to-r from-red-600 to-red-400',
                conviction: 'High',
                convictionColor: 'text-red-400',
                borderHover: 'hover:border-red-500/30',
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
                barColor: 'bg-gradient-to-r from-green-600 to-green-400',
                conviction: 'Very High',
                convictionColor: 'text-green-400',
                borderHover: 'hover:border-green-500/30',
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
                borderHover: 'hover:border-blue-500/30',
                colSpan: 'md:col-span-2 lg:col-span-1',
              },
            ].map((card, i) => (
              <motion.div
                key={i}
                initial="hidden"
                animate={cardsInView ? 'visible' : 'hidden'}
                variants={fadeUp}
                custom={i + 1}
                className={`group relative bg-[#0f0f1a] rounded-3xl overflow-hidden border border-white/10 ${card.borderHover} transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_12px_40px_rgba(168,85,247,0.1)] ${card.colSpan}`}
              >
                <div className="absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" style={{ background: 'linear-gradient(135deg, rgba(168,85,247,0.1), rgba(59,130,246,0.1), rgba(168,85,247,0.1))', backgroundSize: '300% 300%', animation: 'shimmer-border 3s ease infinite' }} />
                <div className={`aspect-video bg-gradient-to-br ${card.gradient} p-6 flex flex-col justify-end relative overflow-hidden`}>
                  <div className={`absolute inset-0 bg-[url('${card.image}')] bg-cover bg-center opacity-20 mix-blend-overlay group-hover:opacity-30 group-hover:scale-105 transition-all duration-500`} />
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
                        <div className={`h-full ${card.barColor} rounded-full transition-all duration-1000`} style={{ width: card.barWidth }} />
                      </div>
                      <div className="flex justify-between mt-2 text-xs text-gray-500">
                        <span>Conviction</span>
                        <span className={`${card.convictionColor} font-bold`}>{card.conviction}</span>
                      </div>
                    </>
                  ) : (
                    <button className="flex items-center gap-2 text-sm font-medium hover:text-purple-400 transition-colors group/btn">
                      View Analysis <div className="bg-white/10 rounded-full p-1 group-hover/btn:bg-purple-500/20 transition-colors"><ChevronRight className="w-3 h-3" /></div>
                    </button>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <FeaturesShowcase />

      <FinalCTA />

      <section className="py-32 text-center px-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#0f0f1a] to-black" />
        <div className="absolute top-1/2 left-1/2 w-[600px] h-[600px] rounded-full blur-[160px] bg-purple-600/10 animate-mesh-1" style={{ transform: 'translate(-50%, -50%)' }} />
        <div className="absolute top-1/2 left-1/2 w-[400px] h-[400px] rounded-full blur-[120px] bg-blue-600/10 animate-mesh-2" style={{ transform: 'translate(-50%, -50%)' }} />
        <div className="absolute inset-0" style={{ backgroundImage: 'radial-gradient(rgba(255,255,255,0.02) 1px, transparent 1px)', backgroundSize: '32px 32px' }} />
        <div className="max-w-4xl mx-auto relative z-10">
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-4xl lg:text-7xl font-bold mb-6 tracking-tight"
          >
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-purple-200 to-white animate-gradient-text">TradeSignal.</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto"
          >
            Professional grade intelligence for the modern investor. Join thousands of traders tracking the smart money today.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Link
              to="/register"
              className="px-10 py-4 bg-white text-black font-bold rounded-full text-lg hover:bg-gray-100 transition-all hover:scale-105 inline-block shadow-[0_0_40px_rgba(255,255,255,0.2)] hover:shadow-[0_0_60px_rgba(255,255,255,0.35)]"
            >
              Get Started
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
