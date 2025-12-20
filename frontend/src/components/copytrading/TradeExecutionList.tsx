import { useState, useMemo } from 'react';
import { ExecutedTrade } from '../../types';
import { formatDate, formatCurrency, formatShares } from '../../utils/formatters';
import { Download, ArrowUpCircle, ArrowDownCircle, CheckCircle2, XCircle, Clock, Ban } from 'lucide-react';

export interface TradeExecutionListProps {
  trades: ExecutedTrade[];
  filters?: {
    status?: ExecutedTrade['execution_status'];
    dateFrom?: string;
    dateTo?: string;
    symbol?: string;
  };
  onTradeClick?: (trade: ExecutedTrade) => void;
}

export default function TradeExecutionList({
  trades,
  filters,
  onTradeClick,
}: TradeExecutionListProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<ExecutedTrade['execution_status'] | 'all'>(
    filters?.status || 'all'
  );
  const [symbolFilter, setSymbolFilter] = useState(filters?.symbol || '');
  const tradesPerPage = 50;

  // Filter trades
  const filteredTrades = useMemo(() => {
    let filtered = [...trades];

    if (statusFilter !== 'all') {
      filtered = filtered.filter((t) => t.execution_status === statusFilter);
    }

    if (symbolFilter) {
      filtered = filtered.filter((t) =>
        t.ticker.toLowerCase().includes(symbolFilter.toLowerCase())
      );
    }

    if (filters?.dateFrom) {
      filtered = filtered.filter((t) => new Date(t.created_at) >= new Date(filters.dateFrom!));
    }

    if (filters?.dateTo) {
      filtered = filtered.filter((t) => new Date(t.created_at) <= new Date(filters.dateTo!));
    }

    return filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  }, [trades, statusFilter, symbolFilter, filters]);

  // Pagination
  const totalPages = Math.ceil(filteredTrades.length / tradesPerPage);
  const paginatedTrades = filteredTrades.slice(
    (currentPage - 1) * tradesPerPage,
    currentPage * tradesPerPage
  );

  const getStatusBadge = (status: ExecutedTrade['execution_status']) => {
    const badges = {
      pending: {
        icon: Clock,
        className: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
        label: 'Pending',
      },
      filled: {
        icon: CheckCircle2,
        className: 'bg-green-500/20 text-green-300 border-green-500/30',
        label: 'Filled',
      },
      rejected: {
        icon: XCircle,
        className: 'bg-red-500/20 text-red-300 border-red-500/30',
        label: 'Rejected',
      },
      cancelled: {
        icon: Ban,
        className: 'bg-gray-500/20 text-gray-300 border-gray-500/30',
        label: 'Cancelled',
      },
    };

    const badge = badges[status];
    const Icon = badge.icon;

    return (
      <span
        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${badge.className}`}
      >
        <Icon className="w-3 h-3" />
        {badge.label}
      </span>
    );
  };

  const exportToCSV = () => {
    const headers = ['Date', 'Symbol', 'Action', 'Quantity', 'Price', 'Total Value', 'Status'];
    const rows = filteredTrades.map((trade) => [
      formatDate(trade.created_at),
      trade.ticker,
      trade.transaction_type,
      trade.shares.toString(),
      formatCurrency(trade.price),
      formatCurrency(trade.total_value),
      trade.execution_status,
    ]);

    const csvContent = [headers, ...rows]
      .map((row) => row.map((cell) => `"${cell}"`).join(','))
      .join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `copy-trades-${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  return (
    <div className="space-y-4">
      {/* Filters and Export */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value as ExecutedTrade['execution_status'] | 'all');
              setCurrentPage(1);
            }}
            className="px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="filled">Filled</option>
            <option value="rejected">Rejected</option>
            <option value="cancelled">Cancelled</option>
          </select>

          {/* Symbol Filter */}
          <input
            type="text"
            value={symbolFilter}
            onChange={(e) => {
              setSymbolFilter(e.target.value.toUpperCase());
              setCurrentPage(1);
            }}
            placeholder="Filter by symbol..."
            className="px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 uppercase"
            maxLength={10}
          />
        </div>

        <button
          onClick={exportToCSV}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors flex items-center gap-2 text-sm font-medium"
        >
          <Download className="w-4 h-4" />
          Export CSV
        </button>
      </div>

      {/* Table - Desktop */}
      <div className="hidden md:block overflow-x-auto">
        <table className="table">
          <thead className="sticky top-0 z-10">
            <tr>
              <th>Date</th>
              <th>Symbol</th>
              <th>Action</th>
              <th className="text-right">Quantity</th>
              <th className="text-right">Price</th>
              <th className="text-right">Total Value</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {paginatedTrades.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-8 text-gray-500">
                  No trades found
                </td>
              </tr>
            ) : (
              paginatedTrades.map((trade) => (
                <tr
                  key={trade.id}
                  onClick={() => onTradeClick?.(trade)}
                  className={onTradeClick ? 'cursor-pointer' : ''}
                >
                  <td className="text-gray-400">{formatDate(trade.created_at)}</td>
                  <td className="font-medium text-white">{trade.ticker}</td>
                  <td>
                    {trade.transaction_type === 'BUY' ? (
                      <span className="inline-flex items-center gap-1 text-green-400">
                        <ArrowUpCircle className="w-4 h-4" />
                        BUY
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-red-400">
                        <ArrowDownCircle className="w-4 h-4" />
                        SELL
                      </span>
                    )}
                  </td>
                  <td className="text-right font-mono text-gray-300">
                    {formatShares(trade.shares)}
                  </td>
                  <td className="text-right font-mono text-gray-300">
                    {formatCurrency(trade.price)}
                  </td>
                  <td className="text-right font-mono font-bold text-white">
                    {formatCurrency(trade.total_value)}
                  </td>
                  <td>{getStatusBadge(trade.execution_status)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Cards - Mobile */}
      <div className="md:hidden space-y-3">
        {paginatedTrades.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No trades found</div>
        ) : (
          paginatedTrades.map((trade) => (
            <div
              key={trade.id}
              onClick={() => onTradeClick?.(trade)}
              className={`bg-gray-900/50 backdrop-blur-sm rounded-xl border border-white/10 p-4 ${
                onTradeClick ? 'cursor-pointer hover:border-purple-500/30 transition-colors' : ''
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h4 className="font-bold text-white text-lg">{trade.ticker}</h4>
                  <p className="text-sm text-gray-400">{formatDate(trade.created_at)}</p>
                </div>
                {getStatusBadge(trade.execution_status)}
              </div>
              <div className="grid grid-cols-2 gap-3 mt-3">
                <div>
                  <p className="text-xs text-gray-400 uppercase font-bold mb-1">Action</p>
                  <p
                    className={`font-semibold ${
                      trade.transaction_type === 'BUY' ? 'text-green-400' : 'text-red-400'
                    }`}
                  >
                    {trade.transaction_type}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-400 uppercase font-bold mb-1">Quantity</p>
                  <p className="font-mono text-white">{formatShares(trade.shares)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400 uppercase font-bold mb-1">Price</p>
                  <p className="font-mono text-white">{formatCurrency(trade.price)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400 uppercase font-bold mb-1">Total</p>
                  <p className="font-mono font-bold text-white">
                    {formatCurrency(trade.total_value)}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
          >
            Previous
          </button>
          <span className="text-sm text-gray-400">
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

