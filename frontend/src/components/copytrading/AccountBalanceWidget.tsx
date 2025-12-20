import { useState, useEffect } from 'react';
import { BrokerageAccount } from '../../types';
import { RefreshCw, TrendingUp, TrendingDown } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';

export interface AccountBalanceWidgetProps {
  account: BrokerageAccount;
  balanceHistory?: Array<{ date: string; balance: number }>;
  onSync?: () => void;
}

export default function AccountBalanceWidget({
  account,
  balanceHistory = [],
  onSync,
}: AccountBalanceWidgetProps) {
  const [isSyncing, setIsSyncing] = useState(false);
  const [animatedBalance, setAnimatedBalance] = useState(account.account_balance || 0);

  // Animate balance number
  useEffect(() => {
    const target = account.account_balance || 0;
    const duration = 1000;
    const steps = 30;
    const increment = (target - animatedBalance) / steps;
    let current = animatedBalance;
    let step = 0;

    const timer = setInterval(() => {
      step++;
      current += increment;
      if (step >= steps || Math.abs(current - target) < 0.01) {
        setAnimatedBalance(target);
        clearInterval(timer);
      } else {
        setAnimatedBalance(current);
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [account.account_balance]);

  const handleSync = async () => {
    if (!onSync) return;
    setIsSyncing(true);
    try {
      await onSync();
    } finally {
      setIsSyncing(false);
    }
  };

  // Prepare chart data (last 30 days)
  const chartData = balanceHistory
    .slice(-30)
    .map((item) => ({
      date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      balance: item.balance,
    }));

  const trend = balanceHistory.length >= 2
    ? balanceHistory[balanceHistory.length - 1].balance - balanceHistory[0].balance
    : 0;

  const trendPercentage = account.account_balance && trend !== 0
    ? ((trend / (account.account_balance - trend)) * 100).toFixed(2)
    : '0.00';

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10 p-6 relative overflow-hidden">
      {/* Glass morphism effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-blue-500/5 pointer-events-none" />
      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-white">Account Balance</h3>
          {onSync && (
            <button
              onClick={handleSync}
              disabled={isSyncing}
              className="p-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors disabled:opacity-50"
              aria-label="Sync balance"
            >
              <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin' : ''}`} />
            </button>
          )}
        </div>

        {/* Total Balance */}
        <div className="mb-6">
          <p className="text-sm text-gray-400 uppercase font-bold mb-2">Total Balance</p>
          <p className="text-4xl font-bold text-white">
            ${animatedBalance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          {trend !== 0 && (
            <div
              className={`flex items-center gap-1 mt-2 ${
                trend >= 0 ? 'text-green-400' : 'text-red-400'
              }`}
            >
              {trend >= 0 ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
              <span className="text-sm font-semibold">
                {trend >= 0 ? '+' : ''}
                {trendPercentage}% ({trend >= 0 ? '+' : ''}
                ${Math.abs(trend).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })})
              </span>
            </div>
          )}
        </div>

        {/* Buying Power */}
        {account.buying_power && (
          <div className="mb-6 p-4 bg-black/20 rounded-xl border border-white/5">
            <p className="text-xs text-gray-400 uppercase font-bold mb-1">Buying Power</p>
            <p className="text-2xl font-bold text-green-400">
              ${account.buying_power.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
          </div>
        )}

        {/* Cash vs Invested Breakdown */}
        {account.account_balance && account.buying_power && (
          <div className="mb-6 space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">Cash</span>
              <span className="text-white font-medium">
                ${(account.buying_power).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">Invested</span>
              <span className="text-white font-medium">
                ${(account.account_balance - account.buying_power).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </div>
            <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-purple-500 to-blue-500"
                style={{
                  width: `${((account.account_balance - account.buying_power) / account.account_balance) * 100}%`,
                }}
              />
            </div>
          </div>
        )}

        {/* Mini Chart */}
        {chartData.length > 0 && (
          <div className="mt-6">
            <p className="text-xs text-gray-400 uppercase font-bold mb-3">Balance History (Last 30 Days)</p>
            <ResponsiveContainer width="100%" height={120}>
              <LineChart data={chartData}>
                <XAxis
                  dataKey="date"
                  tick={{ fill: '#9CA3AF', fontSize: 10 }}
                  tickCount={5}
                />
                <YAxis hide />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1F2937',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '8px',
                    color: '#fff',
                  }}
                  formatter={(value: number) => `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                />
                <Line
                  type="monotone"
                  dataKey="balance"
                  stroke="#A855F7"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, fill: '#A855F7' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}

