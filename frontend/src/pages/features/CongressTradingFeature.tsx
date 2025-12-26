import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Building2, Eye, BarChart3, Bell, CheckCircle, ArrowRight } from 'lucide-react';

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

export default function CongressTradingFeature() {
  const features = [
    {
      icon: <Eye className="w-6 h-6" />,
      title: "Full Transparency",
      description: "Access complete congressional trading disclosures as soon as they're filed with the Clerk of the House."
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Advanced Filtering",
      description: "Filter by representative, party, committee, transaction type, and date range to find exactly what you're looking for."
    },
    {
      icon: <Building2 className="w-6 h-6" />,
      title: "Verified Sources",
      description: "All data sourced directly from official congressional financial disclosure reports."
    },
    {
      icon: <Bell className="w-6 h-6" />,
      title: "Real-Time Updates",
      description: "Get instant notifications when members of Congress trade stocks in your watchlist."
    }
  ];

  const benefits = [
    "Track stock trades by all members of Congress",
    "See which sectors and companies politicians are investing in",
    "Analyze trading patterns before major legislation",
    "Filter by congressional committee assignments",
    "100% free access - no subscription required"
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden px-6">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-600/20 rounded-full blur-[120px]"></div>
        </div>

        <div className="max-w-4xl mx-auto text-center relative z-10">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/20 rounded-full mb-6"
          >
            <Building2 className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-blue-300">Congressional Trading Tracker</span>
          </motion.div>

          <motion.h1
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            className="text-5xl lg:text-7xl font-bold mb-6 tracking-tight"
          >
            Watch{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
              Congress Trade
            </span>
          </motion.h1>

          <motion.p
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            className="text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed mb-10"
          >
            Track real-time stock trades by members of Congress. See what your representatives
            are buying and selling before major policy decisions.
          </motion.p>

          <motion.div
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link
              to="/register"
              className="group px-8 py-3.5 bg-blue-600 hover:bg-blue-700 text-white rounded-full font-medium transition-all hover:shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:scale-105 flex items-center gap-2"
            >
              Access for Free
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/congressional-trades"
              className="px-8 py-3.5 bg-white/5 hover:bg-white/10 border border-white/20 text-white rounded-full font-medium transition-all"
            >
              View Sample Data
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 bg-black/20 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-5xl font-bold mb-4">
              Congressional Trading Intelligence
            </h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Everything you need to track and understand congressional stock trading activity
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
                className="p-6 rounded-2xl border border-white/10 bg-gradient-to-br from-blue-900/20 to-black backdrop-blur-xl hover:border-blue-500/30 transition-all"
              >
                <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center mb-4 text-blue-400">
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
                Why Track Congressional Trades?
              </h2>
              <p className="text-gray-400 text-lg mb-8 leading-relaxed">
                Members of Congress have access to non-public information that could affect stock prices.
                Their trading activity can provide valuable insights into upcoming legislation and policy changes.
              </p>

              <div className="space-y-4">
                {benefits.map((benefit, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                    <p className="text-gray-300">{benefit}</p>
                  </div>
                ))}
              </div>

              <div className="mt-8 p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl">
                <p className="text-sm text-blue-300">
                  <strong>Free Forever:</strong> Congressional trading data is completely free
                  for all TradeSignal users. No subscription required.
                </p>
              </div>
            </div>

            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-tr from-blue-600/20 to-purple-600/20 rounded-3xl blur-3xl"></div>
              <div className="relative bg-gradient-to-br from-gray-900/50 to-black border border-white/10 rounded-3xl p-8">
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                    <div>
                      <p className="text-sm text-gray-400">Representative</p>
                      <p className="font-semibold">Nancy Pelosi</p>
                      <p className="text-xs text-gray-500">House Financial Services</p>
                    </div>
                    <div className="text-right">
                      <p className="text-green-400 font-semibold">Buy</p>
                      <p className="text-xs text-gray-500">NVDA</p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                    <div>
                      <p className="text-sm text-gray-400">Senator</p>
                      <p className="font-semibold">Richard Burr</p>
                      <p className="text-xs text-gray-500">Senate Intelligence</p>
                    </div>
                    <div className="text-right">
                      <p className="text-red-400 font-semibold">Sell</p>
                      <p className="text-xs text-gray-500">BA</p>
                    </div>
                  </div>

                  <p className="text-xs text-gray-500 text-center pt-4">
                    Example data for illustration purposes
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
            Start Tracking Congress Today
          </h2>
          <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
            Free access to all congressional trading data. No credit card required.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/register"
              className="group px-8 py-3.5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white rounded-full font-medium transition-all hover:shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:scale-105 flex items-center gap-2"
            >
              Get Started Free
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/about"
              className="px-8 py-3.5 bg-white/5 hover:bg-white/10 border border-white/20 text-white rounded-full font-medium transition-all"
            >
              Learn More
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
