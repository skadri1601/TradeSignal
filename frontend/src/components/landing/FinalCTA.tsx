import { CheckCircle2, Zap, Shield, Calendar } from 'lucide-react';
import { Link } from 'react-router-dom';

const FinalCTA = () => {
  // PORTFOLIO MODE: Removed business claims, kept factual benefits
  const benefits = [
    {
      icon: Zap,
      text: "Setup in 60 seconds"
    },
    {
      icon: Shield,
      text: "100% free access"
    },
    {
      icon: Calendar,
      text: "No credit card required"
    }
  ];

  return (
    <section className="py-20 px-4 bg-gradient-to-b from-[#0a0a0a] to-[#0f0f1a] relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[80%] bg-gradient-to-r from-purple-900/20 via-blue-900/20 to-purple-900/20 blur-[100px] rounded-full"></div>

      <div className="max-w-5xl mx-auto relative z-10">
        {/* Main Card */}
        <div className="bg-gradient-to-br from-[#0f0f1a] to-[#1a1a2e] border border-white/10 rounded-3xl p-12 lg:p-16 text-center shadow-2xl">
          {/* Badge - PORTFOLIO MODE: Removed fake user count */}
          <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded-full px-4 py-2 mb-6">
            <CheckCircle2 className="w-4 h-4 text-green-400" />
            <span className="text-sm text-green-300">Free Portfolio Demo</span>
          </div>

          {/* Heading */}
          <h2 className="text-4xl lg:text-5xl font-bold mb-6">
            <span className="text-white">Start Trading</span>
            <span className="block bg-gradient-to-r from-green-400 via-blue-400 to-purple-400 bg-clip-text text-transparent mt-2">
              Smarter Today
            </span>
          </h2>

          {/* Subheading */}
          <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
            Join thousands of traders using insider intelligence to gain an edge.
            Track insider trades, congressional activity, and get AI-powered insights in real-time.
          </p>

          {/* Benefits Checklist */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 mb-10">
            {benefits.map((benefit, index) => (
              <div key={index} className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/5 border border-white/10 rounded-full flex items-center justify-center">
                  <benefit.icon className="w-5 h-5 text-purple-400" />
                </div>
                <span className="text-sm text-gray-300">{benefit.text}</span>
              </div>
            ))}
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
            <Link
              to="/register"
              className="inline-flex items-center justify-center gap-2 bg-white text-black px-10 py-5 rounded-full font-bold text-lg hover:bg-gray-200 transition-all hover:scale-105 shadow-xl hover:shadow-2xl group"
            >
              <Zap className="w-5 h-5 fill-black" />
              Start Your Free Trial
            </Link>
            <Link
              to="/contact"
              className="inline-flex items-center justify-center gap-2 bg-white/5 border-2 border-white/20 text-white px-10 py-5 rounded-full font-bold text-lg hover:bg-white/10 transition-all"
            >
              Schedule Demo
            </Link>
          </div>

          {/* Trust Indicators - PORTFOLIO MODE: Replaced false claims with factual info */}
          <div className="flex flex-wrap items-center justify-center gap-6 text-xs text-gray-500">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-400" />
              <span>Open Source</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-400" />
              <span>Real SEC Data</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-400" />
              <span>AI-Powered</span>
            </div>
          </div>
        </div>

        {/* Stats Bar Below - PORTFOLIO MODE: Factual stats only */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-12">
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-400 mb-2">535</div>
            <div className="text-sm text-gray-500">Congress Members</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-400 mb-2">SEC</div>
            <div className="text-sm text-gray-500">Form 4 Data</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-400 mb-2">&lt;2min</div>
            <div className="text-sm text-gray-500">Alert Speed</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-400 mb-2">Gemini</div>
            <div className="text-sm text-gray-500">AI Powered</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FinalCTA;
