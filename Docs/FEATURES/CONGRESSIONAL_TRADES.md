# Congressional Trades Feature Guide

Learn how to use TradeSignal's Congressional Trades feature to monitor stock transactions by members of the U.S. Congress.

## Overview

The Congressional Trades feature tracks stock transactions by members of the U.S. Congress, as required by the STOCK Act (Stop Trading on Congressional Knowledge Act). This feature is in **Beta** and may require API key configuration.

## What are Congressional Trades?

Under the STOCK Act, members of Congress and their staff must publicly disclose stock transactions within 45 days. These disclosures provide transparency into congressional trading activity and help identify potential conflicts of interest.

## Feature Status

⚠️ **Beta Feature:** Congressional Trades is currently in Beta status.

**Requirements:**
- `FINNHUB_API_KEY` configured in backend (optional, uses fallback if not set)
- Data may have 1-7 day delays
- Fallback data sources available if Finnhub is unavailable

**See:** [Release Notes](../RELEASE_NOTES_ALPHA_v1.0.0.md) for complete status

## Accessing Congressional Trades

### Navigation

1. Log in to TradeSignal
2. Click "Congressional" or "Congressional Trades" in the main navigation
3. You'll see a list of recent congressional trades

### Default View

The Congressional Trades page shows:
- Recent congressional stock transactions
- Representative information
- Trade details (ticker, type, value, date)
- Filing information
- Sortable and filterable columns

## Understanding the Data

### Representative Information

Each trade shows:
- **Representative Name:** Member of Congress who made the trade
- **Chamber:** House of Representatives or Senate
- **State/District:** Representative's state or district
- **Party:** Political party affiliation

### Trade Details

- **Ticker Symbol:** Stock that was traded
- **Company Name:** Full company name
- **Trade Type:** Buy or Sell
- **Transaction Date:** Date trade occurred
- **Filing Date:** Date disclosure was filed
- **Value Range:** Estimated trade value (may be a range)

### Filing Information

- **Filing Period:** When the disclosure was filed
- **Filing Source:** Where the filing originated
- **Link to Original Filing:** Direct link to source document

## Filtering Congressional Trades

### By Representative

1. Search by representative name
2. Filter by chamber (House/Senate)
3. Filter by state or district
4. Filter by political party

### By Ticker Symbol

1. Enter ticker symbol in search/filter
2. View all congressional trades for that company
3. Useful for tracking specific stocks

### By Date Range

1. Select start and end dates
2. View trades within that period
3. Note: Data may have delays (1-7 days)

### By Trade Type

- **Buy Only:** Congressional purchases
- **Sell Only:** Congressional sales
- **Both:** All trades (default)

### By Value

1. Set minimum trade value
2. Filter to significant trades only
3. Note: Values may be estimated ranges

## Viewing Trade Details

### Click on a Trade

Clicking on any trade opens detailed information:

- **Representative Details:**
  - Full name and title
  - Chamber and party
  - State/district information
  - Link to representative profile

- **Trade Information:**
  - Transaction date
  - Filing date
  - Trade type and value
  - Company information

- **Filing Details:**
  - Original filing source
  - Filing period
  - Link to original document

- **Related Trades:**
  - Other trades by same representative
  - Other trades in same company

## Data Freshness & Limitations

### Update Frequency

- **Data Source:** Finnhub API (if configured) or fallback sources
- **Update Schedule:** Varies based on data source
- **Delays:** May have 1-7 day delays from transaction date

### Data Accuracy

- Values may be estimated ranges
- Some transactions may be missing
- Filing dates may differ from transaction dates
- Data depends on source availability

### Known Limitations

- **Beta Status:** Feature is still in development
- **API Dependency:** Requires FINNHUB_API_KEY for best results
- **Data Delays:** Not real-time, may have significant delays
- **Coverage:** May not include all congressional trades

## Best Practices

### Monitoring Specific Representatives

