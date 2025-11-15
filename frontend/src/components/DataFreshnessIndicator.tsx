/**
 * Data Freshness Indicator Component
 *
 * Displays staleness indicators for stock quote data.
 * Based on TRUTH_FREE.md Phase 3.1 specifications.
 */

interface DataFreshnessProps {
  is_stale?: boolean;
  data_age_seconds?: number;
  last_updated?: string;
  cached?: boolean;
  data_source?: string;
  compact?: boolean;
}

export const DataFreshnessIndicator = ({
  is_stale = false,
  data_age_seconds = 0,
  last_updated,
  cached = false,
  data_source = 'yahoo_finance',
  compact = false
}: DataFreshnessProps) => {
  // Determine freshness color
  const getFreshnessColor = () => {
    if (data_age_seconds < 15) return 'text-green-600';
    if (data_age_seconds < 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Format data age
  const formatDataAge = () => {
    if (data_age_seconds < 60) return `${data_age_seconds}s ago`;
    if (data_age_seconds < 3600) return `${Math.floor(data_age_seconds / 60)}m ago`;
    return `${Math.floor(data_age_seconds / 3600)}h ago`;
  };

  // Get freshness icon
  const getFreshnessIcon = () => {
    if (data_age_seconds < 15) return '🟢';
    if (data_age_seconds < 60) return '🟡';
    return '🔴';
  };

  // Get data source display name
  const getSourceName = () => {
    const names: Record<string, string> = {
      'yahoo_finance': 'Yahoo Finance',
      'alpha_vantage': 'Alpha Vantage',
      'finnhub': 'Finnhub',
      'stale_cache': 'Cache (Stale)'
    };
    return names[data_source] || data_source;
  };

  // Get source badge color
  const getSourceColor = () => {
    const colors: Record<string, string> = {
      'yahoo_finance': 'bg-green-100 text-green-800',
      'alpha_vantage': 'bg-purple-100 text-purple-800',
      'finnhub': 'bg-blue-100 text-blue-800',
      'stale_cache': 'bg-red-100 text-red-800'
    };
    return colors[data_source] || 'bg-gray-100 text-gray-800';
  };

  if (compact) {
    return (
      <div className="flex items-center gap-2 text-xs">
        <span className={`font-medium ${getFreshnessColor()}`}>
          {getFreshnessIcon()} {formatDataAge()}
        </span>
        {is_stale && (
          <span className="bg-red-100 text-red-800 px-1.5 py-0.5 rounded font-semibold">
            STALE
          </span>
        )}
        {cached && !is_stale && (
          <span className="bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">
            CACHED
          </span>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1">
      {/* Freshness Indicator */}
      <div className="flex items-center gap-2 text-xs">
        <span className={`font-medium ${getFreshnessColor()}`}>
          {getFreshnessIcon()} {formatDataAge()}
        </span>

        {last_updated && (
          <>
            <span className="text-gray-400">|</span>
            <span className="text-gray-500">
              Updated: {new Date(last_updated).toLocaleTimeString()}
            </span>
          </>
        )}
      </div>

      {/* Status Badges */}
      <div className="flex items-center gap-2">
        {/* Stale Warning */}
        {is_stale && (
          <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded font-semibold inline-flex items-center gap-1">
            ⚠️ STALE DATA
          </span>
        )}

        {/* Cached Badge */}
        {cached && !is_stale && (
          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded inline-flex items-center gap-1">
            📦 CACHED
          </span>
        )}

        {/* Data Source Badge */}
        <span className={`text-xs px-2 py-1 rounded ${getSourceColor()}`}>
          ✓ {getSourceName()}
        </span>
      </div>
    </div>
  );
};

export default DataFreshnessIndicator;
