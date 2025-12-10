import { FormEvent, ChangeEvent, useCallback, useMemo, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { tradesApi } from '../api/trades';
import TradeList from '../components/trades/TradeList';
import LoadingSpinner from '../components/common/LoadingSpinner';
import CompanyAutocomplete from '../components/common/CompanyAutocomplete';
import TradeValueSparkline from '../components/trades/TradeValueSparkline';
import type { PaginatedResponse, Trade, TradeFilters, TradeStats } from '../types';
import { formatNumber, formatCurrencyCompact } from '../utils/formatters';
import useTradeStream from '../hooks/useTradeStream';
import { LegalDisclaimer } from '../components/LegalDisclaimer';

export default function TradesPage() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const limit = 20;
  const [filterForm, setFilterForm] = useState({
    ticker: '',
    transactionType: 'ALL' as 'ALL' | 'BUY' | 'SELL',
    minValue: '',
    maxValue: '',
    startDate: '',
    endDate: '',
  });
  const [filters, setFilters] = useState<TradeFilters>({});
  const [validationError, setValidationError] = useState<string | null>(null);

  const hasActiveFilters = useMemo(
    () => Object.keys(filters).length > 0,
    [filters]
  );

  const handleFilterInputChange = (
    event: ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = event.target;
    setFilterForm(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleApplyFilters = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const nextFilters: TradeFilters = {};

    const ticker = filterForm.ticker.trim();
    const minValue = filterForm.minValue ? Number(filterForm.minValue) : undefined;
    const maxValue = filterForm.maxValue ? Number(filterForm.maxValue) : undefined;
    const startDate = filterForm.startDate ? filterForm.startDate : undefined;
    const endDate = filterForm.endDate ? filterForm.endDate : undefined;

    if (Number.isFinite(minValue) && Number.isFinite(maxValue) && minValue! > maxValue!) {
      setValidationError('Minimum value cannot be greater than maximum value.');
      return;
    }

    if (startDate && endDate && startDate > endDate) {
      setValidationError('Start date cannot be after end date.');
      return;
    }

    if (ticker) {
      nextFilters.ticker = ticker.toUpperCase();
    }

    if (filterForm.transactionType !== 'ALL') {
      nextFilters.transaction_type = filterForm.transactionType;
    }

    if (Number.isFinite(minValue)) {
      nextFilters.min_value = minValue!;
    }

    if (Number.isFinite(maxValue)) {
      nextFilters.max_value = maxValue!;
    }

    if (startDate) {
      nextFilters.transaction_date_from = startDate;
    }

    if (endDate) {
      nextFilters.transaction_date_to = endDate;
    }

    setValidationError(null);
    setFilters(nextFilters);
    setPage(1);
  };

  const handleResetFilters = () => {
    setFilterForm({ ticker: '', transactionType: 'ALL', minValue: '', maxValue: '', startDate: '', endDate: '' });
    setFilters({});
    setValidationError(null);
    setPage(1);
  };

  const { data, isLoading, error, isFetching } = useQuery<PaginatedResponse<Trade>>({
    queryKey: ['trades', { page, limit, filters }],
    queryFn: () => tradesApi.getTrades({ page, limit, ...filters }),
    placeholderData: previousData => previousData,
  });

  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
    isFetching: statsFetching,
  } = useQuery<TradeStats>({
    queryKey: ['tradeStats', filters],
    queryFn: () => tradesApi.getTradeStats(filters),
    placeholderData: previousData => previousData,
  });

  const tradesForChart = useMemo(() => data?.items ?? [], [data]);

  const handleStreamMessage = useCallback(
    (payload: { type?: string; trade?: Trade }) => {
      if (!payload || typeof payload !== 'object') return;
      if (payload.type === 'trade_created' || payload.type === 'trade_updated') {
        queryClient.invalidateQueries({ queryKey: ['trades'] });
        queryClient.invalidateQueries({ queryKey: ['tradeStats'] });
      }
    },
    [queryClient]
  );

  useTradeStream(handleStreamMessage);

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400">Error loading trades. Please try again.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <LegalDisclaimer />
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">All Trades</h1>
        <p className="mt-2 text-gray-400">Browse all insider trading transactions</p>
      </div>

      {/* Filters */}
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-lg border border-white/10 p-6">
        <form className="space-y-4" onSubmit={handleApplyFilters}>
          <div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-6 gap-4">
            <div className="flex flex-col">
              <label htmlFor="ticker" className="text-sm font-medium text-gray-300 mb-1">
                Ticker
              </label>
              <CompanyAutocomplete
                value={filterForm.ticker}
                onChange={(ticker) => setFilterForm(prev => ({ ...prev, ticker }))}
                placeholder="Search ticker (e.g., AAPL)"
              />
            </div>

            <div className="flex flex-col">
              <label htmlFor="transactionType" className="text-sm font-medium text-gray-300 mb-1">
                Transaction Type
              </label>
              <select
                id="transactionType"
                name="transactionType"
                value={filterForm.transactionType}
                onChange={handleFilterInputChange}
                className="w-full px-4 py-2.5 bg-black/50 border border-white/10 rounded-xl text-white focus:ring-2 focus:ring-purple-500 outline-none transition-all"
              >
                <option value="ALL">All</option>
                <option value="BUY">Buy</option>
                <option value="SELL">Sell</option>
              </select>
            </div>

            <div className="flex flex-col">
              <label htmlFor="minValue" className="text-sm font-medium text-gray-300 mb-1">
                Min Value (USD)
              </label>
              <input
                id="minValue"
                name="minValue"
                type="number"
                min={0}
                step={1000}
                value={filterForm.minValue}
                onChange={handleFilterInputChange}
                placeholder="e.g. 500000"
                className="w-full px-4 py-2.5 bg-black/50 border border-white/10 rounded-xl text-white placeholder:text-gray-600 focus:ring-2 focus:ring-purple-500 outline-none transition-all"
              />
            </div>

            <div className="flex flex-col">
              <label htmlFor="maxValue" className="text-sm font-medium text-gray-300 mb-1">
                Max Value (USD)
              </label>
              <input
                id="maxValue"
                name="maxValue"
                type="number"
                min={0}
                step={1000}
                value={filterForm.maxValue}
                onChange={handleFilterInputChange}
                placeholder="e.g. 10000000"
                className="w-full px-4 py-2.5 bg-black/50 border border-white/10 rounded-xl text-white placeholder:text-gray-600 focus:ring-2 focus:ring-purple-500 outline-none transition-all"
              />
            </div>
            <div className="flex flex-col">
              <label htmlFor="startDate" className="text-sm font-medium text-gray-300 mb-1">
                Start Date
              </label>
              <input
                id="startDate"
                name="startDate"
                type="date"
                value={filterForm.startDate}
                onChange={handleFilterInputChange}
                className="w-full px-4 py-2.5 bg-black/50 border border-white/10 rounded-xl text-white focus:ring-2 focus:ring-purple-500 outline-none transition-all [color-scheme:dark]"
              />
            </div>

            <div className="flex flex-col">
              <label htmlFor="endDate" className="text-sm font-medium text-gray-300 mb-1">
                End Date
              </label>
              <input
                id="endDate"
                name="endDate"
                type="date"
                value={filterForm.endDate}
                onChange={handleFilterInputChange}
                className="w-full px-4 py-2.5 bg-black/50 border border-white/10 rounded-xl text-white focus:ring-2 focus:ring-purple-500 outline-none transition-all [color-scheme:dark]"
              />
            </div>
          </div>

          {/* Date Range Presets */}
          <div className="flex flex-wrap gap-2">
            <span className="text-sm font-medium text-gray-400 self-center">Quick Select:</span>
            <button
              type="button"
              onClick={() => {
                const end = new Date();
                const start = new Date();
                start.setDate(start.getDate() - 7);
                setFilterForm(prev => ({
                  ...prev,
                  startDate: start.toISOString().split('T')[0],
                  endDate: end.toISOString().split('T')[0],
                }));
              }}
              className="px-3 py-1 text-sm bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded-lg hover:bg-blue-500/30 transition-colors"
            >
              Last 7 Days
            </button>
            <button
              type="button"
              onClick={() => {
                const end = new Date();
                const start = new Date();
                start.setDate(start.getDate() - 30);
                setFilterForm(prev => ({
                  ...prev,
                  startDate: start.toISOString().split('T')[0],
                  endDate: end.toISOString().split('T')[0],
                }));
              }}
              className="px-3 py-1 text-sm bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded-lg hover:bg-blue-500/30 transition-colors"
            >
              Last 30 Days
            </button>
            <button
              type="button"
              onClick={() => {
                const end = new Date();
                const start = new Date();
                start.setDate(start.getDate() - 90);
                setFilterForm(prev => ({
                  ...prev,
                  startDate: start.toISOString().split('T')[0],
                  endDate: end.toISOString().split('T')[0],
                }));
              }}
              className="px-3 py-1 text-sm bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded-lg hover:bg-blue-500/30 transition-colors"
            >
              Last 90 Days
            </button>
            <button
              type="button"
              onClick={() => {
                const end = new Date();
                const start = new Date();
                start.setFullYear(start.getFullYear() - 1);
                setFilterForm(prev => ({
                  ...prev,
                  startDate: start.toISOString().split('T')[0],
                  endDate: end.toISOString().split('T')[0],
                }));
              }}
              className="px-3 py-1 text-sm bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded-lg hover:bg-blue-500/30 transition-colors"
            >
              Last Year
            </button>
            <button
              type="button"
              onClick={() => {
                setFilterForm(prev => ({
                  ...prev,
                  startDate: '',
                  endDate: '',
                }));
              }}
              className="px-3 py-1 text-sm bg-white/10 text-gray-300 border border-white/10 rounded-lg hover:bg-white/20 transition-colors"
            >
              Clear Dates
            </button>
          </div>

          {validationError && (
            <p className="text-sm text-red-400">{validationError}</p>
          )}

          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pt-4 border-t border-white/10">
            <div className="text-sm text-gray-400">
              {hasActiveFilters
                ? 'Filters applied.'
                : 'Filter trades by ticker, type, dollar value, and date range.'}
            </div>
            <div className="flex gap-3">
              <button 
                type="button" 
                className="px-4 py-2 border border-white/20 text-gray-300 rounded-lg hover:bg-white/10 transition-colors font-medium" 
                onClick={handleResetFilters}
              >
                Reset
              </button>
              <button 
                type="submit" 
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors font-medium shadow-lg shadow-purple-500/20"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Summary */}
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-lg border border-white/10 p-6">
        {statsLoading ? (
          <div className="flex items-center justify-center h-24">
            <LoadingSpinner />
          </div>
        ) : statsError ? (
          <div className="text-sm text-red-400">Unable to load trade statistics.</div>
        ) : (
          <div>
            {statsFetching && (
              <div className="mb-3 text-xs text-blue-400">Refreshing summary...</div>
            )}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
              <div className="rounded-xl border border-white/10 bg-black/30 p-4">
                <p className="text-sm text-gray-400">Total Trades</p>
                <p className="mt-1 text-2xl font-semibold text-white">
                  {formatNumber(stats?.total_trades ?? 0)}
                </p>
              </div>
              <div className="rounded-xl border border-white/10 bg-black/30 p-4">
                <p className="text-sm text-gray-400">Companies</p>
                <p className="mt-1 text-2xl font-semibold text-blue-400">
                  151
                </p>
              </div>
              <div className="rounded-xl border border-white/10 bg-black/30 p-4">
                <p className="text-sm text-gray-400">Buy Trades</p>
                <p className="mt-1 text-2xl font-semibold text-green-400">
                  {formatNumber(stats?.total_buys ?? 0)}
                </p>
              </div>
              <div className="rounded-xl border border-white/10 bg-black/30 p-4">
                <p className="text-sm text-gray-400">Sell Trades</p>
                <p className="mt-1 text-2xl font-semibold text-red-400">
                  {formatNumber(stats?.total_sells ?? 0)}
                </p>
              </div>
              <div className="rounded-xl border border-white/10 bg-black/30 p-4">
                <p className="text-sm text-gray-400">Buy Volume</p>
                <p className="mt-1 text-2xl font-semibold text-green-400">
                  {formatCurrencyCompact(stats?.total_buy_value ?? 0)}
                </p>
                <p className="text-xs text-gray-500">Total purchased</p>
              </div>
              <div className="rounded-xl border border-white/10 bg-black/30 p-4">
                <p className="text-sm text-gray-400">Sell Volume</p>
                <p className="mt-1 text-2xl font-semibold text-red-400">
                  {formatCurrencyCompact(stats?.total_sell_value ?? 0)}
                </p>
                <p className="text-xs text-gray-500">Total sold</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Value Trend */}
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-lg border border-white/10 p-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-white">Trade Value Trend</h2>
          {isFetching && !isLoading && (
            <span className="text-xs text-blue-400">Updating...</span>
          )}
        </div>
        {tradesForChart.length > 0 ? (
          <>
            <TradeValueSparkline trades={tradesForChart} />
            <p className="text-xs text-gray-500 mt-2 text-center">
              Showing trend for {tradesForChart.length} trades on current page
            </p>
          </>
        ) : (
          <div className="h-64 flex items-center justify-center border-2 border-dashed border-white/10 rounded-xl bg-black/20">
            <div className="text-center">
              <svg className="mx-auto h-12 w-12 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <p className="mt-2 text-sm font-medium text-gray-400">No trade data available</p>
              <p className="text-sm text-gray-600">Try adjusting your filters to see the trend</p>
            </div>
          </div>
        )}
      </div>

      {/* Trades Table */}
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-lg border border-white/10 p-6">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <LoadingSpinner />
          </div>
        ) : (
          <>
            {isFetching && (
              <div className="mb-4 text-sm text-blue-400">Updating results...</div>
            )}
            <TradeList trades={data?.items || []} />

            {/* Pagination */}
            {data && data.pages > 1 && (
              <div className="flex items-center justify-between mt-6 pt-6 border-t border-white/10">
                <div className="text-sm text-gray-400">
                  Page {data.page} of {data.pages} ({data.total} total trades)
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={!data.has_prev}
                    className="px-4 py-2 border border-white/10 text-gray-300 rounded-lg hover:bg-white/5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(p => p + 1)}
                    disabled={!data.has_next}
                    className="px-4 py-2 border border-white/10 text-gray-300 rounded-lg hover:bg-white/5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}