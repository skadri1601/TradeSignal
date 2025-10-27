import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { insidersApi } from '../api/insiders';
import TradeList from '../components/trades/TradeList';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { User, Briefcase } from 'lucide-react';

export default function InsiderPage() {
  const { id } = useParams<{ id: string }>();
  const insiderId = parseInt(id!);

  const { data: insider, isLoading: insiderLoading } = useQuery({
    queryKey: ['insider', insiderId],
    queryFn: () => insidersApi.getInsider(insiderId),
    enabled: !!insiderId,
  });

  const { data: trades, isLoading: tradesLoading } = useQuery({
    queryKey: ['insiderTrades', insiderId],
    queryFn: () => insidersApi.getInsiderTrades(insiderId),
    enabled: !!insiderId,
  });

  if (insiderLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (!insider) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Insider not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Insider Header */}
      <div className="card">
        <div className="flex items-start space-x-4">
          <div className="p-3 bg-purple-100 rounded-lg">
            <User className="h-8 w-8 text-purple-600" />
          </div>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">{insider.name}</h1>
            {insider.title && (
              <p className="text-lg text-gray-600 mt-1 flex items-center">
                <Briefcase className="h-5 w-5 mr-2" />
                {insider.title}
              </p>
            )}
          </div>
        </div>

        {/* Roles */}
        <div className="flex flex-wrap gap-2 mt-6">
          {insider.is_director && (
            <span className="badge badge-gray">Director</span>
          )}
          {insider.is_officer && (
            <span className="badge badge-gray">Officer</span>
          )}
          {insider.is_ten_percent_owner && (
            <span className="badge badge-gray">10% Owner</span>
          )}
          {insider.is_other && (
            <span className="badge badge-gray">Other</span>
          )}
        </div>
      </div>

      {/* Recent Trades */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Trading Activity</h2>
        {tradesLoading ? (
          <div className="flex items-center justify-center h-32">
            <LoadingSpinner />
          </div>
        ) : (
          <TradeList trades={trades || []} />
        )}
      </div>
    </div>
  );
}
