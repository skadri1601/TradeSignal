import { TrendingUp, Building2, LineChart, Users, Zap, Target, CheckCircle2, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const UseCasesPage = () => {
  const useCases = [
    {
      icon: TrendingUp,
      title: "Retail Investors",
      subtitle: "Follow the Smart Money",
      description: "Track insider trades and congressional stock transactions to make more informed investment decisions alongside Wall Street professionals.",
      challenges: [
        "Limited access to institutional-grade data",
        "Difficulty tracking insider activity manually",
        "Missing opportunities before they become public",
        "Overwhelmed by market noise and conflicting signals"
      ],
      solutions: [
        "Real-time insider trade alerts sent to your phone",
        "AI-powered insights that identify patterns before the market reacts",
        "Congressional trading dashboard showing what politicians are buying",
        "Custom watchlists that track insiders at companies you care about"
      ],
      gradient: "from-blue-400 to-purple-400"
    },
    {
      icon: LineChart,
      title: "Day Traders & Swing Traders",
      subtitle: "Spot Opportunities Before the Crowd",
      description: "Use insider activity and congressional trades as confirmation signals for your technical analysis and momentum strategies.",
      challenges: [
        "Need fast, actionable signals to time entries/exits",
        "Looking for high-conviction trade ideas with catalyst support",
        "Want to avoid stocks with insider selling pressure",
        "Need real-time data to stay ahead of retail sentiment"
      ],
      solutions: [
        "WebSocket alerts for instant notifications when insiders make moves",
        "Cluster detection AI identifies abnormal buying/selling patterns",
        "Integration with Discord and trading platforms via webhooks",
        "Advanced screener with 50+ filters including transaction size and frequency"
      ],
      gradient: "from-green-400 to-blue-400"
    },
    {
      icon: Building2,
      title: "Financial Analysts & Researchers",
      subtitle: "Institutional-Grade Intelligence",
      description: "Access comprehensive insider trading data, AI analysis, and export capabilities for professional research and client reporting.",
      challenges: [
        "Need clean, structured data for quantitative models",
        "Manually aggregating SEC filings is time-consuming",
        "Clients expect deeper insights beyond public news",
        "Require audit trails and compliance-ready reporting"
      ],
      solutions: [
        "Enterprise API with programmatic access",
        "CSV/Excel exports with historical data and technical indicators",
        "LUNA AI provides conviction scores and insights",
        "White-label reports with your firm's branding"
      ],
      gradient: "from-purple-400 to-pink-400"
    },
    {
      icon: Users,
      title: "Wealth Managers & RIAs",
      subtitle: "Enhance Client Portfolios",
      description: "Add insider intelligence to your investment process and demonstrate value through data-driven insights your competitors don't have.",
      challenges: [
        "Clients demand better returns in competitive markets",
        "Need to justify fees with differentiated strategies",
        "Want to proactively identify risks in client holdings",
        "Require scalable solutions for multiple client accounts"
      ],
      solutions: [
        "Multi-account dashboards to monitor all client portfolios",
        "Automatic alerts when insiders sell stocks your clients own",
        "Research badges (IVT, TS Score) for due diligence reports",
        "Client-facing dashboards with white-label branding"
      ],
      gradient: "from-orange-400 to-red-400"
    }
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Hero Section */}
      <section className="pt-32 pb-16 px-4 bg-gradient-to-b from-[#0f0f1a] to-[#0a0a0a]">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-4 py-2 mb-6">
            <Target className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-blue-300">Use Cases</span>
          </div>
          <h1 className="text-5xl font-bold mb-6">
            How TradeSignal
            <span className="block bg-gradient-to-r from-blue-400 via-purple-400 to-blue-400 bg-clip-text text-transparent mt-2">
              Helps Traders
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Discover how TradeSignal provides insider trading intelligence and tools for different types of traders
          </p>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto space-y-32">
          {useCases.map((useCase, index) => (
            <div key={index} className={`${index % 2 === 1 ? 'flex-row-reverse' : ''}`}>
              {/* Header */}
              <div className="text-center mb-12">
                <div className={`inline-flex items-center gap-3 bg-gradient-to-r ${useCase.gradient} bg-clip-text text-transparent mb-4`}>
                  <useCase.icon className="w-8 h-8" style={{ color: 'inherit', WebkitTextFillColor: 'unset' }} />
                  <h2 className="text-3xl font-bold">{useCase.title}</h2>
                </div>
                <p className="text-xl text-gray-400 mb-2">{useCase.subtitle}</p>
                <p className="text-gray-500 max-w-3xl mx-auto">{useCase.description}</p>
              </div>

              {/* Two Column Layout */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
                {/* Challenges */}
                <div className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-8">
                  <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                    <span className="text-red-400">⚠</span> Common Challenges
                  </h3>
                  <ul className="space-y-3">
                    {useCase.challenges.map((challenge, cIndex) => (
                      <li key={cIndex} className="flex items-start gap-3 text-gray-400">
                        <span className="text-red-400 mt-1 flex-shrink-0">✗</span>
                        <span className="text-sm">{challenge}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Solutions */}
                <div className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-8">
                  <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                    <Zap className="w-5 h-5 text-green-400" /> TradeSignal Solutions
                  </h3>
                  <ul className="space-y-3">
                    {useCase.solutions.map((solution, sIndex) => (
                      <li key={sIndex} className="flex items-start gap-3 text-gray-300">
                        <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{solution}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing CTA */}
      <section className="py-20 px-4 bg-gradient-to-b from-[#0a0a0a] to-[#0f0f1a]">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-[#0f0f1a] border border-purple-500/20 rounded-3xl p-12">
            <Target className="w-12 h-12 text-purple-400 mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
            <p className="text-gray-400 mb-8">
              Start tracking insider trades and congressional activity. Choose the plan that fits your needs.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="inline-flex items-center justify-center gap-2 bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-200 transition-all"
              >
                Start Free Trial
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                to="/pricing"
                className="inline-flex items-center justify-center gap-2 bg-white/5 border border-white/10 text-white px-8 py-4 rounded-full font-bold hover:bg-white/10 transition-all"
              >
                View Pricing
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default UseCasesPage;
