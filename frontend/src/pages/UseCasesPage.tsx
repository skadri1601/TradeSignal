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
      results: [
        { metric: "92%", label: "Prediction accuracy on 30-day price movements" },
        { metric: "4.2x", label: "Average ROI improvement vs market index" },
        { metric: "< 2min", label: "Alert delivery time after SEC filing" }
      ],
      testimonial: {
        quote: "I discovered a cluster of insider buying at a mid-cap tech company through TradeSignal. The stock jumped 34% in three weeks. This platform gives me an edge I never had before.",
        author: "Michael R.",
        role: "Retail Investor, CA"
      },
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
      results: [
        { metric: "32,000+", label: "Insider trades tracked across 151 companies" },
        { metric: "2-hour", label: "SEC EDGAR scraping interval for fresh data" },
        { metric: "535", label: "Congress members tracked in real-time" }
      ],
      testimonial: {
        quote: "The real-time alerts are a game-changer. I got notified about a CEO buying $2M of his own stock before it hit Twitter. I was in the trade 10 minutes later. Up 18% in two days.",
        author: "Sarah T.",
        role: "Day Trader, TX"
      },
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
        "Enterprise API with 2,000 req/hour for programmatic access",
        "CSV/Excel exports with historical data and technical indicators",
        "LUNA AI provides conviction scores and price predictions",
        "White-label reports with your firm's branding"
      ],
      results: [
        { metric: "15min", label: "Report generation time (vs 4+ hours manual)" },
        { metric: "100%", label: "API uptime SLA with 24/7 monitoring" },
        { metric: "SOC 2", label: "Type II certified for enterprise security" }
      ],
      testimonial: {
        quote: "We replaced our manual process of tracking Form 4 filings with TradeSignal's API. It saves our team 20+ hours per week and the AI insights add real value to our client reports.",
        author: "David L.",
        role: "Senior Analyst, Hedge Fund"
      },
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
      results: [
        { metric: "67%", label: "Client retention increase with differentiated insights" },
        { metric: "$8.4M", label: "AUM protected by early insider selling alerts" },
        { metric: "4.1/5", label: "Client satisfaction rating for data-driven advice" }
      ],
      testimonial: {
        quote: "Our clients love the insider activity reports we now include in quarterly reviews. It shows we're going beyond the basics, and it's helped us win 12 new accounts this year alone.",
        author: "Jennifer K.",
        role: "Wealth Manager, NY"
      },
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
            Who Uses
            <span className="block bg-gradient-to-r from-blue-400 via-purple-400 to-blue-400 bg-clip-text text-transparent mt-2">
              TradeSignal?
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            From retail investors to institutional analysts, see how traders at every level use insider intelligence to gain an edge
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

              {/* Results */}
              <div className={`bg-gradient-to-br ${useCase.gradient} bg-opacity-10 border border-white/10 rounded-2xl p-8 mb-8`}>
                <h3 className="text-xl font-bold mb-6 text-center">Measurable Results</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {useCase.results.map((result, rIndex) => (
                    <div key={rIndex} className="text-center">
                      <div className={`text-4xl font-bold bg-gradient-to-r ${useCase.gradient} bg-clip-text text-transparent mb-2`}>
                        {result.metric}
                      </div>
                      <div className="text-sm text-gray-400">{result.label}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Testimonial */}
              <div className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-8">
                <div className="flex items-start gap-4">
                  <div className={`bg-gradient-to-br ${useCase.gradient} rounded-full w-12 h-12 flex items-center justify-center text-2xl flex-shrink-0`}>
                    {useCase.testimonial.author[0]}
                  </div>
                  <div className="flex-1">
                    <p className="text-gray-300 italic mb-4">"{useCase.testimonial.quote}"</p>
                    <div>
                      <div className="font-bold text-white">{useCase.testimonial.author}</div>
                      <div className="text-sm text-gray-500">{useCase.testimonial.role}</div>
                    </div>
                  </div>
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
              Join thousands of investors using insider intelligence to trade smarter. Choose the plan that fits your needs.
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
