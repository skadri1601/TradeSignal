import { useState } from 'react';
import { CopyTradeRule } from '../../types';
import { ChevronDown, ChevronUp, Edit2, Trash2, TrendingUp, TrendingDown } from 'lucide-react';

export interface CopyTradeRuleCardProps {
  rule: CopyTradeRule;
  onEdit: () => void;
  onDelete: () => void;
  onToggle: (isActive: boolean) => void;
}

export default function CopyTradeRuleCard({
  rule,
  onEdit,
  onDelete,
  onToggle,
}: CopyTradeRuleCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const successRate =
    rule.total_trades_executed > 0
      ? ((rule.total_trades_executed - Math.abs(rule.total_profit_loss) / 100) / rule.total_trades_executed) * 100
      : 0;

  const getConditionSummary = (): string => {
    if (rule.source_filter) {
      const filters = rule.source_filter;
      const parts: string[] = [];

      if (filters.insider_role) {
        parts.push(`Insider Role: ${filters.insider_role}`);
      }
      if (filters.min_value) {
        parts.push(`Min Value: $${filters.min_value.toLocaleString()}`);
      }
      if (filters.transaction_type) {
        parts.push(`Type: ${filters.transaction_type}`);
      }

      return parts.length > 0 ? parts.join(', ') : 'All trades';
    }
    return 'All trades';
  };

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-bold text-white">{rule.rule_name}</h3>
            <span
              className={`px-2 py-0.5 text-xs rounded-full font-medium ${
                rule.is_active
                  ? 'bg-green-500/20 text-green-300 border border-green-500/30'
                  : 'bg-gray-500/20 text-gray-300 border border-gray-500/30'
              }`}
            >
              {rule.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
          <p className="text-sm text-gray-400">{getConditionSummary()}</p>
        </div>

        {/* Toggle Switch */}
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={rule.is_active}
            onChange={(e) => onToggle(e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-purple-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
        </label>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div className="bg-black/20 rounded-xl p-3 border border-white/5">
          <p className="text-xs text-gray-400 uppercase font-bold mb-1">Trades Executed</p>
          <p className="text-lg font-bold text-white">{rule.total_trades_executed}</p>
        </div>
        <div className="bg-black/20 rounded-xl p-3 border border-white/5">
          <p className="text-xs text-gray-400 uppercase font-bold mb-1">P/L</p>
          <p
            className={`text-lg font-bold flex items-center gap-1 ${
              rule.total_profit_loss >= 0 ? 'text-green-400' : 'text-red-400'
            }`}
          >
            {rule.total_profit_loss >= 0 ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            ${Math.abs(rule.total_profit_loss).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>
        <div className="bg-black/20 rounded-xl p-3 border border-white/5">
          <p className="text-xs text-gray-400 uppercase font-bold mb-1">Success Rate</p>
          <p className="text-lg font-bold text-white">{successRate.toFixed(1)}%</p>
        </div>
        <div className="bg-black/20 rounded-xl p-3 border border-white/5">
          <p className="text-xs text-gray-400 uppercase font-bold mb-1">Source</p>
          <p className="text-lg font-bold text-purple-400 capitalize">{rule.source_type}</p>
        </div>
      </div>

      {/* Expand/Collapse Button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-center gap-2 py-2 text-sm text-gray-400 hover:text-white transition-colors mb-4"
      >
        {isExpanded ? (
          <>
            <span>Show Less</span>
            <ChevronUp className="w-4 h-4" />
          </>
        ) : (
          <>
            <span>Show Details</span>
            <ChevronDown className="w-4 h-4" />
          </>
        )}
      </button>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="pt-4 border-t border-white/10 space-y-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-gray-400 uppercase font-bold mb-1">Position Size</p>
              <p className="text-sm text-white">
                {rule.position_size_type === 'percentage'
                  ? `${rule.position_size_value}%`
                  : rule.position_size_type === 'fixed_dollar'
                  ? `$${rule.position_size_value.toLocaleString()}`
                  : `${rule.position_size_value} shares`}
              </p>
            </div>
            {rule.max_position_size && (
              <div>
                <p className="text-xs text-gray-400 uppercase font-bold mb-1">Max Position</p>
                <p className="text-sm text-white">${rule.max_position_size.toLocaleString()}</p>
              </div>
            )}
            {rule.max_daily_trades && (
              <div>
                <p className="text-xs text-gray-400 uppercase font-bold mb-1">Max Daily Trades</p>
                <p className="text-sm text-white">{rule.max_daily_trades}</p>
              </div>
            )}
            {rule.stop_loss_pct && (
              <div>
                <p className="text-xs text-gray-400 uppercase font-bold mb-1">Stop Loss</p>
                <p className="text-sm text-white">{rule.stop_loss_pct}%</p>
              </div>
            )}
            {rule.take_profit_pct && (
              <div>
                <p className="text-xs text-gray-400 uppercase font-bold mb-1">Take Profit</p>
                <p className="text-sm text-white">{rule.take_profit_pct}%</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex items-center gap-3 pt-4 border-t border-white/10">
        <button
          onClick={onEdit}
          className="flex-1 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors flex items-center justify-center gap-2 font-medium"
        >
          <Edit2 className="w-4 h-4" />
          Edit
        </button>
        <button
          onClick={onDelete}
          className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-500 transition-colors flex items-center justify-center gap-2 font-medium"
        >
          <Trash2 className="w-4 h-4" />
          Delete
        </button>
      </div>
    </div>
  );
}