1. **Filter by Name:** Search for specific representatives
2. **Set Up Alerts:** Create alerts for representatives you follow
3. **Track Patterns:** Monitor trading patterns over time
4. **Compare Activity:** Compare different representatives' trades

### Tracking Specific Stocks

1. **Filter by Ticker:** View all congressional trades for a stock
2. **Set Up Alerts:** Get notified of new congressional trades
3. **Analyze Trends:** Look for patterns in congressional trading
4. **Cross-Reference:** Compare with insider trades

### Research Workflow

1. **Start with Recent Trades:** See what's happening now
2. **Filter by Interest:** Narrow to representatives or stocks
3. **Review Details:** Click trades for full information
4. **Set Up Monitoring:** Create alerts for ongoing tracking

## Creating Alerts

### Congressional Trade Alerts

You can create alerts for congressional trades:

1. Go to Alerts page
2. Create new alert
3. Set criteria:
   - Representative name (if available)
   - Ticker symbol
   - Trade type
   - Minimum value
4. Configure notifications
5. Save alert

**Note:** Congressional trade alerts work the same as insider trade alerts. See [Alerts Setup Guide](../ALERTS_SETUP.md) for details.

## Understanding Congressional Trading Patterns

### What to Look For

- **Timing:** Trades around significant events or legislation
- **Sector Focus:** Industries representatives trade in
- **Frequency:** How often representatives trade
- **Size:** Value of transactions
- **Patterns:** Buying vs. selling trends

### Important Context

⚠️ **Not Investment Advice:** Congressional trade data is for informational and transparency purposes only.

⚠️ **Consider:**
- Representatives may trade for various reasons
- Not all trades are significant
- Context matters (legislation, committee assignments, etc.)
- Some trades may be managed by financial advisors

## Related Features

### Insider Trades

- Compare congressional trades with corporate insider trades
- See [Insider Trades Guide](INSIDER_TRADES.md)

### Company Profiles

- View company details for traded stocks
- See all trades (insider + congressional) for a company

### Alerts

- Set up alerts for congressional trades
- Get notified of new transactions
- See [Alerts Setup Guide](../ALERTS_SETUP.md)

## FAQ

**Q: How current is the data?**  
A: Data may have 1-7 day delays. This is a Beta feature with known limitations.

**Q: Do I need an API key?**  
A: The backend needs FINNHUB_API_KEY for best results. The feature may use fallback sources if not configured.

**Q: Are all congressional trades included?**  
A: Coverage depends on data source availability. Some trades may be missing.

**Q: Can I see historical data?**  
A: Yes, use date filters to view historical congressional trades.

**Q: How accurate are the trade values?**  
A: Values may be estimated ranges. Check original filings for exact amounts.

**Q: Why is this feature in Beta?**  
A: Congressional trade data has challenges with data sources, delays, and coverage. We're working to improve reliability.

## Troubleshooting

### No Data Showing

- Check if FINNHUB_API_KEY is configured (backend)
- Verify feature is enabled
- Try different date ranges
- Check [Troubleshooting Guide](../TROUBLESHOOTING.md)

### Data Seems Outdated

- Congressional trades may have 1-7 day delays
- This is expected behavior for Beta feature
- Check last update timestamp

### Missing Trades

- Not all trades may be captured
- Coverage depends on data source
- Some representatives may not file on time

## Need Help?

- **Getting Started:** [Getting Started Guide](../GETTING_STARTED.md)
- **Alerts Setup:** [Alerts Setup Guide](../ALERTS_SETUP.md)
- **Troubleshooting:** [Troubleshooting Guide](../TROUBLESHOOTING.md)
- **FAQ:** [FAQ](../FAQ.md)
- **Support:** support@tradesignal.com

---

**Related Documentation:**
- [Insider Trades Guide](INSIDER_TRADES.md)
- [Alerts Setup Guide](../ALERTS_SETUP.md)
- [Release Notes](../RELEASE_NOTES_ALPHA_v1.0.0.md)

