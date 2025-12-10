# Discord Webhooks Setup Guide

Learn how to configure Discord webhooks to receive TradeSignal alerts directly in your Discord server or channel.

## What are Discord Webhooks?

Discord webhooks allow TradeSignal to send automated messages to your Discord server or channel when insider trades match your alert criteria. This is perfect for:

- **Team Collaboration** - Share trade alerts with your team in a dedicated channel
- **Real-time Notifications** - Get instant notifications without checking email
- **Customizable Messages** - Rich formatted messages with trade details
- **No Bot Required** - Simple webhook setup, no Discord bot needed

## Prerequisites

- A Discord account
- Permission to manage webhooks in your Discord server (Server Administrator or Manage Webhooks permission)
- A TradeSignal account with Pro or Enterprise subscription (Discord webhooks are a Pro feature)

## Step-by-Step Setup

### Step 1: Create a Discord Webhook

1. **Open Discord** and navigate to your server
2. **Go to Server Settings:**
   - Right-click on your server name
   - Select "Server Settings"
3. **Navigate to Integrations:**
   - Click "Integrations" in the left sidebar
   - Click "Webhooks" at the top
4. **Create New Webhook:**
   - Click "New Webhook" button
   - Choose the channel where you want alerts to appear
   - Give your webhook a name (e.g., "TradeSignal Alerts")
   - Optionally, upload an avatar image
   - Click "Copy Webhook URL"
   - **Important:** Save this URL securely - you'll need it in Step 2

### Step 2: Configure Alert in TradeSignal

1. **Log in to TradeSignal** and navigate to the Alerts page
2. **Create a New Alert** or **Edit an Existing Alert:**
   - Click "Create Alert" or select an alert to edit
3. **Select Notification Channels:**
   - Check the "Discord" checkbox under notification channels
4. **Enter Your Webhook URL:**
   - Paste the Discord webhook URL you copied in Step 1
   - The URL should look like: `https://discord.com/api/webhooks/123456789/abcdefghijklmnopqrstuvwxyz`
5. **Configure Alert Criteria:**
   - Set your ticker symbols, trade types, thresholds, etc.
6. **Save the Alert:**
   - Click "Save" or "Create Alert"

### Step 3: Test Your Webhook

1. **Trigger a Test Alert:**
   - Wait for a trade that matches your alert criteria, OR
   - Create a test alert with very broad criteria to trigger quickly
2. **Check Discord:**
   - You should see a message in your Discord channel with trade details
   - The message will include:
     - Company name and ticker
     - Insider name and role
     - Trade type (Buy/Sell)
     - Number of shares
     - Trade value
     - Transaction date
     - Link to view more details

## Webhook Message Format

Discord webhook messages from TradeSignal include:

```
🚨 Trade Alert: [TICKER] - [Company Name]

**Insider:** [Insider Name] ([Role])
**Type:** [Buy/Sell]
**Shares:** [Number]
**Value:** $[Amount]
**Date:** [Date]

[View Details](link to TradeSignal)
```

## Troubleshooting

### Webhook Not Receiving Messages

**Problem:** Alerts are configured but no messages appear in Discord.

**Solutions:**
1. **Verify Webhook URL:**
   - Check that the webhook URL is correct and complete
   - Ensure there are no extra spaces or characters
   - Try copying the URL again from Discord

2. **Check Alert Criteria:**
   - Verify that trades are actually matching your alert criteria
   - Check the Alert History in TradeSignal to see if alerts are being triggered

3. **Verify Webhook is Active:**
   - Go back to Discord Server Settings → Integrations → Webhooks
   - Ensure the webhook is still active (not deleted)
   - Check that the channel still exists

4. **Check Subscription Tier:**
   - Discord webhooks require Pro or Enterprise subscription
   - Verify your account has the correct tier

5. **Test Webhook Manually:**
   - You can test the webhook URL directly using curl:
   ```bash
   curl -X POST "YOUR_WEBHOOK_URL" \
     -H "Content-Type: application/json" \
     -d '{"content": "Test message from TradeSignal"}'
   ```

### Webhook Returns 404 Error

**Problem:** Discord returns a 404 error when TradeSignal tries to send a message.

