/**
 * Copy Trading Account Management Page
 * Connect, manage, and configure brokerage accounts
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { brokerageApi } from '../api/brokerage';
import type { BrokerageAccount, BrokerAccountSummary } from '../api/brokerage';
import { RefreshCw, Unlink, ArrowLeft, ExternalLink } from 'lucide-react';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function CopyTradingAccountPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [selectedAccountId, setSelectedAccountId] = useState<number | null>(null);
  const [connectingBroker, setConnectingBroker] = useState<string | null>(null);

  // Fetch accounts
  const { data: accounts, isLoading: loadingAccounts } = useQuery<BrokerageAccount[]>({
    queryKey: ['brokerage-accounts'],
    queryFn: () => brokerageApi.getAccounts(),
  });

  // Fetch account details if one is selected
  const { data: accountDetails, isLoading: loadingDetails } = useQuery<BrokerAccountSummary>({
    queryKey: ['brokerage-account-details', selectedAccountId],
    queryFn: () => brokerageApi.getAccountDetails(selectedAccountId!),
    enabled: selectedAccountId !== null,
  });

  // Sync mutation
  const syncMutation = useMutation({
    mutationFn: (accountId: number) => brokerageApi.syncAccount(accountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brokerage-accounts'] });
      queryClient.invalidateQueries({ queryKey: ['brokerage-account-details', selectedAccountId] });
    },
  });

  // Disconnect mutation
  const disconnectMutation = useMutation({
    mutationFn: (accountId: number) => brokerageApi.disconnectBroker(accountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brokerage-accounts'] });
      setSelectedAccountId(null);
    },
  });

  const handleConnect = async (broker: 'alpaca' | 'td_ameritrade' | 'interactive_brokers') => {
    try {
      setConnectingBroker(broker);
      const response = await brokerageApi.connectBroker(broker);
      // Redirect to OAuth URL
      window.location.href = response.authorization_url;
    } catch (error) {
      console.error('Failed to initiate connection:', error);
      alert('Failed to initiate broker connection. Please try again.');
      setConnectingBroker(null);
    }
  };

  const handleSync = async (accountId: number) => {
    await syncMutation.mutateAsync(accountId);
  };

  const handleDisconnect = async (accountId: number) => {
    if (window.confirm('Are you sure you want to disconnect this account? All associated rules will be deactivated.')) {
      await disconnectMutation.mutateAsync(accountId);
    }
  };

  const formatCurrency = (value?: number | null) => {
    if (value === undefined || value === null) return '--';
    if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(2)}M`;
    if (value >= 1_000) return `$${(value / 1_000).toFixed(2)}K`;
    return `$${value.toFixed(2)}`;
  };

  if (loadingAccounts) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  const brokers: Array<{ id: 'alpaca' | 'td_ameritrade' | 'interactive_brokers'; name: string; description: string }> = [
    { id: 'alpaca', name: 'Alpaca', description: 'Commission-free trading API' },
    { id: 'td_ameritrade', name: 'TD Ameritrade', description: 'TD Ameritrade API' },
    { id: 'interactive_brokers', name: 'Interactive Brokers', description: 'Interactive Brokers API' },
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/copy-trading')}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold">Brokerage Accounts</h1>
            <p className="text-gray-400 mt-1">Connect and manage your brokerage accounts</p>
          </div>
        </div>

        {/* Connected Accounts */}
        {accounts && accounts.length > 0 ? (
          <div className="space-y-4">
            {accounts.map((account) => (
              <div
                key={account.id}
                className="bg-white/5 border border-white/10 rounded-lg p-6 cursor-pointer hover:bg-white/10 transition-colors"
                onClick={() => setSelectedAccountId(account.id === selectedAccountId ? null : account.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`w-3 h-3 rounded-full ${account.is_active ? 'bg-green-400' : 'bg-red-400'}`} />
                    <div>
                      <h3 className="text-xl font-semibold capitalize">{account.broker}</h3>
                      <p className="text-sm text-gray-400">
                        {account.account_name || account.account_number}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-sm text-gray-400">Balance</p>
                      <p className="text-lg font-semibold">{formatCurrency(account.balance)}</p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSync(account.id);
                        }}
                        disabled={syncMutation.isPending}
                        className="p-2 hover:bg-white/10 rounded transition-colors disabled:opacity-50"
                        title="Sync Account"
                      >
                        <RefreshCw className={`w-5 h-5 ${syncMutation.isPending ? 'animate-spin' : ''}`} />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDisconnect(account.id);
                        }}
                        disabled={disconnectMutation.isPending}
                        className="p-2 hover:bg-red-500/20 rounded transition-colors disabled:opacity-50"
                        title="Disconnect"
                      >
                        <Unlink className="w-5 h-5 text-red-400" />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Account Details (expanded) */}
                {selectedAccountId === account.id && (
                  <div className="mt-6 pt-6 border-t border-white/10">
                    {loadingDetails ? (
                      <div className="flex justify-center py-8">
                        <LoadingSpinner />
                      </div>
                    ) : accountDetails ? (
                      <div className="space-y-6">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div>
                            <p className="text-sm text-gray-400">Cash Balance</p>
                            <p className="text-2xl font-bold">{formatCurrency(accountDetails.cash_balance)}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-400">Buying Power</p>
                            <p className="text-2xl font-bold">{formatCurrency(account.buying_power)}</p>
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

                        {/* Positions */}
                        {accountDetails.positions.length > 0 && (
                          <div>
                            <h4 className="font-semibold mb-3">Positions ({accountDetails.positions.length})</h4>
                            <div className="overflow-x-auto">
                              <table className="w-full">
                                <thead>
                                  <tr className="border-b border-white/10">
                                    <th className="text-left py-2 px-4 text-sm text-gray-400">Ticker</th>
                                    <th className="text-left py-2 px-4 text-sm text-gray-400">Quantity</th>
                                    <th className="text-left py-2 px-4 text-sm text-gray-400">Market Value</th>
                                    <th className="text-left py-2 px-4 text-sm text-gray-400">P/L</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {accountDetails.positions.map((position, idx) => (
                                    <tr key={idx} className="border-b border-white/5">
                                      <td className="py-2 px-4 font-semibold">{position.ticker}</td>
                                      <td className="py-2 px-4">{position.quantity}</td>
                                      <td className="py-2 px-4">{formatCurrency(position.market_value)}</td>
                                      <td
                                        className={`py-2 px-4 ${
                                          position.unrealized_pl >= 0 ? 'text-green-400' : 'text-red-400'
                                        }`}
                                      >
                                        {formatCurrency(position.unrealized_pl)} (
                                        {position.unrealized_pl_pct.toFixed(2)}%)
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        )}

                        {/* Recent Orders */}
                        {accountDetails.recent_orders.length > 0 && (
                          <div>
                            <h4 className="font-semibold mb-3">Recent Orders</h4>
                            <div className="overflow-x-auto">
                              <table className="w-full">
                                <thead>
                                  <tr className="border-b border-white/10">
                                    <th className="text-left py-2 px-4 text-sm text-gray-400">Ticker</th>
                                    <th className="text-left py-2 px-4 text-sm text-gray-400">Side</th>
                                    <th className="text-left py-2 px-4 text-sm text-gray-400">Quantity</th>
                                    <th className="text-left py-2 px-4 text-sm text-gray-400">Status</th>
                                    <th className="text-left py-2 px-4 text-sm text-gray-400">Time</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {accountDetails.recent_orders.map((order, idx) => (
                                    <tr key={idx} className="border-b border-white/5">
                                      <td className="py-2 px-4 font-semibold">{order.ticker}</td>
                                      <td className="py-2 px-4">
                                        <span
                                          className={`px-2 py-1 rounded text-xs ${
                                            order.side === 'buy'
                                              ? 'bg-green-500/20 text-green-400'
                                              : 'bg-red-500/20 text-red-400'
                                          }`}
                                        >
                                          {order.side.toUpperCase()}
                                        </span>
                                      </td>
                                      <td className="py-2 px-4">{order.quantity}</td>
                                      <td className="py-2 px-4">
                                        <span
                                          className={`px-2 py-1 rounded text-xs ${
                                            order.status === 'filled'
                                              ? 'bg-green-500/20 text-green-400'
                                              : 'bg-yellow-500/20 text-yellow-400'
                                          }`}
                                        >
                                          {order.status}
                                        </span>
                                      </td>
                                      <td className="py-2 px-4 text-sm text-gray-400">
                                        {new Date(order.created_at).toLocaleString()}
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <p className="text-gray-400 text-center py-4">Failed to load account details</p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white/5 border border-white/10 rounded-lg p-12 text-center">
            <p className="text-gray-400 mb-6">No brokerage accounts connected</p>
          </div>
        )}

        {/* Connect New Broker */}
        <div className="bg-white/5 border border-white/10 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Connect New Broker</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {brokers.map((broker) => (
              <button
                key={broker.id}
                onClick={() => handleConnect(broker.id)}
                disabled={connectingBroker === broker.id}
                className="p-4 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors text-left disabled:opacity-50"
              >
                <h3 className="font-semibold mb-1 capitalize">{broker.name}</h3>
                <p className="text-sm text-gray-400 mb-3">{broker.description}</p>
                {connectingBroker === broker.id ? (
                  <div className="flex items-center gap-2 text-purple-400">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Connecting...</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-purple-400">
                    <ExternalLink className="w-4 h-4" />
                    <span className="text-sm">Connect</span>
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

