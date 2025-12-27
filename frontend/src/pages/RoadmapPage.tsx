import { Rocket, CheckCircle2, Clock, Sparkles, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';

const RoadmapPage = () => {
  const roadmapItems = [
    {
      quarter: "Q1 2025",
      status: "In Progress",
      items: [
        { title: "Advanced Portfolio Tracking", description: "Track your holdings alongside insider activity", status: "in-progress", votes: 1243, completedDate: undefined as string | undefined },
        { title: "Mobile App (iOS & Android)", description: "Native mobile apps with push notifications", status: "in-progress", votes: 2156, completedDate: undefined as string | undefined },
        { title: "Options Trading Analysis", description: "Track insider options grants and exercises", status: "in-progress", votes: 892, completedDate: undefined as string | undefined },
        { title: "Enhanced LUNA AI Models", description: "Improved prediction accuracy with advanced AI architecture", status: "planned", votes: 1567, completedDate: undefined as string | undefined }
      ]
    },
    {
      quarter: "Q2 2025",
      status: "Planned",
      items: [
        { title: "Social Trading Features", description: "Follow top performers and copy their strategies", status: "planned", votes: 1834, completedDate: undefined as string | undefined },
        { title: "Screener 2.0", description: "Advanced filtering with 50+ criteria", status: "planned", votes: 1123, completedDate: undefined as string | undefined },
        { title: "Real-time WebSocket Alerts", description: "Instant notifications via WebSocket connections", status: "planned", votes: 967, completedDate: undefined as string | undefined },
        { title: "International Markets", description: "Expand beyond US to EU and Asia markets", status: "planned", votes: 2045, completedDate: undefined as string | undefined }
      ]
    },
    {
      quarter: "Q3 2025",
      status: "Future",
      items: [
        { title: "Hedge Fund 13F Tracking", description: "Track quarterly hedge fund holdings and changes", status: "future", votes: 1456, completedDate: undefined as string | undefined },
        { title: "Sentiment Analysis", description: "AI-powered news and social media sentiment tracking", status: "future", votes: 1289, completedDate: undefined as string | undefined },
        { title: "Custom Dashboards", description: "Build personalized dashboards with drag-and-drop widgets", status: "future", votes: 934, completedDate: undefined as string | undefined },
        { title: "Integration Marketplace", description: "Connect with brokers, Discord bots, and trading platforms", status: "future", votes: 1678, completedDate: undefined as string | undefined }
      ]
    },
    {
      quarter: "Recently Completed",
      status: "Completed",
      items: [
        { title: "LUNA AI Engine Launch", description: "Unified AI analysis with proprietary dual-model architecture", status: "completed", votes: undefined as number | undefined, completedDate: "Dec 2024" },
        { title: "Congressional Trading Dashboard", description: "Real-time tracking of all 535 Congress members", status: "completed", votes: undefined as number | undefined, completedDate: "Nov 2024" },
        { title: "Enterprise API v1", description: "RESTful API with 2,000 req/hour rate limits", status: "completed", votes: undefined as number | undefined, completedDate: "Oct 2024" },
        { title: "Discord Alerts Integration", description: "Send trade alerts directly to Discord channels", status: "completed", votes: undefined as number | undefined, completedDate: "Sep 2024" },
        { title: "Advanced Filters & Search", description: "Filter by 20+ criteria including transaction type, amount, date", status: "completed", votes: undefined as number | undefined, completedDate: "Aug 2024" }
      ]
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'in-progress': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'planned': return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      case 'future': return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
      case 'completed': return 'bg-green-500/20 text-green-400 border-green-500/30';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'in-progress': return <Clock className="w-4 h-4" />;
      case 'completed': return <CheckCircle2 className="w-4 h-4" />;
      default: return <Sparkles className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Hero Section */}
      <section className="pt-32 pb-16 px-4 bg-gradient-to-b from-[#0f0f1a] to-[#0a0a0a]">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 rounded-full px-4 py-2 mb-6">
            <Rocket className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-purple-300">Product Roadmap</span>
          </div>
          <h1 className="text-5xl font-bold mb-6">
            What's Coming
            <span className="block bg-gradient-to-r from-purple-400 via-blue-400 to-purple-400 bg-clip-text text-transparent mt-2">
              to TradeSignal
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
            See what we're building next and vote on features you want to see. Your feedback shapes our product.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Link
              to="/register"
              className="inline-flex items-center gap-2 bg-white text-black px-6 py-3 rounded-full font-bold hover:bg-gray-200 transition-all"
            >
              <Sparkles className="w-5 h-5" />
              Get Early Access
            </Link>
            <a
              href="mailto:feedback@tradesignal.com"
              className="inline-flex items-center gap-2 bg-white/5 border border-white/10 text-white px-6 py-3 rounded-full font-bold hover:bg-white/10 transition-all"
            >
              Submit Feature Request
            </a>
          </div>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="py-8 px-4 border-b border-white/5">
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-400 mb-1">4</div>
            <div className="text-sm text-gray-500">In Progress</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-400 mb-1">8</div>
            <div className="text-sm text-gray-500">Planned</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-400 mb-1">5</div>
            <div className="text-sm text-gray-500">Recently Shipped</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-400 mb-1">12K+</div>
            <div className="text-sm text-gray-500">Feature Votes</div>
          </div>
        </div>
      </section>

      {/* Roadmap Timeline */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto space-y-16">
          {roadmapItems.map((quarter, qIndex) => (
            <div key={qIndex}>
              {/* Quarter Header */}
              <div className="flex items-center gap-4 mb-8">
                <div className="flex-shrink-0">
                  <div className={`px-4 py-2 rounded-full text-sm font-bold ${
                    quarter.status === 'In Progress' ? 'bg-blue-500/20 text-blue-400' :
                    quarter.status === 'Planned' ? 'bg-purple-500/20 text-purple-400' :
                    quarter.status === 'Completed' ? 'bg-green-500/20 text-green-400' :
                    'bg-gray-500/20 text-gray-400'
                  }`}>
                    {quarter.quarter}
                  </div>
                </div>
                <div className="flex-1 h-px bg-white/10"></div>
              </div>

              {/* Feature Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {quarter.items.map((item, itemIndex) => (
                  <div
                    key={itemIndex}
                    className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-6 hover:border-purple-500/30 transition-all group cursor-pointer"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(item.status)}
                        <span className={`text-xs font-medium px-3 py-1 rounded-full border ${getStatusColor(item.status)}`}>
                          {item.status === 'in-progress' ? 'In Progress' :
                           item.status === 'planned' ? 'Planned' :
                           item.status === 'future' ? 'Future' :
                           'Completed'}
                        </span>
                      </div>
                      {item.votes && (
                        <button className="flex items-center gap-1 px-3 py-1 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full text-xs font-medium transition-all">
                          <TrendingUp className="w-3 h-3" />
                          {item.votes.toLocaleString()}
                        </button>
                      )}
                    </div>
                    <h3 className="text-xl font-bold mb-2 group-hover:text-purple-400 transition-colors">
                      {item.title}
                    </h3>
                    <p className="text-gray-400 text-sm mb-4">{item.description}</p>
                    {item.completedDate && (
                      <div className="flex items-center gap-2 text-xs text-green-400">
                        <CheckCircle2 className="w-3 h-3" />
                        Shipped {item.completedDate}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Feature Request CTA */}
      <section className="py-20 px-4 bg-gradient-to-b from-[#0a0a0a] to-[#0f0f1a]">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-[#0f0f1a] border border-purple-500/20 rounded-3xl p-12">
            <Sparkles className="w-12 h-12 text-purple-400 mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-4">Have a Feature Idea?</h2>
            <p className="text-gray-400 mb-8">
              We'd love to hear your suggestions! Your feedback directly influences what we build next.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="mailto:feedback@tradesignal.com"
                className="inline-flex items-center justify-center gap-2 bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-200 transition-all"
              >
                Submit Feedback
              </a>
              <Link
                to="/pricing"
                className="inline-flex items-center justify-center gap-2 bg-white/5 border border-white/10 text-white px-8 py-4 rounded-full font-bold hover:bg-white/10 transition-all"
              >
                Get Early Access
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default RoadmapPage;
