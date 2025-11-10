import { Building2, TrendingUp, Filter, Zap, Database, Shield, Bell, Mail, Webhook, Brain, Sparkles } from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          About TradeSignal
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Real-time insider trading intelligence platform tracking SEC Form 4 filings
          from corporate executives, directors, and major shareholders.
        </p>
      </div>

      {/* What We Do */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">What We Do</h2>
        <p className="text-gray-700 mb-4">
          TradeSignal automatically scrapes and analyzes SEC Form 4 filings to provide
          you with real-time insights into insider trading activity. Track what company
          insiders are buying and selling to inform your investment decisions.
        </p>
        <p className="text-gray-700">
          All data is sourced directly from the SEC EDGAR database, ensuring 100% accuracy
          and compliance with securities regulations.
        </p>
      </div>

      {/* Key Features */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Key Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Feature 1 */}
          <div className="card">
            <div className="flex items-center mb-3">
              <div className="p-2 bg-blue-100 rounded-lg mr-3">
                <Database className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Live SEC Data</h3>
            </div>
            <p className="text-gray-600">
              3,761+ real insider trades from SEC Form 4 filings across 164 companies.
              No dummy data - all transactions are authentic and verified from the SEC.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="card">
            <div className="flex items-center mb-3">
              <div className="p-2 bg-green-100 rounded-lg mr-3">
                <Filter className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Advanced Filtering</h3>
            </div>
            <p className="text-gray-600">
              Filter trades by ticker, transaction type (buy/sell), value range, and date range.
              Combine multiple filters to find exactly what you're looking for.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="card">
            <div className="flex items-center mb-3">
              <div className="p-2 bg-purple-100 rounded-lg mr-3">
                <Zap className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Real-Time Updates</h3>
            </div>
            <p className="text-gray-600">
              WebSocket-powered live updates. See new insider trades and alert notifications
              instantly without refreshing the page.
            </p>
          </div>

          {/* Feature 4 */}
          <div className="card">
            <div className="flex items-center mb-3">
              <div className="p-2 bg-red-100 rounded-lg mr-3">
                <TrendingUp className="h-6 w-6 text-red-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Trade Analytics</h3>
            </div>
            <p className="text-gray-600">
              Summary statistics, trend visualizations, and insights on the most active
              insiders and companies.
            </p>
          </div>

          {/* Feature 5 */}
          <div className="card">
            <div className="flex items-center mb-3">
              <div className="p-2 bg-yellow-100 rounded-lg mr-3">
                <Building2 className="h-6 w-6 text-yellow-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Company Profiles</h3>
            </div>
            <p className="text-gray-600">
              Detailed company information with all insider trading history. Track
              activity across 164 major companies including NASDAQ-100, Dow Jones 30, and top tech stocks.
            </p>
          </div>

          {/* Feature 6 */}
          <div className="card">
            <div className="flex items-center mb-3">
              <div className="p-2 bg-indigo-100 rounded-lg mr-3">
                <Shield className="h-6 w-6 text-indigo-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">SEC Verified</h3>
            </div>
            <p className="text-gray-600">
              Every trade links directly to the official SEC Form 4 filing. Verify
              any transaction with a single click.
            </p>
          </div>

          {/* Feature 7 - AI Insights */}
          <div className="card border-2 border-blue-300 bg-gradient-to-br from-blue-50 to-purple-50">
            <div className="flex items-center mb-3">
              <div className="p-2 bg-blue-100 rounded-lg mr-3">
                <Brain className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">AI-Powered Insights</h3>
              <Sparkles className="h-4 w-4 text-yellow-500 ml-2" />
            </div>
            <p className="text-gray-600">
              Google Gemini 2.0 Flash AI analyzes insider trading patterns, generates
              daily news summaries, provides trading signals, and answers questions about
              insider activity with real-time database access.
            </p>
          </div>

          {/* Feature 8 - Auto Scraping */}
          <div className="card">
            <div className="flex items-center mb-3">
              <div className="p-2 bg-green-100 rounded-lg mr-3">
                <Zap className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Automated Scraping</h3>
            </div>
            <p className="text-gray-600">
              Hourly automated scraping of all 164 companies. New SEC Form 4 filings
              are detected and processed automatically, keeping data fresh and up-to-date.
            </p>
          </div>

          {/* Feature 9 - Smart Alerts */}
          <div className="card">
            <div className="flex items-center mb-3">
              <div className="p-2 bg-purple-100 rounded-lg mr-3">
                <Bell className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Smart Alerts</h3>
            </div>
            <p className="text-gray-600">
              Create custom alerts with advanced filtering. Get notified via webhooks,
              email, browser push, or in-app when trades match your criteria.
            </p>
          </div>
        </div>
      </div>

      {/* AI Features Section */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">AI-Powered Analysis</h2>
        <p className="text-gray-600 mb-6">
          TradeSignal uses Google Gemini 2.0 Flash to provide intelligent insights into insider trading
          patterns. Our AI has real-time access to the complete database of insider trades.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Daily Summary */}
          <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
            <div className="flex items-center mb-3">
              <div className="p-2 bg-blue-100 rounded-lg mr-3">
                <Sparkles className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Daily News Feed</h3>
            </div>
            <p className="text-gray-600 text-sm mb-3">
              AI-generated news-style summaries of the top 10 companies with the most significant
              insider trading activity. Updates every 5 minutes with fresh insights.
            </p>
            <div className="text-xs text-blue-700 bg-blue-100 rounded px-2 py-1 inline-block">
              Last 7 days • Auto-refresh
            </div>
          </div>

          {/* Trading Signals */}
          <div className="card bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
            <div className="flex items-center mb-3">
              <div className="p-2 bg-green-100 rounded-lg mr-3">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Trading Signals</h3>
            </div>
            <p className="text-gray-600 text-sm mb-3">
              AI analyzes 30 days of insider activity to generate BULLISH/BEARISH/NEUTRAL signals
              with strength indicators and detailed reasoning for each company.
            </p>
            <div className="text-xs text-green-700 bg-green-100 rounded px-2 py-1 inline-block">
              Last 30 days • AI reasoning included
            </div>
          </div>

          {/* Company Analysis */}
          <div className="card bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200">
            <div className="flex items-center mb-3">
              <div className="p-2 bg-purple-100 rounded-lg mr-3">
                <Building2 className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Company Deep-Dive</h3>
            </div>
            <p className="text-gray-600 text-sm mb-3">
              Get AI-powered analysis for any company with sentiment classification, key insights,
              and pattern detection based on configurable time periods (7-90 days).
            </p>
            <div className="text-xs text-purple-700 bg-purple-100 rounded px-2 py-1 inline-block">
              Customizable timeframe • Sentiment analysis
            </div>
          </div>

          {/* AI Chat */}
          <div className="card bg-gradient-to-br from-orange-50 to-yellow-50 border-orange-200">
            <div className="flex items-center mb-3">
              <div className="p-2 bg-orange-100 rounded-lg mr-3">
                <Brain className="h-6 w-6 text-orange-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">AI Chat Assistant</h3>
            </div>
            <p className="text-gray-600 text-sm mb-3">
              Ask questions about insider trading data and get precise, data-driven answers.
              The AI queries the database in real-time to provide accurate insights with insider names and positions.
            </p>
            <div className="text-xs text-orange-700 bg-orange-100 rounded px-2 py-1 inline-block">
              Real-time DB queries • Precise answers
            </div>
          </div>
        </div>
      </div>

      {/* Multi-Channel Alerts */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Multi-Channel Alert System</h2>
        <p className="text-gray-600 mb-6">
          Create custom alerts for insider trading activity and receive notifications through
          your preferred channels. Get notified instantly when trades match your criteria.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* In-App Notifications */}
          <div className="card">
            <div className="flex items-center mb-3">
              <div className="p-2 bg-emerald-100 rounded-lg mr-3">
                <Bell className="h-6 w-6 text-emerald-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">In-App Toasts</h3>
            </div>
            <p className="text-gray-600 text-sm">
              Real-time toast notifications inside the app via WebSocket. No setup required -
              works automatically when you're using TradeSignal.
            </p>
          </div>

          {/* Browser Push */}
          <div className="card">
            <div className="flex items-center mb-3">
              <div className="p-2 bg-blue-100 rounded-lg mr-3">
                <Bell className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Browser Push</h3>
            </div>
            <p className="text-gray-600 text-sm">
              System-level browser notifications that work even when the app is closed.
              One-click opt-in for desktop and mobile alerts.
            </p>
          </div>

          {/* Email Alerts */}
          <div className="card">
            <div className="flex items-center mb-3">
              <div className="p-2 bg-orange-100 rounded-lg mr-3">
                <Mail className="h-6 w-6 text-orange-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Email Alerts</h3>
            </div>
            <p className="text-gray-600 text-sm">
              Professional email notifications via SendGrid with detailed trade information
              and direct links to view more details.
            </p>
          </div>

          {/* Webhooks */}
          <div className="card">
            <div className="flex items-center mb-3">
              <div className="p-2 bg-purple-100 rounded-lg mr-3">
                <Webhook className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Webhooks</h3>
            </div>
            <p className="text-gray-600 text-sm">
              Send alerts to Discord, Slack, or any custom webhook endpoint. Perfect for
              teams and automated workflows.
            </p>
          </div>
        </div>

        {/* Alert Types */}
        <div className="mt-6 card bg-gradient-to-r from-emerald-50 to-blue-50 border-emerald-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Customizable Alert Criteria</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="flex items-start">
              <span className="text-emerald-600 mr-2">✓</span>
              <span className="text-gray-700"><strong>Large Trades:</strong> Alert when trades exceed a specific dollar value</span>
            </div>
            <div className="flex items-start">
              <span className="text-emerald-600 mr-2">✓</span>
              <span className="text-gray-700"><strong>Company Watch:</strong> Monitor all trading activity for specific tickers</span>
            </div>
            <div className="flex items-start">
              <span className="text-emerald-600 mr-2">✓</span>
              <span className="text-gray-700"><strong>Insider Roles:</strong> Track trades by CEOs, CFOs, Directors, and more</span>
            </div>
            <div className="flex items-start">
              <span className="text-emerald-600 mr-2">✓</span>
              <span className="text-gray-700"><strong>Buy/Sell Filter:</strong> Only get notified for purchases or sales</span>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">How It Works</h2>
        <div className="space-y-6">
          <div className="flex items-start">
            <div className="flex-shrink-0 h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold mr-4">
              1
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">SEC Data Collection</h3>
              <p className="text-gray-600">
                Our scraper automatically fetches Form 4 filings from the SEC EDGAR database
                using their official API. We respect rate limits and follow all SEC guidelines.
              </p>
            </div>
          </div>

          <div className="flex items-start">
            <div className="flex-shrink-0 h-10 w-10 bg-green-100 rounded-full flex items-center justify-center text-green-600 font-bold mr-4">
              2
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">XML Parsing & Validation</h3>
              <p className="text-gray-600">
                Form 4 XML documents are parsed to extract transaction details: shares traded,
                price per share, total value, and insider information. All data is validated
                before being saved.
              </p>
            </div>
          </div>

          <div className="flex items-start">
            <div className="flex-shrink-0 h-10 w-10 bg-purple-100 rounded-full flex items-center justify-center text-purple-600 font-bold mr-4">
              3
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">Real-Time Display</h3>
              <p className="text-gray-600">
                Trades are displayed instantly via WebSocket connections. Filter, search,
                and analyze the data using our intuitive dashboard interface.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="card bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Platform Statistics
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div>
            <p className="text-3xl font-bold text-blue-600">3,761</p>
            <p className="text-sm text-gray-600 mt-1">Total Trades</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-green-600">164</p>
            <p className="text-sm text-gray-600 mt-1">Companies</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-purple-600">600+</p>
            <p className="text-sm text-gray-600 mt-1">Insiders</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-red-600">Live Data</p>
            <p className="text-sm text-gray-600 mt-1">Auto-Updated</p>
          </div>
        </div>
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-600">
            Database updated hourly via automated SEC scraping • Last 7 days of activity
          </p>
        </div>
      </div>

      {/* Transaction Types */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Understanding Transaction Types</h2>
        <p className="text-gray-700 mb-4">
          SEC Form 4 filings contain various transaction codes that indicate different types
          of insider trading activity. Here's what they mean:
        </p>
        <div className="space-y-3">
          <div className="flex items-start">
            <span className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-green-100 text-green-600 font-semibold mr-3 flex-shrink-0">
              P
            </span>
            <div>
              <h4 className="font-semibold text-gray-900">Purchase (BUY)</h4>
              <p className="text-sm text-gray-600">
                Open market purchase of stock. Insider bought shares at market price.
                This typically signals confidence in the company's future.
              </p>
            </div>
          </div>

          <div className="flex items-start">
            <span className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-red-100 text-red-600 font-semibold mr-3 flex-shrink-0">
              S
            </span>
            <div>
              <h4 className="font-semibold text-gray-900">Sale (SELL)</h4>
              <p className="text-sm text-gray-600">
                Open market sale of stock. Insider sold shares at market price.
                Could indicate profit-taking, diversification, or liquidity needs.
              </p>
            </div>
          </div>

          <div className="flex items-start">
            <span className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-purple-100 text-purple-600 font-semibold mr-3 flex-shrink-0">
              G
            </span>
            <div>
              <h4 className="font-semibold text-gray-900">Gift</h4>
              <p className="text-sm text-gray-600">
                Transfer of shares as a gift (e.g., to family trust or charity).
                No money changes hands, so price and value will show as N/A.
              </p>
            </div>
          </div>

          <div className="flex items-start">
            <span className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-blue-100 text-blue-600 font-semibold mr-3 flex-shrink-0">
              A
            </span>
            <div>
              <h4 className="font-semibold text-gray-900">Award (Grant)</h4>
              <p className="text-sm text-gray-600">
                Stock or options granted as compensation (e.g., RSUs, performance shares).
                Often has no immediate cash cost to the insider.
              </p>
            </div>
          </div>

          <div className="flex items-start">
            <span className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-yellow-100 text-yellow-600 font-semibold mr-3 flex-shrink-0">
              M
            </span>
            <div>
              <h4 className="font-semibold text-gray-900">Exercise of Options</h4>
              <p className="text-sm text-gray-600">
                Insider exercised stock options to convert them to actual shares.
                May or may not involve immediate sale of the underlying stock.
              </p>
            </div>
          </div>

          <div className="flex items-start">
            <span className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-orange-100 text-orange-600 font-semibold mr-3 flex-shrink-0">
              F
            </span>
            <div>
              <h4 className="font-semibold text-gray-900">Tax Withholding</h4>
              <p className="text-sm text-gray-600">
                Shares withheld or sold to pay taxes on vested equity compensation.
                Often appears alongside awards or option exercises.
              </p>
            </div>
          </div>
        </div>
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-gray-700">
            <strong>Note:</strong> Some transactions (gifts, awards, certain option exercises)
            may show "N/A" for price or value because no money was exchanged. This is normal
            and reflects the actual SEC filing data.
          </p>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="card bg-yellow-50 border-yellow-200">
        <h2 className="text-xl font-bold text-gray-900 mb-3">Disclaimer</h2>
        <p className="text-sm text-gray-700">
          This platform is for informational and educational purposes only. It is not
          financial advice. Insider trading data is publicly available information from
          SEC filings, but past transactions do not guarantee future performance. Always
          do your own research and consult with a financial advisor before making
          investment decisions.
        </p>
      </div>
    </div>
  );
}
