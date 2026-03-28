import { Database, Brain, Bell, LineChart, Users, Smartphone, Shield, Zap, Check } from 'lucide-react';
import { Link } from 'react-router-dom';
import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';

const FeaturesShowcase = () => {
  const gridRef = useRef(null);
  const isInView = useInView(gridRef, { once: true, margin: "-100px" });

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
    <section className="py-24 px-4 bg-[#0a0a0a] relative overflow-hidden">
      <style>{`
        @keyframes meshFloat1 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -30px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.95); }
        }
        @keyframes meshFloat2 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(-40px, 20px) scale(1.05); }
          66% { transform: translate(20px, -30px) scale(1.1); }
        }
        @keyframes iconGradientRotate {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes shimmerBorder {
          0% { background-position: -200% center; }
          100% { background-position: 200% center; }
        }
        .shimmer-badge {
          background: linear-gradient(90deg, transparent 0%, rgba(168,85,247,0.4) 50%, transparent 100%);
          background-size: 200% 100%;
          animation: shimmerBorder 3s linear infinite;
        }
        .dot-pattern {
          background-image: radial-gradient(rgba(255,255,255,0.03) 1px, transparent 1px);
          background-size: 24px 24px;
        }
        .feature-card {
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .feature-card:hover {
          transform: translateY(-8px);
          border-color: rgba(168, 85, 247, 0.5);
          box-shadow: 0 20px 40px -12px rgba(168, 85, 247, 0.15), 0 0 20px rgba(168, 85, 247, 0.05);
        }
        .icon-container {
          position: relative;
          overflow: hidden;
        }
        .icon-container::before {
          content: '';
          position: absolute;
          inset: -50%;
          animation: iconGradientRotate 6s linear infinite;
          border-radius: inherit;
        }
        .cta-glow:hover {
          box-shadow: 0 0 30px rgba(255, 255, 255, 0.3), 0 0 60px rgba(168, 85, 247, 0.2);
        }
        .cta-outline-glow:hover {
          box-shadow: 0 0 20px rgba(168, 85, 247, 0.15);
        }
      `}</style>

      <div className="absolute inset-0 dot-pattern" />

      <div
        className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-purple-900/10 blur-[120px] rounded-full"
        style={{ animation: 'meshFloat1 12s ease-in-out infinite' }}
      />
      <div
        className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-blue-900/10 blur-[120px] rounded-full"
        style={{ animation: 'meshFloat2 15s ease-in-out infinite' }}
      />
      <div
        className="absolute top-[30%] right-[20%] w-[30%] h-[30%] bg-indigo-900/8 blur-[100px] rounded-full"
        style={{ animation: 'meshFloat1 18s ease-in-out infinite' }}
      />

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center mb-20">
          <div className="inline-flex items-center gap-2 rounded-full px-4 py-2 mb-6 relative">
            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-purple-500/10 to-blue-500/10" />
            <div className="absolute inset-0 rounded-full border border-purple-500/20 shimmer-badge" />
            <div className="absolute inset-0 rounded-full border border-purple-500/20" />
            <Zap className="w-4 h-4 text-purple-400 relative z-10" />
            <span className="text-sm text-purple-300 relative z-10">Powerful Features</span>
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

        <div ref={gridRef} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-20">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
              transition={{ duration: 0.5, delay: index * 0.1, ease: [0.4, 0, 0.2, 1] }}
              className="feature-card bg-white/[0.03] backdrop-blur-sm border border-white/[0.08] rounded-2xl p-6 cursor-pointer group relative overflow-hidden"
            >
              <div
                className={`absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r ${feature.gradient}`}
              />

              <div
                className={`icon-container w-14 h-14 bg-gradient-to-br ${feature.gradient} rounded-2xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300`}
              >
                <feature.icon className="w-7 h-7 text-white relative z-10" />
              </div>

              <h3 className="text-xl font-bold text-white mb-2 group-hover:text-purple-400 transition-colors duration-300">
                {feature.title}
              </h3>
              <p className="text-sm text-gray-400 mb-4">{feature.description}</p>

              <ul className="space-y-2.5">
                {feature.details.map((detail, detailIndex) => (
                  <li key={detailIndex} className="flex items-start gap-2.5 text-xs text-gray-500">
                    <Check
                      className="w-3.5 h-3.5 mt-0.5 flex-shrink-0"
                      style={{ color: feature.accentColor }}
                    />
                    <span>{detail}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        <div className="text-center">
          <div className="inline-flex flex-col sm:flex-row gap-4">
            <Link
              to="/register"
              className="cta-glow inline-flex items-center justify-center gap-2 bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-100 transition-all duration-300 hover:scale-105"
            >
              Start Free Trial
            </Link>
            <Link
              to="/about"
              className="cta-outline-glow inline-flex items-center justify-center gap-2 bg-white/5 border border-white/10 text-white px-8 py-4 rounded-full font-bold hover:bg-white/10 transition-all duration-300"
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
