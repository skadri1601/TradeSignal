/**
 * Copy Trading Dashboard Page
 * Main dashboard for copy trading with broker connection status, account balance, rules, and trades
 */

import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { brokerageApi } from '../api/brokerage';
import type { BrokerageAccount, CopyTradeRule, ExecutedTrade } from '../api/brokerage';
import { RefreshCw, Plus, Settings } from 'lucide-react';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function CopyTradingPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [selectedAccountId, setSelectedAccountId] = useState<number | null>(null);

  // Fetch accounts
  const { data: accounts, isLoading: loadingAccounts } = useQuery<BrokerageAccount[]>({
    queryKey: ['brokerage-accounts'],
    queryFn: () => brokerageApi.getAccounts(),
  });

  // Fetch account details if one is selected
  const { data: accountDetails } = useQuery({
    queryKey: ['brokerage-account-details', selectedAccountId],
    queryFn: () => brokerageApi.getAccountDetails(selectedAccountId!),
    enabled: selectedAccountId !== null,
  });

  // Fetch rules
  const { data: rules, isLoading: loadingRules } = useQuery<CopyTradeRule[]>({
    queryKey: ['copy-trade-rules'],
    queryFn: () => brokerageApi.getRules(),
  });

  // Fetch recent trades
  const { data: trades, isLoading: loadingTrades } = useQuery<ExecutedTrade[]>({
    queryKey: ['executed-trades'],
    queryFn: () => brokerageApi.getTrades({ limit: 10 }),
  });

  const activeRules = rules?.filter(r => r.is_active) || [];

  const formatCurrency = (value?: number | null) => {
    if (value === undefined || value === null) return '--';
    if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(2)}M`;
    if (value >= 1_000) return `$${(value / 1_000).toFixed(2)}K`;
    return `$${value.toFixed(2)}`;
  };

  const handleSyncAccount = async (accountId: number) => {
    try {
      await brokerageApi.syncAccount(accountId);
      queryClient.invalidateQueries({ queryKey: ['brokerage-accounts'] });
      queryClient.invalidateQueries({ queryKey: ['brokerage-account-details', accountId] });
    } catch (error) {
      console.error('Failed to sync account:', error);
    }
  };

  if (loadingAccounts || loadingRules || loadingTrades) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Copy Trading</h1>
            <p className="text-gray-400 mt-1">Automatically copy insider trades to your brokerage account</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => navigate('/copy-trading/rules')}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center gap-2 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Create Rule
            </button>
            <button
              onClick={() => navigate('/copy-trading/account')}
              className="px-4 py-2 border border-white/20 hover:bg-white/10 rounded-lg flex items-center gap-2 transition-colors"
            >
              <Settings className="w-4 h-4" />
              Manage Accounts
            </button>
          </div>
        </div>

        {/* Broker Connection Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {accounts && accounts.length > 0 ? (
            accounts.map((account) => (
              <div
                key={account.id}
                className="bg-white/5 border border-white/10 rounded-lg p-4 cursor-pointer hover:bg-white/10 transition-colors"
                onClick={() => setSelectedAccountId(account.id)}
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold capitalize">{account.broker}</h3>
                  <span
                    className={`px-2 py-1 rounded text-xs ${
                      account.is_active
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-red-500/20 text-red-400'
                    }`}
                  >
                    {account.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mb-3">{account.account_name || account.account_number}</p>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Balance:</span>
                    <span className="font-semibold">{formatCurrency(account.balance)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Buying Power:</span>
                    <span className="font-semibold">{formatCurrency(account.buying_power)}</span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSyncAccount(account.id);
                    }}
                    className="w-full mt-3 px-3 py-1.5 bg-white/10 hover:bg-white/20 rounded text-sm flex items-center justify-center gap-2 transition-colors"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Sync
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-full bg-white/5 border border-white/10 rounded-lg p-8 text-center">
              <p className="text-gray-400 mb-4">No brokerage accounts connected</p>
              <button
                onClick={() => navigate('/copy-trading/account')}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
              >
                Connect Broker
              </button>
            </div>
          )}
        </div>

        {/* Account Details (if selected) */}
        {accountDetails && (
          <div className="bg-white/5 border border-white/10 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Account Summary</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-400">Cash Balance</p>
                <p className="text-2xl font-bold">{formatCurrency(accountDetails.cash_balance)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Total Positions</p>
                <p className="text-2xl font-bold">{accountDetails.total_positions}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Market Value</p>
                <p className="text-2xl font-bold">{formatCurrency(accountDetails.total_market_value)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Unrealized P/L</p>
                <p
                  className={`text-2xl font-bold ${
                    accountDetails.total_unrealized_pl >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}
                >
                  {formatCurrency(accountDetails.total_unrealized_pl)}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Active Rules */}
        <div className="bg-white/5 border border-white/10 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Active Rules ({activeRules.length})</h2>
            <button
              onClick={() => navigate('/copy-trading/rules')}
              className="text-sm text-purple-400 hover:text-purple-300"
            >
              View All →
            </button>
          </div>
          {activeRules.length > 0 ? (
            <div className="space-y-3">
              {activeRules.slice(0, 5).map((rule) => (
                <div
                  key={rule.id}
                  className="bg-white/5 border border-white/10 rounded-lg p-4 hover:bg-white/10 transition-colors cursor-pointer"
                  onClick={() => navigate(`/copy-trading/rules?rule=${rule.id}`)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold">{rule.name}</h3>
                      <p className="text-sm text-gray-400 mt-1">
                        {rule.brokerage_account_name || 'Unknown Account'} • {rule.copy_percentage}% copy
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-400">Trades Executed</p>
                      <p className="text-lg font-semibold">{rule.trades_executed}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-center py-8">No active rules. Create one to get started!</p>
          )}
        </div>

        {/* Recent Trades */}
        <div className="bg-white/5 border border-white/10 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Trades</h2>
          {trades && trades.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-3 px-4 text-sm text-gray-400">Ticker</th>
                    <th className="text-left py-3 px-4 text-sm text-gray-400">Side</th>
                    <th className="text-left py-3 px-4 text-sm text-gray-400">Quantity</th>
                    <th className="text-left py-3 px-4 text-sm text-gray-400">Price</th>
                    <th className="text-left py-3 px-4 text-sm text-gray-400">Status</th>
                    <th className="text-left py-3 px-4 text-sm text-gray-400">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.map((trade) => (
                    <tr key={trade.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                      <td className="py-3 px-4 font-semibold">{trade.ticker}</td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-1 rounded text-xs ${
                            trade.side === 'buy'
                              ? 'bg-green-500/20 text-green-400'
                              : 'bg-red-500/20 text-red-400'
                          }`}
                        >
                          {trade.side.toUpperCase()}
                        </span>
                      </td>
                      <td className="py-3 px-4">{trade.quantity}</td>
                      <td className="py-3 px-4">{formatCurrency(trade.filled_price)}</td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-1 rounded text-xs ${
                            trade.status === 'filled'
                              ? 'bg-green-500/20 text-green-400'
                              : trade.status === 'pending'
                              ? 'bg-yellow-500/20 text-yellow-400'
                              : 'bg-red-500/20 text-red-400'
                          }`}
                        >
                          {trade.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-400">
                        {trade.execution_time
                          ? new Date(trade.execution_time).toLocaleString()
                          : new Date(trade.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-400 text-center py-8">No trades executed yet</p>
          )}
        </div>
      </div>
    </div>
  );
}

