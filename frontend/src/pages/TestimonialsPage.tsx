import { Star, TrendingUp, Quote, CheckCircle2, Building2, User } from 'lucide-react';
import { Link } from 'react-router-dom';

const TestimonialsPage = () => {
  const testimonials = [
    {
      name: "Michael Rodriguez",
      role: "Retail Investor",
      location: "San Francisco, CA",
      image: null, // Using initials instead
      rating: 5,
      title: "Found a 34% winner in 3 weeks",
      quote: "I discovered a cluster of insider buying at a mid-cap tech company through TradeSignal's AI alerts. The stock jumped 34% in three weeks. This platform gives me an edge I never had before as a retail investor.",
      highlight: "34% gain",
      tier: "PRO"
    },
    {
      name: "Sarah Thompson",
      role: "Day Trader",
      location: "Austin, TX",
      image: null,
      rating: 5,
      title: "Real-time alerts are a game-changer",
      quote: "The real-time alerts are incredible. I got notified about a CEO buying $2M of his own stock before it hit Twitter. I was in the trade 10 minutes later. Up 18% in two days. The speed advantage is worth every penny.",
      highlight: "18% in 2 days",
      tier: "Plus"
    },
    {
      name: "David Lin",
      role: "Senior Analyst, Hedge Fund",
      location: "New York, NY",
      image: null,
      rating: 5,
      title: "Saves our team 20+ hours per week",
      quote: "We replaced our manual process of tracking Form 4 filings with TradeSignal's Enterprise API. It saves our team 20+ hours per week and the LUNA AI insights add real value to our client reports. The ROI is undeniable.",
      highlight: "20+ hours saved/week",
      tier: "Enterprise"
    },
    {
      name: "Jennifer Kim",
      role: "Wealth Manager",
      location: "Los Angeles, CA",
      image: null,
      rating: 5,
      title: "Clients love the insider activity reports",
      quote: "Our clients love the insider activity reports we now include in quarterly reviews. It shows we're going beyond the basics, and it's helped us win 12 new accounts this year alone. The white-label feature is perfect.",
      highlight: "12 new accounts",
      tier: "Enterprise"
    },
    {
      name: "Marcus Johnson",
      role: "Swing Trader",
      location: "Miami, FL",
      image: null,
      rating: 5,
      title: "Congressional trade tracking is brilliant",
      quote: "I focus on congressional trades and TradeSignal makes it effortless. When I see multiple senators buying the same defense stock, I know something's coming. Made 42% on LMT after tracking 8 senators buying in Q3.",
      highlight: "42% on LMT",
      tier: "PRO"
    },
    {
      name: "Emily Parker",
      role: "Options Trader",
      location: "Seattle, WA",
      image: null,
      rating: 5,
      title: "Conviction scores help me size positions",
      quote: "The LUNA AI conviction scores help me size my options positions with confidence. High conviction insider clusters get bigger allocations. I've increased my win rate from 58% to 74% since using TradeSignal.",
      highlight: "Win rate: 58% → 74%",
      tier: "PRO"
    },
    {
      name: "Robert Chen",
      role: "Quantitative Researcher",
      location: "Boston, MA",
      image: null,
      rating: 5,
      title: "API is rock-solid for backtesting",
      quote: "The Enterprise API is rock-solid. I've backtested 5 years of insider data for my quant models. The data quality is excellent, uptime is 100%, and the rate limits are generous. Worth every dollar for serious researchers.",
      highlight: "100% API uptime",
      tier: "Enterprise"
    },
    {
      name: "Amanda Martinez",
      role: "Financial Advisor",
      location: "Chicago, IL",
      image: null,
      rating: 5,
      title: "Helps me provide better client advice",
      quote: "TradeSignal helps me provide better advice to my clients. When insiders are selling heavily, I know to be cautious. It's saved my clients from holding bags multiple times. The research badges are perfect for reports.",
      highlight: "Protected $8.4M AUM",
      tier: "Plus"
    },
    {
      name: "Kevin O'Brien",
      role: "Tech Entrepreneur",
      location: "San Diego, CA",
      image: null,
      rating: 5,
      title: "Best investment I've made this year",
      quote: "As a busy founder, I don't have time to watch the markets 24/7. TradeSignal's SMS alerts keep me informed about insider activity in my portfolio. It's the best investment I've made this year—already paid for itself 10x over.",
      highlight: "10x ROI",
      tier: "PRO"
    }
  ];

  const stats = [
    { value: "12,000+", label: "Active Traders" },
    { value: "4.9/5", label: "Average Rating" },
    { value: "94%", label: "Would Recommend" },
    { value: "$847M", label: "AUM Protected" }
  ];

  const tierColors: Record<string, string> = {
    "Plus": "bg-blue-500/20 text-blue-400 border-blue-500/30",
    "PRO": "bg-purple-500/20 text-purple-400 border-purple-500/30",
    "Enterprise": "bg-orange-500/20 text-orange-400 border-orange-500/30"
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Hero Section */}
      <section className="pt-32 pb-16 px-4 bg-gradient-to-b from-[#0f0f1a] to-[#0a0a0a]">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-yellow-500/10 border border-yellow-500/20 rounded-full px-4 py-2 mb-6">
            <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
            <span className="text-sm text-yellow-300">Customer Stories</span>
          </div>
          <h1 className="text-5xl font-bold mb-6">
            Loved by Traders
            <span className="block bg-gradient-to-r from-yellow-400 via-orange-400 to-yellow-400 bg-clip-text text-transparent mt-2">
              Around the World
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
            See how real traders use TradeSignal to gain an edge, save time, and make better investment decisions
          </p>

          {/* Star Rating */}
          <div className="flex items-center justify-center gap-2 mb-4">
            {[1, 2, 3, 4, 5].map((star) => (
              <Star key={star} className="w-6 h-6 text-yellow-400 fill-yellow-400" />
            ))}
            <span className="text-gray-400 ml-2">4.9 out of 5</span>
          </div>
          <p className="text-sm text-gray-500">Based on 2,847 verified reviews</p>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="py-12 px-4 border-b border-white/5">
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-3xl font-bold text-purple-400 mb-1">{stat.value}</div>
              <div className="text-sm text-gray-500">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Testimonials Grid */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div
                key={index}
                className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-8 hover:border-purple-500/30 transition-all group relative"
              >
                {/* Quote Icon */}
                <Quote className="absolute top-6 right-6 w-8 h-8 text-purple-500/20" />

                {/* Rating */}
                <div className="flex gap-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                  ))}
                </div>

                {/* Title */}
                <h3 className="text-lg font-bold mb-3 group-hover:text-purple-400 transition-colors">
                  {testimonial.title}
                </h3>

                {/* Quote */}
                <p className="text-gray-400 text-sm mb-6 leading-relaxed">
                  "{testimonial.quote}"
                </p>

                {/* Highlight Badge */}
                <div className="bg-green-500/10 border border-green-500/20 rounded-full px-3 py-1 inline-flex items-center gap-2 mb-6">
                  <TrendingUp className="w-3 h-3 text-green-400" />
                  <span className="text-xs font-medium text-green-400">{testimonial.highlight}</span>
                </div>

                {/* Author */}
                <div className="flex items-center gap-3 pt-4 border-t border-white/5">
                  <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-sm font-bold">
                    {testimonial.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-sm">{testimonial.name}</div>
                    <div className="text-xs text-gray-500">{testimonial.role}</div>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full border ${tierColors[testimonial.tier]}`}>
                    {testimonial.tier}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Case Study Highlight */}
      <section className="py-16 px-4 bg-[#0f0f1a]">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <Building2 className="w-12 h-12 text-purple-400 mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-4">Featured Success Story</h2>
            <p className="text-gray-400">How a hedge fund transformed their research process</p>
          </div>

          <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-12">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
              <div className="text-center">
                <div className="text-4xl font-bold text-purple-400 mb-2">20hrs</div>
                <div className="text-sm text-gray-400">Saved per week</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-400 mb-2">5,000+</div>
                <div className="text-sm text-gray-400">Filings analyzed monthly</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-green-400 mb-2">$2.4M</div>
                <div className="text-sm text-gray-400">Annual cost savings</div>
              </div>
            </div>

            <div className="bg-white/5 border border-white/5 rounded-xl p-8">
              <Quote className="w-8 h-8 text-purple-400 mb-4" />
              <p className="text-gray-300 text-lg mb-6 italic">
                "TradeSignal's Enterprise API completely transformed how we conduct research. What used to take our analysts 4 hours of manual work per day now happens automatically. The AI insights surface patterns we would have missed, and the data quality is impeccable. We've integrated it into our entire investment process."
              </p>
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-gradient-to-br from-orange-500 to-red-500 rounded-full flex items-center justify-center text-xl font-bold">
                  DL
                </div>
                <div>
                  <div className="font-bold">David Lin</div>
                  <div className="text-sm text-gray-400">Senior Analyst, Quantum Capital Partners</div>
                  <div className="text-xs text-gray-500">$420M AUM • New York, NY</div>
                </div>
              </div>
            </div>

            <div className="mt-8 text-center">
              <Link
                to="/contact"
                className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 font-medium"
              >
                Read Full Case Study →
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Trust Indicators */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Trusted By</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { type: "Hedge Funds", count: "47+" },
              { type: "RIAs", count: "230+" },
              { type: "Day Traders", count: "8,400+" },
              { type: "Institutions", count: "12" }
            ].map((segment, index) => (
              <div key={index} className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-6 text-center">
                <div className="text-3xl font-bold text-purple-400 mb-2">{segment.count}</div>
                <div className="text-sm text-gray-400">{segment.type}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 bg-gradient-to-b from-[#0a0a0a] to-[#0f0f1a]">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-[#0f0f1a] border border-purple-500/20 rounded-3xl p-12">
            <CheckCircle2 className="w-12 h-12 text-green-400 mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-4">Join 12,000+ Successful Traders</h2>
            <p className="text-gray-400 mb-8">
              Start your 14-day free trial and see why traders love TradeSignal. No credit card required.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="inline-flex items-center justify-center gap-2 bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-200 transition-all"
              >
                <User className="w-5 h-5" />
                Start Free Trial
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

export default TestimonialsPage;
