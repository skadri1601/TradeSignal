import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { aiApi } from '../api/ai';
import LoadingSpinner from '../components/common/LoadingSpinner';
import AIChat from '../components/ai/AIChat';
import CompanyAnalysis from '../components/ai/CompanyAnalysis';
import TradingSignals from '../components/ai/TradingSignals';
import DailySummaryCard from '../components/ai/DailySummaryCard';
import { LegalDisclaimer } from '../components/LegalDisclaimer';

export default function AIInsightsPage() {
  const [activeTab, setActiveTab] = useState<'chat' | 'analysis' | 'signals' | 'summary'>('summary');

  // Check AI status
  const { data: aiStatus, isLoading: statusLoading } = useQuery({
    queryKey: ['ai-status'],
    queryFn: () => aiApi.getStatus(),
    staleTime: 5 * 60 * 1000, // Consider fresh for 5 minutes
    refetchInterval: 5 * 60 * 1000, // Check every 5 minutes (reduced from 30s)
    refetchOnWindowFocus: false, // Don't refetch on window focus
  });

  if (statusLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner />
      </div>
    );
  }

  // AI not available
  if (!aiStatus?.available) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-xl p-6">
          <h1 className="text-2xl font-bold text-yellow-400 mb-4">
            AI Insights Not Available
          </h1>
          <div className="space-y-4">
            <p className="text-gray-300">
              AI-powered insights are currently unavailable. This feature requires:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-400">
              <li>
                <strong>Gemini API Key</strong> (recommended - free 1500 requests/day)
                <br />
                <a
                  href="https://makersuite.google.com/app/apikey"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:text-blue-300 hover:underline ml-6"
                >
                  Get free Gemini API key →
                </a>
              </li>
              <li>
                <strong>Or OpenAI API Key</strong> (paid)
                <br />
                <a
                  href="https://platform.openai.com/api-keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:text-blue-300 hover:underline ml-6"
                >
                  Get OpenAI API key →
                </a>
              </li>
            </ul>

            <div className="bg-black/30 rounded-lg p-4 mt-4 border border-white/10">
              <h3 className="font-semibold text-white mb-2">Current Status:</h3>
              <div className="space-y-1 text-sm text-gray-400">
                <p>
                  <span className="font-medium text-gray-300">Enabled:</span>{' '}
                  <span className={aiStatus?.enabled ? 'text-green-400' : 'text-red-400'}>
                    {aiStatus?.enabled ? 'Yes' : 'No'}
                  </span>
                </p>
                <p>
                  <span className="font-medium text-gray-300">Primary Provider:</span> {aiStatus?.providers.primary}
                </p>
                <p>
                  <span className="font-medium text-gray-300">Gemini:</span>{' '}
                  <span className={aiStatus?.providers.gemini.configured ? 'text-green-400' : 'text-gray-500'}>
                    {aiStatus?.providers.gemini.configured ? 'Configured' : 'Not configured'}
                  </span>
                </p>
                <p>
                  <span className="font-medium text-gray-300">OpenAI:</span>{' '}
                  <span className={aiStatus?.providers.openai.configured ? 'text-green-400' : 'text-gray-500'}>
                    {aiStatus?.providers.openai.configured ? 'Configured' : 'Not configured'}
                  </span>
                </p>
              </div>
            </div>

            <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4 mt-4">
              <h3 className="font-semibold text-blue-300 mb-2">Setup Instructions:</h3>
              <ol className="list-decimal list-inside space-y-1 text-sm text-blue-200">
                <li>Get a free Gemini API key from the link above</li>
                <li>Add <code className="bg-black/50 px-1.5 py-0.5 rounded text-blue-100">GEMINI_API_KEY=your-key</code> to backend/.env</li>
                <li>Set <code className="bg-black/50 px-1.5 py-0.5 rounded text-blue-100">ENABLE_AI_INSIGHTS=true</code> in backend/.env</li>
                <li>Restart the backend: <code className="bg-black/50 px-1.5 py-0.5 rounded text-blue-100">docker-compose restart backend</code></li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // AI available - show interface
  return (
    <div className="space-y-6">
      <LegalDisclaimer />

      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">AI-Powered Insights</h1>
          <p className="mt-2 text-gray-400">
            Advanced analysis powered by {aiStatus.active_provider === 'gemini' ? 'Google Gemini 2.0 Flash' : 'OpenAI GPT-4o-mini'}
          </p>
        </div>
        <div className="flex items-center space-x-2 text-sm">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(34,197,94,0.5)]" />
          <span className="text-green-400 font-medium">AI Active</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-white/10">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'summary', label: 'Daily Summary' },
            { id: 'signals', label: 'Trading Signals' },
            { id: 'analysis', label: 'Company Analysis' },
            { id: 'chat', label: 'AI Chat' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm transition-all duration-300
                ${
                  activeTab === tab.id
                    ? 'border-purple-500 text-purple-400'
                    : 'border-transparent text-gray-500 hover:text-gray-300 hover:border-white/20'
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'summary' && <DailySummaryCard />}
        {activeTab === 'signals' && <TradingSignals />}
        {activeTab === 'analysis' && <CompanyAnalysis />}
        {activeTab === 'chat' && <AIChat />}
      </div>
    </div>
  );
}