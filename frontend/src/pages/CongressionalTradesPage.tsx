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
        <p className="text-red-400">Error loading congressional trades. Please try again.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <LegalDisclaimer />
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Congressional Trades</h1>
        <p className="mt-2 text-gray-400">Track stock trading by US House and Senate members</p>
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
              <label htmlFor="chamber" className="text-sm font-medium text-gray-300 mb-1">
                Chamber
              </label>
              <select
                id="chamber"
                name="chamber"
                value={filterForm.chamber}
                onChange={handleFilterInputChange}
                className="w-full px-4 py-2.5 bg-black/50 border border-white/10 rounded-xl text-white focus:ring-2 focus:ring-purple-500 outline-none transition-all"
              >
                <option value="ALL">All</option>
                <option value="HOUSE">House</option>
                <option value="SENATE">Senate</option>
              </select>
            </div>

            <div className="flex flex-col">
              <label htmlFor="state" className="text-sm font-medium text-gray-300 mb-1">
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
                className="w-full px-4 py-2.5 bg-black/50 border border-white/10 rounded-xl text-white placeholder:text-gray-600 focus:ring-2 focus:ring-purple-500 outline-none transition-all uppercase"
              />
            </div>

            <div className="flex flex-col">
              <label htmlFor="party" className="text-sm font-medium text-gray-300 mb-1">
                Party
              </label>
              <select
                id="party"
                name="party"
                value={filterForm.party}
                onChange={handleFilterInputChange}
                className="w-full px-4 py-2.5 bg-black/50 border border-white/10 rounded-xl text-white focus:ring-2 focus:ring-purple-500 outline-none transition-all"
              >
                <option value="ALL">All</option>
                <option value="DEMOCRAT">Democrat</option>
                <option value="REPUBLICAN">Republican</option>
                <option value="INDEPENDENT">Independent</option>
              </select>
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
              <label htmlFor="ownerType" className="text-sm font-medium text-gray-300 mb-1">
                Owner Type
              </label>
              <select
                id="ownerType"
                name="ownerType"
                value={filterForm.ownerType}
                onChange={handleFilterInputChange}
                className="w-full px-4 py-2.5 bg-black/50 border border-white/10 rounded-xl text-white focus:ring-2 focus:ring-purple-500 outline-none transition-all"
              >
                <option value="ALL">All</option>
                <option value="Self">Self</option>
                <option value="Spouse">Spouse</option>
                <option value="Dependent Child">Dependent Child</option>
                <option value="Joint">Joint</option>
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
                placeholder="e.g. 50000"
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
                placeholder="e.g. 1000000"
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

            <div className="flex flex-col justify-end">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  name="significantOnly"
                  checked={filterForm.significantOnly}
                  onChange={handleFilterInputChange}
                  className="rounded border-gray-600 bg-black/50 text-purple-600 focus:ring-purple-500"
                />
                <span className="text-sm font-medium text-gray-300">Significant Only (&gt;$100k)</span>
              </label>
            </div>
          </div>

          {/* Date Range Presets */}
          <div className="flex flex-wrap gap-2 pt-4 border-t border-white/10">
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
                : 'Filter congressional trades by ticker, chamber, state, party, type, owner, value, and date.'}
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
                <p className="text-sm text-gray-400">House Trades</p>
                <p className="mt-1 text-2xl font-semibold text-blue-400">
                  {formatNumber(stats?.house_trade_count ?? 0)}
                </p>
              </div>
              <div className="rounded-xl border border-white/10 bg-black/30 p-4">
                <p className="text-sm text-gray-400">Senate Trades</p>
                <p className="mt-1 text-2xl font-semibold text-purple-400">
                  {formatNumber(stats?.senate_trade_count ?? 0)}
                </p>
              </div>
              <div className="rounded-xl border border-white/10 bg-black/30 p-4">
                <p className="text-sm text-gray-400">Total Value</p>
                <p className="mt-1 text-2xl font-semibold text-white">
                  {formatCurrencyCompact(stats?.total_value ?? 0)}
                </p>
                <p className="text-xs text-gray-500">Estimated</p>
              </div>
            </div>

            {/* Party Breakdown */}
            {stats && (stats.democrat_buy_count > 0 || stats.republican_buy_count > 0) && (
              <div className="mt-6 pt-6 border-t border-white/10">
                <h3 className="text-sm font-medium text-gray-300 mb-4">Party Breakdown</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="rounded-xl border border-blue-500/20 bg-blue-900/10 p-3">
                    <p className="text-xs text-gray-400">Democrat Buys</p>
                    <p className="mt-1 text-xl font-semibold text-blue-400">
                      {formatNumber(stats.democrat_buy_count)}
                    </p>
                  </div>
                  <div className="rounded-xl border border-blue-500/20 bg-blue-900/10 p-3">
                    <p className="text-xs text-gray-400">Democrat Sells</p>
                    <p className="mt-1 text-xl font-semibold text-blue-400">
                      {formatNumber(stats.democrat_sell_count)}
                    </p>
                  </div>
                  <div className="rounded-xl border border-red-500/20 bg-red-900/10 p-3">
                    <p className="text-xs text-gray-400">Republican Buys</p>
                    <p className="mt-1 text-xl font-semibold text-red-400">
                      {formatNumber(stats.republican_buy_count)}
                    </p>
                  </div>
                  <div className="rounded-xl border border-red-500/20 bg-red-900/10 p-3">
                    <p className="text-xs text-gray-400">Republican Sells</p>
                    <p className="mt-1 text-xl font-semibold text-red-400">
                      {formatNumber(stats.republican_sell_count)}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Most Active */}
            {stats && (stats.most_active_congressperson || stats.most_active_company) && (
              <div className="mt-6 pt-6 border-t border-white/10">
                <h3 className="text-sm font-medium text-gray-300 mb-4">Most Active</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {stats.most_active_congressperson && (
                    <div className="rounded-xl border border-white/10 bg-black/30 p-3">
                      <p className="text-xs text-gray-400">Most Active Member</p>
                      <p className="mt-1 text-lg font-semibold text-white">
                        {stats.most_active_congressperson}
                      </p>
                    </div>
                  )}
                  {stats.most_active_company && (
                    <div className="rounded-xl border border-white/10 bg-black/30 p-3">
                      <p className="text-xs text-gray-400">Most Traded Company</p>
                      <p className="mt-1 text-lg font-semibold text-white">
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
            <CongressionalTradeList trades={data?.items || []} />

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