/**
 * Copy Trading Rules Management Page
 * Create, edit, and manage copy trade rules
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { brokerageApi } from '../api/brokerage';
import type { CopyTradeRule } from '../api/brokerage';
import { Plus, Edit, Trash2, ToggleLeft, ToggleRight, ArrowLeft } from 'lucide-react';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function CopyTradingRulesPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [filter, setFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Fetch rules
  const { data: rules, isLoading: loadingRules } = useQuery<CopyTradeRule[]>({
    queryKey: ['copy-trade-rules'],
    queryFn: () => brokerageApi.getRules(),
  });

  // Toggle rule mutation
  const toggleMutation = useMutation({
    mutationFn: (ruleId: number) => brokerageApi.toggleRule(ruleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['copy-trade-rules'] });
    },
  });

  // Delete rule mutation
  const deleteMutation = useMutation({
    mutationFn: (ruleId: number) => brokerageApi.deleteRule(ruleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['copy-trade-rules'] });
    },
  });

  const filteredRules =
    rules?.filter((rule) => {
      if (filter === 'active') return rule.is_active;
      if (filter === 'inactive') return !rule.is_active;
      return true;
    }) || [];

  const handleToggle = async (ruleId: number) => {
    if (window.confirm('Are you sure you want to toggle this rule?')) {
      await toggleMutation.mutateAsync(ruleId);
    }
  };

  const handleDelete = async (ruleId: number) => {
    if (window.confirm('Are you sure you want to delete this rule? This action cannot be undone.')) {
      await deleteMutation.mutateAsync(ruleId);
    }
  };

  if (loadingRules) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/copy-trading')}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-3xl font-bold">Copy Trade Rules</h1>
              <p className="text-gray-400 mt-1">Manage your automated trading rules</p>
            </div>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center gap-2 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Create Rule
          </button>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 border-b border-white/10">
          {(['all', 'active', 'inactive'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 capitalize border-b-2 transition-colors ${
                filter === f
                  ? 'border-purple-500 text-purple-400'
                  : 'border-transparent text-gray-400 hover:text-white'
              }`}
            >
              {f} ({f === 'all' ? rules?.length || 0 : filteredRules.length})
            </button>
          ))}
        </div>

        {/* Rules List */}
        {filteredRules.length > 0 ? (
          <div className="space-y-4">
            {filteredRules.map((rule) => (
              <div
                key={rule.id}
                className="bg-white/5 border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-semibold">{rule.name}</h3>
                      <span
                        className={`px-2 py-1 rounded text-xs ${
                          rule.is_active
                            ? 'bg-green-500/20 text-green-400'
                            : 'bg-gray-500/20 text-gray-400'
                        }`}
                      >
                        {rule.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    {rule.description && (
                      <p className="text-gray-400 mb-4">{rule.description}</p>
                    )}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-400">Account</p>
                        <p className="font-semibold">{rule.brokerage_account_name || 'Unknown'}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-400">Copy Percentage</p>
                        <p className="font-semibold">{rule.copy_percentage}%</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-400">Trades Executed</p>
                        <p className="font-semibold">{rule.trades_executed}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-400">Total Volume</p>
                        <p className="font-semibold">${rule.total_volume.toLocaleString()}</p>
                      </div>
                    </div>
                    <div className="mb-4">
                      <p className="text-sm text-gray-400 mb-2">Conditions:</p>
                      <div className="flex flex-wrap gap-2">
                        {Array.isArray(rule.conditions) && rule.conditions.length > 0 ? (
                          rule.conditions.map((condition: any, idx: number) => (
                            <span
                              key={idx}
                              className="px-2 py-1 bg-white/10 rounded text-xs"
                            >
                              {condition.field} {condition.operator} {String(condition.value)}
                            </span>
                          ))
                        ) : (
                          <span className="text-gray-500 text-sm">No conditions</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => handleToggle(rule.id)}
                      className="p-2 hover:bg-white/10 rounded transition-colors"
                      title={rule.is_active ? 'Deactivate' : 'Activate'}
                    >
                      {rule.is_active ? (
                        <ToggleRight className="w-5 h-5 text-green-400" />
                      ) : (
                        <ToggleLeft className="w-5 h-5 text-gray-400" />
                      )}
                    </button>
                    <button
                      onClick={() => {
                        // TODO: Implement edit modal
                        alert('Edit functionality coming soon');
                      }}
                      className="p-2 hover:bg-white/10 rounded transition-colors"
                      title="Edit"
                    >
                      <Edit className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleDelete(rule.id)}
                      className="p-2 hover:bg-red-500/20 rounded transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-5 h-5 text-red-400" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white/5 border border-white/10 rounded-lg p-12 text-center">
            <p className="text-gray-400 mb-4">
              {filter === 'all'
                ? 'No rules created yet'
                : filter === 'active'
                ? 'No active rules'
                : 'No inactive rules'}
            </p>
            {filter === 'all' && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
              >
                Create Your First Rule
              </button>
            )}
          </div>
        )}

        {/* Create Rule Modal (Simplified - full implementation would be more complex) */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-[#1a1a1a] border border-white/10 rounded-lg p-6 max-w-2xl w-full mx-4">
              <h2 className="text-2xl font-bold mb-4">Create Copy Trade Rule</h2>
              <p className="text-gray-400 mb-6">
                Rule creation form coming soon. For now, please use the API directly or contact support.
              </p>
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-white/20 hover:bg-white/10 rounded-lg transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

