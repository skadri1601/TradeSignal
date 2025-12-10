import { useQuery } from '@tanstack/react-query';
import { aiApi } from '../../api/ai';
import Skeleton from '../common/Skeleton';
import AISkeleton from '../common/AISkeleton';
import { formatCurrency } from '../../utils/formatters';
import { Newspaper, TrendingUp, TrendingDown, RefreshCw, AlertCircle, Clock } from 'lucide-react';

export default function DailySummaryCard() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['ai-daily-summary'],
    queryFn: () => aiApi.getDailySummary(),
    staleTime: 1000 * 60 * 5, // 5 minutes - more frequent updates
    refetchInterval: 1000 * 60 * 5, // Auto-refresh every 5 minutes
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
          <div className="flex items-start justify-between">
            <div className="w-full">
              <Skeleton width="40%" height="2rem" className="mb-4" />
              <AISkeleton message="AI is analyzing daily market activity..." />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    return (
      <div className="bg-red-900/20 border border-red-500/30 rounded-2xl p-6 flex items-start space-x-4">
        <AlertCircle className="h-6 w-6 text-red-400 flex-shrink-0" />
        <div className="flex-1">
          <h3 className="text-lg font-medium text-red-300">Failed to load daily summary</h3>
          <p className="text-sm text-red-400/80 mt-1">{errorMessage}</p>
          <button
            onClick={() => refetch()}
            className="mt-4 px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-300 rounded-lg transition-colors text-sm font-medium border border-red-500/30"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data || !data.company_summaries || data.company_summaries.length === 0) {
    return (
      <div className="bg-gray-900/30 border border-white/10 rounded-2xl p-12 text-center">
        <Newspaper className="mx-auto h-12 w-12 text-gray-600 mb-4" />
        <h3 className="mt-2 text-lg font-medium text-white">No Recent Activity</h3>
        <p className="mt-1 text-sm text-gray-400">
          No significant insider trades detected in the last 7 days.
        </p>
      </div>
    );
  }

  const getTrendColor = (buyCount: number, sellCount: number) => {
    if (buyCount > sellCount * 2) return 'text-green-400';
    if (sellCount > buyCount * 2) return 'text-red-400';
    return 'text-gray-400';
  };

  const getTrendIcon = (buyCount: number, sellCount: number) => {
    if (buyCount > sellCount * 2) return <TrendingUp className="w-5 h-5" />;
    if (sellCount > buyCount * 2) return <TrendingDown className="w-5 h-5" />;
    return <div className="w-2 h-2 rounded-full bg-gray-500" />;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-900/40 to-indigo-900/40 backdrop-blur-sm rounded-2xl border border-white/10 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <Newspaper className="w-6 h-6 text-blue-400" />
            </div>
            <h2 className="text-2xl font-bold text-white">Insider Trading News Feed</h2>
          </div>
          <p className="text-sm text-gray-300">
            Top {data.company_summaries.length} companies by trade value • {data.total_trades} total trades analyzed
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <span className="flex items-center text-xs font-medium text-green-400 bg-green-500/10 px-3 py-1.5 rounded-full border border-green-500/20">
            <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse mr-2" />
            LIVE MARKET DATA
          </span>
          <button
            onClick={() => refetch()}
            className="p-2 text-gray-400 hover:text-white bg-white/5 rounded-lg hover:bg-white/10 transition-colors border border-white/5"
            title="Refresh"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* AI Overview (if available) */}
      {data.ai_overview && (
        <div className="bg-purple-900/20 border border-purple-500/30 rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 blur-[40px] rounded-full -z-10" />
          <h3 className="text-sm font-bold text-purple-300 uppercase tracking-wider mb-3">AI Market Analysis</h3>
          <p className="text-white leading-relaxed text-lg font-light">
            {data.ai_overview}
          </p>
        </div>
      )}

      {/* Company News Items */}
      <div className="grid gap-4">
        {data.company_summaries.map((company, index) => (
          <div
            key={company.ticker}
            className="group bg-gray-900/50 backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:border-blue-500/30 transition-all hover:bg-gray-900/80"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-4">
                <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-white/5 text-gray-400 font-mono text-sm font-bold border border-white/5">
                  {index + 1}
                </span>
                <div>
                  <h3 className="text-xl font-bold text-white group-hover:text-blue-400 transition-colors">
                    {company.ticker}
                  </h3>
                  <p className="text-xs text-gray-500 font-medium">{company.company_name}</p>
                </div>
              </div>
              <div className={`flex items-center gap-2 px-3 py-1 rounded-full bg-black/30 border border-white/5 ${getTrendColor(company.buy_count, company.sell_count)}`}>
                {getTrendIcon(company.buy_count, company.sell_count)}
                <span className="text-xs font-bold uppercase">
                  {company.buy_count > company.sell_count ? 'Buying' : 'Selling'}
                </span>
              </div>
            </div>

            <p className="text-gray-300 leading-relaxed mb-6 pl-12 border-l-2 border-white/5">
              {company.summary}
            </p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-black/20 rounded-xl p-4 ml-12">
              <div>
                <p className="text-[10px] uppercase tracking-wider text-gray-500 font-bold mb-1">Volume</p>
                <p className="text-white font-mono">{formatCurrency(company.total_value)}</p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-gray-500 font-bold mb-1">Trades</p>
                <p className="text-white font-mono">{company.trade_count}</p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-gray-500 font-bold mb-1">Insiders</p>
                <p className="text-white font-mono">{company.insider_count}</p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-gray-500 font-bold mb-1">Latest</p>
                <div className="flex items-center text-white font-mono text-xs mt-0.5">
                  <Clock className="w-3 h-3 mr-1.5 text-gray-600" />
                  {new Date(company.latest_date).toLocaleDateString()}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="text-center pt-8 border-t border-white/5">
        <p className="text-xs text-gray-600">
          AI analysis based on SEC Form 4 filings processed in real-time.
        </p>
      </div>
    </div>
  );
}