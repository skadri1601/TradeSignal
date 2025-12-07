import { useState, useEffect, useContext } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { alertsApi } from "../../api/alerts";
import { Alert, AlertType, NotificationChannel } from "../../types";
import { usePushNotifications } from "../../hooks/usePushNotifications";
import { AuthContext } from "../../contexts/AuthContext";
import { Bell, BellOff, MessageSquare, Hash, Smartphone, Crown } from "lucide-react";

interface EditAlertModalProps {
  isOpen: boolean;
  onClose: () => void;
  alert: Alert;
}

export default function EditAlertModal({
  isOpen,
  onClose,
  alert,
}: EditAlertModalProps) {
  const queryClient = useQueryClient();
  const authContext = useContext(AuthContext);
  const user = authContext?.user;
  const { supported, subscribed, loading, subscribe } = usePushNotifications();
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
  const [email, setEmail] = useState("");
  const [discordWebhookUrl, setDiscordWebhookUrl] = useState("");
  const [slackWebhookUrl, setSlackWebhookUrl] = useState("");
  const [smsPhoneNumber, setSmsPhoneNumber] = useState("");

  // Check if user has Pro tier for SMS
  const isPro = user?.stripe_subscription_tier === 'pro' || user?.stripe_subscription_tier === 'enterprise' || user?.is_superuser;

  useEffect(() => {
    if (alert) {
      setName(alert.name);
      setAlertType(alert.alert_type);
      setTicker(alert.ticker || "");
      setMinValue(alert.min_value || "");
      setTransactionType(alert.transaction_type || "");
      setNotificationChannels(alert.notification_channels);
      setWebhookUrl(alert.webhook_url || "");
      setEmail(alert.email || "");
      setDiscordWebhookUrl(alert.discord_webhook_url || "");
      setSlackWebhookUrl(alert.slack_webhook_url || "");
      setSmsPhoneNumber(alert.sms_phone_number || "");
    }
  }, [alert]);

  const mutation = useMutation({
    mutationFn: (updatedAlert: Partial<Alert>) =>
      alertsApi.updateAlert(alert.id, updatedAlert),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
      onClose();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const updatedAlert: Partial<Alert> = {
      name,
      alert_type: alertType,
      ticker: ticker || null,
      min_value: Number(minValue) || null,
      transaction_type: transactionType || null,
      notification_channels: notificationChannels,
      webhook_url: webhookUrl || null,
      email: email || null,
      discord_webhook_url: discordWebhookUrl || null,
      slack_webhook_url: slackWebhookUrl || null,
      sms_phone_number: smsPhoneNumber || null,
    };
    mutation.mutate(updatedAlert);
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
        <h2 className="text-2xl font-bold mb-4">Edit Alert</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="input"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Alert Type
            </label>
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
            <label className="block text-sm font-medium text-gray-700">
              Ticker
            </label>
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              className="input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Minimum Value ($)
            </label>
            <input
              type="number"
              value={minValue}
              onChange={(e) => setMinValue(e.target.value)}
              className="input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Transaction Type
            </label>
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
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notification Channels
            </label>
            <div className="grid grid-cols-2 gap-2">
              {/* Email */}
              <label className="flex items-center p-2 border rounded hover:bg-gray-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationChannels.includes("email")}
                  onChange={() => handleChannelChange("email")}
                  className="mr-2"
                />
                <span>Email</span>
              </label>

              {/* Browser Push */}
              <label className="flex items-center p-2 border rounded hover:bg-gray-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationChannels.includes("push")}
                  onChange={async (e) => {
                    if (e.target.checked) {
                      if (!subscribed) {
                        try {
                          await subscribe();
                        } catch (error) {
                          console.error('Failed to enable push:', error);
                          return;
                        }
                      }
                      handleChannelChange("push");
                    } else {
                      handleChannelChange("push");
                    }
                  }}
                  disabled={!supported || loading}
                  className="mr-2"
                />
                <div className="flex items-center gap-1">
                  {notificationChannels.includes("push") ? (
                    <Bell className="h-4 w-4 text-green-600" />
                  ) : (
                    <BellOff className="h-4 w-4 text-gray-400" />
                  )}
                  <span>Push</span>
                </div>
              </label>

              {/* Discord */}
              <label className="flex items-center p-2 border rounded hover:bg-gray-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationChannels.includes("discord")}
                  onChange={() => handleChannelChange("discord")}
                  className="mr-2"
                />
                <div className="flex items-center gap-1">
                  <Hash className="h-4 w-4 text-indigo-600" />
                  <span>Discord</span>
                </div>
              </label>

              {/* Slack */}
              <label className="flex items-center p-2 border rounded hover:bg-gray-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationChannels.includes("slack")}
                  onChange={() => handleChannelChange("slack")}
                  className="mr-2"
                />
                <div className="flex items-center gap-1">
                  <MessageSquare className="h-4 w-4 text-green-600" />
                  <span>Slack</span>
                </div>
              </label>

              {/* SMS - Pro Only */}
              <label className={`flex items-center p-2 border rounded ${isPro ? 'hover:bg-gray-50 cursor-pointer' : 'opacity-50 cursor-not-allowed'}`}>
                <input
                  type="checkbox"
                  checked={notificationChannels.includes("sms")}
                  onChange={() => handleChannelChange("sms")}
                  disabled={!isPro}
                  className="mr-2"
                />
                <div className="flex items-center gap-1">
                  <Smartphone className="h-4 w-4 text-blue-600" />
                  <span>SMS</span>
                  {!isPro && <Crown className="h-3 w-3 text-yellow-500 ml-1" aria-label="Pro tier required" />}
                </div>
              </label>

              {/* Custom Webhook */}
              <label className="flex items-center p-2 border rounded hover:bg-gray-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationChannels.includes("webhook")}
                  onChange={() => handleChannelChange("webhook")}
                  className="mr-2"
                />
                <span>Webhook</span>
              </label>
            </div>
            {!isPro && (
              <p className="text-xs text-gray-500 mt-2">
                SMS notifications require a Pro subscription. <a href="/pricing" className="text-blue-600 hover:underline">Upgrade now</a>
              </p>
            )}
          </div>
          {notificationChannels.includes("email") && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
                placeholder="alerts@example.com"
                required
              />
            </div>
          )}
          {notificationChannels.includes("discord") && (
            <div>
              <label className="block text-sm font-medium text-gray-700">
                <div className="flex items-center gap-1">
                  <Hash className="h-4 w-4 text-indigo-600" />
                  Discord Webhook URL
                </div>
              </label>
              <input
                type="url"
                value={discordWebhookUrl}
                onChange={(e) => setDiscordWebhookUrl(e.target.value)}
                className="input"
                placeholder="https://discord.com/api/webhooks/..."
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Get this from Discord: Server Settings → Integrations → Webhooks
              </p>
            </div>
          )}
          {notificationChannels.includes("slack") && (
            <div>
              <label className="block text-sm font-medium text-gray-700">
                <div className="flex items-center gap-1">
                  <MessageSquare className="h-4 w-4 text-green-600" />
                  Slack Webhook URL
                </div>
              </label>
              <input
                type="url"
                value={slackWebhookUrl}
                onChange={(e) => setSlackWebhookUrl(e.target.value)}
                className="input"
                placeholder="https://hooks.slack.com/services/..."
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Get this from Slack: Apps → Incoming Webhooks
              </p>
            </div>
          )}
          {notificationChannels.includes("sms") && (
            <div>
              <label className="block text-sm font-medium text-gray-700">
                <div className="flex items-center gap-1">
                  <Smartphone className="h-4 w-4 text-blue-600" />
                  Phone Number
                </div>
              </label>
              <input
                type="tel"
                value={smsPhoneNumber}
                onChange={(e) => setSmsPhoneNumber(e.target.value)}
                className="input"
                placeholder="+1 (555) 123-4567"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Include country code. SMS charges may apply.
              </p>
            </div>
          )}
          {notificationChannels.includes("webhook") && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Custom Webhook URL</label>
              <input
                type="url"
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                className="input"
                placeholder="https://your-server.com/webhook"
                required
              />
            </div>
          )}
          <div className="flex justify-end mt-4">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary ml-2"
              disabled={mutation.isPending}
            >
              {mutation.isPending ? "Saving..." : "Save"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
