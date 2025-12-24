import { motion } from 'framer-motion';
import { Calendar, User, ArrowRight, Tag } from 'lucide-react';

// Educational & Feature-Focused Blog Content
const blogPosts = [
  {
    id: 1,
    title: "Mastering SEC Form 4: A Trader's Guide",
    excerpt: "Decode the language of insider trading. Learn the difference between Transaction Code 'P' (Purchase) and 'S' (Sale), and why clustered filing dates matter more than individual trades.",
    date: "Dec 18, 2025",
    author: "Research Team",
    category: "Education",
    image: "https://images.unsplash.com/photo-1611974765270-ca1258634369?auto=format&fit=crop&q=80&w=800",
    slug: "mastering-sec-form-4"
  },
  {
    id: 2,
    title: "The STOCK Act: Tracking Congressional Trades",
    excerpt: "Members of Congress consistently beat the S&P 500. We explain how the STOCK Act mandates disclosure and how you can use our Congressional Trading feature to track their moves.",
    date: "Dec 15, 2025",
    author: "Policy Analyst",
    category: "Market Analysis",
    image: "https://images.unsplash.com/photo-1555848962-6e79363ec58f?auto=format&fit=crop&q=80&w=800",
    slug: "stock-act-explained"
  },
  {
    id: 3,
    title: "Meet LUNA: Our Advanced AI Sentiment Engine",
    excerpt: "TradeSignal isn't just a data feed. Discover how LUNA analyzes thousands of filings to assign 'Bullish' or 'Bearish' sentiment scores to complex transaction patterns.",
    date: "Dec 10, 2025",
    author: "Engineering",
    category: "Technology",
    image: "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&q=80&w=800",
    slug: "ai-sentiment-engine"
  }
];

const BlogPage = () => {
  return (
    <div className="min-h-screen bg-black text-white font-sans selection:bg-purple-500/30 overflow-x-hidden">
      
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6 overflow-hidden">
        {/* Abstract Background */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-purple-900/20 rounded-full blur-[120px] -z-10" />
        
        <div className="max-w-7xl mx-auto text-center relative z-10">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-5xl lg:text-7xl font-bold mb-6 tracking-tight"
          >
            Market <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">Insights</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-xl text-gray-400 max-w-2xl mx-auto"
          >
            Learn how to decode the smart money. TradeSignal tracks SEC Form 4 filings, congressional
            trades, and institutional flows with LUNA AI. Explore educational resources, feature deep-dives,
            and analysis to trade with institutional confidence.
          </motion.p>
        </div>
      </section>

      {/* Platform Introduction */}
      <section className="py-12 px-6 border-b border-white/10">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-gray-400 leading-relaxed mb-6">
            TradeSignal is a real-time insider trading intelligence platform designed for retail investors,
            day traders, and financial analysts. We process 15 million+ filings with 92% sentiment accuracy
            using LUNA, our advanced AI engine.
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-sm">
            <div className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-full">
              <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
              <span className="text-gray-300">SEC Form 4 Tracking</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-full">
              <span className="w-2 h-2 bg-purple-400 rounded-full"></span>
              <span className="text-gray-300">Congressional Trades</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-full">
              <span className="w-2 h-2 bg-green-400 rounded-full"></span>
              <span className="text-gray-300">LUNA AI Insights</span>
            </div>
          </div>
        </div>
      </section>

      {/* Blog Grid */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {blogPosts.map((post, index) => (
              <motion.article 
                key={post.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
                className="group bg-gray-900/50 border border-white/10 rounded-3xl overflow-hidden hover:border-purple-500/30 transition-all duration-300 flex flex-col"
              >
                {/* Image */}
                <div className="aspect-[16/9] overflow-hidden relative">
                  <div className="absolute inset-0 bg-gradient-to-t from-gray-900 to-transparent opacity-60 z-10" />
                  <img 
                    src={post.image} 
                    alt={post.title}
                    className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-4 left-4 z-20">
                    <span className="px-3 py-1 bg-black/50 backdrop-blur-md border border-white/10 rounded-full text-xs font-medium text-white flex items-center gap-1">
                      <Tag className="w-3 h-3" /> {post.category}
                    </span>
                  </div>
                </div>

                {/* Content */}
                <div className="p-6 flex-1 flex flex-col">
                  <div className="flex items-center gap-4 text-xs text-gray-500 mb-4">
                    <div className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {post.date}
                    </div>
                    <div className="flex items-center gap-1">
                      <User className="w-3 h-3" />
                      {post.author}
                    </div>
                  </div>

                  <h2 className="text-xl font-bold text-white mb-3 group-hover:text-purple-400 transition-colors line-clamp-2">
                    {post.title}
                  </h2>
                  <p className="text-gray-400 text-sm mb-6 flex-1 line-clamp-3 leading-relaxed">
                    {post.excerpt}
                  </p>

                  <button 
                    className="inline-flex items-center gap-2 text-sm font-medium text-white group-hover:gap-3 transition-all cursor-not-allowed opacity-80"
                    title="Coming Soon"
                  >
                    Read Article <ArrowRight className="w-4 h-4 text-purple-400" />
                  </button>
                </div>
              </motion.article>
            ))}
          </div>
        </div>
      </section>

      {/* Newsletter CTA */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-white/10 rounded-3xl p-8 md:p-12 text-center relative overflow-hidden">
          <div className="relative z-10">
            <h2 className="text-3xl font-bold text-white mb-4">Never Miss a Signal</h2>
            <p className="text-gray-400 mb-8 max-w-lg mx-auto">
              Join 10,000+ traders getting weekly breakdowns of the most significant insider moves and congressional trades.
            </p>
            
            <form className="max-w-md mx-auto relative flex items-center">
              <input 
                type="email" 
                placeholder="Enter your email" 
                className="w-full bg-black/50 border border-white/20 rounded-full py-4 pl-6 pr-32 text-white placeholder:text-gray-500 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-colors"
              />
              <button 
                type="button"
                className="absolute right-2 top-2 bottom-2 bg-white text-black font-semibold px-6 rounded-full hover:bg-gray-200 transition-colors"
              >
                Subscribe
              </button>
            </form>
          </div>
          
          {/* Decorative background */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/10 rounded-full blur-[80px]" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-500/10 rounded-full blur-[80px]" />
        </div>
      </section>

    </div>
  );
};

export default BlogPage;
