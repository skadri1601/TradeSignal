# Alerts Setup Guide

Learn how to create and manage trade alerts in TradeSignal to get notified when insider trades match your criteria.

## Overview

TradeSignal alerts allow you to monitor insider trading activity and receive notifications when trades match your specific criteria. You can set up alerts for:

- Specific companies (ticker symbols)
- Trade types (buys, sells, or both)
- Trade value thresholds
- Insider roles (CEO, CFO, Director, etc.)
- Date ranges
- Multiple notification channels

## Creating Your First Alert

### Step 1: Navigate to Alerts

1. Log in to your TradeSignal account
2. Click "Alerts" in the navigation menu
3. Click the "Create Alert" button

### Step 2: Configure Alert Criteria

**Alert Name:**
- Give your alert a descriptive name (e.g., "NVDA CEO Buys")

**Ticker Symbols:**
- Enter one or more ticker symbols (e.g., NVDA, TSLA, AAPL)
- Separate multiple tickers with commas
- Leave blank to monitor all companies

**Trade Type:**
- **Buy Only:** Only notify on insider purchases
- **Sell Only:** Only notify on insider sales
- **Both:** Notify on both buys and sells

**Minimum Trade Value:**
- Set a minimum dollar value threshold (e.g., $100,000)
- Only trades above this value will trigger alerts
- Leave blank or set to $0 to receive all trades

**Insider Roles (Optional):**
- Filter by specific insider roles:
  - CEO (Chief Executive Officer)
  - CFO (Chief Financial Officer)
  - Director
  - Officer
  - 10% Owner
- Leave blank to monitor all insiders

**Date Range (Optional):**
- Monitor trades within a specific date range
- Leave blank to monitor all recent trades

### Step 3: Configure Notification Channels

Select one or more notification channels:

**Email:**
- Requires: Email address
- Available on: All tiers
- Best for: Daily summaries and important alerts

**Push Notifications:**
- Requires: Browser permission (granted when you enable)
- Available on: All tiers
- Best for: Real-time alerts when browser is open

**Discord Webhook:**
- Requires: Discord webhook URL (Pro/Enterprise only)
- Available on: Pro, Enterprise tiers
- Best for: Team collaboration and channel organization
- See: [Discord Webhooks Guide](ALERTS_DISCORD_WEBHOOKS.md)

**Slack Webhook:**
- Requires: Slack webhook URL (Pro/Enterprise only)
- Available on: Pro, Enterprise tiers
- Best for: Team collaboration in Slack

**SMS:**
- Requires: Phone number (Pro/Enterprise only)
- Available on: Pro, Enterprise tiers
- Best for: Critical alerts when away from computer

**Generic Webhook:**
- Requires: Webhook URL
- Available on: All tiers
- Best for: Custom integrations

### Step 4: Save Your Alert

1. Review your alert configuration
2. Click "Create Alert" or "Save"
3. Your alert is now active and will trigger when trades match your criteria

## Managing Alerts

### Viewing Your Alerts

- Go to the Alerts page to see all your active alerts
- Each alert shows:
  - Alert name
  - Criteria summary
  - Notification channels
  - Last triggered date
  - Status (Active/Inactive)

### Editing Alerts

1. Click on an alert to open the edit modal
2. Modify any criteria or notification settings
3. Click "Save" to update

### Deleting Alerts

1. Click on an alert to open the edit modal
2. Click "Delete" button
3. Confirm deletion

**Note:** Deleting an alert also deletes its history. Consider deactivating instead if you want to keep historical data.

### Alert Limits

- **Free Tier:** Maximum 5 alerts
- **Plus Tier:** Unlimited alerts
- **Pro Tier:** Unlimited alerts
- **Enterprise:** Unlimited alerts

## Alert History

View the history of all alert triggers:

1. Go to the Alerts page
2. Click on an alert
3. View the "Alert History" tab
4. See all trades that matched your alert criteria
5. View notification delivery status for each trigger

## Notification Channels Explained

### Email Notifications

**Setup:**
- Simply enter your email address when creating/editing an alert
- Verify your email if prompted

**Best For:**
- Daily summaries
- Important alerts you don't want to miss
- Archival purposes

**Delivery:**
- Sent within 5 minutes of trade detection
- Includes full trade details
- Can be filtered/routed in your email client

### Push Notifications

**Setup:**
- Select "Push" as a notification channel
- Grant browser permission when prompted
- Works even when TradeSignal tab is closed (if browser is running)

**Best For:**
- Real-time alerts
- When you're actively monitoring the market
- Quick notifications without checking email

**Requirements:**
- Modern browser with push notification support
- Permission granted to TradeSignal
- Browser must be running (not closed)

### Discord Webhooks

**Setup:**
- Requires Pro or Enterprise subscription
- Create a Discord webhook (see [Discord Webhooks Guide](ALERTS_DISCORD_WEBHOOKS.md))
- Enter webhook URL in alert configuration

