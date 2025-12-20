import { useState } from 'react';
import { CopyTradeSettings } from '../../types';
import { Save, CheckCircle2 } from 'lucide-react';
import toast from 'react-hot-toast';

export interface CopyTradeSettingsFormProps {
  settings: CopyTradeSettings;
  onSave: (settings: CopyTradeSettings) => Promise<void>;
}

export default function CopyTradeSettingsForm({
  settings: initialSettings,
  onSave,
}: CopyTradeSettingsFormProps) {
  const [settings, setSettings] = useState<CopyTradeSettings>(initialSettings);
  const [isSaving, setIsSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (settings.max_trade_size <= 0) {
      newErrors.max_trade_size = 'Max trade size must be greater than 0';
    }

    if (settings.max_daily_trades <= 0) {
      newErrors.max_daily_trades = 'Max daily trades must be greater than 0';
    }

    if (settings.auto_sell_enabled && settings.auto_sell_on_loss_pct !== null) {
      if (settings.auto_sell_on_loss_pct <= 0 || settings.auto_sell_on_loss_pct >= 100) {
        newErrors.auto_sell_on_loss_pct = 'Auto-sell percentage must be between 0 and 100';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSaving(true);
    try {
      await onSave(settings);
      toast.success('Settings saved successfully!', {
        icon: <CheckCircle2 className="w-5 h-5 text-green-400" />,
      });
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <form onSubmit={handleSave} className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
      <h2 className="text-2xl font-bold text-white mb-6">Copy Trading Settings</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Max Trade Size */}
        <div>
          <label htmlFor="max-trade-size" className="block text-sm font-medium text-gray-300 mb-2">
            Max Trade Size ($)
          </label>
          <input
            id="max-trade-size"
            type="number"
            value={settings.max_trade_size}
            onChange={(e) =>
              setSettings({ ...settings, max_trade_size: parseFloat(e.target.value) || 0 })
            }
            min="0"
            step="0.01"
            className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            placeholder="0.00"
          />
          {errors.max_trade_size && (
            <p className="text-sm text-red-400 mt-1">{errors.max_trade_size}</p>
          )}
        </div>

        {/* Max Daily Trades */}
        <div>
          <label htmlFor="max-daily-trades" className="block text-sm font-medium text-gray-300 mb-2">
            Max Daily Trades
          </label>
          <input
            id="max-daily-trades"
            type="number"
            value={settings.max_daily_trades}
            onChange={(e) =>
              setSettings({ ...settings, max_daily_trades: parseInt(e.target.value) || 0 })
            }
            min="1"
            className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            placeholder="0"
          />
          {errors.max_daily_trades && (
            <p className="text-sm text-red-400 mt-1">{errors.max_daily_trades}</p>
          )}
        </div>

        {/* Risk Tolerance Slider */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Risk Tolerance: <span className="text-purple-400 capitalize">{settings.risk_tolerance}</span>
          </label>
          <div className="flex items-center gap-4">
            <span className="text-xs text-gray-400">Conservative</span>
            <input
              type="range"
              min="0"
              max="2"
              value={
                settings.risk_tolerance === 'conservative' ? 0 : settings.risk_tolerance === 'moderate' ? 1 : 2
              }
              onChange={(e) => {
                const value = parseInt(e.target.value);
                const risk: CopyTradeSettings['risk_tolerance'] =
                  value === 0 ? 'conservative' : value === 1 ? 'moderate' : 'aggressive';
                setSettings({ ...settings, risk_tolerance: risk });
              }}
              className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-600"
            />
            <span className="text-xs text-gray-400">Aggressive</span>
          </div>
          <div className="flex items-center justify-between mt-1 text-xs text-gray-500">
            <span>Lower risk, smaller positions</span>
            <span>Higher risk, larger positions</span>
          </div>
        </div>

        {/* Auto-Sell Toggle */}
        <div className="md:col-span-2">
          <div className="flex items-center justify-between p-4 bg-black/20 rounded-xl border border-white/5">
            <div>
              <label htmlFor="auto-sell-toggle" className="block text-sm font-medium text-white mb-1">
                Auto-Sell on Loss
              </label>
              <p className="text-xs text-gray-400">
                Automatically sell positions when they reach a certain loss percentage
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                id="auto-sell-toggle"
                type="checkbox"
                checked={settings.auto_sell_enabled}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    auto_sell_enabled: e.target.checked,
                    auto_sell_on_loss_pct: e.target.checked ? settings.auto_sell_on_loss_pct || 10 : null,
                  })
                }
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-purple-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>

          {settings.auto_sell_enabled && (
            <div className="mt-3">
              <label htmlFor="auto-sell-pct" className="block text-sm font-medium text-gray-300 mb-2">
                Auto-Sell Loss Percentage (%)
              </label>
              <input
                id="auto-sell-pct"
                type="number"
                value={settings.auto_sell_on_loss_pct || ''}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    auto_sell_on_loss_pct: parseFloat(e.target.value) || null,
                  })
                }
                min="0"
                max="100"
                step="0.1"
                className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                placeholder="10.0"
              />
              {errors.auto_sell_on_loss_pct && (
                <p className="text-sm text-red-400 mt-1">{errors.auto_sell_on_loss_pct}</p>
              )}
            </div>
          )}
        </div>

        {/* Notification Preferences */}
        <div className="md:col-span-2">
          <h3 className="text-sm font-medium text-white mb-3">Notification Preferences</h3>
          <div className="space-y-3">
            <label className="flex items-center gap-3 p-3 bg-black/20 rounded-lg border border-white/5 cursor-pointer hover:bg-black/30 transition-colors">
              <input
                type="checkbox"
                checked={settings.notifications_enabled}
                onChange={(e) =>
                  setSettings({ ...settings, notifications_enabled: e.target.checked })
                }
                className="w-4 h-4 text-purple-600 bg-black/50 border-white/10 rounded focus:ring-purple-500"
              />
              <span className="text-sm text-white">Enable Notifications</span>
            </label>

            {settings.notifications_enabled && (
              <>
                <label className="flex items-center gap-3 p-3 bg-black/20 rounded-lg border border-white/5 cursor-pointer hover:bg-black/30 transition-colors">
                  <input
                    type="checkbox"
                    checked={settings.email_notifications}
                    onChange={(e) =>
                      setSettings({ ...settings, email_notifications: e.target.checked })
                    }
                    className="w-4 h-4 text-purple-600 bg-black/50 border-white/10 rounded focus:ring-purple-500"
                  />
                  <span className="text-sm text-white">Email Notifications</span>
                </label>

                <label className="flex items-center gap-3 p-3 bg-black/20 rounded-lg border border-white/5 cursor-pointer hover:bg-black/30 transition-colors">
                  <input
                    type="checkbox"
                    checked={settings.push_notifications}
                    onChange={(e) =>
                      setSettings({ ...settings, push_notifications: e.target.checked })
                    }
                    className="w-4 h-4 text-purple-600 bg-black/50 border-white/10 rounded focus:ring-purple-500"
                  />
                  <span className="text-sm text-white">Push Notifications</span>
                </label>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex items-center justify-end gap-3 pt-6 mt-6 border-t border-white/10">
        <button
          type="submit"
          disabled={isSaving}
          className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center gap-2"
        >
          <Save className="w-5 h-5" />
          {isSaving ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </form>
  );
}

