import { Calendar, Clock, TrendingUp, Bell, ArrowRight, Sparkles } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

export default function FedCalendarPage() {
  const navigate = useNavigate();

  const plannedFeatures = [
    {
      icon: Calendar,
      title: 'FOMC Meeting Schedule',
      description: 'Track all Federal Open Market Committee meetings and decision dates',
    },
    {
      icon: TrendingUp,
      title: 'Interest Rate Tracking',
      description: 'Monitor Federal Reserve interest rate decisions and changes in real-time',
    },
    {
      icon: Clock,
      title: 'Economic Calendar',
      description: 'View upcoming economic indicators, GDP releases, and inflation reports',
    },
    {
      icon: Bell,
      title: 'Rate Change Alerts',
      description: 'Get notified immediately when the Fed announces rate changes or policy updates',
    },
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Hero Section */}
      <section className="pt-24 pb-16 px-4 bg-gradient-to-b from-[#0f0f1a] to-[#0a0a0a]">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 rounded-full px-4 py-2 mb-6">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-purple-300">Future Enhancement</span>
          </div>
          <div className="flex justify-center mb-6">
            <div className="w-20 h-20 bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-2xl flex items-center justify-center border border-purple-500/30">
              <Calendar className="w-10 h-10 text-purple-400" />
            </div>
          </div>
          <h1 className="text-5xl font-bold mb-6">
            Fed Calendar
            <span className="block bg-gradient-to-r from-purple-400 via-blue-400 to-purple-400 bg-clip-text text-transparent mt-2">
              Coming Soon
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
            Track Federal Reserve meetings, interest rate decisions, and economic indicators all in one place. 
            Stay ahead of market-moving Fed announcements with our comprehensive calendar.
          </p>
        </div>
      </section>

      {/* Planned Features */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Planned Features</h2>
            <p className="text-gray-400">Everything you need to track Federal Reserve activity</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
            {plannedFeatures.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-6 hover:border-purple-500/30 transition-all"
                >
                  <div className="flex items-start space-x-4">
                    <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center flex-shrink-0 border border-purple-500/20">
                      <Icon className="w-6 h-6 text-purple-400" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
                      <p className="text-gray-400 text-sm">{feature.description}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Coming Soon Banner */}
          <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl p-8 border border-white/10">
            <div className="text-center">
              <Calendar className="w-12 h-12 text-purple-400 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">Fed Calendar Coming Soon!</h3>
              <p className="text-gray-400 max-w-2xl mx-auto mb-6">
                We're building a comprehensive Federal Reserve calendar that will help you track all FOMC meetings, 
                interest rate decisions, and economic indicators. Stay tuned for updates!
              </p>
              <div className="flex items-center justify-center space-x-4">
                <Link
                  to="/roadmap"
                  className="px-6 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors flex items-center gap-2"
                >
                  <Sparkles className="w-4 h-4" />
                  View Roadmap
                </Link>
                <button
                  onClick={() => navigate('/trades')}
                  className="px-6 py-3 bg-white/10 text-white border border-white/20 rounded-lg font-medium hover:bg-white/20 transition-colors flex items-center gap-2"
                >
                  Explore Insider Trades
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Additional Info Section */}
      <section className="py-16 px-4 bg-[#0f0f1a]">
        <div className="max-w-4xl mx-auto">
          <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-8">
            <h3 className="text-2xl font-bold text-white mb-4">Why Fed Calendar Matters</h3>
            <div className="space-y-4 text-gray-400">
              <p>
                Federal Reserve decisions on interest rates are among the most significant market-moving events. 
                The Fed Calendar will help you:
              </p>
              <ul className="space-y-2 ml-6 list-disc">
                <li>Plan your trading strategy around FOMC meeting dates</li>
                <li>Stay informed about upcoming interest rate decisions</li>
                <li>Track economic indicators that influence Fed policy</li>
                <li>Set alerts for rate changes and policy announcements</li>
                <li>Understand the relationship between Fed policy and insider trading activity</li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

