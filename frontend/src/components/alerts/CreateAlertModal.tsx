import { useState, useContext } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { alertsApi } from "../../api/alerts";
import { Alert, AlertType, NotificationChannel } from "../../types";
import { usePushNotifications } from "../../hooks/usePushNotifications";
import { AuthContext } from "../../contexts/AuthContext";
import { Bell, BellOff, MessageSquare, Hash, Smartphone, Crown } from "lucide-react";

interface CreateAlertModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CreateAlertModal({
  isOpen,
  onClose,
}: CreateAlertModalProps) {
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
      email: email || null,
      discord_webhook_url: discordWebhookUrl || null,
      slack_webhook_url: slackWebhookUrl || null,
      sms_phone_number: smsPhoneNumber || null,
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-900/90 backdrop-blur-md p-8 rounded-lg shadow-xl border border-white/10 w-full max-w-lg">
        <h2 className="text-2xl font-bold mb-4 text-white">Create New Alert</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-700 bg-gray-800 text-white shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300">Alert Type</label>
            <select
              value={alertType}
              onChange={(e) => setAlertType(e.target.value as AlertType)}
              className="mt-1 block w-full rounded-md border-gray-700 bg-gray-800 text-white shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
            >
              <option value="large_trade">Large Trade</option>
              <option value="company_watch">Company Watch</option>
              <option value="insider_role">Insider Role</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300">Ticker</label>
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-700 bg-gray-800 text-white shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300">Minimum Value ($)</label>
            <input
              type="number"
              value={minValue}
              onChange={(e) => setMinValue(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-700 bg-gray-800 text-white shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300">Transaction Type</label>
            <select
              value={transactionType}
              onChange={(e) =>
                setTransactionType(e.target.value as "BUY" | "SELL" | "")
              }
              className="mt-1 block w-full rounded-md border-gray-700 bg-gray-800 text-white shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
            >
              <option value="">Any</option>
              <option value="BUY">Buy</option>
              <option value="SELL">Sell</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Notification Channels</label>
            <div className="grid grid-cols-2 gap-2 text-gray-300">
              {/* Email */}
              <label className="flex items-center p-2 border border-gray-700 rounded hover:bg-gray-800 cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationChannels.includes("email")}
                  onChange={() => handleChannelChange("email")}
                  className="mr-2 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-600 rounded bg-gray-700"
                />
                <span>Email</span>
              </label>

              {/* Browser Push */}
              <label className="flex items-center p-2 border border-gray-700 rounded hover:bg-gray-800 cursor-pointer">
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
                  className="mr-2 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-600 rounded bg-gray-700"
                />
                <div className="flex items-center gap-1">
                  {notificationChannels.includes("push") ? (
                    <Bell className="h-4 w-4 text-green-400" />
                  ) : (
                    <BellOff className="h-4 w-4 text-gray-400" />
                  )}
                  <span>Push</span>
                </div>
              </label>

              {/* Discord */}
              <label className="flex items-center p-2 border border-gray-700 rounded hover:bg-gray-800 cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationChannels.includes("discord")}
                  onChange={() => handleChannelChange("discord")}
                  className="mr-2 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-600 rounded bg-gray-700"
                />
                <div className="flex items-center gap-1">
                  <Hash className="h-4 w-4 text-purple-400" />
                  <span>Discord</span>
                </div>
              </label>

              {/* Slack */}
              <label className="flex items-center p-2 border border-gray-700 rounded hover:bg-gray-800 cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationChannels.includes("slack")}
                  onChange={() => handleChannelChange("slack")}
                  className="mr-2 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-600 rounded bg-gray-700"
                />
                <div className="flex items-center gap-1">
                  <MessageSquare className="h-4 w-4 text-green-400" />
                  <span>Slack</span>
                </div>
              </label>

              {/* SMS - Pro Only */}
              <label className={`flex items-center p-2 border border-gray-700 rounded ${isPro ? 'hover:bg-gray-800 cursor-pointer' : 'opacity-50 cursor-not-allowed'}`}>
                <input
                  type="checkbox"
                  checked={notificationChannels.includes("sms")}
                  onChange={() => handleChannelChange("sms")}
                  disabled={!isPro}
                  className="mr-2 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-600 rounded bg-gray-700"
                />
                <div className="flex items-center gap-1">
                  <Smartphone className="h-4 w-4 text-blue-400" />
                  <span>SMS</span>
                  {!isPro && <Crown className="h-3 w-3 text-yellow-400 ml-1" aria-label="Pro tier required" />}
                </div>
              </label>

              {/* Custom Webhook */}
              <label className="flex items-center p-2 border border-gray-700 rounded hover:bg-gray-800 cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationChannels.includes("webhook")}
                  onChange={() => handleChannelChange("webhook")}
                  className="mr-2 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-600 rounded bg-gray-700"
                />
                <span>Webhook</span>
              </label>
            </div>
            {!isPro && (
              <p className="text-xs text-gray-400 mt-2">
                SMS notifications require a Pro subscription. <a href="/pricing" className="text-purple-400 hover:underline">Upgrade now</a>
              </p>
            )}
          </div>
          {notificationChannels.includes("email") && (
            <div>
              <label className="block text-sm font-medium text-gray-300">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-700 bg-gray-800 text-white shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
                placeholder="alerts@example.com"
                required
              />
            </div>
          )}
          {notificationChannels.includes("discord") && (
            <div>
              <label className="block text-sm font-medium text-gray-300">
                <div className="flex items-center gap-1">
                  <Hash className="h-4 w-4 text-purple-400" />
                  Discord Webhook URL
                </div>
              </label>
              <input
                type="url"
                value={discordWebhookUrl}
                onChange={(e) => setDiscordWebhookUrl(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-700 bg-gray-800 text-white shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
                placeholder="https://discord.com/api/webhooks/..."
                required
              />
              <p className="text-xs text-gray-400 mt-1">
                Get this from Discord: Server Settings → Integrations → Webhooks
              </p>
            </div>
          )}
          {notificationChannels.includes("slack") && (
            <div>
              <label className="block text-sm font-medium text-gray-300">
                <div className="flex items-center gap-1">
                  <MessageSquare className="h-4 w-4 text-green-400" />
                  Slack Webhook URL
                </div>
              </label>
              <input
                type="url"
                value={slackWebhookUrl}
                onChange={(e) => setSlackWebhookUrl(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-700 bg-gray-800 text-white shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
                placeholder="https://hooks.slack.com/services/..."
                required
              />
              <p className="text-xs text-gray-400 mt-1">
                Get this from Slack: Apps → Incoming Webhooks
              </p>
            </div>
          )}
          {notificationChannels.includes("sms") && (
            <div>
              <label className="block text-sm font-medium text-gray-300">
                <div className="flex items-center gap-1">
                  <Smartphone className="h-4 w-4 text-blue-400" />
                  Phone Number
                </div>
              </label>
              <input
                type="tel"
                value={smsPhoneNumber}
                onChange={(e) => setSmsPhoneNumber(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-700 bg-gray-800 text-white shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
                placeholder="+1 (555) 123-4567"
                required
              />
              <p className="text-xs text-gray-400 mt-1">
                Include country code. SMS charges may apply.
              </p>
            </div>
          )}
          {notificationChannels.includes("webhook") && (
            <div>
              <label className="block text-sm font-medium text-gray-300">Custom Webhook URL</label>
              <input
                type="url"
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-700 bg-gray-800 text-white shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
                placeholder="https://your-server.com/webhook"
                required
              />
            </div>
          )}
          <div className="flex justify-end mt-4">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded-lg text-sm font-medium bg-gray-700 text-white hover:bg-gray-600 transition-colors">
              Cancel
            </button>
            <button type="submit" className="px-4 py-2 rounded-lg text-sm font-medium bg-purple-600 text-white hover:bg-purple-700 transition-colors ml-2" disabled={mutation.isPending}>
              {mutation.isPending ? "Creating..." : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}