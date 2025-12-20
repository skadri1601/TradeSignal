import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { insidersApi } from '../api/insiders';
import { companiesApi } from '../api/companies';
import TradeList from '../components/trades/TradeList';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { User, Briefcase, Building2, TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react';
import { formatNumber, formatCurrencyCompact } from '../utils/formatters';
import TradePieChart from '../components/trades/TradePieChart';

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
  const companyTicker = trades && trades.length > 0 ? trades[0].company?.ticker : null;
  const { data: company } = useQuery({
    queryKey: ['company', companyTicker],
    queryFn: () => companiesApi.getCompany(companyTicker!),
    enabled: !!companyTicker,
  });

  // Calculate statistics from trades for the TradePieChart
  const stats = trades ? {
    total_trades: trades.length,
    total_buys: trades.filter(t => t.transaction_type === 'BUY').length,
    total_sells: trades.filter(t => t.transaction_type === 'SELL').length,
    total_value: trades.reduce((sum, t) => sum + (Number(t.total_value) || 0), 0),
    total_buy_value: trades.filter(t => t.transaction_type === 'BUY').reduce((sum, t) => sum + (Number(t.total_value) || 0), 0),
    total_sell_value: trades.filter(t => t.transaction_type === 'SELL').reduce((sum, t) => sum + (Number(t.total_value) || 0), 0),
    // Dummy values for fields not directly available here, but required by TradeStats schema
    total_shares_traded: 0,
    average_trade_size: 0,
    largest_trade: 0,
    most_active_company: null,
    most_active_insider: null,
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
        <p className="text-gray-400">Insider not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Insider Header */}
      <div className="card">
        <div className="flex items-start space-x-4">
          <div className="p-3 bg-purple-500/20 rounded-lg">
            <User className="h-8 w-8 text-purple-400" />
          </div>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-white">{insider.name}</h1>
            {insider.title && (
              <p className="text-lg text-gray-400 mt-1 flex items-center">
                <Briefcase className="h-5 w-5 mr-2" />
                {insider.title}
              </p>
            )}
            {company && (
              <Link
                to={`/companies/${company.ticker}`}
                className="text-md text-blue-400 hover:text-blue-300 mt-2 flex items-center transition-colors"
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
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  Officer
                </span>
              )}
              {insider.is_director && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  Director
                </span>
              )}
              {insider.is_ten_percent_owner && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-500/20 text-green-300 border border-green-500/30">
                  10% Owner
                </span>
              )}
              {insider.is_other && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-700/50 text-gray-300 border border-gray-600">
                  Other
                </span>
              )}
              {!insider.is_officer && !insider.is_director && !insider.is_ten_percent_owner && !insider.is_other && (
                <span className="text-gray-500 text-sm">No specific roles listed</span>
              )}
            </div>
          </div>

          {/* Position/Title */}
          {insider.primary_role && insider.primary_role !== 'Unknown' && (
            <div>
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Position</h3>
              <p className="text-lg font-medium text-white">{insider.primary_role}</p>
            </div>
          )}
        </div>
      </div>

      {/* Trading Statistics */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-white/10 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Total Trades</p>
                <p className="text-2xl font-bold text-white mt-1">{formatNumber(stats.total_trades)}</p>
              </div>
              <Activity className="h-8 w-8 text-gray-600" />
            </div>
          </div>

          <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-white/10 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Buy Transactions</p>
                <p className="text-2xl font-bold text-green-400 mt-1">{formatNumber(stats.total_buys)}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-500/50" />
            </div>
          </div>

          <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-white/10 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Sell Transactions</p>
                <p className="text-2xl font-bold text-red-400 mt-1">{formatNumber(stats.total_sells)}</p>
              </div>
              <TrendingDown className="h-8 w-8 text-red-500/50" />
            </div>
          </div>

          <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-white/10 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">Total Buy Value</p>
                <p className="text-2xl font-bold text-green-400 mt-1">{formatCurrencyCompact(stats.total_buy_value)}</p>
                {stats.total_buy_value > 0 && (
                  <p className="text-xs text-gray-500 mt-1">{stats.total_buys} purchases</p>
                )}
              </div>
              <DollarSign className="h-8 w-8 text-green-500/50" />
            </div>
          </div>

          {stats.total_sell_value > 0 && (
            <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-white/10 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-400">Total Sell Value</p>
                  <p className="text-2xl font-bold text-red-400 mt-1">{formatCurrencyCompact(stats.total_sell_value)}</p>
                  <p className="text-xs text-gray-500 mt-1">{stats.total_sells} sales</p>
                </div>
                <DollarSign className="h-8 w-8 text-red-500/50" />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Trade Distribution Charts */}
      {stats && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Buy vs Sell Count */}
          <div className="card">
            <h2 className="text-lg font-semibold text-white mb-4">
              Buy vs Sell (Trade Count)
            </h2>
            <TradePieChart stats={{
              total_trades: stats.total_trades,
              total_buys: stats.total_buys,
              total_sells: stats.total_sells,
              total_shares_traded: 0, // Not available in current stats
              total_value: stats.total_value,
              total_buy_value: stats.total_buy_value,
              total_sell_value: stats.total_sell_value,
              average_trade_size: 0, // Not available in current stats
              largest_trade: 0, // Not available in current stats
              most_active_company: "", // Not available in current stats
              most_active_insider: "", // Not available in current stats
            }} mode="count" />
          </div>

          {/* Buy vs Sell Volume */}
          <div className="card">
            <h2 className="text-lg font-semibold text-white mb-4">
              Buy vs Sell (Dollar Volume)
            </h2>
            <TradePieChart stats={{
              total_trades: stats.total_trades,
              total_buys: stats.total_buys,
              total_sells: stats.total_sells,
              total_shares_traded: 0, // Not available in current stats
              total_value: stats.total_value,
              total_buy_value: stats.total_buy_value,
              total_sell_value: stats.total_sell_value,
              average_trade_size: 0, // Not available in current stats
              largest_trade: 0, // Not available in current stats
              most_active_company: "", // Not available in current stats
              most_active_insider: "", // Not available in current stats
            }} mode="value" />
          </div>
        </div>
      )}

      {/* Recent Trades */}
      <div className="card">
        <h2 className="text-xl font-bold text-white mb-4">Trading Activity</h2>
        {tradesLoading ? (
          <div className="flex items-center justify-center h-32">
            <LoadingSpinner />
          </div>
        ) : trades && trades.length > 0 ? (
          <TradeList trades={trades} />
        ) : (
          <div className="text-center py-12">
            <Activity className="h-12 w-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-500">No trading activity found</p>
          </div>
        )}
      </div>
    </div>
  );
}