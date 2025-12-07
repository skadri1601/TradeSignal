import { FormEvent, ChangeEvent, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { congressionalTradesApi } from '../api/congressionalTrades';
import CongressionalTradeList from '../components/congressional/CongressionalTradeList';
import LoadingSpinner from '../components/common/LoadingSpinner';
import CompanyAutocomplete from '../components/common/CompanyAutocomplete';
import type { PaginatedResponse, CongressionalTrade, CongressionalTradeFilters, CongressionalTradeStats } from '../types';
import { formatNumber, formatCurrencyCompact } from '../utils/formatters';
import { LegalDisclaimer } from '../components/LegalDisclaimer';

export default function CongressionalTradesPage() {
  const [page, setPage] = useState(1);
  const limit = 20;
  const [filterForm, setFilterForm] = useState({
    ticker: '',
    chamber: 'ALL' as 'ALL' | 'HOUSE' | 'SENATE',
    state: '',
    party: 'ALL' as 'ALL' | 'DEMOCRAT' | 'REPUBLICAN' | 'INDEPENDENT',
    transactionType: 'ALL' as 'ALL' | 'BUY' | 'SELL',
    ownerType: 'ALL' as 'ALL' | 'Self' | 'Spouse' | 'Dependent Child' | 'Joint',
    minValue: '',
    maxValue: '',
    startDate: '',
    endDate: '',
    significantOnly: false,
  });
  const [filters, setFilters] = useState<CongressionalTradeFilters>({});
  const [validationError, setValidationError] = useState<string | null>(null);

  const hasActiveFilters = useMemo(
    () => Object.keys(filters).length > 0,
    [filters]
  );

  const handleFilterInputChange = (
    event: ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value, type } = event.target;
    const checked = (event.target as HTMLInputElement).checked;
    setFilterForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleApplyFilters = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const nextFilters: CongressionalTradeFilters = {};

    const ticker = filterForm.ticker.trim();
    const state = filterForm.state.trim();
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

    if (filterForm.chamber !== 'ALL') {
      nextFilters.chamber = filterForm.chamber;
    }

    if (state) {
      nextFilters.state = state.toUpperCase();
    }

    if (filterForm.party !== 'ALL') {
      nextFilters.party = filterForm.party;
    }

    if (filterForm.transactionType !== 'ALL') {
      nextFilters.transaction_type = filterForm.transactionType;
    }

    if (filterForm.ownerType !== 'ALL') {
      nextFilters.owner_type = filterForm.ownerType;
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

    if (filterForm.significantOnly) {
      nextFilters.significant_only = true;
    }

    setValidationError(null);
    setFilters(nextFilters);
    setPage(1);
  };

  const handleResetFilters = () => {
    setFilterForm({
      ticker: '',
      chamber: 'ALL',
      state: '',
      party: 'ALL',
      transactionType: 'ALL',
      ownerType: 'ALL',
      minValue: '',
      maxValue: '',
      startDate: '',
      endDate: '',
      significantOnly: false,
    });
    setFilters({});
    setValidationError(null);
    setPage(1);
  };

  const { data, isLoading, error, isFetching } = useQuery<PaginatedResponse<CongressionalTrade>>({
    queryKey: ['congressionalTrades', { page, limit, filters }],
    queryFn: () => congressionalTradesApi.getTrades({ page, limit, ...filters }),
    placeholderData: previousData => previousData,
  });

  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
    isFetching: statsFetching,
  } = useQuery<CongressionalTradeStats>({
    queryKey: ['congressionalTradeStats', filters],
    queryFn: () => congressionalTradesApi.getTradeStats(filters),
    placeholderData: previousData => previousData,
  });

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Error loading congressional trades. Please try again.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <LegalDisclaimer />
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Congressional Trades</h1>
        <p className="mt-2 text-gray-600">Track stock trading by US House and Senate members</p>
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
              <label htmlFor="chamber" className="text-sm font-medium text-gray-700">
                Chamber
              </label>
              <select
                id="chamber"
                name="chamber"
                value={filterForm.chamber}
                onChange={handleFilterInputChange}
                className="input"
              >
                <option value="ALL">All</option>
                <option value="HOUSE">House</option>
                <option value="SENATE">Senate</option>
              </select>
            </div>

            <div className="flex flex-col">
              <label htmlFor="state" className="text-sm font-medium text-gray-700">
                State
              </label>
              <input
                id="state"
                name="state"
                type="text"
                maxLength={2}
                value={filterForm.state}
                onChange={handleFilterInputChange}
                placeholder="e.g. CA, NY"
                className="input uppercase"
              />
            </div>

            <div className="flex flex-col">
              <label htmlFor="party" className="text-sm font-medium text-gray-700">
                Party
              </label>
              <select
                id="party"
                name="party"
                value={filterForm.party}
                onChange={handleFilterInputChange}
                className="input"
              >
                <option value="ALL">All</option>
                <option value="DEMOCRAT">Democrat</option>
                <option value="REPUBLICAN">Republican</option>
                <option value="INDEPENDENT">Independent</option>
              </select>
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
              <label htmlFor="ownerType" className="text-sm font-medium text-gray-700">
                Owner Type
              </label>
              <select
                id="ownerType"
                name="ownerType"
                value={filterForm.ownerType}
                onChange={handleFilterInputChange}
                className="input"
              >
                <option value="ALL">All</option>
                <option value="Self">Self</option>
                <option value="Spouse">Spouse</option>
                <option value="Dependent Child">Dependent Child</option>
                <option value="Joint">Joint</option>
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
                placeholder="e.g. 50000"
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
                placeholder="e.g. 1000000"
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

            <div className="flex flex-col justify-end">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  name="significantOnly"
                  checked={filterForm.significantOnly}
                  onChange={handleFilterInputChange}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">Significant Only (&gt;$100k)</span>
              </label>
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
                : 'Filter congressional trades by ticker, chamber, state, party, type, owner, value, and date.'}
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
              <div className="rounded-xl border border-green-200 bg-green-50 p-4">
                <p className="text-sm text-gray-600">Buy Trades</p>
                <p className="mt-1 text-2xl font-semibold text-green-600">
                  {formatNumber(stats?.total_buys ?? 0)}
                </p>
              </div>
              <div className="rounded-xl border border-red-200 bg-red-50 p-4">
                <p className="text-sm text-gray-600">Sell Trades</p>
                <p className="mt-1 text-2xl font-semibold text-red-600">
                  {formatNumber(stats?.total_sells ?? 0)}
                </p>
              </div>
              <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
                <p className="text-sm text-gray-600">House Trades</p>
                <p className="mt-1 text-2xl font-semibold text-blue-600">
                  {formatNumber(stats?.house_trade_count ?? 0)}
                </p>
              </div>
              <div className="rounded-xl border border-purple-200 bg-purple-50 p-4">
                <p className="text-sm text-gray-600">Senate Trades</p>
                <p className="mt-1 text-2xl font-semibold text-purple-600">
                  {formatNumber(stats?.senate_trade_count ?? 0)}
                </p>
              </div>
              <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
                <p className="text-sm text-gray-600">Total Value</p>
                <p className="mt-1 text-2xl font-semibold text-gray-900">
                  {formatCurrencyCompact(stats?.total_value ?? 0)}
                </p>
                <p className="text-xs text-gray-500">Estimated</p>
              </div>
            </div>

            {/* Party Breakdown */}
            {stats && (stats.democrat_buy_count > 0 || stats.republican_buy_count > 0) && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-sm font-medium text-gray-700 mb-4">Party Breakdown</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="rounded-xl border border-blue-200 bg-blue-50 p-3">
                    <p className="text-xs text-gray-600">Democrat Buys</p>
                    <p className="mt-1 text-xl font-semibold text-blue-600">
                      {formatNumber(stats.democrat_buy_count)}
                    </p>
                  </div>
                  <div className="rounded-xl border border-blue-200 bg-blue-50 p-3">
                    <p className="text-xs text-gray-600">Democrat Sells</p>
                    <p className="mt-1 text-xl font-semibold text-blue-600">
                      {formatNumber(stats.democrat_sell_count)}
                    </p>
                  </div>
                  <div className="rounded-xl border border-red-200 bg-red-50 p-3">
                    <p className="text-xs text-gray-600">Republican Buys</p>
                    <p className="mt-1 text-xl font-semibold text-red-600">
                      {formatNumber(stats.republican_buy_count)}
                    </p>
                  </div>
                  <div className="rounded-xl border border-red-200 bg-red-50 p-3">
                    <p className="text-xs text-gray-600">Republican Sells</p>
                    <p className="mt-1 text-xl font-semibold text-red-600">
                      {formatNumber(stats.republican_sell_count)}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Most Active */}
            {stats && (stats.most_active_congressperson || stats.most_active_company) && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-sm font-medium text-gray-700 mb-4">Most Active</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {stats.most_active_congressperson && (
                    <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
                      <p className="text-xs text-gray-600">Most Active Member</p>
                      <p className="mt-1 text-lg font-semibold text-gray-900">
                        {stats.most_active_congressperson}
                      </p>
                    </div>
                  )}
                  {stats.most_active_company && (
                    <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
                      <p className="text-xs text-gray-600">Most Traded Company</p>
                      <p className="mt-1 text-lg font-semibold text-gray-900">
                        {stats.most_active_company}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

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
            <CongressionalTradeList trades={data?.items || []} />

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
