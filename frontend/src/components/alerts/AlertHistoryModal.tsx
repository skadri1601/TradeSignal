import { useQuery } from "@tanstack/react-query";
import { alertsApi } from "../../api/alerts";
import { AlertHistory } from "../../types";
import LoadingSpinner from "../common/LoadingSpinner";
import {
  X,
  CheckCircle,
  XCircle,
  RefreshCw,
  Mail,
  Bell,
  Hash,
  MessageSquare,
  Smartphone,
  Webhook
} from "lucide-react";

interface AlertHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  alertId: number;
  alertName: string;
}

export default function AlertHistoryModal({
  isOpen,
  onClose,
  alertId,
  alertName,
}: AlertHistoryModalProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["alertHistory", alertId],
    queryFn: () => alertsApi.getAlertHistory(alertId),
    enabled: isOpen,
  });

  if (!isOpen) {
    return null;
  }

  // Channel icons
  const channelIcons: Record<string, JSX.Element> = {
    email: <Mail className="h-4 w-4" />,
    push: <Bell className="h-4 w-4" />,
    discord: <Hash className="h-4 w-4" />,
    slack: <MessageSquare className="h-4 w-4" />,
    sms: <Smartphone className="h-4 w-4" />,
    webhook: <Webhook className="h-4 w-4" />,
  };

  // Status icons
  const statusIcons: Record<string, JSX.Element> = {
    sent: <CheckCircle className="h-4 w-4 text-green-600" />,
    failed: <XCircle className="h-4 w-4 text-red-600" />,
    retrying: <RefreshCw className="h-4 w-4 text-yellow-600 animate-spin" />,
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Alert History</h2>
            <p className="text-sm text-gray-500">{alertName}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <LoadingSpinner />
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <XCircle className="h-12 w-12 text-red-400 mx-auto mb-2" />
              <p className="text-red-600">Failed to load history</p>
            </div>
          ) : data?.items && data.items.length > 0 ? (
            <div className="space-y-3">
              {data.items.map((history: AlertHistory) => (
                <div
                  key={history.id}
                  className="flex items-start justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-start gap-3">
                    {/* Channel Icon */}
                    <div className="p-2 bg-white rounded-lg shadow-sm">
                      {channelIcons[history.notification_channel] || history.notification_channel}
                    </div>

                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium capitalize">
                          {history.notification_channel}
                        </span>
                        <span className="flex items-center gap-1 text-sm">
                          {statusIcons[history.notification_status]}
                          <span className={`capitalize ${
                            history.notification_status === 'sent' ? 'text-green-600' :
                            history.notification_status === 'failed' ? 'text-red-600' :
                            'text-yellow-600'
                          }`}>
                            {history.notification_status}
                          </span>
                        </span>
                      </div>

                      {history.error_message && (
                        <p className="text-sm text-red-500 mt-1">
                          {history.error_message}
                        </p>
                      )}

                      <p className="text-xs text-gray-400 mt-1">
                        Trade ID: {history.trade_id}
                      </p>
                    </div>
                  </div>

                  <div className="text-right text-sm text-gray-500">
                    {new Date(history.created_at).toLocaleDateString()}
                    <br />
                    <span className="text-xs">
                      {new Date(history.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))}

              {data.total > data.items.length && (
                <p className="text-center text-sm text-gray-500 pt-2">
                  Showing {data.items.length} of {data.total} notifications
                </p>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <Bell className="h-12 w-12 text-gray-300 mx-auto mb-2" />
              <p className="text-gray-500">No notifications sent yet</p>
              <p className="text-sm text-gray-400 mt-1">
                Notifications will appear here when this alert triggers
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t bg-gray-50">
          <button
            onClick={onClose}
            className="btn btn-secondary w-full"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
