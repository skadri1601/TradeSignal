import { APIKeyUsage } from '../../types';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip, ReferenceLine } from 'recharts';

export interface APIKeyUsageChartProps {
  usageData: APIKeyUsage[];
  keyId: number;
  rateLimit?: number;
}

export default function APIKeyUsageChart({
  usageData,
  rateLimit,
}: APIKeyUsageChartProps) {
  // Prepare chart data (last 30 days)
  const chartData = usageData
    .slice(-30)
    .map((item) => ({
      date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      requests: item.request_count,
    }));

  // Calculate average usage
  const averageUsage =
    chartData.length > 0
      ? chartData.reduce((sum, item) => sum + item.requests, 0) / chartData.length
      : 0;

  // Calculate peak usage
  const peakUsage = chartData.length > 0 ? Math.max(...chartData.map((item) => item.requests)) : 0;

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
      <div className="mb-6">
        <h3 className="text-lg font-bold text-white mb-2">API Key Usage (Last 30 Days)</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="bg-black/20 rounded-xl p-3 border border-white/5">
            <p className="text-xs text-gray-400 uppercase font-bold mb-1">Average</p>
            <p className="text-xl font-bold text-white">{Math.round(averageUsage).toLocaleString()}</p>
            <p className="text-xs text-gray-500">requests/day</p>
          </div>
          <div className="bg-black/20 rounded-xl p-3 border border-white/5">
            <p className="text-xs text-gray-400 uppercase font-bold mb-1">Peak</p>
            <p className="text-xl font-bold text-purple-400">{peakUsage.toLocaleString()}</p>
            <p className="text-xs text-gray-500">requests/day</p>
          </div>
          {rateLimit && (
            <div className="bg-black/20 rounded-xl p-3 border border-white/5">
              <p className="text-xs text-gray-400 uppercase font-bold mb-1">Rate Limit</p>
              <p className="text-xl font-bold text-yellow-400">{rateLimit.toLocaleString()}</p>
              <p className="text-xs text-gray-500">requests/hour</p>
            </div>
          )}
        </div>
      </div>

      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <XAxis
              dataKey="date"
              tick={{ fill: '#9CA3AF', fontSize: 12 }}
              tickCount={7}
            />
            <YAxis
              tick={{ fill: '#9CA3AF', fontSize: 12 }}
              label={{ value: 'Requests', angle: -90, position: 'insideLeft', fill: '#9CA3AF' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                color: '#fff',
              }}
              formatter={(value: number) => [`${value.toLocaleString()} requests`, 'Usage']}
              labelFormatter={(label) => `Date: ${label}`}
            />
            {rateLimit && (
              <ReferenceLine
                y={rateLimit * 24}
                stroke="#F59E0B"
                strokeDasharray="5 5"
                label={{ value: 'Daily Rate Limit', position: 'top', fill: '#F59E0B' }}
              />
            )}
            <Line
              type="monotone"
              dataKey="requests"
              stroke="#A855F7"
              strokeWidth={2}
              dot={{ fill: '#A855F7', r: 4 }}
              activeDot={{ r: 6, fill: '#A855F7' }}
              name="Requests"
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div className="flex items-center justify-center h-[300px] text-gray-500">
          <p>No usage data available</p>
        </div>
      )}
    </div>
  );
}

