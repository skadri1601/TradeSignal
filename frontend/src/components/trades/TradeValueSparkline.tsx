import { useMemo } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
  Dot,
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
      <div className="h-32 flex items-center justify-center text-sm text-gray-500">
        No value data for the selected filters.
      </div>
    );
  }

  const CustomDot = (props: any) => {
    const { cx, cy, payload } = props;
    return (
      <Dot
        cx={cx}
        cy={cy}
        r={4}
        fill="#3B82F6"
        stroke="#fff"
        strokeWidth={2}
      />
    );
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-semibold text-gray-700 mb-1">{formatDate(label)}</p>
          <p className="text-lg font-bold text-blue-600">{formatCurrency(payload[0].value)}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => {
              const date = new Date(value);
              return `${date.getMonth() + 1}/${date.getDate()}`;
            }}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => formatCurrencyCompact(value)}
            width={80}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="total"
            stroke="#3B82F6"
            strokeWidth={3}
            dot={<CustomDot />}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
