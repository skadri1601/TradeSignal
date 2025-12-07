/**
 * Strategies Page - Trading Strategies Based on Insider Data
 */

import { Users, TrendingUp, Target, BarChart3, Zap, Shield, Clock } from 'lucide-react';
import { useCustomAlert } from '../hooks/useCustomAlert';
import CustomAlert from '../components/common/CustomAlert';

export default function StrategiesPage() {
  const { alertState, showAlert, hideAlert } = useCustomAlert();
  const strategies = [
    {
      id: 1,
      name: 'Follow the Insiders',
      description: 'Track and mirror trades made by company insiders with proven track records',
      riskLevel: 'Medium',
      timeframe: 'Medium-term (3-12 months)',
      icon: Users,
      color: 'blue',
      features: [
        'Identify high-performing insiders',
        'Monitor their buying patterns',
        'Set alerts for their transactions',
        'Analyze historical performance'
      ]
    },
    {
      id: 2,
      name: 'Cluster Buying Signal',
      description: 'Identify when multiple insiders buy shares simultaneously - a strong bullish indicator',
      riskLevel: 'Low-Medium',
      timeframe: 'Short-term (1-6 months)',
      icon: TrendingUp,
      color: 'green',
      features: [
        'Detect coordinated insider buying',
        'Track buying volume spikes',
        'Filter by time windows',
        'Measure conviction strength'
      ]
    },
    {
      id: 3,
      name: 'CEO Conviction Play',
      description: 'Focus on large purchases by CEOs - they have the most insight into company performance',
      riskLevel: 'Medium',
      timeframe: 'Medium-term (6-18 months)',
      icon: Target,
      color: 'purple',
      features: [
        'Filter for CEO transactions only',
        'Identify unusually large buys',
        'Compare to historical patterns',
        'Track post-trade stock performance'
      ]
    },
    {
      id: 4,
      name: 'Sector Rotation',
      description: 'Identify sectors with increasing insider buying activity before market catches on',
      riskLevel: 'Medium-High',
      timeframe: 'Long-term (12+ months)',
      icon: BarChart3,
      color: 'orange',
      features: [
        'Aggregate insider activity by sector',
        'Spot emerging trends early',
        'Compare sector performance',
        'Diversify across industries'
      ]
    },
  ];

  const colorMap: Record<string, { bg: string; text: string; border: string }> = {
    blue: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
    green: { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200' },
    purple: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
    orange: { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200' },
  };

  const riskColors: Record<string, string> = {
    'Low-Medium': 'bg-green-100 text-green-700',
    'Medium': 'bg-yellow-100 text-yellow-700',
    'Medium-High': 'bg-orange-100 text-orange-700',
    'High': 'bg-red-100 text-red-700',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Zap className="w-8 h-8 mr-3 text-blue-600" />
          Trading Strategies
        </h1>
        <p className="text-gray-600 mt-2">
          Proven strategies for leveraging insider trading data in your investment decisions
        </p>
      </div>

      {/* Risk Disclaimer */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
        <div className="flex items-start space-x-3">
          <Shield className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-gray-900 mb-1">Important Disclaimer</h3>
            <p className="text-sm text-gray-700">
              Insider trading data is one of many factors to consider when making investment decisions.
              Past performance does not guarantee future results. Always do your own research and consider
              consulting with a financial advisor before making investment decisions.
            </p>
          </div>
        </div>
      </div>

      {/* Strategies */}
      <div className="space-y-6">
        {strategies.map((strategy) => {
          const Icon = strategy.icon;
          const colors = colorMap[strategy.color];

          return (
            <div
              key={strategy.id}
              onClick={() => {
                // For now, show strategy details
                // In the future, this could navigate to /strategies/{strategy.id} or open a modal
                showAlert(
                  `"${strategy.name}" strategy details coming soon! This strategy focuses on ${strategy.description.toLowerCase()}`,
                  { type: 'info', title: 'TradeSignal' }
                );
              }}
              className={`bg-white rounded-2xl shadow-sm border-2 ${colors.border} p-6 hover:shadow-md transition-all cursor-pointer`}
            >
              <div className="flex items-start space-x-6">
                <div className={`w-16 h-16 ${colors.bg} rounded-xl flex items-center justify-center flex-shrink-0`}>
                  <Icon className={`w-8 h-8 ${colors.text}`} />
                </div>

                <div className="flex-1">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900 mb-2">{strategy.name}</h3>
                      <p className="text-gray-600">{strategy.description}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                        <Shield className="w-5 h-5 text-gray-600" />
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Risk Level</p>
                        <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${riskColors[strategy.riskLevel]}`}>
                          {strategy.riskLevel}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                        <Clock className="w-5 h-5 text-gray-600" />
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Timeframe</p>
                        <p className="font-medium text-gray-900 text-sm">{strategy.timeframe}</p>
                      </div>
                    </div>
                  </div>

                  <div className="border-t border-gray-200 pt-4">
                    <p className="text-sm font-semibold text-gray-700 mb-3">Key Features:</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {strategy.features.map((feature, idx) => (
                        <div key={idx} className="flex items-start space-x-2">
                          <div className={`w-1.5 h-1.5 ${colors.bg} rounded-full mt-2 flex-shrink-0`}></div>
                          <p className="text-sm text-gray-600">{feature}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Coming Soon */}
      <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl p-8 border border-indigo-200">
        <div className="text-center">
          <Zap className="w-12 h-12 text-indigo-600 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">Strategy Backtesting Coming Soon!</h3>
          <p className="text-gray-600 max-w-2xl mx-auto mb-4">
            We're building tools to backtest these strategies against historical data,
            so you can see exactly how they would have performed before investing real money.
          </p>
          <div className="flex items-center justify-center space-x-4">
            <button 
              onClick={() => {
                showAlert(
                  'Notification feature coming soon! We\'ll notify you when strategy backtesting is available.',
                  { type: 'info', title: 'TradeSignal' }
                );
              }}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors"
            >
              Get Notified
            </button>
            <button 
              onClick={() => {
                showAlert(
                  'Learn more about our strategy backtesting feature coming soon!',
                  { type: 'info', title: 'TradeSignal' }
                );
              }}
              className="px-6 py-3 bg-white text-indigo-600 border-2 border-indigo-600 rounded-lg font-medium hover:bg-indigo-50 transition-colors"
            >
              Learn More
            </button>
          </div>
        </div>
      </div>

      {/* Custom Alert Modal */}
      <CustomAlert
        show={alertState.show}
        message={alertState.message}
        title={alertState.title || 'TradeSignal'}
        type={alertState.type}
        onClose={hideAlert}
      />
    </div>
  );
}
