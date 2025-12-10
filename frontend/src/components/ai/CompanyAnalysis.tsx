import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { patternsApi, PatternAnalysis } from '../../api/patterns';
import AISkeleton from '../common/AISkeleton';
import CompanyAutocomplete from '../common/CompanyAutocomplete';
import { BarChart2, TrendingUp, AlertCircle, TrendingDown, MinusCircle } from 'lucide-react';

export default function CompanyAnalysis() {
  const [ticker, setTicker] = useState('');
  const [daysBack, setDaysBack] = useState(30);
  const [analysis, setAnalysis] = useState<PatternAnalysis | null>(null);

  const analyzeMutation = useMutation({
    mutationFn: ({ ticker, daysBack }: { ticker: string; daysBack: number }) =>
      patternsApi.analyzeCompany(ticker, daysBack),
    onSuccess: (data) => {
      setAnalysis(data);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticker.trim()) return;
    analyzeMutation.mutate({ ticker: ticker.toUpperCase(), daysBack });
  };

  const getTrendColor = (trend: string) => {
    if (trend === 'BULLISH') return 'text-green-400';
    if (trend === 'BEARISH') return 'text-red-400';
    return 'text-gray-400';
  };

  const getTrendIcon = (trend: string) => {
    if (trend === 'BULLISH') return <TrendingUp className="w-5 h-5 text-green-400" />;
    if (trend === 'BEARISH') return <TrendingDown className="w-5 h-5 text-red-400" />;
    return <MinusCircle className="w-5 h-5 text-gray-400" />;
  };

  return (
    <div className="space-y-6">
      {/* Search Form */}
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-lg border border-white/10 p-6">
        <div className="flex items-center space-x-2 mb-4">
          <BarChart2 className="w-5 h-5 text-purple-400" />
          <h3 className="text-lg font-bold text-white">
            Analyze Company Insider Trading
          </h3>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <label htmlFor="ticker" className="block text-sm font-medium text-gray-300 mb-2">
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
              <label htmlFor="daysBack" className="block text-sm font-medium text-gray-300 mb-2">
                Days to Analyze
              </label>
              <select
                id="daysBack"
                value={daysBack}
                onChange={(e) => setDaysBack(Number(e.target.value))}
                className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-xl text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
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
            className="px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-500 transition-colors disabled:opacity-50 font-semibold shadow-lg shadow-purple-500/20 w-full md:w-auto"
          >
            {analyzeMutation.isPending ? 'Analyzing...' : 'Analyze'}
          </button>
        </form>
      </div>

      {/* Loading State */}
      {analyzeMutation.isPending && (
        <div className="space-y-6">
          <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
            <AISkeleton message={`AI is analyzing ${ticker} insider trading patterns...`} />
          </div>
          <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10 p-6 space-y-4">
             <div className="h-8 bg-white/10 rounded w-1/3 animate-pulse"></div>
             <div className="h-4 bg-white/10 rounded w-1/2 animate-pulse"></div>
             <div className="grid grid-cols-2 gap-4 pt-4">
                <div className="h-24 bg-white/5 rounded-xl animate-pulse"></div>
                <div className="h-24 bg-white/5 rounded-xl animate-pulse"></div>
             </div>
          </div>
        </div>
      )}

      {/* Error State */}
      {analyzeMutation.isError && (
        <div className="bg-red-900/20 border border-red-500/30 rounded-xl p-6 flex items-start">
          <AlertCircle className="h-5 w-5 text-red-400 mt-0.5 mr-3 flex-shrink-0" />
          <div>
            <h3 className="text-sm font-medium text-red-300">Analysis Failed</h3>
            <p className="text-sm text-red-400/80 mt-1">
              {analyzeMutation.error instanceof Error
                ? analyzeMutation.error.message
                : 'Failed to analyze company. Please try again.'}
            </p>
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {analysis && !analyzeMutation.isPending && (
        <div className="space-y-6">
          {/* Header Card */}
          <div className="bg-gradient-to-r from-purple-900/40 to-blue-900/40 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h2 className="text-2xl font-bold text-white">
                  {analysis.ticker} - {analysis.company_name}
                </h2>
                <p className="text-sm text-gray-300 mt-1">
                  Analysis over {analysis.days_analyzed} days • {analysis.total_trades} trades analyzed
                </p>
              </div>
              <div className="flex items-center gap-3 bg-black/20 p-3 rounded-xl border border-white/5">
                <div className="text-right">
                  <p className="text-xs text-gray-400 uppercase font-bold">Trend</p>
                  <p className={`text-lg font-bold ${getTrendColor(analysis.trend)}`}>{analysis.trend}</p>
                </div>
                {getTrendIcon(analysis.trend)}
              </div>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
             <div className="bg-gray-900/50 backdrop-blur-sm p-4 rounded-xl border border-white/10">
               <p className="text-xs text-gray-500 uppercase font-bold mb-1">Confidence</p>
               <p className="text-xl font-mono text-white">{(analysis.confidence * 100).toFixed(0)}%</p>
               <div className="w-full bg-gray-700 h-1.5 rounded-full mt-2 overflow-hidden">
                 <div className="h-full bg-purple-500" style={{ width: `${analysis.confidence * 100}%` }} />
               </div>
             </div>
             <div className="bg-gray-900/50 backdrop-blur-sm p-4 rounded-xl border border-white/10">
               <p className="text-xs text-gray-500 uppercase font-bold mb-1">Buy Ratio</p>
               <p className="text-xl font-mono text-green-400">{(analysis.buy_ratio * 100).toFixed(1)}%</p>
             </div>
             <div className="bg-gray-900/50 backdrop-blur-sm p-4 rounded-xl border border-white/10">
               <p className="text-xs text-gray-500 uppercase font-bold mb-1">Sell Ratio</p>
               <p className="text-xl font-mono text-red-400">{(analysis.sell_ratio * 100).toFixed(1)}%</p>
             </div>
             <div className="bg-gray-900/50 backdrop-blur-sm p-4 rounded-xl border border-white/10">
               <p className="text-xs text-gray-500 uppercase font-bold mb-1">Insiders</p>
               <p className="text-xl font-mono text-white">{analysis.active_insiders}</p>
             </div>
          </div>

          {/* Main Pattern & Prediction */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Pattern Card */}
            <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10 p-6 md:col-span-1">
              <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Detected Pattern</h3>
              <div className="bg-white/5 rounded-xl p-4 border border-white/5">
                <div className="flex items-center gap-2 mb-2">
                   <BarChart2 className="w-5 h-5 text-purple-400" />
                   <h4 className="font-bold text-white text-lg">{analysis.pattern.replace('_', ' ')}</h4>
                </div>
                <div className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-bold border ${
                  analysis.risk_level === 'HIGH' ? 'bg-red-500/20 text-red-300 border-red-500/30' :
                  analysis.risk_level === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30' :
                  'bg-green-500/20 text-green-300 border-green-500/30'
                }`}>
                  {analysis.risk_level} RISK
                </div>
              </div>
              <div className="mt-4 bg-white/5 rounded-xl p-4 border border-white/5">
                 <p className="text-xs text-gray-500 uppercase font-bold mb-1">Recommendation</p>
                 <p className={`text-xl font-bold ${
                   analysis.recommendation.includes('BUY') ? 'text-green-400' : 
                   analysis.recommendation.includes('SELL') ? 'text-red-400' : 'text-gray-300'
                 }`}>
                   {analysis.recommendation.replace('_', ' ')}
                 </p>
              </div>
            </div>

            {/* AI Prediction */}
            <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10 p-6 md:col-span-2 relative overflow-hidden">
               <div className="absolute top-0 right-0 w-64 h-64 bg-purple-600/10 blur-[60px] rounded-full pointer-events-none -z-10" />
               <h3 className="text-sm font-bold text-purple-300 uppercase tracking-wider mb-4 flex items-center gap-2">
                 <span className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" />
                 AI Market Prediction
               </h3>
               <div className="bg-black/20 rounded-xl p-6 border border-white/5">
                 <p className="text-lg text-gray-200 leading-relaxed font-light">
                   {analysis.prediction || "No prediction generated."}
                 </p>
               </div>
            </div>
          </div>

          {/* Info Footer */}
          <div className="text-center pb-6">
            <p className="text-xs text-gray-600">
              Pattern analysis based on SEC Form 4 data from the last {analysis.days_analyzed} days
            </p>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!analysis && !analyzeMutation.isPending && !analyzeMutation.isError && (
        <div className="bg-gray-900/30 border border-white/10 rounded-2xl p-12 text-center">
          <BarChart2 className="mx-auto h-12 w-12 text-gray-600 mb-4" />
          <h3 className="text-lg font-medium text-white">No Analysis Yet</h3>
          <p className="mt-2 text-sm text-gray-400">
            Enter a ticker symbol above to generate a real-time AI analysis.
          </p>
        </div>
      )}
    </div>
  );
}