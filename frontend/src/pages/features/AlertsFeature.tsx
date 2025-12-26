import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Bell, Smartphone, Zap, Filter, CheckCircle, ArrowRight, Mail } from 'lucide-react';

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

export default function AlertsFeature() {
  const features = [
    {
      icon: <Bell className="w-6 h-6" />,
      title: "Real-Time Notifications",
      description: "Get instant alerts when insider trades, congressional disclosures, or AI insights match your criteria."
    },
    {
      icon: <Filter className="w-6 h-6" />,
      title: "Custom Filters",
      description: "Create personalized alert rules based on companies, trade size, position, transaction type, and more."
    },
    {
      icon: <Smartphone className="w-6 h-6" />,
      title: "Multi-Channel Delivery",
      description: "Receive alerts via email, push notifications, or in-app - choose what works best for you."
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Priority Alerts",
      description: "LUNA AI flags high-confidence signals so you never miss critical opportunities."
    }
  ];

  const alertTypes = [
    {
      title: "Insider Trade Alerts",
      description: "Get notified when insiders buy or sell in companies you're watching",
      example: "CEO of AAPL purchased $2.5M worth of shares"
    },
    {
      title: "Congressional Activity",
      description: "Track when members of Congress trade stocks in your watchlist",
      example: "Senator purchased 1,000 shares of NVDA"
    },
    {
      title: "AI Signal Alerts",
      description: "Receive notifications when LUNA AI detects high-confidence patterns",
      example: "Bullish signal detected for TSLA (92% confidence)"
    },
    {
      title: "Price Movement Alerts",
      description: "Get alerts when stocks with recent insider activity hit price targets",
      example: "MSFT reached $400 following insider buying"
    }
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
            <Bell className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-blue-300">Smart Alert System</span>
          </motion.div>

          <motion.h1
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            className="text-5xl lg:text-7xl font-bold mb-6 tracking-tight"
          >
            Never Miss{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
              an Opportunity
            </span>
          </motion.h1>

          <motion.p
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            className="text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed mb-10"
          >
            Stay ahead of the market with real-time alerts for insider trades, congressional activity,
            and AI-generated signals - all customized to your watchlist.
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
              Start Getting Alerts
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/pricing"
              className="px-8 py-3.5 bg-white/5 hover:bg-white/10 border border-white/20 text-white rounded-full font-medium transition-all"
            >
              View Alert Limits
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 bg-black/20 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-5xl font-bold mb-4">
              Intelligent Alert System
            </h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Customizable, real-time notifications delivered exactly how and when you need them
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

      {/* Alert Types Section */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-5xl font-bold mb-4">
              Alert Types
            </h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Choose from multiple alert types to stay informed about what matters most
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {alertTypes.map((type, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: i % 2 === 0 ? -20 : 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="p-6 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 transition-all"
              >
                <div className="flex items-start gap-3 mb-3">
                  <CheckCircle className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <h3 className="text-xl font-bold mb-2">{type.title}</h3>
                    <p className="text-gray-400 text-sm mb-3">{type.description}</p>
                    <div className="bg-black/40 border border-white/10 rounded-lg p-3">
                      <p className="text-xs text-gray-500 mb-1">Example Alert:</p>
                      <p className="text-sm text-blue-300">{type.example}</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Delivery Methods */}
      <section className="py-24 bg-black/20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl lg:text-5xl font-bold mb-6">
                Alerts Your Way
              </h2>
              <p className="text-gray-400 text-lg mb-8 leading-relaxed">
                Receive notifications through your preferred channels. Whether you're at your desk
                or on the go, stay connected to market opportunities.
              </p>

              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Mail className="w-6 h-6 text-purple-400" />
                  </div>
                  <div>
                    <h3 className="font-bold mb-1">Email Alerts</h3>
                    <p className="text-sm text-gray-400">
                      Detailed alerts with full context delivered to your inbox
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Smartphone className="w-6 h-6 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="font-bold mb-1">Push Notifications</h3>
                    <p className="text-sm text-gray-400">
                      Instant mobile notifications for time-sensitive alerts
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Bell className="w-6 h-6 text-green-400" />
                  </div>
                  <div>
                    <h3 className="font-bold mb-1">In-App Notifications</h3>
                    <p className="text-sm text-gray-400">
                      Stay informed while browsing with real-time in-app alerts
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-tr from-blue-600/20 to-purple-600/20 rounded-3xl blur-3xl"></div>
              <div className="relative bg-gradient-to-br from-gray-900/50 to-black border border-white/10 rounded-3xl p-8">
                <div className="space-y-4">
                  <div className="flex items-start gap-3 p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl">
                    <Bell className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-sm font-semibold mb-1">Insider Trade Alert</p>
                      <p className="text-xs text-gray-400">
                        CEO of AAPL purchased 50,000 shares worth $2.5M
                      </p>
                      <p className="text-xs text-gray-500 mt-1">2 minutes ago</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-4 bg-purple-500/10 border border-purple-500/20 rounded-xl">
                    <Zap className="w-5 h-5 text-purple-400 mt-0.5 flex-shrink-0 fill-purple-400" />
                    <div>
                      <p className="text-sm font-semibold mb-1">AI Signal Detected</p>
                      <p className="text-xs text-gray-400">
                        Bullish pattern for NVDA (87% confidence)
                      </p>
                      <p className="text-xs text-gray-500 mt-1">15 minutes ago</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-4 bg-green-500/10 border border-green-500/20 rounded-xl">
                    <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-sm font-semibold mb-1">Price Target Hit</p>
                      <p className="text-xs text-gray-400">
                        TSLA reached $250 following insider activity
                      </p>
                      <p className="text-xs text-gray-500 mt-1">1 hour ago</p>
                    </div>
                  </div>
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
            Start Receiving Alerts Today
          </h2>
          <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
            Never miss another trading opportunity. Get real-time alerts tailored to your watchlist.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/register"
              className="group px-8 py-3.5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white rounded-full font-medium transition-all hover:shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:scale-105 flex items-center gap-2"
            >
              Enable Alerts Free
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/pricing"
              className="px-8 py-3.5 bg-white/5 hover:bg-white/10 border border-white/20 text-white rounded-full font-medium transition-all"
            >
              Compare Plans
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
