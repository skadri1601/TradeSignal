import { CheckCircle2, Zap, Shield, Calendar } from 'lucide-react';
import { Link } from 'react-router-dom';

const FinalCTA = () => {
  const benefits = [
    { icon: Zap, text: "Setup in 60 seconds" },
    { icon: Shield, text: "100% free access" },
    { icon: Calendar, text: "No credit card required" }
  ];

  const stats = [
    { value: "535", label: "Congress Members" },
    { value: "SEC", label: "Form 4 Data" },
    { value: "<2min", label: "Alert Speed" },
    { value: "Gemini", label: "AI Powered" }
  ];

  return (
    <section className="py-24 px-4 bg-[#0a0a0a]">
      <div className="max-w-5xl mx-auto">
        <div className="bg-[#111] border border-white/[0.06] rounded-3xl p-12 lg:p-16 text-center">
          <div className="inline-flex items-center gap-2 border border-white/[0.06] rounded-full px-4 py-2 mb-6">
            <CheckCircle2 className="w-4 h-4 text-green-400" />
            <span className="text-sm text-gray-400">Free Portfolio Demo</span>
          </div>

          <h2 className="text-4xl lg:text-5xl font-bold mb-6">
            <span className="text-white">Start Trading</span>
            <span className="block text-purple-500 mt-2">
              Smarter Today
            </span>
          </h2>

          <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
            Join thousands of traders using insider intelligence to gain an edge.
            Track insider trades, congressional activity, and get AI-powered insights in real-time.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 mb-10">
            {benefits.map((benefit, index) => (
              <div key={index} className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/[0.04] border border-white/[0.06] rounded-full flex items-center justify-center">
                  <benefit.icon className="w-5 h-5 text-purple-500" />
                </div>
                <span className="text-sm text-gray-300">{benefit.text}</span>
              </div>
            ))}
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
            <Link
              to="/register"
              className="inline-flex items-center justify-center gap-2 bg-white text-black px-10 py-5 rounded-full font-semibold text-lg hover:bg-gray-200 transition-colors duration-200"
            >
              <Zap className="w-5 h-5 fill-black" />
              Start Your Free Trial
            </Link>
            <Link
              to="/contact"
              className="inline-flex items-center justify-center gap-2 border border-white/10 text-white px-10 py-5 rounded-full font-semibold text-lg hover:bg-white/5 transition-colors duration-200"
            >
              Schedule Demo
            </Link>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-6 text-xs text-gray-500">
            {["Open Source", "Real SEC Data", "AI-Powered"].map((text, i) => (
              <div key={i} className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-400" />
                <span>{text}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-12">
          {stats.map((stat, index) => (
            <div
              key={index}
              className="bg-[#111] border border-white/[0.06] rounded-2xl p-6 text-center"
            >
              <div className="text-3xl font-bold text-white mb-2">{stat.value}</div>
              <div className="text-sm text-gray-500">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FinalCTA;
