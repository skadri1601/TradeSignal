import { Database, Brain, Bell, LineChart, Users, Smartphone, Shield, Zap, Check } from 'lucide-react';
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
      gradient: "from-purple-500 to-indigo-500",
      accentColor: "#8b5cf6"
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
      gradient: "from-blue-500 to-cyan-500",
      accentColor: "#3b82f6"
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
      gradient: "from-green-500 to-emerald-500",
      accentColor: "#22c55e"
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
      gradient: "from-orange-500 to-red-500",
      accentColor: "#f97316"
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
      gradient: "from-pink-500 to-rose-500",
      accentColor: "#ec4899"
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
      gradient: "from-violet-500 to-purple-500",
      accentColor: "#8b5cf6"
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
      gradient: "from-teal-500 to-cyan-500",
      accentColor: "#14b8a6"
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
      gradient: "from-yellow-500 to-orange-500",
      accentColor: "#eab308"
    }
  ];

  return (
    <section className="py-24 px-4 bg-[#0a0a0a]">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-20">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/[0.06] px-4 py-2 mb-6">
            <Zap className="w-4 h-4 text-purple-500" />
            <span className="text-sm text-gray-400">Powerful Features</span>
          </div>

          <h2 className="text-4xl lg:text-5xl font-bold mb-6">
            <span className="text-white">Everything You Need to</span>
            <span className="block text-purple-500 mt-2">
              Trade Smarter
            </span>
          </h2>

          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            A complete platform for tracking insider trades, congressional activity, and AI-powered market intelligence
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-20">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-[#111] border border-white/[0.06] rounded-2xl p-6 hover:bg-white/[0.04] hover:border-white/10 transition-colors duration-200"
            >
              <div className="w-12 h-12 bg-white/[0.04] rounded-xl flex items-center justify-center mb-5">
                <feature.icon className="w-6 h-6 text-purple-500" />
              </div>

              <h3 className="text-lg font-semibold text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-gray-400 mb-4">{feature.description}</p>

              <ul className="space-y-2.5">
                {feature.details.map((detail, detailIndex) => (
                  <li key={detailIndex} className="flex items-start gap-2.5 text-xs text-gray-500">
                    <Check className="w-3.5 h-3.5 mt-0.5 flex-shrink-0 text-purple-500" />
                    <span>{detail}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="text-center">
          <div className="inline-flex flex-col sm:flex-row gap-4">
            <Link
              to="/register"
              className="inline-flex items-center justify-center gap-2 bg-white text-black px-8 py-4 rounded-full font-semibold hover:bg-gray-200 transition-colors duration-200"
            >
              Start Free Trial
            </Link>
            <Link
              to="/about"
              className="inline-flex items-center justify-center gap-2 border border-white/10 text-white px-8 py-4 rounded-full font-semibold hover:bg-white/5 transition-colors duration-200"
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
