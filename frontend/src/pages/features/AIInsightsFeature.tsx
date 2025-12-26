import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Zap, Brain, Target, TrendingUp, CheckCircle, ArrowRight, Sparkles } from 'lucide-react';

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

export default function AIInsightsFeature() {
  const features = [
    {
      icon: <Brain className="w-6 h-6" />,
      title: "LUNA AI Engine",
      description: "Our proprietary AI analyzes millions of data points to generate high-confidence trading signals."
    },
    {
      icon: <Target className="w-6 h-6" />,
      title: "Pattern Recognition",
      description: "Identifies complex trading patterns and correlations that humans would miss."
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Sentiment Analysis",
      description: "Analyzes insider and congressional trading sentiment across sectors and companies."
    },
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: "Predictive Signals",
      description: "Get actionable insights before the market reacts to insider activity."
    }
  ];

  const benefits = [
    "AI-powered analysis of insider trading patterns",
    "Real-time sentiment scoring for stocks and sectors",
    "Automated detection of unusual trading activity",
    "Personalized insights based on your watchlist",
    "Daily AI-generated market intelligence reports"
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden px-6">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-600/20 rounded-full blur-[120px]"></div>
          <div className="absolute top-1/4 right-1/4 w-[400px] h-[400px] bg-blue-600/20 rounded-full blur-[100px]"></div>
        </div>

        <div className="max-w-4xl mx-auto text-center relative z-10">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/20 rounded-full mb-6"
          >
            <Zap className="w-4 h-4 text-purple-400 fill-purple-400" />
            <span className="text-sm text-transparent bg-clip-text bg-gradient-to-r from-purple-300 to-blue-300">
              LUNA AI Intelligence
            </span>
          </motion.div>

          <motion.h1
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            className="text-5xl lg:text-7xl font-bold mb-6 tracking-tight"
          >
            AI-Powered{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400">
              Trading Insights
            </span>
          </motion.h1>

          <motion.p
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            className="text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed mb-10"
          >
            LUNA AI analyzes millions of insider trades, congressional disclosures, and market signals
            to deliver actionable intelligence you can trust.
          </motion.p>

          <motion.div
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link
              to="/register"
              className="group px-8 py-3.5 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white rounded-full font-medium transition-all hover:shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:scale-105 flex items-center gap-2"
            >
              Try LUNA AI Free
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/pricing"
              className="px-8 py-3.5 bg-white/5 hover:bg-white/10 border border-white/20 text-white rounded-full font-medium transition-all"
            >
              View Pro Features
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 bg-black/20 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-5xl font-bold mb-4">
              Next-Generation AI Analysis
            </h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              LUNA AI processes vast amounts of trading data to uncover hidden opportunities
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="p-6 rounded-2xl border border-white/10 bg-gradient-to-br from-purple-900/20 via-pink-900/10 to-black backdrop-blur-xl hover:border-purple-500/30 transition-all group"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-xl flex items-center justify-center mb-4 text-purple-400 group-hover:scale-110 transition-transform">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl lg:text-5xl font-bold mb-6">
                Why Use AI Insights?
              </h2>
              <p className="text-gray-400 text-lg mb-8 leading-relaxed">
                The financial markets move fast. LUNA AI processes millions of data points in real-time,
                identifying patterns and opportunities that would take humans days or weeks to discover.
              </p>

              <div className="space-y-4">
                {benefits.map((benefit, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                    <p className="text-gray-300">{benefit}</p>
                  </div>
                ))}
              </div>

              <div className="mt-8 p-4 bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/20 rounded-xl">
                <p className="text-sm text-purple-300">
                  <strong className="text-purple-200">Pro Feature:</strong> Full access to LUNA AI requires a
                  Pro or Enterprise subscription.
                </p>
              </div>
            </div>

            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-tr from-purple-600/20 via-pink-600/20 to-blue-600/20 rounded-3xl blur-3xl"></div>
              <div className="relative bg-gradient-to-br from-gray-900/50 to-black border border-white/10 rounded-3xl p-8">
                <div className="space-y-6">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
                      <Zap className="w-5 h-5 text-purple-400 fill-purple-400" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <p className="font-semibold">AAPL - Apple Inc</p>
                        <span className="text-xs px-2 py-0.5 bg-green-500/20 text-green-400 rounded-full">
                          Bullish
                        </span>
                      </div>
                      <p className="text-sm text-gray-400">
                        Heavy insider buying detected. 3 executives purchased shares.
                      </p>
                      <div className="mt-2 flex items-center gap-2">
                        <div className="h-1.5 flex-1 bg-gray-800 rounded-full overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-purple-500 to-blue-500 w-[85%]"></div>
                        </div>
                        <span className="text-xs text-gray-500">85% confidence</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
                      <Zap className="w-5 h-5 text-purple-400 fill-purple-400" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <p className="font-semibold">TSLA - Tesla</p>
                        <span className="text-xs px-2 py-0.5 bg-yellow-500/20 text-yellow-400 rounded-full">
                          Neutral
                        </span>
                      </div>
                      <p className="text-sm text-gray-400">
                        Mixed signals. Monitoring for clearer trend.
                      </p>
                      <div className="mt-2 flex items-center gap-2">
                        <div className="h-1.5 flex-1 bg-gray-800 rounded-full overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-purple-500 to-blue-500 w-[45%]"></div>
                        </div>
                        <span className="text-xs text-gray-500">45% confidence</span>
                      </div>
                    </div>
                  </div>

                  <p className="text-xs text-gray-500 text-center pt-4">
                    Example AI insights for illustration
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl lg:text-5xl font-bold mb-6">
            Ready to Leverage AI Intelligence?
          </h2>
          <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
            Join traders who use LUNA AI to make smarter, data-driven decisions
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/register"
              className="group px-8 py-3.5 bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 hover:from-purple-500 hover:via-pink-500 hover:to-blue-500 text-white rounded-full font-medium transition-all hover:shadow-[0_0_30px_rgba(139,92,246,0.4)] hover:scale-105 flex items-center gap-2"
            >
              Start Free Trial
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/pricing"
              className="px-8 py-3.5 bg-white/5 hover:bg-white/10 border border-white/20 text-white rounded-full font-medium transition-all"
            >
              View Pricing
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
