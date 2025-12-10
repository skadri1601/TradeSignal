import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fedApi } from '../api/fed';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { LegalDisclaimer } from '../components/LegalDisclaimer';
import { Calendar, TrendingUp, DollarSign, Users, LineChart } from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

export default function FedCalendarPage() {
  const [rateHistoryDays, setRateHistoryDays] = useState(365);

  const { data: calendar, isLoading: calendarLoading } = useQuery({
    queryKey: ['fed-calendar'],
    queryFn: () => fedApi.getCalendar(6),
  });

  const { data: interestRate, isLoading: rateLoading } = useQuery({
    queryKey: ['fed-interest-rate'],
    queryFn: () => fedApi.getInterestRate(),
  });

  const { data: indicators, isLoading: indicatorsLoading } = useQuery({
    queryKey: ['fed-indicators'],
    queryFn: () => fedApi.getEconomicIndicators(),
  });

  // Fetch rate history for the chart
  const { data: rateHistory, isLoading: historyLoading } = useQuery({
    queryKey: ['fed-rate-history', rateHistoryDays],
    queryFn: () => fedApi.getRateHistory(rateHistoryDays),
  });

  if (calendarLoading || rateLoading || indicatorsLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner />
      </div>
    );
  }

  // Format chart data (reverse to show oldest first)
  const chartData = rateHistory?.history?.slice().reverse().map((point) => ({
    date: new Date(point.date).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
    rate: point.rate,
    fullDate: point.date,
  })) || [];

  const upcomingEvents = calendar?.events || [];

  // Calculate days until dynamically based on current date
  const calculateDaysUntil = (eventDate: string): number => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const event = new Date(eventDate);
    event.setHours(0, 0, 0, 0);
    const diffTime = event.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays >= 0 ? diffDays : 0;
  };

  return (
    <div className="space-y-6">
      <LegalDisclaimer />

      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Federal Reserve Calendar</h1>
        <p className="mt-2 text-gray-400">
          Track FOMC meetings, rate decisions, and economic data releases
        </p>
      </div>

      {/* Current Interest Rate */}
      {interestRate && (
        <div className="bg-gradient-to-r from-blue-900/40 to-indigo-900/40 border border-blue-500/30 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-white">Current Interest Rate</h2>
              <p className="text-sm text-gray-400 mt-1">{interestRate.description}</p>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold text-blue-400">{interestRate.rate}%</div>
              <p className="text-sm text-gray-500 mt-1">As of {interestRate.date}</p>
            </div>
          </div>
        </div>
      )}

      {/* Interest Rate History Chart */}
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-lg border border-white/10 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <LineChart className="h-5 w-5 text-blue-400" />
            <h2 className="text-xl font-semibold text-white">Interest Rate History</h2>
          </div>
          <div className="flex space-x-2">
            {[
              { label: '1Y', days: 365 },
              { label: '2Y', days: 730 },
              { label: '5Y', days: 1825 },
              { label: '10Y', days: 3650 },
            ].map((option) => (
              <button
                key={option.days}
                onClick={() => setRateHistoryDays(option.days)}
                className={`px-3 py-1 text-sm rounded transition-colors ${
                  rateHistoryDays === option.days
                    ? 'bg-blue-600 text-white'
                    : 'bg-white/5 text-gray-400 hover:bg-white/10'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {historyLoading ? (
          <div className="flex items-center justify-center h-64">
            <LoadingSpinner />
          </div>
        ) : chartData.length > 0 ? (
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRate" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12, fill: '#9CA3AF' }}
                  tickLine={false}
                  axisLine={false}
                  minTickGap={30}
                />
                <YAxis
                  tick={{ fontSize: 12, fill: '#9CA3AF' }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => `${value}%`}
                  domain={['auto', 'auto']}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1F2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.5)',
                    color: '#F3F4F6'
                  }}
                  itemStyle={{ color: '#60A5FA' }}
                  formatter={(value: number) => [`${value}%`, 'Interest Rate']}
                  labelFormatter={(label, payload) => {
                    if (payload && payload[0]) {
                      return new Date(payload[0].payload.fullDate).toLocaleDateString('en-US', {
                        month: 'long',
                        day: 'numeric',
                        year: 'numeric',
                      });
                    }
                    return label;
                  }}
                />
                <Area
                  type="stepAfter"
                  dataKey="rate"
                  stroke="#3B82F6"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorRate)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No rate history available. Configure FRED_API_KEY in .env for historical data.
          </div>
        )}
      </div>

      {/* Economic Indicators */}
      {indicators && indicators.indicators && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {indicators.indicators.inflation && (
            <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-white/10 p-6 shadow-lg">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-green-400" />
                <h3 className="font-semibold text-white">Inflation (CPI)</h3>
              </div>
              <p className="text-2xl font-bold text-white mt-2">
                {indicators.indicators.inflation.value?.toFixed(2) || 'N/A'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {indicators.indicators.inflation.date}
              </p>
            </div>
          )}

          {indicators.indicators.unemployment && (
            <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-white/10 p-6 shadow-lg">
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-blue-400" />
                <h3 className="font-semibold text-white">Unemployment</h3>
              </div>
              <p className="text-2xl font-bold text-white mt-2">
                {indicators.indicators.unemployment.value?.toFixed(1) || 'N/A'}%
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {indicators.indicators.unemployment.date}
              </p>
            </div>
          )}

          {indicators.indicators.gdp && (
            <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-white/10 p-6 shadow-lg">
              <div className="flex items-center space-x-2">
                <DollarSign className="h-5 w-5 text-green-400" />
                <h3 className="font-semibold text-white">GDP</h3>
              </div>
              <p className="text-2xl font-bold text-white mt-2">
                ${indicators.indicators.gdp.value ? (indicators.indicators.gdp.value / 1e12).toFixed(2) + 'T' : 'N/A'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {indicators.indicators.gdp.date}
              </p>
            </div>
          )}

          {indicators.indicators.retail_sales && (
            <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-white/10 p-6 shadow-lg">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-purple-400" />
                <h3 className="font-semibold text-white">Retail Sales</h3>
              </div>
              <p className="text-2xl font-bold text-white mt-2">
                ${indicators.indicators.retail_sales.value ? (indicators.indicators.retail_sales.value / 1e9).toFixed(1) + 'B' : 'N/A'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {indicators.indicators.retail_sales.date}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Upcoming Events */}
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-lg border border-white/10 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">Upcoming Events</h2>
          <span className="text-sm text-gray-500">{upcomingEvents.length} events</span>
        </div>

        {upcomingEvents.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No upcoming events found. Configure FRED_API_KEY in .env for full calendar.
          </div>
        ) : (
          <div className="space-y-3">
            {upcomingEvents.map((event, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-l-4 ${
                  event.importance === 'HIGH'
                    ? 'bg-red-900/20 border-red-500/50'
                    : 'bg-gray-800/50 border-gray-600'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      <span className="text-sm font-medium text-gray-300">{event.type}</span>
                      {event.importance === 'HIGH' && (
                        <span className="px-2 py-0.5 text-xs font-semibold bg-red-500/20 text-red-300 rounded border border-red-500/20">
                          HIGH IMPORTANCE
                        </span>
                      )}
                    </div>
                    <h3 className="font-semibold text-white mt-1">{event.description}</h3>
                    {event.expected_outcome && (
                      <p className="text-sm text-gray-400 mt-1">{event.expected_outcome}</p>
                    )}
                  </div>
                  <div className="text-right ml-4">
                    <div className="text-lg font-bold text-white">
                      {new Date(event.date).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                      })}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {(() => {
                        const daysUntil = calculateDaysUntil(event.date);
                        if (daysUntil === 0) return 'Today';
                        if (daysUntil === 1) return 'Tomorrow';
                        return `${daysUntil} days`;
                      })()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Info Banner */}
      <div className="bg-blue-900/20 border-l-4 border-blue-500 p-4 rounded-r-lg">
        <p className="text-sm text-blue-200">
          <strong>Note:</strong> FED meetings and rate decisions significantly impact stock markets.
          Track these events to time your trades around major market catalysts.
        </p>
      </div>
    </div>
  );
}