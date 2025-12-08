import React from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, Shield, Zap, Search, ChevronRight, ArrowRight, BarChart2, Globe } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const LandingPage = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-black text-white selection:bg-purple-500 selection:text-white font-sans overflow-x-hidden">
      
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
        {/* Abstract Background Elements */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-purple-600/30 rounded-full blur-[120px] -z-10" />
        <div className="absolute bottom-0 right-0 w-[800px] h-[600px] bg-blue-600/20 rounded-full blur-[120px] -z-10" />

        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="max-w-3xl">
            <h1 className="text-5xl lg:text-7xl font-bold leading-tight mb-6">
              Insider Trading <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">
                Decoded by AI
              </span>
            </h1>
            <p className="text-xl text-gray-400 mb-8 max-w-xl leading-relaxed">
              Get superhuman market insights with TradeSignal AI. Track congressional trades, insider moves, and institutional flows in one convenient app.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link 
                to="/register" 
                className="px-8 py-4 bg-white text-black font-semibold rounded-full text-lg hover:bg-gray-100 transition-all hover:scale-105 flex items-center justify-center gap-2"
              >
                Start Free Trial <ArrowRight className="w-5 h-5" />
              </Link>
              <Link 
                to="/login"
                className="px-8 py-4 bg-white/10 backdrop-blur-sm border border-white/10 text-white font-semibold rounded-full text-lg hover:bg-white/20 transition-all flex items-center justify-center"
              >
                View Live Demo
              </Link>
            </div>
          </div>
        </div>

        {/* Hero Visual / Wave Approximation */}
        <div className="absolute bottom-0 left-0 w-full h-48 sm:h-64 lg:h-96 -z-10 overflow-hidden translate-y-20">
             <svg className="absolute bottom-0 w-full h-full" viewBox="0 0 1440 320" preserveAspectRatio="none">
                <path fill="url(#hero-gradient)" fillOpacity="1" d="M0,160L48,176C96,192,192,224,288,224C384,224,480,192,576,165.3C672,139,768,117,864,128C960,139,1056,181,1152,197.3C1248,213,1344,203,1392,197.3L1440,192L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path>
                <defs>
                  <linearGradient id="hero-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#7c3aed" />
                    <stop offset="100%" stopColor="#3b82f6" />
                  </linearGradient>
                </defs>
              </svg>
        </div>
      </section>

      {/* Features Grid - "Navigate the Markets" */}
      <section className="py-24 bg-gradient-to-b from-black to-gray-900" id="features">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl lg:text-5xl font-bold mb-6">
                Navigate the Markets <br/> with Confidence
              </h2>
              <p className="text-lg text-gray-400 mb-8">
                Navigate the markets with confidence using AI-powered insights that simplify complex data into clear, actionable strategies.
              </p>
              <Link to="/register" className="px-6 py-3 bg-white/10 hover:bg-white/20 rounded-full text-white font-medium transition-colors inline-flex items-center gap-2">
                Explore Features <ChevronRight className="w-4 h-4" />
              </Link>
            </div>

            <div className="space-y-8">
              {[
                {
                  icon: <Zap className="w-6 h-6" />,
                  title: "Timely Market Insights",
                  desc: "TradeSignal AI is your personal investment analyst. Get the current outlook on any stock or cryptocurrency instantly."
                },
                {
                  icon: <Search className="w-6 h-6" />,
                  title: "Discover Your Next Trade",
                  desc: "See the big movers today, and find out what caused the price movement. It's the best way to find your new favorite market."
                },
                {
                  icon: <Shield className="w-6 h-6" />,
                  title: "AI That You Can Rely On",
                  desc: "Smart filters, quality news data, and advanced prompt engineering means our AI avoids hallucinations."
                }
              ].map((feature, i) => (
                <div key={i} className="flex gap-4 p-6 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                  <div className="shrink-0 w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center text-purple-400">
                    {feature.icon}
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                    <p className="text-gray-400 leading-relaxed">{feature.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Dark Cards Section - "Effortless Market Intelligence" */}
      <section className="py-24 bg-black">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-purple-400 font-semibold tracking-wider text-sm uppercase mb-2 block">Features</span>
            <h2 className="text-4xl lg:text-5xl font-bold mb-6">
              Effortless Market Intelligence,<br /> Right At Your Fingertips.
            </h2>
            <p className="text-gray-400 text-lg">
              Find out why a market is trending without having to read twenty news articles. Unlike some AI tools, we provide accurate, verified information.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Card 1 */}
            <div className="group relative bg-gray-900 rounded-3xl overflow-hidden border border-white/10 hover:border-purple-500/50 transition-all duration-300">
              <div className="aspect-video bg-gradient-to-br from-blue-900 to-black p-6 flex flex-col justify-end relative">
                 <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1611974765270-ca1258634369?auto=format&fit=crop&q=80&w=800')] bg-cover bg-center opacity-40 mix-blend-overlay"></div>
                 <div className="relative z-10">
                   <div className="flex items-center gap-2 mb-2">
                     <div className="bg-red-500 p-1 rounded-full"><TrendingUp className="w-4 h-4 text-white" /></div>
                     <span className="text-sm font-medium">MCD is up</span>
                     <span className="text-xs text-gray-400">7h ago</span>
                   </div>
                   <h3 className="text-xl font-bold leading-tight">AI Predicts Strong Bullish Momentum</h3>
                 </div>
              </div>
              <div className="p-6">
                <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                  McDonald's Corporation is an American multinational fast food chain, founded in 1940 as a restaurant operated by Richard and Maurice McDonald.
                </p>
                <button className="flex items-center gap-2 text-sm font-medium hover:text-purple-400 transition-colors">
                  View More <div className="bg-white/10 rounded-full p-1"><ChevronRight className="w-3 h-3" /></div>
                </button>
              </div>
            </div>

            {/* Card 2 */}
            <div className="group relative bg-gray-900 rounded-3xl overflow-hidden border border-white/10 hover:border-purple-500/50 transition-all duration-300">
               <div className="aspect-video bg-gradient-to-br from-purple-900 to-black p-6 flex flex-col justify-end relative">
                 <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1621761191319-c6fb62004040?auto=format&fit=crop&q=80&w=800')] bg-cover bg-center opacity-40 mix-blend-overlay"></div>
                 <div className="relative z-10">
                   <div className="flex items-center gap-2 mb-2">
                     <div className="bg-white p-1 rounded-full text-black"><TrendingUp className="w-4 h-4" /></div>
                     <span className="text-sm font-medium">AAPL is up</span>
                     <span className="text-xs text-gray-400">2h ago</span>
                   </div>
                   <h3 className="text-xl font-bold leading-tight">Tech Sector Rally Continues</h3>
                 </div>
              </div>
              <div className="p-6">
                <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                  Apple Inc. is an American multinational technology company headquartered in Cupertino, California. Apple is the world's largest technology company.
                </p>
                <button className="flex items-center gap-2 text-sm font-medium hover:text-purple-400 transition-colors">
                  View More <div className="bg-white/10 rounded-full p-1"><ChevronRight className="w-3 h-3" /></div>
                </button>
              </div>
            </div>

             {/* Card 3 */}
            <div className="group relative bg-gray-900 rounded-3xl overflow-hidden border border-white/10 hover:border-purple-500/50 transition-all duration-300 md:col-span-2 lg:col-span-1">
               <div className="aspect-video bg-gradient-to-br from-green-900 to-black p-6 flex flex-col justify-end relative">
                 <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1518546305927-5a555bb7020d?auto=format&fit=crop&q=80&w=800')] bg-cover bg-center opacity-40 mix-blend-overlay"></div>
                 <div className="relative z-10">
                   <div className="flex items-center gap-2 mb-2">
                     <div className="bg-green-500 p-1 rounded-full"><TrendingUp className="w-4 h-4 text-white" /></div>
                     <span className="text-sm font-medium">BTC is up</span>
                     <span className="text-xs text-gray-400">Live</span>
                   </div>
                   <h3 className="text-xl font-bold leading-tight">Crypto Market Breakout</h3>
                 </div>
              </div>
              <div className="p-6">
                <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                   Bitcoin (BTC) is a cryptocurrency token that was created in 2009. It is the first decentralized cryptocurrency.
                </p>
                <button className="flex items-center gap-2 text-sm font-medium hover:text-purple-400 transition-colors">
                  View More <div className="bg-white/10 rounded-full p-1"><ChevronRight className="w-3 h-3" /></div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* App Showcase Section - "Turn Insights Into Action" */}
      <section className="py-24 bg-gray-50 text-gray-900">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-12 mb-16">
            <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 max-w-xl">
              Turn insights into action: <br />
              <span className="text-gray-500">Discover your trading edge.</span>
            </h2>
            <Link to="/register" className="px-8 py-3 bg-black text-white rounded-full font-medium hover:bg-gray-800 transition-colors">
              Get Started
            </Link>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Feature Box 1 */}
            <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 flex flex-col items-center text-center">
              <div className="w-full max-w-sm aspect-[4/3] bg-gray-100 rounded-2xl mb-8 relative overflow-hidden group">
                 <div className="absolute inset-0 flex items-center justify-center text-gray-400 font-medium">
                   {/* Placeholder for App UI */}
                   <div className="space-y-4 w-3/4">
                      <div className="h-2 bg-gray-300 rounded w-1/2 mx-auto"></div>
                      <div className="h-32 bg-white shadow-lg rounded-xl border border-gray-200 p-4">
                        <div className="flex justify-between mb-4">
                           <div className="h-4 w-12 bg-gray-200 rounded"></div>
                           <div className="h-4 w-8 bg-green-100 rounded text-green-600 text-xs flex items-center justify-center">Buy</div>
                        </div>
                        <div className="h-12 w-full bg-blue-50 rounded-lg mb-2"></div>
                         <div className="h-2 w-full bg-gray-100 rounded"></div>
                      </div>
                   </div>
                 </div>
              </div>
              <h3 className="text-2xl font-bold mb-3">The all-in-one trading app</h3>
              <p className="text-gray-500 max-w-sm">
                Trade every market imaginable in one place. Invest in stocks, congressional trades, and insider moves.
              </p>
            </div>

            {/* Feature Box 2 */}
            <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 flex flex-col items-center text-center">
               <div className="w-full max-w-sm aspect-[4/3] bg-gray-100 rounded-2xl mb-8 relative overflow-hidden">
                  {/* Abstract Chart UI */}
                   <div className="absolute inset-0 flex items-center justify-center">
                      <div className="relative w-48 h-48">
                         <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-tr from-purple-100 to-blue-50 rounded-full animate-pulse"></div>
                         <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-white rounded-lg shadow-xl flex items-center justify-center">
                            <BarChart2 className="w-12 h-12 text-blue-600" />
                         </div>
                         <div className="absolute -top-4 -right-4 bg-white p-2 rounded-lg shadow-md">
                           <span className="text-xs font-bold text-green-600">+12.5%</span>
                         </div>
                      </div>
                   </div>
               </div>
              <h3 className="text-2xl font-bold mb-3">Follow the Smart Money</h3>
              <p className="text-gray-500 max-w-sm">
                 Track verified insider trades and congressional stock activities in real-time.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Footer Section */}
      <section className="py-32 bg-gradient-to-b from-purple-900 via-indigo-900 to-black text-center px-6 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-full bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
        <div className="max-w-4xl mx-auto relative z-10">
          <h2 className="text-4xl lg:text-6xl font-bold mb-6">
            Unlike Any Trading Platform
          </h2>
          <p className="text-xl text-purple-200 mb-10 max-w-2xl mx-auto">
            We rebuilt financial intelligence from the ground up. All in the pursuit of the perfect trading experience.
          </p>
          <Link 
            to="/register" 
            className="px-10 py-4 bg-white text-black font-bold rounded-full text-lg hover:bg-gray-100 transition-all hover:scale-105 inline-block"
          >
            Get Started
          </Link>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
