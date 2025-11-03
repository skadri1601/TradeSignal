import { useMemo } from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from 'recharts';
import type { TradeStats } from '../../types';
import { formatNumber, formatCurrencyCompact } from '../../utils/formatters';

interface TradePieChartProps {
  stats: TradeStats | undefined;
  mode: 'count' | 'value';
}

export default function TradePieChart({ stats, mode }: TradePieChartProps) {
  const chartData = useMemo(() => {
    if (!stats) return [];

    if (mode === 'count') {
      return [
        { name: 'Buy Trades', value: stats.total_buys, color: '#10b981' },
        { name: 'Sell Trades', value: stats.total_sells, color: '#ef4444' },
      ];
    } else {
      return [
        { name: 'Buy Volume', value: stats.total_buy_value, color: '#10b981' },
        { name: 'Sell Volume', value: stats.total_sell_value, color: '#ef4444' },
      ];
    }
  }, [stats, mode]);

  const total = useMemo(() => {
    return chartData.reduce((sum, item) => sum + item.value, 0);
  }, [chartData]);

  // Always use bar chart for consistency - looks more professional
  const useBarChart = true;

  const formatValue = (value: number) => {
    if (mode === 'count') {
      return formatNumber(value);
    } else {
      return formatCurrencyCompact(value);
    }
  };

  const renderCustomLabel = ({
    cx,
    cy,
    midAngle,
    innerRadius,
    outerRadius,
    percent,
  }: any) => {
    // Don't show label if slice is too small (< 5%)
    if (percent < 0.05) return null;

    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        className="text-sm font-semibold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900">{data.name}</p>
          <p className="text-lg font-bold" style={{ color: data.payload.color }}>
            {formatValue(data.value)}
          </p>
          <p className="text-xs text-gray-500">
            {((data.value / total) * 100).toFixed(1)}% of total
          </p>
        </div>
      );
    }
    return null;
  };

  if (!stats || total === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        No data available
      </div>
    );
  }

  // Use bar chart for consistent, professional look
  if (useBarChart) {
    return (
      <div className="flex flex-col gap-3 p-4">
        {chartData.map((item, index) => {
          const percent = ((item.value / total) * 100).toFixed(1);
          return (
            <div key={index} className="flex items-center justify-between p-4 rounded-lg border border-gray-200 bg-gradient-to-r from-white to-gray-50 hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3 min-w-[140px]">
                <div
                  className="w-4 h-4 rounded-full shadow-sm"
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-sm font-semibold text-gray-800">{item.name}</span>
              </div>
              <div className="flex items-center gap-6 flex-1">
                <div className="flex-1 bg-gray-200 rounded-full h-3 max-w-md shadow-inner">
                  <div
                    className="h-3 rounded-full transition-all duration-500 shadow-sm"
                    style={{
                      backgroundColor: item.color,
                      width: `${percent}%`
                    }}
                  />
                </div>
                <div className="text-right min-w-[140px]">
                  <div className="text-xl font-bold text-gray-900">{formatValue(item.value)}</div>
                  <div className="text-sm text-gray-600 font-medium">{percent}% of total</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={renderCustomLabel}
          outerRadius={100}
          fill="#8884d8"
          dataKey="value"
          minAngle={15}
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend
          verticalAlign="bottom"
          height={36}
          formatter={(value, entry: any) => (
            <span className="text-sm text-gray-700">
              {value}: <strong>{formatValue(entry.payload.value)}</strong>
            </span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