**Solutions:**
1. **Webhook was deleted:** The webhook URL is no longer valid. Create a new webhook and update your alert.
2. **Channel was deleted:** The channel the webhook was configured for no longer exists. Create a new webhook pointing to an existing channel.
3. **Server was deleted:** The Discord server no longer exists. Create a new webhook in a different server.

### Messages Appear in Wrong Channel

**Problem:** Alerts are going to a different channel than expected.

**Solution:**
- Each webhook URL is tied to a specific channel
- To change the channel, create a new webhook in the desired channel and update your alert with the new URL

### Rate Limiting

**Problem:** Some messages are not being delivered.

**Solution:**
- Discord has rate limits for webhooks (approximately 30 requests per minute)
- If you have many alerts triggering simultaneously, some may be delayed
- TradeSignal automatically retries failed webhook deliveries up to 3 times

## Security Best Practices

### Keep Your Webhook URL Secret

⚠️ **Important:** Your Discord webhook URL is like a password - anyone with the URL can send messages to your channel.

**Do:**
- ✅ Store the webhook URL securely in TradeSignal (it's encrypted in our database)
- ✅ Only share the URL with trusted team members
- ✅ Use different webhooks for different purposes (e.g., one for alerts, one for testing)

**Don't:**
- ❌ Share webhook URLs in public channels or forums
- ❌ Commit webhook URLs to version control (Git)
- ❌ Post screenshots containing webhook URLs

### Revoke Compromised Webhooks

If you suspect your webhook URL has been compromised:

1. **Delete the Webhook:**
   - Go to Discord Server Settings → Integrations → Webhooks
   - Find the compromised webhook
   - Click the three dots (⋯) → "Delete Webhook"

2. **Create a New Webhook:**
   - Follow Step 1 above to create a new webhook
   - Update your TradeSignal alert with the new URL

3. **Monitor Your Channel:**
   - Check for any unauthorized messages
   - If spam appears, delete the webhook immediately

### Use Separate Webhooks for Different Alerts

**Best Practice:** Create separate webhooks for:
- Production alerts (main trading alerts)
- Test alerts (for testing new alert configurations)
- Different teams or purposes

This allows you to:
- Revoke access independently if needed
- Organize messages into different channels
- Control who has access to which alerts

## Advanced Configuration

### Custom Channel Organization

You can organize alerts by creating multiple webhooks:

- **High-Priority Alerts:** Create a webhook in a dedicated #alerts-urgent channel
- **Daily Summary:** Create a webhook in a #daily-summary channel
- **Specific Tickers:** Create separate webhooks for different ticker symbols

### Webhook Permissions

Discord webhooks inherit the permissions of the channel they're configured for:

- If the channel is private, only members with access can see webhook messages
- If the channel is public, all server members can see the messages
- Webhooks can mention roles or users if the channel permissions allow it

## FAQ

**Q: Can I use the same webhook for multiple alerts?**  
A: Yes! You can configure multiple alerts to use the same Discord webhook URL. All matching alerts will be sent to the same channel.

**Q: Do I need a Discord bot?**  
A: No! Discord webhooks work without a bot. They're simpler to set up and don't require bot permissions.

**Q: Can I customize the message format?**  
A: Currently, TradeSignal sends a standardized format. Custom message formatting may be available in future updates.

**Q: What happens if Discord is down?**  
A: TradeSignal will retry failed webhook deliveries up to 3 times. If Discord is unavailable, alerts will be logged in your Alert History for later review.

**Q: Can I use webhooks on a free Discord server?**  
A: Yes! Discord webhooks work on both free and paid Discord servers.

**Q: How many webhooks can I create?**  
A: Discord allows up to 10 webhooks per channel. You can create multiple webhooks across different channels as needed.

## Need Help?

If you're still having issues:

1. **Check the Troubleshooting section** above
2. **Review your Alert History** in TradeSignal to see if alerts are being triggered
3. **Contact Support:** support@tradesignal.com
4. **See General Alerts Setup:** [ALERTS_SETUP.md](ALERTS_SETUP.md)

---

**Related Documentation:**
- [General Alerts Setup Guide](ALERTS_SETUP.md)
- [Getting Started Guide](GETTING_STARTED.md)
- [FAQ](FAQ.md)

