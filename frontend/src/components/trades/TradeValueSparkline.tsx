import { useMemo } from 'react';
import {
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
  Area,
  AreaChart,
} from 'recharts';
import type { Trade } from '../../types';
import { formatCurrency, formatCurrencyCompact, formatDate } from '../../utils/formatters';

interface TradeValueSparklineProps {
  trades: Trade[];
}

export default function TradeValueSparkline({ trades }: TradeValueSparklineProps) {
  const chartData = useMemo(() => {
    const totals = new Map<string, number>();

    const parseNumeric = (input: string | number | null | undefined): number | null => {
      if (input === null || input === undefined) {
        return null;
      }
      if (typeof input === 'string' && input.trim() === '') {
        return null;
      }
      const numeric = typeof input === 'string' ? Number(input) : input;
      return Number.isFinite(numeric) ? numeric : null;
    };

    trades.forEach((trade) => {
      const dateKey = trade.transaction_date;

      let value = 0;
      const shares = parseNumeric(trade.shares);
      const price = parseNumeric(trade.price_per_share);
      const total = parseNumeric(trade.total_value);

      if (Number.isFinite(total) && total !== null) {
        value = total;
      } else if (Number.isFinite(shares) && shares && Number.isFinite(price) && price !== null) {
        value = shares * price;
      } else {
        value = 0;
      }

      if (!totals.has(dateKey)) {
        totals.set(dateKey, 0);
      }

      totals.set(dateKey, totals.get(dateKey)! + value);
    });

    return Array.from(totals.entries())
      .map(([date, total]) => ({ date, total }))
      .sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0));
  }, [trades]);

  if (chartData.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center border-2 border-dashed border-gray-300 rounded-xl bg-gray-50">
        <div className="text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p className="mt-2 text-sm font-medium text-gray-900">No trade value data</p>
          <p className="text-sm text-gray-500">Try adjusting your filters to see the trend</p>
        </div>
      </div>
    );
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white/95 backdrop-blur-sm p-4 border border-gray-200 rounded-xl shadow-xl">
          <p className="text-xs font-medium text-gray-500 mb-1">{formatDate(label)}</p>
          <p className="text-xl font-bold text-blue-600">{formatCurrency(payload[0].value)}</p>
          <div className="mt-2 flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span className="text-xs text-gray-600">Total Trade Value</span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-72 p-4 bg-gradient-to-br from-blue-50/50 to-white rounded-xl">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 10, bottom: 10 }}>
          <defs>
            <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: '#6B7280' }}
            tickFormatter={(value) => {
              const date = new Date(value);
              return `${date.getMonth() + 1}/${date.getDate()}`;
            }}
            interval="preserveStartEnd"
            axisLine={{ stroke: '#E5E7EB' }}
            tickLine={{ stroke: '#E5E7EB' }}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#6B7280' }}
            tickFormatter={(value) => formatCurrencyCompact(value)}
            width={70}
            axisLine={{ stroke: '#E5E7EB' }}
            tickLine={{ stroke: '#E5E7EB' }}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#3B82F6', strokeWidth: 1, strokeDasharray: '5 5' }} />
          <Area
            type="monotone"
            dataKey="total"
            stroke="#3B82F6"
            strokeWidth={3}
            fill="url(#colorTotal)"
            dot={{ r: 4, fill: '#3B82F6', stroke: '#fff', strokeWidth: 2 }}
            activeDot={{ r: 6, fill: '#2563EB', stroke: '#fff', strokeWidth: 3 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