**Best For:**
- Team collaboration
- Channel organization
- Real-time team notifications

### Slack Webhooks

**Setup:**
- Requires Pro or Enterprise subscription
- Create a Slack webhook in your workspace
- Enter webhook URL in alert configuration

**Best For:**
- Team collaboration in Slack
- Integration with existing Slack workflows

### SMS Notifications

**Setup:**
- Requires Pro or Enterprise subscription
- Enter your phone number (with country code, e.g., +1234567890)
- Verify your phone number if prompted

**Best For:**
- Critical alerts when away from computer
- Urgent notifications
- High-value trade alerts

**Limitations:**
- SMS delivery may be delayed (up to 15 minutes)
- Carrier charges may apply
- Not available in all countries

### Generic Webhooks

**Setup:**
- Enter any webhook URL (HTTP/HTTPS)
- TradeSignal will POST JSON data to your endpoint

**Best For:**
- Custom integrations
- Third-party services
- Automation workflows

**Webhook Payload:**
```json
{
  "alert_name": "NVDA CEO Buys",
  "ticker": "NVDA",
  "company_name": "NVIDIA Corporation",
  "insider_name": "Jensen Huang",
  "insider_role": "CEO",
  "trade_type": "Buy",
  "shares": 10000,
  "value": 5000000,
  "transaction_date": "2025-12-14",
  "alert_id": 123
}
```

## Alert Best Practices

### Organize by Purpose

Create separate alerts for different purposes:

- **High-Priority Alerts:** Critical trades (CEO buys > $1M)
- **Daily Monitoring:** All trades for specific tickers
- **Role-Based:** Monitor specific insider roles across companies
- **Value-Based:** Only significant trades (e.g., > $500K)

### Use Multiple Channels

Combine notification channels for redundancy:

- **Email + Push:** Email for archive, push for immediate notification
- **Discord + Email:** Discord for team, email for personal backup
- **SMS + Email:** SMS for urgent, email for details

### Set Realistic Thresholds

- Start with higher value thresholds to avoid alert fatigue
- Adjust thresholds based on your needs
- Monitor alert history to fine-tune criteria

### Review Alert History Regularly

- Check which alerts are triggering most often
- Adjust criteria to reduce false positives
- Identify patterns in insider trading activity

## Troubleshooting

### Alerts Not Triggering

**Check:**
1. Alert is active (not paused/deleted)
2. Trades actually match your criteria
3. Alert History shows no recent triggers
4. Your subscription tier supports the number of alerts you have

**Solutions:**
- Verify ticker symbols are correct
- Check minimum value threshold isn't too high
- Review Alert History to see what trades are being detected

### Notifications Not Arriving

**Email:**
- Check spam/junk folder
- Verify email address is correct
- Check email service isn't blocking TradeSignal

**Push:**
- Verify browser permission is granted
- Check browser notifications aren't disabled
- Ensure browser is running

**Discord/Slack:**
- Verify webhook URL is correct
- Check webhook is still active in Discord/Slack
- See [Discord Webhooks Guide](ALERTS_DISCORD_WEBHOOKS.md) for troubleshooting

**SMS:**
- Verify phone number format (include country code)
- Check carrier isn't blocking messages
- Verify Pro/Enterprise subscription is active

### Too Many Alerts

**Solutions:**
- Increase minimum trade value threshold
- Filter by specific insider roles
- Limit to specific ticker symbols
- Use date ranges to monitor specific periods
- Combine multiple criteria to narrow results

## FAQ

**Q: How quickly do alerts trigger after a trade is detected?**  
A: Alerts typically trigger within 5 minutes of trade detection. This may vary based on data source freshness.

**Q: Can I pause an alert without deleting it?**  
A: Yes, you can deactivate alerts temporarily. They won't trigger but remain in your alert list.

**Q: Do alerts work for historical trades?**  
A: Alerts only trigger for new trades detected after the alert is created. They don't scan historical data.

**Q: Can I set up alerts for congressional trades?**  
A: Yes! Congressional trades can be monitored with the same alert system. Note that congressional trade data may have delays (see Release Notes).

**Q: How many notification channels can I use per alert?**  
A: You can use as many notification channels as your subscription tier allows. There's no limit on channels per alert.

**Q: Can I share alerts with my team?**  
A: Currently, alerts are per-user. Team sharing may be available in Enterprise plans. Use Discord/Slack webhooks for team notifications.

## Need Help?

- **Discord Webhooks:** See [ALERTS_DISCORD_WEBHOOKS.md](ALERTS_DISCORD_WEBHOOKS.md)
- **General Questions:** See [FAQ.md](FAQ.md)
- **Troubleshooting:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Contact Support:** support@tradesignal.com

---

**Related Documentation:**
- [Discord Webhooks Guide](ALERTS_DISCORD_WEBHOOKS.md)
- [Getting Started Guide](GETTING_STARTED.md)
- [FAQ](FAQ.md)

