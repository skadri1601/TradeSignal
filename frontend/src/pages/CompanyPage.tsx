import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { companiesApi } from '../api/companies';
import TradeList from '../components/trades/TradeList';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { formatCurrency } from '../utils/formatters';
import { Building2, ExternalLink } from 'lucide-react';

export default function CompanyPage() {
  const { ticker } = useParams<{ ticker: string }>();

  const { data: company, isLoading: companyLoading } = useQuery({
    queryKey: ['company', ticker],
    queryFn: () => companiesApi.getCompany(ticker!),
    enabled: !!ticker,
  });

  const { data: trades, isLoading: tradesLoading } = useQuery({
    queryKey: ['companyTrades', ticker],
    queryFn: () => companiesApi.getCompanyTrades(ticker!),
    enabled: !!ticker,
  });

  if (companyLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (!company) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Company not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Company Header */}
      <div className="card">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Building2 className="h-8 w-8 text-blue-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{company.name}</h1>
              <p className="text-lg text-gray-600 mt-1">{company.ticker}</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
          <div>
            <p className="text-sm text-gray-600">Sector</p>
            <p className="text-lg font-semibold text-gray-900">{company.sector || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Industry</p>
            <p className="text-lg font-semibold text-gray-900">{company.industry || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Market Cap</p>
            <p className="text-lg font-semibold text-gray-900">
              {company.market_cap ? formatCurrency(company.market_cap) : 'N/A'}
            </p>
          </div>
        </div>

        {company.website && (
          <div className="mt-4">
            <a
              href={company.website}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 inline-flex items-center"
            >
              {company.website}
              <ExternalLink className="h-4 w-4 ml-1" />
            </a>
          </div>
        )}
      </div>

      {/* Recent Trades */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Insider Trades</h2>
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
