# Phase 5: Notifications & Alerts - Implementation Plan

**Branch:** `feature/notifications/alerts`
**Status:** 🚧 IN PROGRESS
**Started:** November 2, 2025
**Last Updated:** November 2, 2025 02:30 AM

---

there's a alert page, but no alrts are found and an 3 tabs called- all, active, inactive and an buttton for crate alert which doesn't click on. also keep the amounts round off like $3.6M or $500B like round off instead off showing whole value and in the dashboard only 10 trades were shown earlier what happened to that? Also there was an auto dilter for default days like- 7 days, 30 days, 60 days and 90 days what happened to that? Also when I typed stock name a list was showing in the filter, but now it's not there- what happened to that?

## 🎯 Phase Overview

Implement a comprehensive alert and notification system that allows users to receive real-time notifications when significant insider trades occur. Start with webhooks (Slack/Discord) for immediate value, then add email notifications, and optionally add browser push notifications.

---

## 📋 Implementation Phases

### **Phase 5A: Webhook Notifications (MVP)** 🚧 IN PROGRESS

**Goal:** Get instant notifications via Slack/Discord webhooks

**Time Estimate:** 1-2 hours

#### Backend Tasks
- [ ] 1. Create database models
  - [ ] `backend/app/models/alert.py` - Alert rule storage
  - [ ] `backend/app/models/alert_history.py` - Triggered alerts log
  - [ ] Update `backend/app/models/__init__.py`

- [ ] 2. Create Pydantic schemas
  - [ ] `backend/app/schemas/alert.py` - Request/response schemas
  - [ ] Update `backend/app/schemas/__init__.py`

- [ ] 3. Create alert services
  - [ ] `backend/app/services/alert_service.py` - Alert matching engine
  - [ ] `backend/app/services/notification_service.py` - Webhook sender

- [ ] 4. Create API endpoints
  - [ ] `backend/app/routers/alerts.py` - CRUD + test endpoints
  - [ ] Register router in `main.py`

- [ ] 5. Add configuration
  - [ ] Update `backend/app/config.py` with alert settings
  - [ ] Update `.env.example`

- [ ] 6. Integrate with scheduler
  - [ ] Update `backend/app/services/scheduler_service.py`
  - [ ] Add job to check alerts every 5 minutes

- [ ] 7. Database migration
  - [ ] Create tables on startup
  - [ ] Verify schema in PostgreSQL

#### Frontend Tasks
- [ ] 8. Create TypeScript types
  - [ ] Update `frontend/src/types/index.ts`

- [ ] 9. Create API client
  - [ ] `frontend/src/api/alerts.ts`

- [ ] 10. Create Alerts page
  - [ ] `frontend/src/pages/AlertsPage.tsx`
  - [ ] Add route to `App.tsx`
  - [ ] Add nav link to `Navbar.tsx`

- [ ] 11. Create Alert components
  - [ ] `frontend/src/components/alerts/AlertList.tsx`
  - [ ] `frontend/src/components/alerts/AlertCard.tsx`
  - [ ] `frontend/src/components/alerts/CreateAlertModal.tsx`

- [ ] 12. Testing & Polish
  - [ ] Create test alert
  - [ ] Trigger test notification
  - [ ] Verify Slack/Discord webhook delivery
  - [ ] Test CRUD operations

---

### **Phase 5B: Email Notifications** ⏳ NOT STARTED

**Goal:** Send HTML emails when alerts trigger

**Time Estimate:** 1 hour

#### Tasks
- [ ] 1. Choose email service (Brevo/Resend/SendGrid)
- [ ] 2. Sign up and get API key
- [ ] 3. Add email config to `config.py`
- [ ] 4. Create email templates
  - [ ] `backend/app/templates/alert_email.html`
  - [ ] `backend/app/templates/alert_email.txt` (plaintext fallback)
- [ ] 5. Update `notification_service.py` with email sender
- [ ] 6. Add email channel to alert creation UI
- [ ] 7. Test email delivery
- [ ] 8. Verify spam score (use mail-tester.com)

