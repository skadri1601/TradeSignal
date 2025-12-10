# Insider Trades Feature Guide

Learn how to use TradeSignal's Insider Trades feature to track SEC Form 4 filings and insider trading activity.

## Overview

The Insider Trades feature provides real-time access to SEC Form 4 filings, which disclose insider trading activity. This is the core feature of TradeSignal and is production-ready.

## What are SEC Form 4 Filings?

SEC Form 4 is a document that must be filed with the Securities and Exchange Commission (SEC) whenever corporate insiders (officers, directors, or 10% owners) buy or sell company stock. These filings are public records and provide transparency into insider trading activity.

## Accessing Insider Trades

### Navigation

1. Log in to TradeSignal
2. Click "Trades" in the main navigation menu
3. You'll see a list of recent insider trades

### Default View

The Trades page shows:
- Recent SEC Form 4 filings
- Trade details (company, insider, type, shares, value)
- Sortable and filterable columns
- Pagination for browsing historical data

## Filtering Trades

### By Ticker Symbol

1. Enter ticker symbol in the search/filter box
2. Results filter to show only trades for that company
3. You can enter multiple tickers (comma-separated)

### By Date Range

1. Click date filter
2. Select start and end dates
3. View trades within that range

### By Trade Type

- **Buy Only:** Show only insider purchases
- **Sell Only:** Show only insider sales
- **Both:** Show all trades (default)

### By Value

1. Set minimum trade value
2. Filter to show only trades above threshold
3. Useful for finding significant trades

### By Insider Role

Filter by:
- CEO (Chief Executive Officer)
- CFO (Chief Financial Officer)
- Director
- Officer
- 10% Owner
- Other roles

## Viewing Trade Details

### Click on a Trade

Clicking on any trade opens a detailed view showing:

- **Company Information:**
  - Company name and ticker
  - Industry and sector
  - Company profile link

- **Insider Information:**
  - Insider name and role
  - Insider profile link
  - Historical trades by this insider

- **Trade Details:**
  - Transaction date
  - Trade type (Buy/Sell)
  - Number of shares
  - Trade value
  - Price per share
  - Form 4 filing date

- **Additional Information:**
  - Transaction code
  - Ownership type
  - Link to SEC EDGAR filing

## Understanding Trade Data

### Trade Types

- **Buy (P):** Purchase of shares
- **Sell (S):** Sale of shares
- **Option Exercise:** Exercise of stock options
- **Gift:** Gift of shares
- **Other:** Other transaction types

### Transaction Codes

SEC Form 4 uses transaction codes:
- **P:** Open market purchase
- **S:** Open market sale
- **A:** Award/grant
- **F:** Tax withholding
- And more (see SEC documentation)

### Value Calculations

- **Trade Value:** Total dollar value of transaction
- **Shares:** Number of shares traded
- **Price:** Price per share (calculated from value/shares)

## Sorting and Organization

### Sort Options

Sort by:
- **Date:** Most recent first (default)
- **Value:** Highest value first
- **Company:** Alphabetical by ticker
- **Insider:** Alphabetical by insider name

### Pagination

- Navigate through pages of results
- Adjust items per page (if available)
- Use page numbers or next/previous buttons

## Creating Alerts from Trades

### Quick Alert Creation

1. Find a trade you want to monitor
2. Click "Create Alert" (if available)
3. Alert pre-populates with trade criteria
4. Configure notification channels
5. Save alert

### Manual Alert Creation

1. Go to Alerts page
2. Create new alert
3. Use trade information to set criteria:
   - Ticker symbol
   - Trade type
   - Minimum value
   - Insider role

## Data Freshness

### Update Frequency

- **SEC Form 4 Filings:** Updated every 6 hours
- **Automated Scraper:** Runs at scheduled intervals
- **Real-time:** New filings appear within 6 hours of SEC publication

### Understanding Timestamps

- **Transaction Date:** Date trade occurred
- **Filing Date:** Date Form 4 was filed with SEC
- **Last Updated:** When TradeSignal last updated this record

**Note:** There may be a delay between transaction date and filing date (insiders have 2 business days to file).

## Best Practices

### Finding Significant Trades

1. **Filter by Value:** Set high minimum value (e.g., $1M+)
2. **Filter by Role:** Focus on CEO/CFO trades
3. **Sort by Value:** See largest trades first
4. **Check Recent Activity:** Look for patterns in recent trades

### Monitoring Specific Companies

1. **Set Up Alerts:** Create alerts for companies you follow
2. **Check Regularly:** Review trades page daily
3. **Track Patterns:** Look for buying/selling patterns
4. **Compare Insiders:** See who's buying vs. selling

### Research Workflow

1. **Start Broad:** View all recent trades
2. **Narrow Down:** Apply filters for your interests
3. **Deep Dive:** Click trades for detailed information
4. **Set Alerts:** Create alerts for ongoing monitoring

## Understanding Insider Trading Patterns

### What to Look For

- **Cluster Buying:** Multiple insiders buying (bullish signal)
- **Cluster Selling:** Multiple insiders selling (bearish signal)
- **CEO/CFO Activity:** Leadership trades are often significant
- **Large Transactions:** High-value trades may indicate confidence
- **Pattern Changes:** Shifts in trading patterns

### Important Notes

⚠️ **Not Investment Advice:** Insider trading data is for informational purposes only. It does not constitute investment advice.

⚠️ **Context Matters:** Consider:
- Company fundamentals
- Market conditions
- Insider's historical trading patterns
- Transaction reasons (options exercise, tax planning, etc.)

## Exporting Data

### Copy Information

- Copy trade details to clipboard
- Share specific trades
- Use for research and analysis

### API Access

- Use TradeSignal API to programmatically access trade data
- See API documentation at `/docs` endpoint
- Requires authentication

## Related Features

### Company Profiles

- Click company name to view full profile
- See all trades for that company
- View company details and financials

### Insider Profiles

- Click insider name to view profile
- See all trades by that insider
- Track insider's trading history

### Alerts

- Set up alerts based on trade criteria
- Get notified when matching trades occur
- See [Alerts Setup Guide](../ALERTS_SETUP.md)

## FAQ

**Q: How quickly are new trades added?**  
A: Trades are updated every 6 hours via automated scraper.

**Q: Can I see historical trades?**  
A: Yes, use date filters to view historical data. TradeSignal maintains a database of historical filings.

**Q: Are all SEC Form 4 filings included?**  
A: TradeSignal focuses on significant trades. Some smaller transactions may be filtered.

**Q: How do I know if a trade is significant?**  
A: Consider trade value, insider role, and context. Large CEO purchases are typically more significant than small director sales.

**Q: Can I export trade data?**  
A: Currently, you can copy trade details. Bulk export may be available in future updates.

## Need Help?

- **Alerts Setup:** [Alerts Setup Guide](../ALERTS_SETUP.md)
- **Getting Started:** [Getting Started Guide](../GETTING_STARTED.md)
- **FAQ:** [FAQ](../FAQ.md)
- **Support:** support@tradesignal.com

---

**Related Documentation:**
- [Getting Started Guide](../GETTING_STARTED.md)
- [Alerts Setup Guide](../ALERTS_SETUP.md)
- [Congressional Trades Guide](CONGRESSIONAL_TRADES.md)

