import { Trade } from '../../types';
import { formatCurrency, formatDate, formatShares } from '../../utils/formatters';
import { ArrowUpCircle, ArrowDownCircle, ExternalLink } from 'lucide-react';

interface TradeListProps {
  trades: Trade[];
}

export default function TradeList({ trades }: TradeListProps) {
  const parseNumeric = (value: string | number | null | undefined): number | null => {
    if (value === null || value === undefined) {
      return null;
    }
    const numericValue = typeof value === 'string' ? parseFloat(value) : value;
    return Number.isFinite(numericValue) ? numericValue : null;
  };

  if (trades.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No trades found
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="table">
        <thead>
          <tr>
            <th>Filing Date</th>
            <th>Company</th>
            <th>Insider</th>
            <th>Type</th>
            <th className="text-right">Shares</th>
            <th className="text-right">Price</th>
            <th className="text-right">Value</th>
            <th>Filing</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => {
            const sharesNumber = parseNumeric(trade.shares);
            let priceNumber = parseNumeric(trade.price_per_share);
            let totalValueNumber = parseNumeric(trade.total_value);

            if (!totalValueNumber && sharesNumber && priceNumber) {
              totalValueNumber = sharesNumber * priceNumber;
            }

            if (!priceNumber && totalValueNumber && sharesNumber) {
              priceNumber = totalValueNumber / sharesNumber;
            }


            return (
              <tr key={trade.id}>
              <td className="text-gray-400">{formatDate(trade.filing_date)}</td>
              <td className="font-medium text-white">
                <a
                  href={`/companies/${trade.company?.ticker ?? trade.company_id}`}
                  className="hover:text-blue-400 transition-colors"
                >
                  {trade.company?.name ? (
                    <>
                      {trade.company.name}
                      {trade.company.ticker ? (
                        <span className="text-gray-500 font-normal"> ({trade.company.ticker})</span>
                      ) : null}
                    </>
                  ) : (
                    <>Company #{trade.company_id}</>
                  )}
                </a>
              </td>
              <td>
                <a href={`/insiders/${trade.insider_id}`} className="text-gray-400 hover:text-blue-400 transition-colors">
                  {trade.insider?.name ?? `Insider #${trade.insider_id}`}
                </a>
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
              <td className="text-right font-mono text-gray-300">{formatShares(trade.shares)}</td>
              <td className="text-right font-mono text-gray-300">
                {priceNumber ? formatCurrency(priceNumber) : 'N/A'}
              </td>
              <td className="text-right font-mono font-bold text-white">
                {totalValueNumber ? formatCurrency(totalValueNumber) : 'N/A'}
              </td>
              <td>
                <a
                  href={trade.sec_filing_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:text-blue-300 inline-flex items-center transition-colors"
                >
                  <ExternalLink className="h-4 w-4" />
                </a>
              </td>
            </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}