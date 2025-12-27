import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { aiApi, type CompanyAnalysis, type PricePredictionResponse } from '../../api/ai';
import AISkeleton from '../common/AISkeleton';
import CompanyAutocomplete from '../common/CompanyAutocomplete';
import PricePredictionCard from './PricePredictionCard';
import { BarChart2, TrendingUp, AlertCircle, TrendingDown, MinusCircle, Sparkles } from 'lucide-react';

interface CompanyAnalysisProcessingResponse {
  status: 'processing';
  message: string;
}

type CompanyAnalysisResponse =
  | CompanyAnalysis
  | CompanyAnalysisProcessingResponse;

export default function CompanyAnalysis() {
  const [ticker, setTicker] = useState('');
  const [daysBack, setDaysBack] = useState(30);
  const [analysis, setAnalysis] = useState<CompanyAnalysis & Partial<PricePredictionResponse> | null>(null);
  // Backend async processing state (separate from React Query's isPending)
  // isPending: Frontend waiting for API response
  // isBackendProcessing: Backend accepted request but still processing (queued job)
  const [isBackendProcessing, setIsBackendProcessing] = useState(false);
  const [backendProcessingMessage, setBackendProcessingMessage] = useState<string | null>(null);

  const analyzeMutation = useMutation({
    mutationFn: ({ ticker, daysBack }: { ticker: string; daysBack: number }) =>
      aiApi.analyzeCompany(ticker, daysBack),
    onSuccess: (data: CompanyAnalysisResponse) => {
      // Check if API returned processing status (if backend still does async queueing)
      if ('status' in data && data.status === 'processing') {
        setIsBackendProcessing(true);
        setBackendProcessingMessage(data.message);
        setAnalysis(null);
      } else {
        setIsBackendProcessing(false);
        setBackendProcessingMessage(null);
        setAnalysis(data as CompanyAnalysis & Partial<PricePredictionResponse>);
      }
    },
    onError: (error: unknown) => {
      setIsBackendProcessing(false);
      setBackendProcessingMessage(null);
      console.error('Company analysis failed:', error);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticker.trim()) return;
    setIsBackendProcessing(false);
    setBackendProcessingMessage(null);
    setAnalysis(null);
    analyzeMutation.mutate({ ticker: ticker.toUpperCase(), daysBack });
  };

  const getTrendColor = (sentiment: string) => {
    if (sentiment === 'BULLISH') return 'text-green-400';
    if (sentiment === 'BEARISH') return 'text-red-400';
    return 'text-gray-400';
  };

  const getTrendIcon = (sentiment: string) => {
    if (sentiment === 'BULLISH') return <TrendingUp className="w-5 h-5 text-green-400" />;
    if (sentiment === 'BEARISH') return <TrendingDown className="w-5 h-5 text-red-400" />;
    return <MinusCircle className="w-5 h-5 text-gray-400" />;
  };

  return (
    <div className="space-y-6">
      {/* Search Form */}
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-lg border border-white/10 p-6 relative z-20">
        <div className="flex items-center space-x-2 mb-4">
          <BarChart2 className="w-5 h-5 text-purple-400" />
          <h3 className="text-lg font-bold text-white">
            LUNA Forensic Analysis
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
                <option value={30}>Last 30 days</option>
                <option value={90}>Last 90 days</option>
              </select>
            </div>
          </div>
          <button
            type="submit"
            disabled={!ticker.trim() || analyzeMutation.isPending}
            className="px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-500 transition-colors disabled:opacity-50 font-semibold shadow-lg shadow-purple-500/20 w-full md:w-auto"
          >
            {analyzeMutation.isPending ? 'Running Forensic Scan...' : 'Run LUNA Analysis'}
          </button>
        </form>
      </div>

      {/* Loading State */}
      {analyzeMutation.isPending && (
        <div className="space-y-6 mt-6 relative z-0">
          <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
            <AISkeleton message={`LUNA AI is synthesizing Earnings, Technicals, and Insider data for ${ticker}...`} />
          </div>
        </div>
      )}

      {/* Processing State */}
      {isBackendProcessing && !analyzeMutation.isPending && (
        <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-6 flex items-start mt-6 relative z-0">
          <BarChart2 className="h-5 w-5 text-blue-400 mt-0.5 mr-3 flex-shrink-0 animate-pulse" />
          <div>
            <h3 className="text-sm font-medium text-blue-300">Analysis Queued</h3>
            <p className="text-sm text-blue-400/80 mt-1">
              {backendProcessingMessage || 'Analysis is being processed. Please check back shortly.'}
            </p>
          </div>
        </div>
      )}

      {/* Error State */}
      {analyzeMutation.isError && (
        <div className="bg-red-900/20 border border-red-500/30 rounded-xl p-6 flex items-start mt-6 relative z-0">
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
      {analysis && !analyzeMutation.isPending && !isBackendProcessing && (
        <div className="space-y-6 mt-6 relative z-0">
          {/* Header Card */}
          <div className="bg-gradient-to-r from-purple-900/40 to-blue-900/40 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h2 className="text-2xl font-bold text-white">
                    {analysis.ticker} - {analysis.company_name}
                  </h2>
                  <span className="px-2 py-0.5 bg-purple-500/20 border border-purple-500/30 rounded text-[10px] font-bold text-purple-300 uppercase tracking-widest">
                    LUNA Forensic Report
                  </span>
                </div>
                <p className="text-sm text-gray-300">
                  Analysis over {analysis.days_analyzed ?? 0} days • Powered by TradeSignal AI
                </p>
              </div>
              <div className="flex items-center gap-3 bg-black/20 p-3 rounded-xl border border-white/5">
                <div className="text-right">
                  <p className="text-xs text-gray-400 uppercase font-bold">Sentiment</p>
                  <p className={`text-lg font-bold ${getTrendColor(analysis.sentiment)}`}>{analysis.sentiment}</p>
                </div>
                {getTrendIcon(analysis.sentiment)}
              </div>
            </div>
          </div>

          {/* Main Analysis Text */}
          <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Forensic Summary</h3>
            <p className="text-gray-300 leading-relaxed text-lg">
              {analysis.analysis}
            </p>
            
            {/* Insights List */}
            {analysis.insights && analysis.insights.length > 0 && (
              <div className="mt-6 space-y-2">
                {analysis.insights.map((insight: string, idx: number) => (
                  <div key={`insight-${idx}-${insight.slice(0, 20)}`} className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-purple-500 mt-2 flex-shrink-0" />
                    <p className="text-gray-400 text-sm">{insight}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Integrated Price Prediction (Now Automatic) */}
          {analysis.price_predictions && analysis.price_predictions.length > 0 && (
            <div className="space-y-4">
               <h3 className="text-sm font-bold text-purple-300 uppercase tracking-wider flex items-center gap-2">
                 <Sparkles className="w-4 h-4" /> LUNA Price Targets
               </h3>
               <PricePredictionCard
                ticker={analysis.ticker}
                predictions={analysis.price_predictions}
                recommendation={analysis.recommendation || analysis.sentiment}
                riskLevel={analysis.risk_level || 'MEDIUM'}
                disclaimer={analysis.disclaimer}
              />
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!analysis && !analyzeMutation.isPending && !analyzeMutation.isError && !isBackendProcessing && (
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