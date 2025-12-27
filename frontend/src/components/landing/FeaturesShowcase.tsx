import { Database, Brain, Bell, LineChart, Users, Smartphone, Shield, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

const FeaturesShowcase = () => {
  const features = [
    {
      icon: Database,
      title: "Ingest",
      description: "Real-time data from SEC EDGAR and Capitol Hill",
      details: [
        "32,000+ insider trades tracked",
        "535 Congress members monitored",
        "2-hour refresh rate",
        "Form 4 filings within minutes"
      ],
      gradient: "from-purple-500 to-indigo-500"
    },
    {
      icon: Brain,
      title: "Analyze",
      description: "LUNA AI - Intelligence engine powered by Google Gemini",
      details: [
        "AI-powered sentiment analysis",
        "Cluster detection algorithms",
        "Pattern recognition",
        "Conviction scoring system"
      ],
      gradient: "from-blue-500 to-cyan-500"
    },
    {
      icon: Bell,
      title: "Alert",
      description: "Multi-channel real-time notifications",
      details: [
        "SMS, Email, Discord alerts",
        "Custom filter conditions",
        "Webhook integrations",
        "< 2 minute delivery time"
      ],
      gradient: "from-green-500 to-emerald-500"
    },
    {
      icon: LineChart,
      title: "Research",
      description: "Institutional-grade analysis tools",
      details: [
        "IVT (Intrinsic Value Target)",
        "TS Score proprietary metric",
        "Risk level assessments",
        "Technical indicators"
      ],
      gradient: "from-orange-500 to-red-500"
    },
    {
      icon: Users,
      title: "Community",
      description: "Connect with fellow traders",
      details: [
        "Active trading forum",
        "Copy trading feature",
        "Strategy sharing",
        "Community insights"
      ],
      gradient: "from-pink-500 to-rose-500"
    },
    {
      icon: Smartphone,
      title: "Mobile Ready",
      description: "Fully responsive web experience",
      details: [
        "Responsive web design",
        "Mobile-optimized interface",
        "Touch-friendly controls",
        "Works on any device"
      ],
      gradient: "from-violet-500 to-purple-500"
    },
    {
      icon: Shield,
      title: "Security",
      description: "Built with security best practices",
      details: [
        "HTTPS encryption",
        "Secure authentication (JWT)",
        "Password hashing (bcrypt)",
        "Input validation & sanitization"
      ],
      gradient: "from-teal-500 to-cyan-500"
    },
    {
      icon: Zap,
      title: "API Access",
      description: "Programmatic data integration (Future Enhancement)",
      details: [
        "RESTful API endpoints",
        "FastAPI backend",
        "Interactive Swagger docs",
        "Comprehensive documentation"
      ],
      gradient: "from-yellow-500 to-orange-500"
    }
  ];

  return (
    <section className="py-20 px-4 bg-[#0a0a0a] relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-purple-900/10 blur-[120px] rounded-full"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-blue-900/10 blur-[120px] rounded-full"></div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/20 rounded-full px-4 py-2 mb-6">
            <Zap className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-purple-300">Powerful Features</span>
          </div>

          <h2 className="text-4xl lg:text-5xl font-bold mb-6">
            <span className="text-white">Everything You Need to</span>
            <span className="block bg-gradient-to-r from-purple-400 via-blue-400 to-purple-400 bg-clip-text text-transparent mt-2">
              Trade Smarter
            </span>
          </h2>

          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            A complete platform for tracking insider trades, congressional activity, and AI-powered market intelligence
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-6 hover:border-purple-500/30 transition-all group cursor-pointer"
            >
              {/* Icon */}
              <div className={`w-14 h-14 bg-gradient-to-br ${feature.gradient} rounded-2xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform`}>
                <feature.icon className="w-7 h-7 text-white" />
              </div>

              {/* Title & Description */}
              <h3 className="text-xl font-bold text-white mb-2 group-hover:text-purple-400 transition-colors">
                {feature.title}
              </h3>
              <p className="text-sm text-gray-400 mb-4">{feature.description}</p>

              {/* Details List */}
              <ul className="space-y-2">
                {feature.details.map((detail, detailIndex) => (
                  <li key={detailIndex} className="flex items-start gap-2 text-xs text-gray-500">
                    <span className="text-purple-400 mt-0.5 flex-shrink-0">•</span>
                    <span>{detail}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <div className="inline-flex flex-col sm:flex-row gap-4">
            <Link
              to="/register"
              className="inline-flex items-center justify-center gap-2 bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-200 transition-all hover:scale-105"
            >
              Start Free Trial
            </Link>
            {/* PORTFOLIO MODE: Changed from pricing to about */}
            <Link
              to="/about"
              className="inline-flex items-center justify-center gap-2 bg-white/5 border border-white/10 text-white px-8 py-4 rounded-full font-bold hover:bg-white/10 transition-all"
            >
              Learn More
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FeaturesShowcase;
