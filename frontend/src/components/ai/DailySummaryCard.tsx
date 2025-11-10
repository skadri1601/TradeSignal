import { useQuery } from '@tanstack/react-query';
import { aiApi } from '../../api/ai';
import LoadingSpinner from '../common/LoadingSpinner';
import { formatCurrency } from '../../utils/formatters';

export default function DailySummaryCard() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['ai-daily-summary'],
    queryFn: () => aiApi.getDailySummary(),
    staleTime: 1000 * 60 * 5, // 5 minutes - more frequent updates
    refetchInterval: 1000 * 60 * 5, // Auto-refresh every 5 minutes
  });

  if (isLoading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card bg-red-50 border border-red-200">
        <p className="text-red-600">Failed to load market summary. Please try again.</p>
        <button
          onClick={() => refetch()}
          className="mt-4 btn btn-secondary"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!data || !data.company_summaries || data.company_summaries.length === 0) {
    return (
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
              d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No Recent Activity</h3>
          <p className="mt-1 text-sm text-gray-500">
            No insider trades detected in the last 7 days.
          </p>
        </div>
      </div>
    );
  }

  const getTrendColor = (buyCount: number, sellCount: number) => {
    if (buyCount > sellCount * 2) return 'text-green-600';
    if (sellCount > buyCount * 2) return 'text-red-600';
    return 'text-gray-600';
  };

  const getTrendIcon = (buyCount: number, sellCount: number) => {
    if (buyCount > sellCount * 2) {
      return (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
        </svg>
      );
    }
    if (sellCount > buyCount * 2) {
      return (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
        </svg>
      );
    }
    return (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9a1 1 0 000 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
      </svg>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Insider Trading News Feed</h2>
            <p className="text-sm text-gray-600 mt-1">
              {data.period} • Top {data.company_summaries.length} companies by trade value • {data.total_trades} total trades
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-1 text-xs text-gray-500">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span>Live</span>
            </div>
            <button
              onClick={() => refetch()}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Company News Items */}
      <div className="space-y-4">
        {data.company_summaries.map((company, index) => (
          <div
            key={company.ticker}
            className="card hover:shadow-lg transition-shadow border-l-4 border-l-blue-500"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className="flex items-center justify-center w-8 h-8 bg-blue-600 text-white rounded-full font-bold text-sm">
                  {index + 1}
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">
                    {company.ticker}
                    <span className="text-gray-600 font-normal text-sm ml-2">
                      {company.company_name}
                    </span>
                  </h3>
                  <p className="text-xs text-gray-500">
                    {new Date(company.latest_date).toLocaleDateString()} • {company.insider_count} insiders
                  </p>
                </div>
              </div>
              <div className={`flex items-center space-x-1 ${getTrendColor(company.buy_count, company.sell_count)}`}>
                {getTrendIcon(company.buy_count, company.sell_count)}
              </div>
            </div>

            {/* AI Summary */}
            <p className="text-gray-700 leading-relaxed mb-4">
              {company.summary}
            </p>

            {/* Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
              <div>
                <p className="text-xs text-gray-500">Total Value</p>
                <p className="text-sm font-semibold text-gray-900">
                  {formatCurrency(company.total_value)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Trades</p>
                <p className="text-sm font-semibold text-gray-900">
                  {company.trade_count}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Buys</p>
                <p className="text-sm font-semibold text-green-600">
                  {company.buy_count}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Sells</p>
                <p className="text-sm font-semibold text-red-600">
                  {company.sell_count}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="text-center">
        <p className="text-xs text-gray-500">
          Last updated {new Date(data.generated_at).toLocaleTimeString()} • Auto-refreshes every 5 minutes
        </p>
      </div>
    </div>
  );
}
