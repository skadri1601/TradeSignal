import { CheckCircle2, Zap, Shield, Calendar } from 'lucide-react';
import { Link } from 'react-router-dom';
import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';

const FinalCTA = () => {
  const sectionRef = useRef(null);
  const isInView = useInView(sectionRef, { once: true, margin: "-100px" });

  const benefits = [
    {
      icon: Zap,
      text: "Setup in 60 seconds",
      glowColor: "rgba(234, 179, 8, 0.3)"
    },
    {
      icon: Shield,
      text: "100% free access",
      glowColor: "rgba(59, 130, 246, 0.3)"
    },
    {
      icon: Calendar,
      text: "No credit card required",
      glowColor: "rgba(34, 197, 94, 0.3)"
    }
  ];

  const stats = [
    { value: "535", label: "Congress Members", color: "text-purple-400" },
    { value: "SEC", label: "Form 4 Data", color: "text-blue-400" },
    { value: "<2min", label: "Alert Speed", color: "text-green-400" },
    { value: "Gemini", label: "AI Powered", color: "text-orange-400" }
  ];

  return (
    <section ref={sectionRef} className="py-24 px-4 bg-gradient-to-b from-[#0a0a0a] to-[#0f0f1a] relative overflow-hidden">
      <style>{`
        @keyframes rotatingBorder {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes shimmerText {
          0% { background-position: -200% center; }
          100% { background-position: 200% center; }
        }
        @keyframes badgePulse {
          0%, 100% { box-shadow: 0 0 8px rgba(34, 197, 94, 0.2); }
          50% { box-shadow: 0 0 20px rgba(34, 197, 94, 0.4); }
        }
        @keyframes floatParticle {
          0%, 100% { transform: translateY(0) translateX(0); opacity: 0; }
          10% { opacity: 0.6; }
          90% { opacity: 0.6; }
          50% { transform: translateY(-40px) translateX(20px); }
        }
        @keyframes meshMove {
          0%, 100% { transform: translate(0, 0); }
          50% { transform: translate(30px, -20px); }
        }
        .shimmer-heading {
          background-size: 200% 100%;
          animation: shimmerText 4s linear infinite;
        }
        .badge-pulse {
          animation: badgePulse 2.5s ease-in-out infinite;
        }
        .rotating-border-wrapper {
          position: relative;
          border-radius: 1.5rem;
          padding: 1px;
          overflow: hidden;
        }
        .rotating-border-wrapper::before {
          content: '';
          position: absolute;
          top: -50%;
          left: -50%;
          width: 200%;
          height: 200%;
          background: conic-gradient(from 0deg, transparent 0%, rgba(168,85,247,0.4) 10%, transparent 20%, rgba(59,130,246,0.4) 30%, transparent 40%, rgba(34,197,94,0.3) 50%, transparent 60%, rgba(168,85,247,0.4) 70%, transparent 80%, rgba(59,130,246,0.3) 90%, transparent 100%);
          animation: rotatingBorder 8s linear infinite;
        }
        .rotating-border-inner {
          position: relative;
          border-radius: calc(1.5rem - 1px);
          z-index: 1;
        }
        .stat-card {
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .stat-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 24px -8px rgba(168, 85, 247, 0.15);
        }
        .cta-primary-glow {
          box-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .cta-primary-glow:hover {
          box-shadow: 0 0 40px rgba(255, 255, 255, 0.4), 0 0 80px rgba(168, 85, 247, 0.2);
          transform: scale(1.05);
        }
        .particle {
          position: absolute;
          width: 3px;
          height: 3px;
          border-radius: 50%;
          background: rgba(168, 85, 247, 0.4);
        }
      `}</style>

      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[80%] bg-gradient-to-r from-purple-900/20 via-blue-900/20 to-purple-900/20 blur-[100px] rounded-full" style={{ animation: 'meshMove 12s ease-in-out infinite' }} />

      {[...Array(12)].map((_, i) => (
        <div
          key={i}
          className="particle"
          style={{
            left: `${10 + (i * 7) % 80}%`,
            top: `${15 + (i * 11) % 70}%`,
            animationDelay: `${i * 0.8}s`,
            animation: `floatParticle ${4 + (i % 3)}s ease-in-out infinite`,
            background: i % 3 === 0 ? 'rgba(168,85,247,0.4)' : i % 3 === 1 ? 'rgba(59,130,246,0.4)' : 'rgba(34,197,94,0.3)'
          }}
        />
      ))}

      <div className="max-w-5xl mx-auto relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
          transition={{ duration: 0.7, ease: [0.4, 0, 0.2, 1] }}
        >
          <div className="rotating-border-wrapper">
            <div className="rotating-border-inner bg-gradient-to-br from-[#0f0f1a] via-[#131328] to-[#1a1a2e] p-12 lg:p-16 text-center relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-900/5 via-transparent to-blue-900/5" />

              <div className="relative z-10">
                <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded-full px-4 py-2 mb-6 badge-pulse">
                  <CheckCircle2 className="w-4 h-4 text-green-400" />
                  <span className="text-sm text-green-300">Free Portfolio Demo</span>
                </div>

                <h2 className="text-4xl lg:text-5xl font-bold mb-6">
                  <span className="text-white">Start Trading</span>
                  <span className="block mt-2 bg-gradient-to-r from-green-400 via-blue-400 to-purple-400 via-green-400 bg-clip-text text-transparent shimmer-heading">
                    Smarter Today
                  </span>
                </h2>

                <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
                  Join thousands of traders using insider intelligence to gain an edge.
                  Track insider trades, congressional activity, and get AI-powered insights in real-time.
                </p>

                <div className="flex flex-col sm:flex-row items-center justify-center gap-6 mb-10">
                  {benefits.map((benefit, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                      transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
                      className="flex items-center gap-3"
                    >
                      <div
                        className="w-10 h-10 bg-white/5 border border-white/10 rounded-full flex items-center justify-center"
                        style={{ boxShadow: `0 0 16px ${benefit.glowColor}` }}
                      >
                        <benefit.icon className="w-5 h-5 text-purple-400" />
                      </div>
                      <span className="text-sm text-gray-300">{benefit.text}</span>
                    </motion.div>
                  ))}
                </div>

                <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
                  <Link
                    to="/register"
                    className="cta-primary-glow inline-flex items-center justify-center gap-2 bg-white text-black px-10 py-5 rounded-full font-bold text-lg group"
                  >
                    <Zap className="w-5 h-5 fill-black" />
                    Start Your Free Trial
                  </Link>
                  <Link
                    to="/contact"
                    className="inline-flex items-center justify-center gap-2 bg-white/5 border-2 border-white/20 text-white px-10 py-5 rounded-full font-bold text-lg hover:bg-white/10 transition-all duration-300 hover:border-purple-500/40"
                  >
                    Schedule Demo
                  </Link>
                </div>

                <div className="flex flex-wrap items-center justify-center gap-6 text-xs text-gray-500">
                  {["Open Source", "Real SEC Data", "AI-Powered"].map((text, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-400" style={{ filter: 'drop-shadow(0 0 4px rgba(34, 197, 94, 0.5))' }} />
                      <span>{text}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-12">
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
              transition={{ duration: 0.5, delay: 0.6 + index * 0.1 }}
              className="stat-card bg-white/[0.03] backdrop-blur-sm border border-white/[0.08] rounded-2xl p-6 text-center cursor-default"
            >
              <div className={`text-3xl font-bold ${stat.color} mb-2`}>{stat.value}</div>
              <div className="text-sm text-gray-500">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FinalCTA;
