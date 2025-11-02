import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { alertsApi } from "../../api/alerts";
import { Alert, AlertType, NotificationChannel } from "../../types";

interface CreateAlertModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CreateAlertModal({
  isOpen,
  onClose,
}: CreateAlertModalProps) {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [alertType, setAlertType] = useState<AlertType>("large_trade");
  const [ticker, setTicker] = useState("");
  const [minValue, setMinValue] = useState<number | string>("");
  const [transactionType, setTransactionType] = useState<"BUY" | "SELL" | "">(
    ""
  );
  const [notificationChannels, setNotificationChannels] = useState<
    NotificationChannel[]
  >([]);
  const [webhookUrl, setWebhookUrl] = useState("");

  const mutation = useMutation({
    mutationFn: (newAlert: Partial<Alert>) => alertsApi.createAlert(newAlert),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
      onClose();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newAlert: Partial<Alert> = {
      name,
      alert_type: alertType,
      ticker: ticker || null,
      min_value: Number(minValue) || null,
      transaction_type: transactionType || null,
      notification_channels: notificationChannels,
      webhook_url: webhookUrl || null,
      is_active: true,
    };
    mutation.mutate(newAlert);
  };

  const handleChannelChange = (channel: NotificationChannel) => {
    setNotificationChannels((prev) =>
      prev.includes(channel)
        ? prev.filter((c) => c !== channel)
        : [...prev, channel]
    );
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-lg">
        <h2 className="text-2xl font-bold mb-4">Create New Alert</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="input"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Alert Type</label>
            <select
              value={alertType}
              onChange={(e) => setAlertType(e.target.value as AlertType)}
              className="input"
            >
              <option value="large_trade">Large Trade</option>
              <option value="company_watch">Company Watch</option>
              <option value="insider_role">Insider Role</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Ticker</label>
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              className="input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Minimum Value ($)</label>
            <input
              type="number"
              value={minValue}
              onChange={(e) => setMinValue(e.target.value)}
              className="input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Transaction Type</label>
            <select
              value={transactionType}
              onChange={(e) =>
                setTransactionType(e.target.value as "BUY" | "SELL" | "")
              }
              className="input"
            >
              <option value="">Any</option>
              <option value="BUY">Buy</option>
              <option value="SELL">Sell</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Notification Channels</label>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={notificationChannels.includes("webhook")}
                  onChange={() => handleChannelChange("webhook")}
                  className="mr-2"
                />
                Webhook
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  disabled
                  className="mr-2"
                />
                Email (soon)
              </label>
            </div>
          </div>
          {notificationChannels.includes("webhook") && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Webhook URL</label>
              <input
                type="url"
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                className="input"
                required
              />
            </div>
          )}
          <div className="flex justify-end mt-4">
            <button type="button" onClick={onClose} className="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn btn-primary ml-2" disabled={mutation.isPending}>
              {mutation.isPending ? "Creating..." : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}