---

### **Phase 5C: Browser Push Notifications** ⏳ NOT STARTED

**Goal:** Native browser notifications using Web Push API

**Time Estimate:** 45 minutes

#### Tasks
- [ ] 1. Generate VAPID keys for push
- [ ] 2. Add service worker for push
  - [ ] `frontend/public/sw.js`
- [ ] 3. Create push notification hook
  - [ ] `frontend/src/hooks/usePushNotifications.ts`
- [ ] 4. Add "Enable Notifications" button to UI
- [ ] 5. Update backend to store push subscriptions
- [ ] 6. Send push notifications from alert service
- [ ] 7. Test on Chrome/Firefox/Edge

---

## 🗄️ Database Schema

### `alerts` Table
```sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    ticker VARCHAR(10),
    min_value DECIMAL(20, 2),
    max_value DECIMAL(20, 2),
    transaction_type VARCHAR(10),
    insider_roles TEXT[],
    notification_channels TEXT[] NOT NULL,
    webhook_url TEXT,
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### `alert_history` Table
```sql
CREATE TABLE alert_history (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER REFERENCES alerts(id) ON DELETE CASCADE,
    trade_id INTEGER REFERENCES trades(id) ON DELETE CASCADE,
    notification_channel VARCHAR(50) NOT NULL,
    notification_status VARCHAR(50) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🎨 Alert Types

### 1. **Large Trade Alert**
- Trigger when trade value > threshold (e.g., $100K, $1M, $10M)
- Filter by BUY/SELL
- Filter by specific tickers

### 2. **Company Watch Alert**
- Monitor specific companies (NVDA, TSLA, AAPL, etc.)
- Any insider trade triggers notification
- Optional: Only significant trades

### 3. **Insider Role Alert**
- CEO/CFO purchases (bullish signal)
- Director trades
- 10% owners
- Filter by transaction type

### 4. **Volume Spike Alert** (Future)
- Unusual activity (3x average volume)
- Multiple insiders trading same day
- Cluster detection

---

## 🔔 Notification Channels

### Webhook (Phase 5A)
- **Slack:** `https://hooks.slack.com/services/YOUR/WEBHOOK/URL`
- **Discord:** `https://discord.com/api/webhooks/ID/TOKEN`
- **Custom:** Any HTTPS endpoint

**Payload Format:**
```json
{
  "text": "🚨 Large Trade Alert: NVDA",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*CEO Jane Smith* bought *$5,000,000* of NVDA stock"
      }
    },
    {
      "type": "section",
      "fields": [
        {"type": "mrkdwn", "text": "*Shares:* 50,000"},
        {"type": "mrkdwn", "text": "*Price:* $100.00"},
        {"type": "mrkdwn", "text": "*Date:* 2025-11-01"},
        {"type": "mrkdwn", "text": "*Type:* Purchase"}
      ]
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {"type": "plain_text", "text": "View SEC Filing"},
          "url": "https://sec.gov/..."
        }
      ]
    }
  ]
}
```

### Email (Phase 5B)
- HTML template with company logo
- Trade details table
- Link to SEC filing
- Link to TradeSignal dashboard

### Browser Push (Phase 5C)
- Native browser notification
- Click to open trade details
- Requires user permission

---

## 🔧 Configuration

### Environment Variables

```bash
# Alert Configuration
ALERTS_ENABLED=true
ALERT_CHECK_INTERVAL_MINUTES=5
MAX_ALERTS_PER_USER=50
ALERT_COOLDOWN_MINUTES=60

# Webhook Configuration
WEBHOOK_TIMEOUT_SECONDS=10
WEBHOOK_RETRY_COUNT=3
WEBHOOK_MAX_REDIRECTS=2

# Email Configuration (Phase 5B)
EMAIL_SERVICE=brevo  # brevo | resend | sendgrid
EMAIL_API_KEY=your_api_key_here
EMAIL_FROM=alerts@tradesignal.com
EMAIL_FROM_NAME=TradeSignal Alerts

# Push Notifications (Phase 5C)
PUSH_ENABLED=false
VAPID_PUBLIC_KEY=your_public_key
VAPID_PRIVATE_KEY=your_private_key
VAPID_CONTACT_EMAIL=admin@tradesignal.com
```

---

## 📊 API Endpoints

### Alert Management

```
POST   /api/v1/alerts/              Create new alert
GET    /api/v1/alerts/              List all alerts (paginated)
GET    /api/v1/alerts/{id}          Get single alert
PATCH  /api/v1/alerts/{id}          Update alert
DELETE /api/v1/alerts/{id}          Delete alert
POST   /api/v1/alerts/{id}/test     Send test notification
POST   /api/v1/alerts/{id}/toggle   Enable/disable alert
```

### Alert History

```
GET    /api/v1/alerts/history               List triggered alerts
GET    /api/v1/alerts/{id}/history          Get alert's trigger history
GET    /api/v1/alerts/stats                 Alert statistics
```

---

## 🧪 Testing Checklist

### Phase 5A: Webhooks
- [ ] Create alert with Slack webhook
- [ ] Create alert with Discord webhook
- [ ] Trigger test notification manually
- [ ] Scrape new trade that matches alert
- [ ] Verify webhook received
- [ ] Test alert cooldown (no duplicate notifications)
- [ ] Test multiple alerts on same trade
- [ ] Test alert deactivation
- [ ] Test alert deletion (cascade to history)
- [ ] Test pagination on alerts list
- [ ] Test filtering on alert history

### Phase 5B: Email
- [ ] Send test email
- [ ] Check spam score (> 8/10 on mail-tester.com)
- [ ] Verify HTML rendering in Gmail
- [ ] Verify HTML rendering in Outlook
- [ ] Test plaintext fallback
- [ ] Verify links work (SEC filing, dashboard)
- [ ] Test email rate limiting

### Phase 5C: Push
- [ ] Request notification permission
- [ ] Subscribe to push
- [ ] Receive push notification
- [ ] Click notification → opens trade
- [ ] Test on Chrome
- [ ] Test on Firefox
- [ ] Test on Edge

---

## 🐛 Known Issues / TODO

- [ ] Multi-user support (currently single admin user)
- [ ] Alert rule validation (prevent invalid configurations)
- [ ] Rate limiting per alert (max 10 notifications/hour)
- [ ] Digest mode (batch notifications)
- [ ] Quiet hours (no notifications 10pm-8am)
- [ ] Alert templates (pre-configured alerts)
- [ ] SMS notifications (Twilio integration)
- [ ] Mobile app push (FCM/APNS)

---

## 📈 Success Metrics

- ✅ Alerts trigger within 5 minutes of new trade
- ✅ Webhook delivery success rate > 95%
- ✅ Email delivery success rate > 99%
- ✅ Zero duplicate notifications
- ✅ Alert creation time < 30 seconds
- ✅ System handles 100+ active alerts without performance degradation

---

## 🚀 Deployment Notes

### Backend Dependencies
```bash
# Add to requirements.txt
httpx>=0.27.0          # For webhook HTTP requests
jinja2>=3.1.0          # Email templating (Phase 5B)
brevoapi>=1.0.0        # If using Brevo (Phase 5B)
resend>=0.7.0          # If using Resend (Phase 5B)
sendgrid>=6.11.0       # If using SendGrid (Phase 5B)
pywebpush>=1.14.0      # Web Push (Phase 5C)
```

### Frontend Dependencies
```bash
# Already installed (no new dependencies for Phase 5A)
# For Phase 5C (Push):
npm install web-push
```

---

## 📝 Progress Log

### 2025-11-02 02:30 AM - Phase 5A Started
- Created PHASE5.md
- Branch: feature/notifications/alerts
- Starting with webhook notifications (Slack/Discord)
- Next: Create database models

---

**Last Updated:** November 2, 2025 02:30 AM
**Author:** Saad Kadri
**Current Focus:** Phase 5A - Webhook Notifications
