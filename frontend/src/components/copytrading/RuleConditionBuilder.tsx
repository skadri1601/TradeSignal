import { useState } from 'react';
import { RuleCondition } from '../../types';
import { Plus, Trash2 } from 'lucide-react';

export interface RuleConditionBuilderProps {
  conditions: RuleCondition[];
  onChange: (conditions: RuleCondition[]) => void;
  availableInsiderRoles?: string[];
}

export default function RuleConditionBuilder({
  conditions,
  onChange,
  availableInsiderRoles = ['CEO', 'CFO', 'CTO', 'Director', 'Officer', '10% Owner'],
}: RuleConditionBuilderProps) {
  const [searchTerm, setSearchTerm] = useState('');

  const conditionTypes = [
    { value: 'insider_role', label: 'Insider Role' },
    { value: 'trade_value', label: 'Trade Value' },
    { value: 'trade_type', label: 'Trade Type' },
    { value: 'ticker', label: 'Ticker Symbol' },
    { value: 'company_sector', label: 'Company Sector' },
  ];

  const operators = [
    { value: 'equals', label: 'Equals' },
    { value: 'greater_than', label: 'Greater Than' },
    { value: 'less_than', label: 'Less Than' },
    { value: 'contains', label: 'Contains' },
    { value: 'in', label: 'In' },
  ];

  const addCondition = () => {
    const newCondition: RuleCondition = {
      type: 'insider_role',
      operator: 'equals',
      value: '',
      logic: conditions.length > 0 ? 'AND' : undefined,
    };
    onChange([...conditions, newCondition]);
  };

  const removeCondition = (index: number) => {
    onChange(conditions.filter((_, i) => i !== index));
  };

  const updateCondition = (index: number, updates: Partial<RuleCondition>) => {
    const updated = [...conditions];
    updated[index] = { ...updated[index], ...updates };
    onChange(updated);
  };

  const updateLogic = (index: number, logic: 'AND' | 'OR') => {
    const updated = [...conditions];
    updated[index] = { ...updated[index], logic };
    onChange(updated);
  };

  const filteredRoles = availableInsiderRoles.filter((role) =>
    role.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const renderValueInput = (condition: RuleCondition, index: number) => {
    switch (condition.type) {
      case 'insider_role':
        return (
          <select
            value={typeof condition.value === 'string' ? condition.value : ''}
            onChange={(e) => updateCondition(index, { value: e.target.value })}
            className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="">Select role...</option>
            {filteredRoles.map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}
          </select>
        );

      case 'trade_value':
        return (
          <input
            type="number"
            value={typeof condition.value === 'number' ? condition.value : ''}
            onChange={(e) => updateCondition(index, { value: parseFloat(e.target.value) || 0 })}
            placeholder="Enter amount..."
            className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        );

      case 'trade_type':
        return (
          <select
            value={typeof condition.value === 'string' ? condition.value : ''}
            onChange={(e) => updateCondition(index, { value: e.target.value })}
            className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="">Select type...</option>
            <option value="BUY">Buy</option>
            <option value="SELL">Sell</option>
          </select>
        );

      case 'ticker':
        return (
          <input
            type="text"
            value={typeof condition.value === 'string' ? condition.value : ''}
            onChange={(e) => updateCondition(index, { value: e.target.value.toUpperCase() })}
            placeholder="e.g., AAPL, TSLA"
            className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 uppercase"
            maxLength={10}
          />
        );

      case 'company_sector':
        return (
          <input
            type="text"
            value={typeof condition.value === 'string' ? condition.value : ''}
            onChange={(e) => updateCondition(index, { value: e.target.value })}
            placeholder="e.g., Technology, Healthcare"
            className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-white">Rule Conditions</h3>
        <button
          onClick={addCondition}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors flex items-center gap-2 text-sm font-medium"
        >
          <Plus className="w-4 h-4" />
          Add Condition
        </button>
      </div>

      {conditions.length === 0 ? (
        <div className="text-center py-8 bg-gray-900/30 rounded-xl border border-white/10">
          <p className="text-gray-400">No conditions added yet</p>
          <p className="text-sm text-gray-500 mt-1">Click "Add Condition" to get started</p>
        </div>
      ) : (
        <div className="space-y-3">
          {conditions.map((condition, index) => (
            <div key={index} className="bg-gray-900/30 rounded-xl border border-white/10 p-4">
              <div className="flex items-start gap-3">
                {/* Logic Connector */}
                {index > 0 && (
                  <div className="flex flex-col items-center gap-2 pt-2">
                    <select
                      value={condition.logic || 'AND'}
                      onChange={(e) => updateLogic(index, e.target.value as 'AND' | 'OR')}
                      className="px-2 py-1 bg-black/50 border border-white/10 rounded text-white text-xs font-bold focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="AND">AND</option>
                      <option value="OR">OR</option>
                    </select>
                    <div className="w-px h-8 bg-purple-500/30"></div>
                  </div>
                )}

                {/* Condition Card */}
                <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-3">
                  {/* Condition Type */}
                  <select
                    value={condition.type}
                    onChange={(e) =>
                      updateCondition(index, {
                        type: e.target.value as RuleCondition['type'],
                        value: '',
                      })
                    }
                    className="px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    {conditionTypes.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>

                  {/* Operator */}
                  <select
                    value={condition.operator}
                    onChange={(e) =>
                      updateCondition(index, {
                        operator: e.target.value as RuleCondition['operator'],
                      })
                    }
                    className="px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    {operators.map((op) => (
                      <option key={op.value} value={op.value}>
                        {op.label}
                      </option>
                    ))}
                  </select>

                  {/* Value Input */}
                  <div className="md:col-span-2">
                    {condition.type === 'insider_role' && (
                      <div className="relative">
                        <input
                          type="text"
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          placeholder="Search roles..."
                          className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 mb-2"
                        />
                      </div>
                    )}
                    {renderValueInput(condition, index)}
                  </div>
                </div>

                {/* Remove Button */}
                <button
                  onClick={() => removeCondition(index)}
                  className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors flex-shrink-0"
                  aria-label="Remove condition"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Preview Panel */}
      {conditions.length > 0 && (
        <div className="mt-6 p-4 bg-black/20 rounded-xl border border-purple-500/30">
          <h4 className="text-sm font-semibold text-purple-300 mb-2 uppercase">Condition Preview</h4>
          <p className="text-sm text-gray-300">
            {conditions.map((c, i) => (
              <span key={i}>
                {i > 0 && <span className="text-purple-400 font-bold mx-2">{c.logic || 'AND'}</span>}
                <span className="font-medium">{c.type.replace('_', ' ')}</span>
                <span className="mx-1">{c.operator}</span>
                <span className="text-purple-300">
                  {typeof c.value === 'string' ? c.value : typeof c.value === 'number' ? `$${c.value.toLocaleString()}` : JSON.stringify(c.value)}
                </span>
              </span>
            ))}
          </p>
        </div>
      )}
    </div>
  );
}

