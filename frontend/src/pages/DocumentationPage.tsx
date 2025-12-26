import { Book, BookOpen, Code, Zap, Shield, TrendingUp, ChevronRight, Search } from 'lucide-react';
import { Link } from 'react-router-dom';

const DocumentationPage = () => {
  const sections = [
    {
      category: "Getting Started",
      icon: BookOpen,
      items: [
        { title: "Quick Start Guide", description: "Get up and running in 5 minutes", time: "5 min" },
        { title: "Understanding Insider Trading", description: "Learn the basics of SEC Form 4 filings", time: "10 min" },
        { title: "Congressional Trading 101", description: "How STOCK Act disclosures work", time: "8 min" },
        { title: "Account Setup & Settings", description: "Configure your TradeSignal account", time: "6 min" }
      ]
    },
    {
      category: "Features & Tools",
      icon: Zap,
      items: [
        { title: "Dashboard Overview", description: "Navigate your TradeSignal dashboard", time: "7 min" },
        { title: "Setting Up Alerts", description: "Create custom trade notifications", time: "12 min" },
        { title: "Using Filters & Search", description: "Find specific trades and insiders", time: "8 min" },
        { title: "Research Badges Explained", description: "IVT, TS Score, and Risk Level", time: "15 min" }
      ]
    },
    {
      category: "LUNA AI Engine",
      icon: Code,
      items: [
        { title: "LUNA AI Overview", description: "Understanding our AI analysis engine", time: "10 min" },
        { title: "Interpreting AI Predictions", description: "How to use AI insights effectively", time: "12 min" },
        { title: "Conviction Scores", description: "Understanding confidence levels", time: "8 min" },
        { title: "Pattern Detection", description: "Cluster analysis and anomalies", time: "14 min" }
      ]
    },
    {
      category: "Advanced Features",
      icon: TrendingUp,
      items: [
        { title: "API Access (Enterprise)", description: "Integrate TradeSignal into your tools", time: "20 min" },
        { title: "Webhooks Setup", description: "Real-time notifications to external systems", time: "15 min" },
        { title: "Copy Trading", description: "Automate trades based on insider activity", time: "18 min" },
        { title: "Export & Reporting", description: "Download data and generate reports", time: "10 min" }
      ]
    },
    {
      category: "Account & Billing",
      icon: Shield,
      items: [
        { title: "Subscription Plans", description: "Compare features across tiers", time: "5 min" },
        { title: "Upgrading Your Account", description: "Move to Plus, PRO, or Enterprise", time: "6 min" },
        { title: "Payment & Invoices", description: "Manage billing and download receipts", time: "7 min" },
        { title: "Cancellation & Refunds", description: "14-day money-back guarantee", time: "5 min" }
      ]
    }
  ];

  const quickLinks = [
    { title: "API Documentation", link: "/api-docs", icon: Code },
    { title: "Security Policy", link: "/security", icon: Shield },
    { title: "Product Roadmap", link: "/roadmap", icon: TrendingUp },
    { title: "FAQ", link: "/faq", icon: Book }
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Hero Section */}
      <section className="pt-32 pb-16 px-4 bg-gradient-to-b from-[#0f0f1a] to-[#0a0a0a]">
        <div className="max-w-7xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-4 py-2 mb-6">
            <Book className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-blue-300">Documentation</span>
          </div>
          <h1 className="text-5xl font-bold mb-6">
            TradeSignal
            <span className="block bg-gradient-to-r from-blue-400 via-purple-400 to-blue-400 bg-clip-text text-transparent mt-2">
              Documentation
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mb-8">
            Everything you need to master insider trading intelligence and congressional trade tracking
          </p>

          {/* Search Bar */}
          <div className="relative max-w-2xl">
            <Search className="absolute left-6 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              placeholder="Search documentation..."
              className="w-full bg-[#0f0f1a] border border-white/10 rounded-full pl-14 pr-6 py-4 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500/50 transition-all"
            />
          </div>
        </div>
      </section>

      {/* Quick Links */}
      <section className="py-12 px-4 border-b border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {quickLinks.map((link, index) => (
              <Link
                key={index}
                to={link.link}
                className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-6 text-center group hover:border-purple-500/30 transition-all"
              >
                <link.icon className="w-8 h-8 text-purple-400 mx-auto mb-3" />
                <span className="text-sm font-medium group-hover:text-purple-400 transition-colors">
                  {link.title}
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Documentation Sections */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto space-y-16">
          {sections.map((section, sectionIndex) => (
            <div key={sectionIndex}>
              <div className="flex items-center gap-3 mb-6">
                <div className="bg-purple-500/10 p-3 rounded-xl">
                  <section.icon className="w-6 h-6 text-purple-400" />
                </div>
                <h2 className="text-2xl font-bold">{section.category}</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {section.items.map((item, itemIndex) => (
                  <div
                    key={itemIndex}
                    className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-6 group hover:border-purple-500/30 transition-all cursor-pointer"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <h3 className="text-lg font-semibold group-hover:text-purple-400 transition-colors">
                        {item.title}
                      </h3>
                      <ChevronRight className="w-5 h-5 text-gray-600 group-hover:text-purple-400 transition-colors flex-shrink-0 ml-2" />
                    </div>
                    <p className="text-gray-400 text-sm mb-4">{item.description}</p>
                    <span className="text-xs text-gray-500">{item.time} read</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Help CTA */}
      <section className="py-20 px-4 bg-gradient-to-b from-[#0a0a0a] to-[#0f0f1a]">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-[#0f0f1a] border border-blue-500/20 rounded-3xl p-12">
            <Book className="w-12 h-12 text-blue-400 mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-4">Need More Help?</h2>
            <p className="text-gray-400 mb-8">
              Can't find what you're looking for? Our support team is here to help.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/support"
                className="inline-flex items-center justify-center gap-2 bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-200 transition-all"
              >
                Visit Help Center
              </Link>
              <Link
                to="/contact"
                className="inline-flex items-center justify-center gap-2 bg-white/5 border border-white/10 text-white px-8 py-4 rounded-full font-bold hover:bg-white/10 transition-all"
              >
                Contact Support
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default DocumentationPage;
