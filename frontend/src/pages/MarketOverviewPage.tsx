import { useQuery } from '@tanstack/react-query';
import { stocksApi } from '../api/stocks';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';
import { useState, useMemo } from 'react';
import { LegalDisclaimer } from '../components/LegalDisclaimer';
import MarketStatusBanner from '../components/MarketStatusBanner';

export default function MarketOverviewPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'market_cap' | 'price' | 'change_percent' | 'volume'>('market_cap');
  const [sortOrder] = useState<'asc' | 'desc'>('desc');
  const [filterBy, setFilterBy] = useState<'all' | 'gainers' | 'losers'>('all');
  const { data: quotes, isLoading, error, refetch } = useQuery({
    queryKey: ['market-overview-all'],
    queryFn: () => stocksApi.getMarketOverview(), // Fetch all companies with live data
    staleTime: 60 * 1000, // Consider fresh for 1 minute
    refetchInterval: 60 * 1000, // Auto-refresh every 1 minute (reduced from 15s)
    gcTime: 5 * 60 * 1000, // Keep in cache for 5 minutes
    refetchOnWindowFocus: false, // Don't refetch on window focus to reduce load
  });

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

  const formatVolume = (volume?: number) => {
    if (!volume) return 'N/A';

    const million = 1e6;
    const thousand = 1e3;

    if (volume >= million) {
      return `${(volume / million).toFixed(2)}M`;
    } else if (volume >= thousand) {
      return `${(volume / thousand).toFixed(2)}K`;
    }
    return volume.toString();
  };

  const getChangeColor = (change: number) => {
    if (change > 0) return 'text-green-400';
    if (change < 0) return 'text-red-400';
    return 'text-gray-400';
  };

  const getChangeBgColor = (change: number) => {
    if (change > 0) return 'bg-green-500/20';
    if (change < 0) return 'bg-red-500/20';
    return 'bg-gray-700/50';
  };

  // Filter and sort quotes
  const filteredAndSortedQuotes = useMemo(() => {
    if (!quotes) return [];

    let filtered = [...quotes];

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(
        (q) =>
          q.ticker.toLowerCase().includes(searchQuery.toLowerCase()) ||
          q.company_name?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply gainers/losers filter
    if (filterBy === 'gainers') {
      filtered = filtered.filter((q) => q.price_change_percent > 0);
    } else if (filterBy === 'losers') {
      filtered = filtered.filter((q) => q.price_change_percent < 0);
    }

    // Sort
    filtered.sort((a, b) => {
      let aValue: number, bValue: number;

      switch (sortBy) {
        case 'market_cap':
          aValue = a.market_cap || 0;
          bValue = b.market_cap || 0;
          break;
        case 'price':
          aValue = a.current_price;
          bValue = b.current_price;
          break;
        case 'change_percent':
          aValue = a.price_change_percent;
          bValue = b.price_change_percent;
          break;
        case 'volume':
          aValue = a.volume || 0;
          bValue = b.volume || 0;
          break;
        default:
          aValue = a.market_cap || 0;
          bValue = b.market_cap || 0;
      }

      return sortOrder === 'desc' ? bValue - aValue : aValue - bValue;
    });

    return filtered;
  }, [quotes, searchQuery, filterBy, sortBy, sortOrder]);

  // Handle loading state
  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  // Handle error state
  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-900/20 border border-red-500/30 rounded-xl p-6">
          <div className="flex items-center space-x-2 text-red-400">
            <AlertCircle className="h-5 w-5" />
            <p>Failed to load market data</p>
          </div>
          <button
            onClick={() => refetch()}
            className="mt-4 px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-300 rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Handle empty state
  if (!quotes || quotes.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-white/10 p-8 text-center">
          <p className="text-gray-400">No market data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <LegalDisclaimer />
      <MarketStatusBanner />

      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">Live Market Overview</h1>
            <p className="text-gray-400 mt-2">
              Real-time stock prices for all companies with insider trades
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
              <span>Auto-refresh 60s</span>
            </div>
            <button
              onClick={() => refetch()}
              className="px-4 py-2 border border-white/10 text-gray-300 rounded-lg hover:bg-white/5 transition-colors font-medium"
            >
              Refresh Now
            </button>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="mt-6 grid grid-cols-1 lg:grid-cols-4 gap-4">
          {/* Search */}
          <div className="lg:col-span-2">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Search by Ticker or Company
            </label>
            <input
              type="text"
              placeholder="Search TSLA, AAPL..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2.5 bg-black/50 border border-white/10 rounded-xl text-white placeholder:text-gray-600 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            />
          </div>

          {/* Sort By */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Sort By
            </label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="w-full px-4 py-2.5 bg-black/50 border border-white/10 rounded-xl text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            >
              <option value="market_cap">Market Cap</option>
              <option value="price">Price</option>
              <option value="change_percent">Change %</option>
              <option value="volume">Volume</option>
            </select>
          </div>

          {/* Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Filter
            </label>
            <select
              value={filterBy}
              onChange={(e) => setFilterBy(e.target.value as any)}
              className="w-full px-4 py-2.5 bg-black/50 border border-white/10 rounded-xl text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            >
              <option value="all">All Stocks</option>
              <option value="gainers">Gainers Only</option>
              <option value="losers">Losers Only</option>
            </select>
          </div>
        </div>

        {/* Statistics */}
        <div className="mt-4 flex items-center justify-between bg-blue-900/20 border border-blue-500/30 rounded-xl p-4">
          <div className="flex items-center space-x-4">
            <div className="text-center">
              <p className="text-sm text-blue-200">Total Companies</p>
              <p className="text-2xl font-bold text-white">{filteredAndSortedQuotes.length}</p>
            </div>
          </div>
          <div className="flex items-center space-x-4 text-right">
            <div>
              <div className="text-xs text-blue-300">
                Sorted by: {sortBy.replace('_', ' ').toUpperCase()}
              </div>
              <div className="text-xs text-blue-400/70 mt-1">
                Live data from Yahoo Finance
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-lg border border-white/10 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-white/5">
            <thead className="bg-black/30">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Symbol / Company
                </th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Change
                </th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Change %
                </th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Volume
                </th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Market Cap
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filteredAndSortedQuotes.map((quote) => (
                <tr key={quote.ticker} className="hover:bg-white/5 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="font-bold text-white text-lg">{quote.ticker}</div>
                      {quote.company_name && (
                        <div className="text-sm text-gray-500 truncate max-w-xs font-medium">
                          {quote.company_name}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="text-lg font-bold text-white font-mono">
                      {formatPrice(quote.current_price)}
                    </div>
                    <div className="text-xs text-gray-500">
                      prev {formatPrice(quote.previous_close)}
                    </div>
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-right font-semibold font-mono ${getChangeColor(quote.price_change)}`}>
                    {quote.price_change > 0 ? '+' : ''}{formatPrice(quote.price_change)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full ${getChangeBgColor(quote.price_change)}`}>
                      {quote.price_change > 0 ? (
                        <TrendingUp className={`h-3 w-3 ${getChangeColor(quote.price_change)}`} />
                      ) : quote.price_change < 0 ? (
                        <TrendingDown className={`h-3 w-3 ${getChangeColor(quote.price_change)}`} />
                      ) : null}
                      <span className={`font-bold text-sm ${getChangeColor(quote.price_change)}`}>
                        {quote.price_change > 0 ? '+' : ''}
                        {quote.price_change_percent.toFixed(2)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-300 font-mono">
                    {formatVolume(quote.volume)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-semibold text-gray-300 font-mono">
                    {formatMarketCap(quote.market_cap)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}