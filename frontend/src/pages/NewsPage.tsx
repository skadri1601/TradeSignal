/**
 * News Page - Market News Articles - Dark Mode
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
          <h1 className="text-3xl font-bold text-white flex items-center">
            <Newspaper className="w-8 h-8 mr-3 text-blue-400" />
            Market News
          </h1>
          <p className="text-gray-400 mt-2">
            Latest market news articles and financial updates
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Last updated: {lastUpdated.toLocaleTimeString()} • Auto-refreshes every 5 minutes
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isLoading}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors disabled:opacity-50 font-medium shadow-lg shadow-blue-500/20"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-blue-600/20 to-blue-900/40 border border-blue-500/30 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-200 text-sm">Total Articles</p>
              <p className="text-3xl font-bold mt-1">{articles.length}</p>
            </div>
            <Newspaper className="w-10 h-10 text-blue-400" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-600/20 to-green-900/40 border border-green-500/30 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-200 text-sm">News Sources</p>
              <p className="text-3xl font-bold mt-1">{uniqueSources}</p>
            </div>
            <Globe className="w-10 h-10 text-green-400" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-600/20 to-purple-900/40 border border-purple-500/30 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-200 text-sm">Last 7 Days</p>
              <p className="text-3xl font-bold mt-1">{articles.length}</p>
            </div>
            <TrendingUp className="w-10 h-10 text-purple-400" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-lg border border-white/10 p-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-300 mb-2">Category</label>
            <div className="flex space-x-2">
              <button
                onClick={() => setCategory('latest')}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
                  category === 'latest'
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20'
                    : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white border border-white/10'
                }`}
              >
                Latest
              </button>
              <button
                onClick={() => setCategory('general')}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
                  category === 'general'
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20'
                    : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white border border-white/10'
                }`}
              >
                General
              </button>
              <button
                onClick={() => setCategory('company')}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
                  category === 'company'
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20'
                    : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white border border-white/10'
                }`}
              >
                Company
              </button>
            </div>
          </div>

          {category === 'company' && (
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-300 mb-2">Search by Ticker</label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={searchTicker}
                  onChange={(e) => setSearchTicker(e.target.value.toUpperCase())}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="e.g., AAPL, MSFT"
                  className="flex-1 px-4 py-2 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
                <button
                  onClick={handleSearch}
                  disabled={!searchTicker || isLoading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors disabled:opacity-50 flex items-center space-x-2 shadow-lg shadow-blue-500/20"
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
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-lg border border-white/10 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-white">
            {category === 'company' && searchTicker
              ? `News for ${searchTicker}`
              : category === 'general'
              ? 'General Market News'
              : 'Latest News'}
          </h2>
          <span className="text-sm text-gray-400">{articles.length} articles</span>
        </div>

        {isLoading ? (
          <div className="text-center py-12 text-gray-500">Loading news articles...</div>
        ) : newsError ? (
          <div className="text-center py-12">
            <div className="text-red-400 mb-2">Failed to load news</div>
            <p className="text-sm text-gray-500 mb-4">
              {newsError instanceof Error ? newsError.message : 'An error occurred while loading news'}
            </p>
            <button
              onClick={() => refetch()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors"
            >
              Try Again
            </button>
          </div>
        ) : category === 'company' && !searchTicker ? (
          <div className="text-center py-12">
            <Search className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">Enter a ticker symbol to search for company news</p>
          </div>
        ) : articles.length > 0 ? (
          <div className="space-y-4">
            {articles.map((article: NewsArticle) => (
              <div
                key={article.id}
                className="flex items-start space-x-4 p-4 hover:bg-white/5 rounded-xl transition-colors border border-transparent hover:border-white/5 group"
              >
                {article.image && (
                  <img
                    src={article.image}
                    alt={article.headline}
                    className="w-24 h-24 object-cover rounded-lg flex-shrink-0 opacity-80 group-hover:opacity-100 transition-opacity"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                )}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-white text-lg hover:text-blue-400 cursor-pointer transition-colors">
                        <a
                          href={article.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:underline decoration-blue-400/50"
                        >
                          {article.headline}
                        </a>
                      </h3>
                      {article.summary && (
                        <p className="text-sm text-gray-400 mt-2 line-clamp-2">{article.summary}</p>
                      )}
                      <div className="flex items-center space-x-4 mt-3 text-sm">
                        <span className="text-gray-500 flex items-center">
                          <Globe className="w-3 h-3 mr-1" />
                          {article.source}
                        </span>
                        <span className="text-gray-500">{formatDate(article.datetime)}</span>
                        {article.category && (
                          <span className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded-full text-xs font-medium border border-blue-500/30">
                            {article.category}
                          </span>
                        )}
                      </div>
                      {article.related && (
                        <div className="mt-2 flex flex-wrap gap-2">
                          {article.related.split(',').map((ticker, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-1 bg-white/10 text-gray-300 rounded text-xs font-medium hover:bg-white/20 transition-colors cursor-default"
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
                      className="ml-4 flex-shrink-0 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors flex items-center space-x-2 shadow-lg shadow-blue-500/20"
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
            <Newspaper className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">No news articles found</p>
            <button
              onClick={() => refetch()}
              className="mt-4 text-blue-400 hover:text-blue-300 font-medium"
            >
              Refresh news →
            </button>
          </div>
        )}
      </div>

      {/* Info Banner */}
      <div className="bg-blue-900/20 border-l-4 border-blue-500 p-4 rounded-r-lg">
        <p className="text-sm text-blue-200">
          <strong>Note:</strong> News articles are fetched from Finnhub API and updated every 5 minutes.
          Click on any article to read the full story on the original source.
        </p>
      </div>
    </div>
  );
}