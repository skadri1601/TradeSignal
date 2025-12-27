import { Star, Quote, CheckCircle2, User } from 'lucide-react';
import { Link } from 'react-router-dom';

const TestimonialsPage = () => {
  const testimonials = [
    {
      name: "Anonymous Retail Trader",
      role: "Individual Investor",
      rating: 5,
      title: "Helpful insider tracking tool",
      quote: "TradeSignal helps me track insider activity that I couldn't find on my own. The interface is intuitive and the alerts are timely.",
      tier: "PRO"
    },
    {
      name: "Anonymous Professional",
      role: "Financial Analyst",
      rating: 5,
      title: "Saves time on research",
      quote: "The platform streamlines my research process. Having SEC filings and insider trades organized in one place makes my workflow much more efficient.",
      tier: "Enterprise"
    },
    {
      name: "Anonymous Trader",
      role: "Active Trader",
      rating: 5,
      title: "Good data aggregation",
      quote: "TradeSignal aggregates data from multiple sources, which helps me spot trends I might have missed. The congressional trading feature is particularly interesting.",
      tier: "Plus"
    }
  ];

  const stats = [
    { value: "Growing", label: "Community" },
    { value: "Highly", label: "Rated" },
    { value: "Trusted", label: "Platform" },
    { value: "Protecting", label: "Assets" }
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
            Hear from traders who use TradeSignal to track insider activity and congressional trades
          </p>

          {/* Star Rating */}
          <div className="flex items-center justify-center gap-2 mb-4">
            {[1, 2, 3, 4, 5].map((star) => (
              <Star key={star} className="w-6 h-6 text-yellow-400 fill-yellow-400" />
            ))}
            <span className="text-gray-400 ml-2">Highly rated by users</span>
          </div>
          <p className="text-sm text-gray-500">Trusted by traders worldwide</p>
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

      {/* CTA */}
      <section className="py-20 px-4 bg-gradient-to-b from-[#0a0a0a] to-[#0f0f1a]">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-[#0f0f1a] border border-purple-500/20 rounded-3xl p-12">
            <CheckCircle2 className="w-12 h-12 text-green-400 mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-4">Join Our Growing Community</h2>
            <p className="text-gray-400 mb-8">
              Start your free trial and experience TradeSignal for yourself. No credit card required.
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
