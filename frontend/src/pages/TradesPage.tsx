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
        <p className="text-red-600">Error loading trades. Please try again.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">All Trades</h1>
        <p className="mt-2 text-gray-600">Browse all insider trading transactions</p>
      </div>

      {/* Filters */}
      <div className="card">
        <form className="space-y-4" onSubmit={handleApplyFilters}>
          <div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-6 gap-4">
            <div className="flex flex-col">
              <label htmlFor="ticker" className="text-sm font-medium text-gray-700">
                Ticker
              </label>
              <CompanyAutocomplete
                value={filterForm.ticker}
                onChange={(ticker) => setFilterForm(prev => ({ ...prev, ticker }))}
                placeholder="Search ticker (e.g., AAPL)"
              />
            </div>

            <div className="flex flex-col">
              <label htmlFor="transactionType" className="text-sm font-medium text-gray-700">
                Transaction Type
              </label>
              <select
                id="transactionType"
                name="transactionType"
                value={filterForm.transactionType}
                onChange={handleFilterInputChange}
                className="input"
              >
                <option value="ALL">All</option>
                <option value="BUY">Buy</option>
                <option value="SELL">Sell</option>
              </select>
            </div>

            <div className="flex flex-col">
              <label htmlFor="minValue" className="text-sm font-medium text-gray-700">
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
                className="input"
              />
            </div>

            <div className="flex flex-col">
              <label htmlFor="maxValue" className="text-sm font-medium text-gray-700">
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
                className="input"
              />
            </div>
            <div className="flex flex-col">
              <label htmlFor="startDate" className="text-sm font-medium text-gray-700">
                Start Date
              </label>
              <input
                id="startDate"
                name="startDate"
                type="date"
                value={filterForm.startDate}
                onChange={handleFilterInputChange}
                className="input"
              />
            </div>

            <div className="flex flex-col">
              <label htmlFor="endDate" className="text-sm font-medium text-gray-700">
                End Date
              </label>
              <input
                id="endDate"
                name="endDate"
                type="date"
                value={filterForm.endDate}
                onChange={handleFilterInputChange}
                className="input"
              />
            </div>
          </div>

          {/* Date Range Presets */}
          <div className="flex flex-wrap gap-2">
            <span className="text-sm font-medium text-gray-700 self-center">Quick Select:</span>
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
              className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
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
              className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
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
              className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
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
              className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
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
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Clear Dates
            </button>
          </div>

          {validationError && (
            <p className="text-sm text-red-600">{validationError}</p>
          )}

          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="text-sm text-gray-500">
              {hasActiveFilters
                ? 'Filters applied.'
                : 'Filter trades by ticker, type, dollar value, and date range.'}
            </div>
            <div className="flex gap-3">
              <button type="button" className="btn btn-secondary" onClick={handleResetFilters}>
                Reset
              </button>
              <button type="submit" className="btn btn-primary">
                Apply Filters
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Summary */}
      <div className="card">
        {statsLoading ? (
          <div className="flex items-center justify-center h-24">
            <LoadingSpinner />
          </div>
        ) : statsError ? (
          <div className="text-sm text-red-600">Unable to load trade statistics.</div>
        ) : (
          <div>
            {statsFetching && (
              <div className="mb-3 text-xs text-blue-600">Refreshing summary...</div>
            )}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
              <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
                <p className="text-sm text-gray-600">Total Trades</p>
                <p className="mt-1 text-2xl font-semibold text-gray-900">
                  {formatNumber(stats?.total_trades ?? 0)}
                </p>
              </div>
              <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
                <p className="text-sm text-gray-600">Companies</p>
                <p className="mt-1 text-2xl font-semibold text-blue-600">
                  151
                </p>
              </div>
              <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
                <p className="text-sm text-gray-600">Buy Trades</p>
                <p className="mt-1 text-2xl font-semibold text-green-600">
                  {formatNumber(stats?.total_buys ?? 0)}
                </p>
              </div>
              <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
                <p className="text-sm text-gray-600">Sell Trades</p>
                <p className="mt-1 text-2xl font-semibold text-red-600">
                  {formatNumber(stats?.total_sells ?? 0)}
                </p>
              </div>
              <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
                <p className="text-sm text-gray-600">Buy Volume</p>
                <p className="mt-1 text-2xl font-semibold text-green-600">
                  {formatCurrencyCompact(stats?.total_buy_value ?? 0)}
                </p>
                <p className="text-xs text-gray-500">Total purchased</p>
              </div>
              <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
                <p className="text-sm text-gray-600">Sell Volume</p>
                <p className="mt-1 text-2xl font-semibold text-red-600">
                  {formatCurrencyCompact(stats?.total_sell_value ?? 0)}
                </p>
                <p className="text-xs text-gray-500">Total sold</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Value Trend */}
      {tradesForChart.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-gray-900">Trade Value Trend</h2>
            {isFetching && !isLoading && (
              <span className="text-xs text-blue-600">Updating...</span>
            )}
          </div>
          <TradeValueSparkline trades={tradesForChart} />
          <p className="text-xs text-gray-500 mt-2 text-center">
            Showing trend for {tradesForChart.length} trades on current page
          </p>
        </div>
      )}

      {/* Trades Table */}
      <div className="card">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <LoadingSpinner />
          </div>
        ) : (
          <>
            {isFetching && (
              <div className="mb-4 text-sm text-blue-600">Updating results...</div>
            )}
            <TradeList trades={data?.items || []} />

            {/* Pagination */}
            {data && data.pages > 1 && (
              <div className="flex items-center justify-between mt-6 pt-6 border-t">
                <div className="text-sm text-gray-600">
                  Page {data.page} of {data.pages} ({data.total} total trades)
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={!data.has_prev}
                    className="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(p => p + 1)}
                    disabled={!data.has_next}
                    className="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
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



