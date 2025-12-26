import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Users, TrendingUp, Shield, Zap, CheckCircle, ArrowRight } from 'lucide-react';

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

export default function InsiderTradesFeature() {
  const features = [
    {
      icon: <Users className="w-6 h-6" />,
      title: "Real-Time Tracking",
      description: "Track insider trades from executives, directors, and major shareholders as they're filed with the SEC."
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Advanced Analytics",
      description: "Analyze trading patterns, sentiment, and trends to identify meaningful insider activity."
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Verified Data",
      description: "All data sourced directly from SEC Form 4 filings, ensuring accuracy and reliability."
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Instant Alerts",
      description: "Get notified immediately when insiders make significant trades in companies you're watching."
    }
  ];

  const benefits = [
    "Follow the smart money: See what company insiders are buying and selling",
    "Identify potential opportunities before the market reacts",
    "Filter by transaction type, position, and company",
    "View historical insider trading patterns",
    "Track insider ownership changes over time"
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden px-6">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-600/20 rounded-full blur-[120px]"></div>
        </div>

        <div className="max-w-4xl mx-auto text-center relative z-10">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            className="inline-flex items-center gap-2 px-4 py-2 bg-purple-500/10 border border-purple-500/20 rounded-full mb-6"
          >
            <Users className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-purple-300">Insider Trading Intelligence</span>
          </motion.div>

          <motion.h1
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            className="text-5xl lg:text-7xl font-bold mb-6 tracking-tight"
          >
            Follow the{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">
              Smart Money
            </span>
          </motion.h1>

          <motion.p
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            className="text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed mb-10"
          >
            Track real-time insider trading activity from company executives and directors.
            See what the people who know their companies best are buying and selling.
          </motion.p>

          <motion.div
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link
              to="/register"
              className="group px-8 py-3.5 bg-purple-600 hover:bg-purple-700 text-white rounded-full font-medium transition-all hover:shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:scale-105 flex items-center gap-2"
            >
              Get Started Free
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/pricing"
              className="px-8 py-3.5 bg-white/5 hover:bg-white/10 border border-white/20 text-white rounded-full font-medium transition-all"
            >
              View Pricing
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 bg-black/20 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-5xl font-bold mb-4">
              Powerful Insider Trading Tools
            </h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Everything you need to track and analyze insider trading activity
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
                className="p-6 rounded-2xl border border-white/10 bg-gradient-to-br from-purple-900/20 to-black backdrop-blur-xl hover:border-purple-500/30 transition-all"
              >
                <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center mb-4 text-purple-400">
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
                Why Track Insider Trades?
              </h2>
              <p className="text-gray-400 text-lg mb-8 leading-relaxed">
                Insiders have unparalleled knowledge of their companies. When they buy or sell stock,
                it can signal their confidence (or lack thereof) in the company's future prospects.
              </p>

              <div className="space-y-4">
                {benefits.map((benefit, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                    <p className="text-gray-300">{benefit}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-tr from-purple-600/20 to-blue-600/20 rounded-3xl blur-3xl"></div>
              <div className="relative bg-gradient-to-br from-gray-900/50 to-black border border-white/10 rounded-3xl p-8">
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-green-500/20 rounded-full flex items-center justify-center">
                        <TrendingUp className="w-5 h-5 text-green-400" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-400">Recent Buy</p>
                        <p className="font-semibold">John Smith - CEO</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-green-400 font-semibold">+50,000</p>
                      <p className="text-xs text-gray-500">shares</p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-red-500/20 rounded-full flex items-center justify-center">
                        <TrendingUp className="w-5 h-5 text-red-400 rotate-180" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-400">Recent Sell</p>
                        <p className="font-semibold">Jane Doe - CFO</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-red-400 font-semibold">-25,000</p>
                      <p className="text-xs text-gray-500">shares</p>
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
            Ready to Track Insider Trades?
          </h2>
          <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
            Join thousands of traders who use TradeSignal to follow the smart money
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/register"
              className="group px-8 py-3.5 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white rounded-full font-medium transition-all hover:shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:scale-105 flex items-center gap-2"
            >
              Start Free Trial
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/pricing"
              className="px-8 py-3.5 bg-white/5 hover:bg-white/10 border border-white/20 text-white rounded-full font-medium transition-all"
            >
              See All Features
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
