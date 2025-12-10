# TradeSignal Alpha v1.0.0 Release Notes

**Release Date:** December 14, 2025  
**Status:** Alpha Release - MVP  
**Version:** 1.0.0-alpha

---

## Welcome to TradeSignal Alpha

Thank you for being an early adopter of TradeSignal! This Alpha release represents our Minimum Viable Product (MVP) with core features ready for production use, along with some features in beta and experimental stages.

## What's New

TradeSignal Alpha brings you:

- **Real-time Insider Trading Intelligence** - Track SEC Form 4 filings as they happen
- **Congressional Trade Monitoring** - Monitor stock transactions by members of Congress
- **AI-Powered Insights** - Get intelligent analysis of trading patterns (Beta)
- **Custom Alerts** - Set up notifications for trades matching your criteria
- **Multi-Channel Notifications** - Receive alerts via email, push notifications, Discord, Slack, and SMS
- **Company & Insider Profiles** - Detailed information about companies and insiders
- **Market Data Integration** - Live stock prices and market indices
- **Subscription Tiers** - Choose from Free, Plus, Pro, or Enterprise plans

## Data Sources Status

### ✅ Production Ready

These data sources are fully operational and production-ready:

- **SEC Form 4 Filings** - Real-time insider trading data from SEC EDGAR
- **Insider Trade Data** - Comprehensive database of historical and current trades
- **Company Profiles** - Detailed company information and profiles
- **Stripe Billing** - Secure payment processing for subscriptions
- **User Authentication** - Secure JWT-based authentication system
- **Email Notifications** - Email alert delivery (via Resend, Brevo, or SendGrid)
- **Push Notifications** - Browser push notifications for alerts

### 🔶 Beta Features

These features are functional but may require additional API keys and may have limitations:

- **Congressional Trades** - Requires `FINNHUB_API_KEY` environment variable
  - Free tier: 60 calls/minute rate limit
  - May use fallback data sources if Finnhub is unavailable
  - Data freshness may vary based on API availability

- **AI Insights** - Requires `GEMINI_API_KEY` or `OPENAI_API_KEY` environment variable
  - Free Gemini tier: 1,500 requests/day
  - Features include: AI Chat, Company Analysis, Trading Signals, Daily Summary
  - Response times may vary (2-10 seconds typical)
  - Requires `ENABLE_AI_INSIGHTS=true` in backend configuration

### ⚠️ Experimental Features

These features are available but may be intermittent or have limited reliability:

- **Earnings Data** - Via yfinance library
  - May be intermittent due to rate limiting
  - Data accuracy depends on external source availability
  - Not guaranteed to be real-time

## Known Limitations

### Data Freshness

- **SEC Form 4 Filings:** Updated every 6 hours via automated scraper
- **Congressional Trades:** Depends on Finnhub API availability (may have 1-7 day delay)
- **Stock Prices:** Real-time when available, may fall back to delayed data
- **AI Insights:** Cached for 24 hours to optimize performance

### Rate Limits

- **SEC EDGAR API:** Respects SEC rate limits (10 requests/second recommended)
- **Finnhub Free Tier:** 60 calls/minute
- **Gemini Free Tier:** 1,500 requests/day
- **OpenAI:** Based on your API plan limits

### API Dependencies

Some features require external API keys:

- **Congressional Trades:** `FINNHUB_API_KEY` (optional, uses fallback if not set)
- **AI Insights:** `GEMINI_API_KEY` or `OPENAI_API_KEY` (required for AI features)
- **Market Data:** `ALPHA_VANTAGE_API_KEY`, `FINNHUB_API_KEY` (optional)
- **Email Alerts:** `EMAIL_API_KEY` (Resend, Brevo, or SendGrid)
- **SMS Alerts:** `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` (Pro tier only)

### Feature Availability by Tier

- **Free Tier:** Basic insider trades, limited alerts (5 alerts max)
- **Plus Tier:** All Free features + unlimited alerts, email notifications
- **Pro Tier:** All Plus features + SMS alerts, Discord/Slack webhooks, priority support
- **Enterprise:** All Pro features + custom integrations, dedicated support

## Breaking Changes

This is the initial Alpha release, so there are no breaking changes from previous versions.

## Upgrade Notes

If you're upgrading from a development version:

1. Ensure all required environment variables are set (see [README.md](../README.md))
2. Run database migrations: `docker-compose exec backend alembic upgrade head`
3. Clear Redis cache if upgrading: `docker-compose exec redis redis-cli FLUSHALL`
4. Restart all services: `docker-compose restart`

## Bug Fixes

- Initial Alpha release - no previous bugs to fix

## Security Notes

- All API endpoints require authentication (except public health checks)
- JWT tokens expire after 24 hours (configurable)
- Passwords are hashed using bcrypt
- Payment processing handled securely by Stripe
- Webhook URLs should be kept secret and rotated if compromised

## Performance

- Average API response time: < 200ms
- Database queries optimized with indexes
- Redis caching for frequently accessed data
- Background task processing via Celery

## Support

- **Documentation:** See [docs/](../docs/) directory
- **Email Support:** support@tradesignal.com
- **GitHub Issues:** For bug reports and feature requests

## What's Next

We're actively working on:

- Mobile app (iOS/Android)
- Advanced charting and analytics
- Portfolio tracking
- Social features and community insights
- Enhanced AI capabilities
- More data sources

## Feedback

Your feedback is invaluable! Please share your thoughts, report bugs, or suggest features:

- Email: support@tradesignal.com
- GitHub Issues: [Create an issue](https://github.com/yourusername/TradeSignal/issues)

---

**Thank you for using TradeSignal!** 🚀

