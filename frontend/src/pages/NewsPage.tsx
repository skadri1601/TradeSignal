/**
 * News Page - Market News Articles
 */

import { useQuery } from '@tanstack/react-query';
import { newsApi } from '../api/news';
import { Newspaper, RefreshCw, ExternalLink, Search, TrendingUp, Globe } from 'lucide-react';
import { useState } from 'react';
import type { NewsArticle } from '../types';

export default function NewsPage() {
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [searchTicker, setSearchTicker] = useState<string>('');
  const [category, setCategory] = useState<'latest' | 'general' | 'company'>('latest');

  // Fetch news based on category
  const { data: newsData, isLoading, error: newsError, refetch } = useQuery({
    queryKey: ['news', category, searchTicker],
    queryFn: async () => {
      try {
        let response;
        if (category === 'company' && searchTicker) {
          response = await newsApi.getCompanyNews(searchTicker.toUpperCase(), 50);
        } else if (category === 'general') {
          response = await newsApi.getGeneralNews(50);
        } else {
          response = await newsApi.getLatestNews(50);
        }
        setLastUpdated(new Date());
        return response;
      } catch (error: any) {
        console.error('Error fetching news:', error);
        setLastUpdated(new Date());
        return { articles: [], total: 0, limit: 50 };
      }
    },
    refetchInterval: 300000, // Auto-refresh every 5 minutes
    staleTime: 240000, // Consider data stale after 4 minutes
    refetchOnWindowFocus: true,
    retry: 1,
    enabled: !(category === 'company' && !searchTicker), // Don't fetch if company category but no ticker
  });

  const articles = newsData?.articles || [];
  const uniqueSources = new Set(articles.map((a: NewsArticle) => a.source)).size;

  const handleSearch = () => {
    if (category === 'company' && searchTicker) {
      refetch();
    }
  };

  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp * 1000);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) {
      return 'Just now';
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <Newspaper className="w-8 h-8 mr-3 text-blue-600" />
            Market News
          </h1>
          <p className="text-gray-600 mt-2">
            Latest market news articles and financial updates
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Last updated: {lastUpdated.toLocaleTimeString()} • Auto-refreshes every 5 minutes
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isLoading}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Total Articles</p>
              <p className="text-3xl font-bold mt-1">{articles.length}</p>
            </div>
            <Newspaper className="w-10 h-10 text-blue-200" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">News Sources</p>
              <p className="text-3xl font-bold mt-1">{uniqueSources}</p>
            </div>
            <Globe className="w-10 h-10 text-green-200" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Last 7 Days</p>
              <p className="text-3xl font-bold mt-1">{articles.length}</p>
            </div>
            <TrendingUp className="w-10 h-10 text-purple-200" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <div className="flex space-x-2">
              <button
                onClick={() => setCategory('latest')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  category === 'latest'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Latest
              </button>
              <button
                onClick={() => setCategory('general')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  category === 'general'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                General
              </button>
              <button
                onClick={() => setCategory('company')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  category === 'company'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Company
              </button>
            </div>
          </div>

          {category === 'company' && (
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">Search by Ticker</label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={searchTicker}
                  onChange={(e) => setSearchTicker(e.target.value.toUpperCase())}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="e.g., AAPL, MSFT"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  onClick={handleSearch}
                  disabled={!searchTicker || isLoading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
                >
                  <Search className="w-4 h-4" />
                  <span>Search</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* News Articles */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">
            {category === 'company' && searchTicker
              ? `News for ${searchTicker}`
              : category === 'general'
              ? 'General Market News'
              : 'Latest News'}
          </h2>
          <span className="text-sm text-gray-500">{articles.length} articles</span>
        </div>

        {isLoading ? (
          <div className="text-center py-12 text-gray-500">Loading news articles...</div>
        ) : newsError ? (
          <div className="text-center py-12">
            <div className="text-red-600 mb-2">Failed to load news</div>
            <p className="text-sm text-gray-500 mb-4">
              {newsError instanceof Error ? newsError.message : 'An error occurred while loading news'}
            </p>
            <button
              onClick={() => refetch()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        ) : category === 'company' && !searchTicker ? (
          <div className="text-center py-12">
            <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">Enter a ticker symbol to search for company news</p>
          </div>
        ) : articles.length > 0 ? (
          <div className="space-y-4">
            {articles.map((article: NewsArticle) => (
              <div
                key={article.id}
                className="flex items-start space-x-4 p-4 hover:bg-gray-50 rounded-xl transition-colors border border-gray-100"
              >
                {article.image && (
                  <img
                    src={article.image}
                    alt={article.headline}
                    className="w-24 h-24 object-cover rounded-lg flex-shrink-0"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                )}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 text-lg hover:text-blue-600 cursor-pointer">
                        <a
                          href={article.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:underline"
                        >
                          {article.headline}
                        </a>
                      </h3>
                      {article.summary && (
                        <p className="text-sm text-gray-600 mt-2 line-clamp-2">{article.summary}</p>
                      )}
                      <div className="flex items-center space-x-4 mt-3 text-sm">
                        <span className="text-gray-500 flex items-center">
                          <Globe className="w-3 h-3 mr-1" />
                          {article.source}
                        </span>
                        <span className="text-gray-500">{formatDate(article.datetime)}</span>
                        {article.category && (
                          <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                            {article.category}
                          </span>
                        )}
                      </div>
                      {article.related && (
                        <div className="mt-2 flex flex-wrap gap-2">
                          {article.related.split(',').map((ticker, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium"
                            >
                              {ticker.trim()}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <a
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-4 flex-shrink-0 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
                    >
                      <ExternalLink className="w-4 h-4" />
                      <span className="text-sm">View</span>
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Newspaper className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No news articles found</p>
            <button
              onClick={() => refetch()}
              className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
            >
              Refresh news →
            </button>
          </div>
        )}
      </div>

      {/* Info Banner */}
      <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg">
        <p className="text-sm text-blue-700">
          <strong>Note:</strong> News articles are fetched from Finnhub API and updated every 5 minutes.
          Click on any article to read the full story on the original source.
        </p>
      </div>
    </div>
  );
}
