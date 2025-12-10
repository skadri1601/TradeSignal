import { useQuery } from '@tanstack/react-query';
import { stocksApi } from '../../api/stocks';
import LoadingSpinner from '../common/LoadingSpinner';
import { TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';
import { useState } from 'react';
import { Link } from 'react-router-dom';

export default function MarketSummaryCard() {
  const [showLosers, setShowLosers] = useState(false);

  const { data: quotes, isLoading, error, refetch } = useQuery({
    queryKey: ['market-summary'],
    queryFn: () => stocksApi.getMarketOverview(), // Fetch all companies
    staleTime: 60 * 1000, // Consider fresh for 1 minute
    refetchInterval: 60 * 1000, // Auto-refresh every 1 minute (reduced from 15s)
    refetchOnWindowFocus: false,
  });

  if (isLoading) {
    return (
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Market Summary</h2>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card bg-red-50 border border-red-200">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Market Summary</h2>
        <div className="flex items-center space-x-2 text-red-600">
          <AlertCircle className="h-5 w-5" />
          <p>Failed to load market data</p>
        </div>
        <button
          onClick={() => refetch()}
          className="mt-4 btn btn-secondary"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!quotes || quotes.length === 0) {
    return (
      <div className="card bg-gray-50">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Market Summary</h2>
        <div className="text-center py-8">
          <p className="text-gray-500">No market data available</p>
        </div>
      </div>
    );
  }

  // Sort by price change percent and get top 6
  const sortedQuotes = [...quotes].sort((a, b) =>
    showLosers
      ? a.price_change_percent - b.price_change_percent  // Ascending for losers (most negative first)
      : b.price_change_percent - a.price_change_percent  // Descending for gainers (most positive first)
  );
  const topQuotes = sortedQuotes.slice(0, 6);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const getChangeColor = (change: number) => {
    if (change > 0) return 'text-green-600';
    if (change < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const getChangeBgColor = (change: number) => {
    if (change > 0) return 'bg-green-100';
    if (change < 0) return 'bg-red-100';
    return 'bg-gray-100';
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Market Summary</h2>
          <p className="text-sm text-gray-500 mt-1">
            Top {showLosers ? 'losers' : 'gainers'} today
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1 text-xs text-gray-500">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span>Live</span>
          </div>
        </div>
      </div>

      {/* Toggle buttons */}
      <div className="flex space-x-2 mb-4">
        <button
          onClick={() => setShowLosers(false)}
          className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
            !showLosers
              ? 'bg-green-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          <div className="flex items-center justify-center space-x-2">
            <TrendingUp className="h-4 w-4" />
            <span>Top Gainers</span>
          </div>
        </button>
        <button
          onClick={() => setShowLosers(true)}
          className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
            showLosers
              ? 'bg-red-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          <div className="flex items-center justify-center space-x-2">
            <TrendingDown className="h-4 w-4" />
            <span>Top Losers</span>
          </div>
        </button>
      </div>

      {/* Stock list */}
      <div className="space-y-2">
        {topQuotes.map((quote) => (
          <div
            key={quote.ticker}
            className="flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center space-x-3 flex-1">
              <div>
                <div className="font-bold text-gray-900">{quote.ticker}</div>
                {quote.company_name && (
                  <div className="text-xs text-gray-500 truncate max-w-[200px]">
                    {quote.company_name}
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Current Price */}
              <div className="text-right">
                <div className="text-lg font-bold text-gray-900">
                  {formatPrice(quote.current_price)}
                </div>
                <div className="text-xs text-gray-500">
                  {formatPrice(quote.price_change)}
                </div>
              </div>

              {/* Price Change */}
              <div className={`flex items-center space-x-1 px-3 py-1 rounded-full ${getChangeBgColor(quote.price_change)}`}>
                {quote.price_change > 0 ? (
                  <TrendingUp className={`h-4 w-4 ${getChangeColor(quote.price_change)}`} />
                ) : quote.price_change < 0 ? (
                  <TrendingDown className={`h-4 w-4 ${getChangeColor(quote.price_change)}`} />
                ) : null}
                <span className={`font-semibold text-sm ${getChangeColor(quote.price_change)}`}>
                  {quote.price_change > 0 ? '+' : ''}
                  {quote.price_change_percent.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer with link to full market overview */}
      <div className="mt-4 pt-3 border-t border-gray-200">
        <Link
          to="/market-overview"
          className="text-sm text-blue-600 hover:text-blue-700 font-medium block text-center"
        >
          View Full Market Overview ({quotes.length} companies) →
        </Link>
      </div>
    </div>
  );
}
