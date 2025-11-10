import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { aiApi, CompanyAnalysis as CompanyAnalysisType } from '../../api/ai';
import LoadingSpinner from '../common/LoadingSpinner';
import CompanyAutocomplete from '../common/CompanyAutocomplete';

export default function CompanyAnalysis() {
  const [ticker, setTicker] = useState('');
  const [daysBack, setDaysBack] = useState(30);
  const [analysis, setAnalysis] = useState<CompanyAnalysisType | null>(null);

  const analyzeMutation = useMutation({
    mutationFn: ({ ticker, daysBack }: { ticker: string; daysBack: number }) =>
      aiApi.analyzeCompany(ticker, daysBack),
    onSuccess: (data) => {
      setAnalysis(data);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticker.trim()) return;
    analyzeMutation.mutate({ ticker: ticker.toUpperCase(), daysBack });
  };

  const getSentimentColor = (sentiment: string) => {
    const s = sentiment.toLowerCase();
    if (s.includes('bullish')) return 'text-green-600';
    if (s.includes('bearish')) return 'text-red-600';
    return 'text-gray-600';
  };

  const getSentimentBg = (sentiment: string) => {
    const s = sentiment.toLowerCase();
    if (s.includes('bullish')) return 'bg-green-100';
    if (s.includes('bearish')) return 'bg-red-100';
    return 'bg-gray-100';
  };

  return (
    <div className="space-y-6">
      {/* Search Form */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Analyze Company Insider Trading
        </h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <label htmlFor="ticker" className="block text-sm font-medium text-gray-700 mb-1">
                Ticker Symbol
              </label>
              <CompanyAutocomplete
                value={ticker}
                onChange={(value) => setTicker(value.toUpperCase())}
                placeholder="e.g., NVDA, TSLA, AAPL"
                disabled={analyzeMutation.isPending}
              />
            </div>
            <div>
              <label htmlFor="daysBack" className="block text-sm font-medium text-gray-700 mb-1">
                Days to Analyze
              </label>
              <select
                id="daysBack"
                value={daysBack}
                onChange={(e) => setDaysBack(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={analyzeMutation.isPending}
              >
                <option value={7}>Last 7 days</option>
                <option value={14}>Last 14 days</option>
                <option value={30}>Last 30 days</option>
                <option value={60}>Last 60 days</option>
                <option value={90}>Last 90 days</option>
                <option value={180}>Last 6 months</option>
                <option value={365}>Last year</option>
              </select>
            </div>
          </div>
          <button
            type="submit"
            disabled={!ticker.trim() || analyzeMutation.isPending}
            className="btn btn-primary w-full md:w-auto"
          >
            {analyzeMutation.isPending ? 'Analyzing...' : 'Analyze'}
          </button>
        </form>
      </div>

      {/* Loading State */}
      {analyzeMutation.isPending && (
        <div className="card flex items-center justify-center py-12">
          <div className="text-center">
            <LoadingSpinner />
            <p className="text-gray-600 mt-4">
              Analyzing {ticker} insider trading patterns...
            </p>
          </div>
        </div>
      )}

      {/* Error State */}
      {analyzeMutation.isError && (
        <div className="card bg-red-50 border border-red-200">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Analysis Failed</h3>
              <p className="text-sm text-red-700 mt-1">
                {analyzeMutation.error instanceof Error
                  ? analyzeMutation.error.message
                  : 'Failed to analyze company. Please try again.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {analysis && !analyzeMutation.isPending && (
        <div className="space-y-6">
          {/* Header Card */}
          <div className="card">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {analysis.ticker} - {analysis.company_name}
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Analysis of {analysis.total_trades} trades over {analysis.days_analyzed} days
                </p>
              </div>
              <div className="text-right">
                <span
                  className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getSentimentBg(
                    analysis.sentiment
                  )} ${getSentimentColor(analysis.sentiment)}`}
                >
                  {analysis.sentiment}
                </span>
              </div>
            </div>
          </div>

          {/* AI Analysis */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Analysis</h3>
            <div className="prose max-w-none">
              <p className="text-gray-700 whitespace-pre-wrap">{analysis.analysis}</p>
            </div>
          </div>

          {/* Key Insights */}
          {analysis.insights && analysis.insights.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Insights</h3>
              <ul className="space-y-3">
                {analysis.insights.map((insight, index) => (
                  <li key={index} className="flex items-start">
                    <svg
                      className="h-5 w-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                    <span className="text-gray-700">{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Info Footer */}
          <div className="text-center">
            <p className="text-xs text-gray-500">
              Analysis based on {analysis.total_trades} insider trades over the last {analysis.days_analyzed} days
            </p>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!analysis && !analyzeMutation.isPending && !analyzeMutation.isError && (
        <div className="card bg-gray-50">
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No Analysis Yet</h3>
            <p className="mt-1 text-sm text-gray-500">
              Enter a ticker symbol above to get AI-powered analysis of insider trading patterns.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
