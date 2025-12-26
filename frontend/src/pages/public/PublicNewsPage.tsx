import { Newspaper, TrendingUp, Calendar, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';

const PublicNewsPage = () => {
  // Static news items (can be replaced with API call later)
  const newsItems = [
    {
      id: 1,
      title: "SEC Announces Enhanced Form 4 Filing Requirements",
      excerpt: "New regulations require corporate insiders to file Form 4 reports within 24 hours of transactions...",
      category: "Regulation",
      date: "2025-12-20",
      source: "SEC.gov",
      image: "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&q=80"
    },
    {
      id: 2,
      title: "Congressional Trading Activity Reaches Record Highs in Q4 2024",
      excerpt: "Analysis shows 535 Congress members reported over 2,400 stock transactions in the final quarter...",
      category: "Congressional Trading",
      date: "2025-12-18",
      source: "TradeSignal Research",
      image: "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=800&q=80"
    },
    {
      id: 3,
      title: "AI-Powered Trade Analysis: The Future of Insider Intelligence",
      excerpt: "Machine learning models are revolutionizing how investors track and analyze insider trading patterns...",
      category: "Technology",
      date: "2025-12-15",
      source: "Financial Tech Weekly",
      image: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80"
    },
    {
      id: 4,
      title: "Major Tech CEOs Report Significant Stock Sales",
      excerpt: "Leading executives at FAANG companies filed Form 4 reports showing coordinated selling activity...",
      category: "Insider Activity",
      date: "2025-12-12",
      source: "Market Watch",
      image: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80"
    },
    {
      id: 5,
      title: "New STOCK Act Amendments Proposed in Congress",
      excerpt: "Bipartisan legislation aims to strengthen restrictions on congressional stock trading...",
      category: "Legislation",
      date: "2025-12-10",
      source: "Congress.gov",
      image: "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800&q=80"
    },
    {
      id: 6,
      title: "TradeSignal Launches LUNA AI Engine",
      excerpt: "New unified AI analysis platform combines Gemini 2.5 Pro and Flash for institutional-grade insights...",
      category: "Product Update",
      date: "2025-12-08",
      source: "TradeSignal",
      image: "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&q=80"
    }
  ];

  const categories = ["All", "Regulation", "Congressional Trading", "Technology", "Insider Activity", "Legislation", "Product Update"];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Hero Section */}
      <section className="pt-32 pb-16 px-4 bg-gradient-to-b from-[#0f0f1a] to-[#0a0a0a]">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 rounded-full px-4 py-2 mb-6">
            <Newspaper className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-purple-300">Market News & Insights</span>
          </div>
          <h1 className="text-5xl font-bold mb-4">
            Stay Informed with
            <span className="block bg-gradient-to-r from-purple-400 via-blue-400 to-purple-400 bg-clip-text text-transparent mt-2">
              Market Intelligence
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Latest news on insider trading, congressional stock transactions, SEC regulations, and market-moving events
          </p>
        </div>
      </section>

      {/* Category Filter */}
      <section className="sticky top-20 z-40 bg-[#0a0a0a]/95 backdrop-blur-xl border-b border-white/5 py-4 px-4">
        <div className="max-w-7xl mx-auto flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
          {categories.map((category) => (
            <button
              key={category}
              className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
                category === "All"
                  ? "bg-purple-600 text-white"
                  : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </section>

      {/* News Grid */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          {/* Featured Article */}
          <div className="mb-12">
            <div className="relative rounded-3xl overflow-hidden bg-[#0f0f1a] border border-white/10 group cursor-pointer hover:border-purple-500/30 transition-all">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 p-8">
                <div className="flex flex-col justify-center">
                  <span className="text-purple-400 text-sm font-medium mb-2">{newsItems[0].category}</span>
                  <h2 className="text-3xl font-bold mb-4 group-hover:text-purple-400 transition-colors">
                    {newsItems[0].title}
                  </h2>
                  <p className="text-gray-400 mb-6">{newsItems[0].excerpt}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      {new Date(newsItems[0].date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                    </div>
                    <span>•</span>
                    <span>{newsItems[0].source}</span>
                  </div>
                  <button className="mt-6 inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 font-medium">
                    Read Full Article <ExternalLink className="w-4 h-4" />
                  </button>
                </div>
                <div className="relative h-64 lg:h-auto">
                  <img
                    src={newsItems[0].image}
                    alt={newsItems[0].title}
                    className="absolute inset-0 w-full h-full object-cover rounded-2xl"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* News Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {newsItems.slice(1).map((item) => (
              <div
                key={item.id}
                className="bg-[#0f0f1a] border border-white/10 rounded-2xl overflow-hidden group cursor-pointer hover:border-purple-500/30 transition-all"
              >
                <div className="relative h-48 overflow-hidden">
                  <img
                    src={item.image}
                    alt={item.title}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                  <div className="absolute top-4 left-4">
                    <span className="bg-purple-600/90 text-white text-xs font-medium px-3 py-1 rounded-full">
                      {item.category}
                    </span>
                  </div>
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-3 group-hover:text-purple-400 transition-colors">
                    {item.title}
                  </h3>
                  <p className="text-gray-400 text-sm mb-4 line-clamp-2">{item.excerpt}</p>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-3 h-3" />
                      {new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </div>
                    <span>{item.source}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Load More */}
          <div className="text-center mt-12">
            <button className="px-8 py-3 bg-white/5 border border-white/10 hover:bg-white/10 rounded-full text-white font-medium transition-all">
              Load More Articles
            </button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-b from-[#0a0a0a] to-[#0f0f1a]">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-[#0f0f1a] border border-purple-500/20 rounded-3xl p-12">
            <TrendingUp className="w-12 h-12 text-purple-400 mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-4">Get Real-Time Alerts</h2>
            <p className="text-gray-400 mb-8">
              Don't miss critical insider trading activity. Get instant notifications when insiders and Congress members make significant trades.
            </p>
            <Link
              to="/register"
              className="inline-flex items-center gap-2 bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-200 transition-all"
            >
              Start Free Trial →
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default PublicNewsPage;
