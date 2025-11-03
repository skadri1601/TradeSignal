import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { insidersApi } from '../api/insiders';
import { companiesApi } from '../api/companies';
import TradeList from '../components/trades/TradeList';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { User, Briefcase, Building2, TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react';
import { formatNumber, formatCurrencyCompact } from '../utils/formatters';

export default function InsiderPage() {
  const { id } = useParams<{ id: string }>();
  const insiderId = parseInt(id!);

  const { data: insider, isLoading: insiderLoading } = useQuery({
    queryKey: ['insider', insiderId],
    queryFn: () => insidersApi.getInsider(insiderId),
    enabled: !!insiderId,
  });

  const { data: trades, isLoading: tradesLoading } = useQuery({
    queryKey: ['insiderTrades', insiderId],
    queryFn: () => insidersApi.getInsiderTrades(insiderId),
    enabled: !!insiderId,
  });

  // Fetch company data if insider has a company
  // Note: We need to get ticker from trades since company_id alone doesn't give us the ticker
  const companyTicker = trades && trades.length > 0 ? trades[0].company?.ticker : null;
  const { data: company } = useQuery({
    queryKey: ['company', companyTicker],
    queryFn: () => companiesApi.getCompany(companyTicker!),
    enabled: !!companyTicker,
  });

  // Calculate statistics from trades
  const stats = trades ? {
    totalTrades: trades.length,
    totalBuys: trades.filter(t => t.transaction_type === 'BUY').length,
    totalSells: trades.filter(t => t.transaction_type === 'SELL').length,
    totalValue: trades.reduce((sum, t) => sum + (Number(t.total_value) || 0), 0),
    buyValue: trades.filter(t => t.transaction_type === 'BUY').reduce((sum, t) => sum + (Number(t.total_value) || 0), 0),
    sellValue: trades.filter(t => t.transaction_type === 'SELL').reduce((sum, t) => sum + (Number(t.total_value) || 0), 0),
  } : null;

  if (insiderLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (!insider) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Insider not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Insider Header */}
      <div className="card">
        <div className="flex items-start space-x-4">
          <div className="p-3 bg-purple-100 rounded-lg">
            <User className="h-8 w-8 text-purple-600" />
          </div>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">{insider.name}</h1>
            {insider.title && (
              <p className="text-lg text-gray-600 mt-1 flex items-center">
                <Briefcase className="h-5 w-5 mr-2" />
                {insider.title}
              </p>
            )}
            {company && (
              <Link
                to={`/companies/${company.ticker}`}
                className="text-md text-blue-600 hover:text-blue-700 mt-2 flex items-center"
              >
                <Building2 className="h-4 w-4 mr-2" />
                {company.name} ({company.ticker})
              </Link>
            )}
          </div>
        </div>

        {/* Roles and Info Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          {/* Roles */}
          <div>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Roles</h3>
            <div className="flex flex-wrap gap-2">
              {insider.is_officer && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                  Officer
                </span>
              )}
              {insider.is_director && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                  Director
                </span>
              )}
              {insider.is_ten_percent_owner && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                  10% Owner
                </span>
              )}
              {insider.is_other && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                  Other
                </span>
              )}
              {!insider.is_officer && !insider.is_director && !insider.is_ten_percent_owner && !insider.is_other && (
                <span className="text-gray-500 text-sm">No specific roles listed</span>
              )}
            </div>
          </div>

          {/* Position/Title - Only show if not "Unknown" */}
          {insider.primary_role && insider.primary_role !== 'Unknown' && (
            <div>
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Position</h3>
              <p className="text-lg font-medium text-gray-900">{insider.primary_role}</p>
            </div>
          )}
        </div>
      </div>

      {/* Trading Statistics */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Trades</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{formatNumber(stats.totalTrades)}</p>
              </div>
              <Activity className="h-8 w-8 text-gray-400" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Buy Transactions</p>
                <p className="text-2xl font-bold text-green-600 mt-1">{formatNumber(stats.totalBuys)}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-400" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Sell Transactions</p>
                <p className="text-2xl font-bold text-red-600 mt-1">{formatNumber(stats.totalSells)}</p>
              </div>
              <TrendingDown className="h-8 w-8 text-red-400" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Buy Value</p>
                <p className="text-2xl font-bold text-green-600 mt-1">{formatCurrencyCompact(stats.buyValue)}</p>
                {stats.buyValue > 0 && (
                  <p className="text-xs text-gray-500 mt-1">{stats.totalBuys} purchases</p>
                )}
              </div>
              <DollarSign className="h-8 w-8 text-green-400" />
            </div>
          </div>

          {stats.sellValue > 0 && (
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Sell Value</p>
                  <p className="text-2xl font-bold text-red-600 mt-1">{formatCurrencyCompact(stats.sellValue)}</p>
                  <p className="text-xs text-gray-500 mt-1">{stats.totalSells} sales</p>
                </div>
                <DollarSign className="h-8 w-8 text-red-400" />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recent Trades */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Trading Activity</h2>
        {tradesLoading ? (
          <div className="flex items-center justify-center h-32">
            <LoadingSpinner />
          </div>
        ) : trades && trades.length > 0 ? (
          <TradeList trades={trades} />
        ) : (
          <div className="text-center py-12">
            <Activity className="h-12 w-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-500">No trading activity found</p>
          </div>
        )}
      </div>
    </div>
  );
}
