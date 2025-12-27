import { HelpCircle, MessageSquare, Book, Mail, Phone, Search, ChevronDown, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useState } from 'react';

const PublicSupportPage = () => {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const faqs = [
    {
      question: "What is insider trading and why should I track it?",
      answer: "Insider trading refers to when corporate insiders (executives, directors, major shareholders) buy or sell their own company's stock. While legal when properly reported via SEC Form 4, these transactions can signal insider confidence or concerns about their company's future. Tracking these trades helps investors identify potential opportunities and risks."
    },
    {
      question: "How does TradeSignal track congressional stock trades?",
      answer: "We monitor STOCK Act filings from all 535 members of Congress in real-time. The Stop Trading on Congressional Knowledge (STOCK) Act requires Congress members to disclose stock transactions within 45 days. TradeSignal aggregates, analyzes, and alerts you to significant congressional trading activity."
    },
    {
      question: "What is LUNA AI and how does it work?",
      answer: "LUNA is our proprietary AI engine built with advanced machine learning technology. It analyzes millions of insider trades, congressional transactions, and market data to identify patterns, clusters, and anomalies. LUNA provides actionable insights with conviction scores and price predictions."
    },
    {
      question: "What's the difference between subscription tiers?",
      answer: "Free tier gives you basic access to view recent insider trades. Plus tier unlocks full congressional trading data and advanced filters. PRO tier adds AI insights, research badges (IVT, TS Score), pattern detection, and unlimited alerts. Enterprise tier provides API access, webhooks, and white-glove support."
    },
    {
      question: "Is the data real-time?",
      answer: "We scrape SEC EDGAR every 2 hours for Form 4 filings and monitor congressional disclosures daily. While SEC filings can be delayed by insiders (up to 2 business days legally), we display them as soon as they appear in official databases. Our system processes over 32,000 trades across 151 companies."
    },
    {
      question: "Can I export data or integrate with my tools?",
      answer: "PRO tier users can export data to CSV/Excel. Enterprise tier customers get full API access, webhooks for real-time notifications, and custom integrations. All exports include historical data, technical indicators, and AI analysis results."
    },
    {
      question: "How accurate are the AI predictions?",
      answer: "LUNA achieves 92% accuracy on directional predictions over a 30-day window. However, AI predictions are probabilistic and should be used as one input in your investment decision process. We provide transparency through conviction scores and model confidence levels."
    },
    {
      question: "What kind of alerts can I set up?",
      answer: "You can create custom alerts for specific stocks, insiders, transaction types, dollar amounts, and more. Notifications are delivered via email, SMS (PRO), Discord, or Slack. Enterprise users can configure webhooks for programmatic access to alerts."
    }
  ];

  const helpCategories = [
    {
      icon: Book,
      title: "Documentation",
      description: "Comprehensive guides and tutorials",
      link: "/docs"
    },
    {
      icon: MessageSquare,
      title: "Community Forum",
      description: "Connect with other traders",
      link: "/forum",
      requiresLogin: true
    },
    {
      icon: Mail,
      title: "Email Support",
      description: "Get help from our team",
      email: "support@tradesignal.com"
    },
    {
      icon: Phone,
      title: "Schedule Demo",
      description: "Talk to a product specialist",
      link: "/contact"
    }
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Hero Section */}
      <section className="pt-32 pb-16 px-4 bg-gradient-to-b from-[#0f0f1a] to-[#0a0a0a]">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-4 py-2 mb-6">
            <HelpCircle className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-blue-300">Help Center</span>
          </div>
          <h1 className="text-5xl font-bold mb-6">
            How can we
            <span className="block bg-gradient-to-r from-blue-400 via-purple-400 to-blue-400 bg-clip-text text-transparent mt-2">
              help you today?
            </span>
          </h1>
          <p className="text-xl text-gray-400 mb-8 max-w-3xl mx-auto">
            Find answers to common questions or reach out to our support team
          </p>

          {/* Search Bar */}
          <div className="relative max-w-2xl mx-auto">
            <Search className="absolute left-6 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              placeholder="Search for help articles, guides, FAQs..."
              className="w-full bg-[#0f0f1a] border border-white/10 rounded-full pl-14 pr-6 py-4 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500/50 transition-all"
            />
          </div>
        </div>
      </section>

      {/* Help Categories */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Get Help</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {helpCategories.map((category, index) => (
              <div
                key={index}
                className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-6 text-center group hover:border-purple-500/30 transition-all cursor-pointer"
              >
                <div className="bg-purple-500/10 p-4 rounded-2xl inline-flex mb-4 group-hover:bg-purple-500/20 transition-all">
                  <category.icon className="w-6 h-6 text-purple-400" />
                </div>
                <h3 className="text-lg font-bold mb-2 group-hover:text-purple-400 transition-colors">
                  {category.title}
                </h3>
                <p className="text-gray-400 text-sm mb-4">{category.description}</p>
                {category.email ? (
                  <a
                    href={`mailto:${category.email}`}
                    className="text-purple-400 text-sm font-medium hover:text-purple-300 inline-flex items-center gap-1"
                  >
                    Send Email <ExternalLink className="w-3 h-3" />
                  </a>
                ) : category.requiresLogin ? (
                  <Link
                    to={category.link!}
                    className="text-purple-400 text-sm font-medium hover:text-purple-300 inline-flex items-center gap-1"
                  >
                    Visit Forum →
                  </Link>
                ) : (
                  <Link
                    to={category.link!}
                    className="text-purple-400 text-sm font-medium hover:text-purple-300 inline-flex items-center gap-1"
                  >
                    Learn More →
                  </Link>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16 px-4 bg-[#0f0f1a]">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Frequently Asked Questions</h2>
            <p className="text-gray-400">Quick answers to questions you may have</p>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div
                key={index}
                className="bg-[#0a0a0a] border border-white/10 rounded-2xl overflow-hidden hover:border-purple-500/30 transition-all"
              >
                <button
                  onClick={() => setOpenFaq(openFaq === index ? null : index)}
                  className="w-full flex items-center justify-between p-6 text-left"
                >
                  <span className="font-semibold text-white pr-4">{faq.question}</span>
                  <ChevronDown
                    className={`w-5 h-5 text-purple-400 flex-shrink-0 transition-transform ${
                      openFaq === index ? 'rotate-180' : ''
                    }`}
                  />
                </button>
                {openFaq === index && (
                  <div className="px-6 pb-6">
                    <p className="text-gray-400 leading-relaxed">{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link
              to="/faq"
              className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 font-medium"
            >
              View All FAQs →
            </Link>
          </div>
        </div>
      </section>

      {/* Popular Articles */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Popular Help Articles</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { title: "Getting Started with TradeSignal", category: "Beginner Guide", time: "5 min read" },
              { title: "Understanding SEC Form 4 Filings", category: "Education", time: "8 min read" },
              { title: "How to Set Up Custom Alerts", category: "Features", time: "4 min read" },
              { title: "Interpreting TS Score and IVT", category: "Research", time: "10 min read" },
              { title: "LUNA AI Analysis Explained", category: "AI Features", time: "6 min read" },
              { title: "Subscription Plans Comparison", category: "Billing", time: "3 min read" }
            ].map((article, index) => (
              <div
                key={index}
                className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-6 hover:border-purple-500/30 transition-all cursor-pointer group"
              >
                <span className="text-purple-400 text-xs font-medium">{article.category}</span>
                <h3 className="text-lg font-bold mt-2 mb-3 group-hover:text-purple-400 transition-colors">
                  {article.title}
                </h3>
                <span className="text-gray-500 text-sm">{article.time}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact CTA */}
      <section className="py-20 px-4 bg-gradient-to-b from-[#0a0a0a] to-[#0f0f1a]">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-[#0f0f1a] border border-blue-500/20 rounded-3xl p-12">
            <MessageSquare className="w-12 h-12 text-blue-400 mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-4">Still need help?</h2>
            <p className="text-gray-400 mb-8">
              Our support team is here to help you succeed with TradeSignal
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/contact"
                className="inline-flex items-center justify-center gap-2 bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-200 transition-all"
              >
                Contact Support
              </Link>
              <a
                href="mailto:support@tradesignal.com"
                className="inline-flex items-center justify-center gap-2 bg-white/5 border border-white/10 text-white px-8 py-4 rounded-full font-bold hover:bg-white/10 transition-all"
              >
                Email Us
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default PublicSupportPage;
