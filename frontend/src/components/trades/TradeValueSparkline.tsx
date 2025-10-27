import { useMemo } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { Trade } from '../../types';
import { formatCurrency } from '../../utils/formatters';

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

  return (
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <XAxis dataKey="date" tick={{ fontSize: 12 }} tickFormatter={(value) => value.slice(5)} interval="preserveEnd" />
          <YAxis hide domain={['auto', 'auto']} />
          <Tooltip
            cursor={{ stroke: '#CBD5F5' }}
            formatter={(value: number) => formatCurrency(value)}
            labelFormatter={(label: string) => label}
          />
          <Line type="monotone" dataKey="total" stroke="#3B82F6" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
