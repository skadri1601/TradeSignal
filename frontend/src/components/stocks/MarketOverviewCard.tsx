import { useQuery } from '@tanstack/react-query';
import { stocksApi } from '../../api/stocks';
import LoadingSpinner from '../common/LoadingSpinner';
import { TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';

export default function MarketOverviewCard() {
  const { data: quotes, isLoading, error, refetch } = useQuery({
    queryKey: ['market-overview'],
    queryFn: () => stocksApi.getMarketOverview(), // Fetch all companies with live data
    staleTime: 60 * 1000, // Consider fresh for 1 minute
    refetchInterval: 60 * 1000, // Auto-refresh every 1 minute (reduced from 15s)
    refetchOnWindowFocus: false,
  });

  if (isLoading) {
    return (
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Live Market Overview</h2>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card bg-red-50 border border-red-200">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Live Market Overview</h2>
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
        <h2 className="text-xl font-bold text-gray-900 mb-4">Live Market Overview</h2>
        <div className="text-center py-8">
          <p className="text-gray-500">No market data available</p>
        </div>
      </div>
    );
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const formatMarketCap = (marketCap?: number) => {
    if (!marketCap) return 'N/A';

    const trillion = 1e12;
    const billion = 1e9;

    if (marketCap >= trillion) {
      return `$${(marketCap / trillion).toFixed(2)}T`;
    } else if (marketCap >= billion) {
      return `$${(marketCap / billion).toFixed(2)}B`;
    }
    return `$${(marketCap / 1e6).toFixed(0)}M`;
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
          <h2 className="text-xl font-bold text-gray-900">Live Market Overview</h2>
          <p className="text-sm text-gray-500 mt-1">
            Real-time stock prices for all companies with insider trades
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1 text-xs text-gray-500">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span>Auto-refresh 15s</span>
          </div>
          <button
            onClick={() => refetch()}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="space-y-2">
        {quotes.map((quote) => (
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
              {/* Market Cap */}
              <div className="text-right hidden md:block">
                <div className="text-xs text-gray-500">Market Cap</div>
                <div className="text-sm font-semibold text-gray-700">
                  {formatMarketCap(quote.market_cap)}
                </div>
              </div>

              {/* Current Price */}
              <div className="text-right">
                <div className="text-lg font-bold text-gray-900">
                  {formatPrice(quote.current_price)}
                </div>
                <div className="text-xs text-gray-500">
                  was {formatPrice(quote.previous_close)}
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

      <div className="mt-4 pt-3 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          Showing {quotes.length} {quotes.length === 1 ? 'company' : 'companies'} • Live data from Yahoo Finance
        </p>
      </div>
    </div>
  );
}
