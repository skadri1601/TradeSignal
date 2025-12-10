import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { alertsApi } from "../../api/alerts";
import { Alert } from "../../types";
import EditAlertModal from "./EditAlertModal";
import AlertHistoryModal from "./AlertHistoryModal";
import { useCustomConfirm } from "../../hooks/useCustomConfirm";
import CustomConfirm from "../common/CustomConfirm";
import {
  Bell,
  Hash,
  MessageSquare,
  Smartphone,
  Mail,
  Webhook,
  Send,
  History,
  Loader2
} from "lucide-react";

interface AlertCardProps {
  alert: Alert;
}

export default function AlertCard({ alert }: AlertCardProps) {
  const queryClient = useQueryClient();
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);
  const [testStatus, setTestStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [testMessage, setTestMessage] = useState('');
  const { confirmState, showConfirm, hideConfirm } = useCustomConfirm();

  const deleteMutation = useMutation({
    mutationFn: () => alertsApi.deleteAlert(alert.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });

  const testMutation = useMutation({
    mutationFn: () => alertsApi.testAlert(alert.id),
    onMutate: () => {
      setTestStatus('loading');
      setTestMessage('');
    },
    onSuccess: (data) => {
      setTestStatus('success');
      setTestMessage(data.message || 'Test notification sent!');
      setTimeout(() => {
        setTestStatus('idle');
        setTestMessage('');
      }, 3000);
    },
    onError: (error: any) => {
      setTestStatus('error');
      setTestMessage(error.response?.data?.detail || 'Failed to send test notification');
      setTimeout(() => {
        setTestStatus('idle');
        setTestMessage('');
      }, 5000);
    },
  });

  const handleDelete = () => {
    showConfirm(
      "Are you sure you want to delete this alert?",
      () => {
        deleteMutation.mutate();
      },
      { type: 'warning', title: 'TradeSignal' }
    );
  };

  // Get channel icons
  const channelIcons: Record<string, JSX.Element> = {
    email: <Mail className="h-4 w-4 text-gray-400" />,
    push: <Bell className="h-4 w-4 text-green-400" />,
    discord: <Hash className="h-4 w-4 text-purple-400" />,
    slack: <MessageSquare className="h-4 w-4 text-green-400" />,
    sms: <Smartphone className="h-4 w-4 text-blue-400" />,
    webhook: <Webhook className="h-4 w-4 text-gray-400" />,
  };

  return (
    <>
      <div className="card">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-semibold text-white">{alert.name}</h2>
              <span
                className={`px-2 py-0.5 text-xs rounded-full ${
                  alert.is_active ? "bg-green-500/20 text-green-300" : "bg-red-500/20 text-red-300"
                }`}
              >
                {alert.is_active ? "Active" : "Inactive"}
              </span>
            </div>
            <p className="text-sm text-gray-400 mt-1">
              {alert.alert_type.replace('_', ' ').toUpperCase()}
              {alert.ticker && ` • ${alert.ticker}`}
              {alert.min_value && ` • Min: $${alert.min_value.toLocaleString()}`}
              {alert.transaction_type && ` • ${alert.transaction_type}`}
            </p>

            {/* Notification Channels */}
            <div className="flex items-center gap-2 mt-2">
              <span className="text-xs text-gray-400">Channels:</span>
              <div className="flex gap-1">
                {alert.notification_channels.map((channel) => (
                  <span
                    key={channel}
                    className="p-1 bg-white/10 rounded"
                    title={channel}
                  >
                    {channelIcons[channel] || channel}
                  </span>
                ))}
              </div>
            </div>

            {/* Test Status Message */}
            {testMessage && (
              <div className={`mt-2 text-sm ${
                testStatus === 'success' ? 'text-green-400' :
                testStatus === 'error' ? 'text-red-400' : 'text-gray-400'
              }`}>
                {testMessage}
              </div>
            )}
          </div>

          <div className="flex items-center space-x-2">
            {/* Test Button */}
            <button
              onClick={() => testMutation.mutate()}
              disabled={testMutation.isPending || !alert.is_active}
              className="px-3 py-2 rounded-lg text-sm font-medium bg-gray-800 text-gray-300 hover:bg-gray-700 transition-colors flex items-center gap-1 disabled:opacity-50 disabled:cursor-not-allowed"
              title={!alert.is_active ? "Activate alert to test" : "Send test notification"}
            >
              {testMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              Test
            </button>

            {/* History Button */}
            <button
              onClick={() => setIsHistoryModalOpen(true)}
              className="px-3 py-2 rounded-lg text-sm font-medium bg-gray-800 text-gray-300 hover:bg-gray-700 transition-colors flex items-center gap-1"
              title="View alert history"
            >
              <History className="h-4 w-4" />
              History
            </button>

            <button
              onClick={() => setIsEditModalOpen(true)}
              className="px-3 py-2 rounded-lg text-sm font-medium bg-gray-800 text-gray-300 hover:bg-gray-700 transition-colors"
            >
              Edit
            </button>
            <button
              onClick={handleDelete}
              className="px-3 py-2 rounded-lg text-sm font-medium bg-red-600 text-white hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? "..." : "Delete"}
            </button>
          </div>
        </div>
      </div>
      <EditAlertModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        alert={alert}
      />
      <AlertHistoryModal
        isOpen={isHistoryModalOpen}
        onClose={() => setIsHistoryModalOpen(false)}
        alertId={alert.id}
        alertName={alert.name}
      />

      {/* Custom Confirm Modal */}
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
