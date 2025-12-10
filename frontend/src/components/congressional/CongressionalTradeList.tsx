import { CongressionalTrade } from '../../types';
import { formatCurrency, formatDate } from '../../utils/formatters';
import { ArrowUpCircle, ArrowDownCircle, ExternalLink, Users, Building2 } from 'lucide-react';

interface CongressionalTradeListProps {
  trades: CongressionalTrade[];
}

export default function CongressionalTradeList({ trades }: CongressionalTradeListProps) {
  const parseNumeric = (value: string | number | null | undefined): number | null => {
    if (value === null || value === undefined) {
      return null;
    }
    const numericValue = typeof value === 'string' ? parseFloat(value) : value;
    return Number.isFinite(numericValue) ? numericValue : null;
  };

  const formatAmountRange = (trade: CongressionalTrade): string => {
    const min = parseNumeric(trade.amount_min);
    const max = parseNumeric(trade.amount_max);
    const estimated = parseNumeric(trade.amount_estimated);

    if (min && max) {
      return `${formatCurrency(min)} - ${formatCurrency(max)}`;
    } else if (estimated) {
      return `~${formatCurrency(estimated)}`;
    }
    return 'N/A';
  };

  const getPartyBadgeClass = (party?: string): string => {
    switch (party) {
      case 'DEMOCRAT':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      case 'REPUBLICAN':
        return 'bg-red-500/20 text-red-300 border-red-500/30';
      case 'INDEPENDENT':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/30';
      default:
        return 'bg-gray-700 text-gray-300 border-gray-600';
    }
  };

  const getPartyAbbrev = (party?: string): string => {
    switch (party) {
      case 'DEMOCRAT':
        return 'D';
      case 'REPUBLICAN':
        return 'R';
      case 'INDEPENDENT':
        return 'I';
      default:
        return '?';
    }
  };

  const getOwnerBadgeClass = (ownerType: string): string => {
    switch (ownerType) {
      case 'Self':
        return 'bg-green-500/20 text-green-300 border-green-500/30';
      case 'Spouse':
        return 'bg-pink-500/20 text-pink-300 border-pink-500/30';
      case 'Dependent Child':
        return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      case 'Joint':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      default:
        return 'bg-gray-700 text-gray-300 border-gray-600';
    }
  };

  if (trades.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No congressional trades found
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Member</th>
            <th>Company</th>
            <th>Type</th>
            <th>Owner</th>
            <th className="text-right">Amount Range</th>
            <th className="text-right">Estimated</th>
            <th>Filing</th>
            <th>Disclosure</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => {
            const estimated = parseNumeric(trade.amount_estimated);

            return (
              <tr key={trade.id}>
                <td className="text-gray-400">{formatDate(trade.transaction_date)}</td>
                <td>
                  <div className="flex flex-col gap-1">
                    <div className="font-medium text-white">
                      {trade.congressperson?.display_name ?? trade.congressperson?.name ?? `Member #${trade.congressperson_id}`}
                    </div>
                    <div className="flex items-center gap-2">
                      {trade.congressperson?.chamber && (
                        <span className="inline-flex items-center gap-1 text-xs text-gray-400">
                          {trade.congressperson.chamber === 'HOUSE' ? (
                            <>
                              <Users className="h-3 w-3" />
                              <span>House</span>
                            </>
                          ) : (
                            <>
                              <Building2 className="h-3 w-3" />
                              <span>Senate</span>
                            </>
                          )}
                        </span>
                      )}
                      {trade.congressperson?.party && (
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold border ${getPartyBadgeClass(trade.congressperson.party)}`}>
                          {getPartyAbbrev(trade.congressperson.party)}
                        </span>
                      )}
                      {trade.congressperson?.state && (
                        <span className="text-xs text-gray-500 font-medium">
                          {trade.congressperson.state}
                        </span>
                      )}
                    </div>
                  </div>
                </td>
                <td className="font-medium text-white">
                  {trade.company ? (
                    <a
                      href={`/companies/${trade.company.ticker ?? trade.company_id}`}
                      className="hover:text-blue-400 transition-colors"
                    >
                      {trade.company.name}
                      {trade.company.ticker && (
                        <span className="text-gray-500 font-normal"> ({trade.company.ticker})</span>
                      )}
                    </a>
                  ) : trade.ticker ? (
                    <span>{trade.ticker}</span>
                  ) : (
                    <span className="text-gray-500 text-sm">{trade.asset_description || 'Unknown'}</span>
                  )}
                </td>
                <td>
                  <span
                    className={`badge ${
                      trade.transaction_type === 'BUY' ? 'badge-buy' : 'badge-sell'
                    }`}
                  >
                    {trade.transaction_type === 'BUY' ? (
                      <ArrowUpCircle className="h-3 w-3 mr-1" />
                    ) : (
                      <ArrowDownCircle className="h-3 w-3 mr-1" />
                    )}
                    {trade.transaction_type}
                  </span>
                </td>
                <td>
                  <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-bold border ${getOwnerBadgeClass(trade.owner_type)}`}>
                    {trade.owner_type}
                  </span>
                </td>
                <td className="text-right font-mono text-sm text-gray-300">
                  {formatAmountRange(trade)}
                </td>
                <td className="text-right font-mono font-bold text-white">
                  {estimated ? formatCurrency(estimated) : 'N/A'}
                </td>
                <td className="text-gray-400 text-sm">
                  {formatDate(trade.disclosure_date)}
                  {trade.filing_delay_days !== null && trade.filing_delay_days > 45 && (
                    <span className="block text-xs text-red-400 font-medium">
                      +{trade.filing_delay_days}d late
                    </span>
                  )}
                </td>
                <td>
                  {trade.disclosure_url ? (
                    <a
                      href={trade.disclosure_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:text-blue-300 inline-flex items-center transition-colors"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  ) : (
                    <span className="text-gray-600">N/A</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}