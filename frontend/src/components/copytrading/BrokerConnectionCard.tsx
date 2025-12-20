import { BrokerageAccount } from '../../types';
import { formatDistanceToNow } from 'date-fns';
import { CheckCircle2, XCircle, Link2, RefreshCw, AlertTriangle, Shield } from 'lucide-react';
import { useCustomConfirm } from '../../hooks/useCustomConfirm';
import CustomConfirm from '../common/CustomConfirm';

export interface BrokerConnectionCardProps {
  account: BrokerageAccount | null;
  onConnect: () => void;
  onDisconnect: () => void;
  onSync?: () => void;
  brokerName?: string;
}

export default function BrokerConnectionCard({
  account,
  onConnect,
  onDisconnect,
  onSync,
  brokerName = 'Brokerage',
}: BrokerConnectionCardProps) {
  const { confirmState, showConfirm, hideConfirm } = useCustomConfirm();

  const isConnected = account !== null && account.is_active && account.is_verified;
  const lastSynced = account?.last_synced_at
    ? formatDistanceToNow(new Date(account.last_synced_at), { addSuffix: true })
    : null;

  const brokerColors: Record<string, string> = {
    alpaca: 'bg-green-500/20 border-green-500/30',
    td_ameritrade: 'bg-blue-500/20 border-blue-500/30',
    etrade: 'bg-purple-500/20 border-purple-500/30',
    default: 'bg-gray-500/20 border-gray-500/30',
  };

  const brokerColor = brokerColors[account?.brokerage_name.toLowerCase() || 'default'] || brokerColors.default;

  const handleDisconnect = () => {
    showConfirm(
      'Are you sure you want to disconnect this brokerage account?',
      () => {
        onDisconnect();
      },
      {
        type: 'warning',
        title: 'Disconnect Account',
        confirmText: 'Disconnect',
        cancelText: 'Cancel',
      }
    );
  };

  return (
    <>
      <div className={`bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10 p-6 ${brokerColor}`}>
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white/10 rounded-xl flex items-center justify-center">
              <Link2 className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">
                {account?.brokerage_name || brokerName}
              </h3>
              <p className="text-sm text-gray-400">
                {account?.account_number || 'Not connected'}
              </p>
            </div>
          </div>

          {/* Status Indicator */}
          <div className="flex items-center gap-2">
            {isConnected ? (
              <>
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                <span className="text-sm font-medium text-green-400">Connected</span>
              </>
            ) : (
              <>
                <XCircle className="w-5 h-5 text-red-400" />
                <span className="text-sm font-medium text-red-400">Disconnected</span>
              </>
            )}
          </div>
        </div>

        {/* Warning Banner if Disconnected */}
        {!isConnected && (
          <div className="mb-4 p-3 bg-yellow-900/20 border border-yellow-500/30 rounded-lg flex items-start gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-yellow-300">Account Not Connected</p>
              <p className="text-xs text-yellow-400/80 mt-1">
                Connect your brokerage account to enable copy trading features.
              </p>
            </div>
          </div>
        )}

        {/* Account Details */}
        {isConnected && account && (
          <div className="space-y-3 mb-4">
            {/* Balance */}
            <div className="bg-black/20 rounded-xl p-4 border border-white/5">
              <p className="text-xs text-gray-400 uppercase font-bold mb-1">Account Balance</p>
              <p className="text-2xl font-bold text-white">
                ${account.account_balance?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
              </p>
            </div>

            {/* Buying Power */}
            {account.buying_power && (
              <div className="bg-black/20 rounded-xl p-4 border border-white/5">
                <p className="text-xs text-gray-400 uppercase font-bold mb-1">Buying Power</p>
                <p className="text-xl font-semibold text-green-400">
                  ${account.buying_power.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
            )}

            {/* Last Synced */}
            {lastSynced && (
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <RefreshCw className="w-4 h-4" />
                <span>Last synced {lastSynced}</span>
              </div>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          {isConnected ? (
            <>
              {onSync && (
                <button
                  onClick={onSync}
                  className="flex-1 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors flex items-center justify-center gap-2 font-medium"
                >
                  <RefreshCw className="w-4 h-4" />
                  Sync Now
                </button>
              )}
              <button
                onClick={handleDisconnect}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-500 transition-colors font-medium"
              >
                Disconnect
              </button>
            </>
          ) : (
            <button
              onClick={onConnect}
              className="w-full px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors font-medium flex items-center justify-center gap-2 shadow-lg shadow-purple-500/20"
            >
              <Shield className="w-5 h-5" />
              Connect Account (OAuth)
            </button>
          )}
        </div>
      </div>

      {/* Confirmation Modal */}
      <CustomConfirm
        show={confirmState.show}
        message={confirmState.message}
        title={confirmState.title || 'TradeSignal'}
        type={confirmState.type}
        confirmText={confirmState.confirmText}
        cancelText={confirmState.cancelText}
        onConfirm={confirmState.onConfirm || (() => {})}
        onCancel={hideConfirm}
      />
    </>
  );
}

