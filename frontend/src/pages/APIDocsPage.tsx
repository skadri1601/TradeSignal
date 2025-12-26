import { Code, Terminal, Key, Zap, Lock, BookOpen, ExternalLink, Copy, Check } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useState } from 'react';

const APIDocsPage = () => {
  const [copiedEndpoint, setCopiedEndpoint] = useState<string | null>(null);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedEndpoint(id);
    setTimeout(() => setCopiedEndpoint(null), 2000);
  };

  const endpoints = [
    {
      category: "Insider Trades",
      description: "Access SEC Form 4 filings and insider trading data",
      items: [
        { method: "GET", path: "/api/v1/trades", description: "List all insider trades with pagination", tier: "Plus" },
        { method: "GET", path: "/api/v1/trades/{id}", description: "Get specific trade details", tier: "Plus" },
        { method: "GET", path: "/api/v1/trades/recent", description: "Get recent trades (last 7 days)", tier: "Free" }
      ]
    },
    {
      category: "Congressional Trades",
      description: "Track STOCK Act filings from Congress members",
      items: [
        { method: "GET", path: "/api/v1/congressional-trades", description: "List congressional trades", tier: "Plus" },
        { method: "GET", path: "/api/v1/congressional-trades/{id}", description: "Get specific congressional trade", tier: "Plus" },
        { method: "GET", path: "/api/v1/congressional-trades/congresspeople", description: "List all Congress members", tier: "Free" }
      ]
    },
    {
      category: "Companies & Insiders",
      description: "Lookup company and insider information",
      items: [
        { method: "GET", path: "/api/v1/companies", description: "Search companies", tier: "Free" },
        { method: "GET", path: "/api/v1/companies/{ticker}", description: "Get company details", tier: "Free" },
        { method: "GET", path: "/api/v1/companies/{ticker}/trades", description: "Get trades for a company", tier: "Plus" },
        { method: "GET", path: "/api/v1/insiders/{id}", description: "Get insider profile", tier: "Plus" }
      ]
    },
    {
      category: "Research & AI",
      description: "Access AI-powered insights and research data (PRO tier)",
      items: [
        { method: "GET", path: "/api/v1/research/ivt/{ticker}", description: "Get Intrinsic Value Target", tier: "PRO" },
        { method: "GET", path: "/api/v1/research/ts-score/{ticker}", description: "Get TradeSignal Score", tier: "PRO" },
        { method: "GET", path: "/api/v1/ai/analysis/{ticker}", description: "Get LUNA AI analysis", tier: "PRO" },
        { method: "GET", path: "/api/v1/ai/summary/{ticker}", description: "Get AI-generated summary", tier: "PRO" }
      ]
    }
  ];

  const rateLimit = [
    { tier: "Free", limit: "100 requests/hour", burst: "10/minute" },
    { tier: "Plus", limit: "500 requests/hour", burst: "50/minute" },
    { tier: "PRO", limit: "2,000 requests/hour", burst: "100/minute" },
    { tier: "Enterprise", limit: "Unlimited", burst: "Custom" }
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Hero Section */}
      <section className="pt-32 pb-16 px-4 bg-gradient-to-b from-[#0f0f1a] to-[#0a0a0a]">
        <div className="max-w-7xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded-full px-4 py-2 mb-6">
            <Code className="w-4 h-4 text-green-400" />
            <span className="text-sm text-green-300">API Documentation</span>
          </div>
          <h1 className="text-5xl font-bold mb-6">
            TradeSignal
            <span className="block bg-gradient-to-r from-green-400 via-blue-400 to-green-400 bg-clip-text text-transparent mt-2">
              API Reference
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mb-8">
            Integrate insider trading intelligence and congressional trade data into your applications with our RESTful API
          </p>

          <div className="flex flex-wrap gap-4">
            <a
              href={`${import.meta.env.VITE_API_URL}/docs`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-white text-black px-6 py-3 rounded-full font-bold hover:bg-gray-200 transition-all"
            >
              <Terminal className="w-5 h-5" />
              Interactive API Docs
              <ExternalLink className="w-4 h-4" />
            </a>
            <Link
              to="/pricing"
              className="inline-flex items-center gap-2 bg-white/5 border border-white/10 text-white px-6 py-3 rounded-full font-bold hover:bg-white/10 transition-all"
            >
              <Key className="w-5 h-5" />
              Get API Key
            </Link>
          </div>
        </div>
      </section>

      {/* Quick Start */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold mb-8">Quick Start</h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-6">
              <div className="bg-purple-500/10 p-3 rounded-xl w-fit mb-4">
                <Key className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-xl font-bold mb-2">1. Get API Key</h3>
              <p className="text-gray-400 text-sm">
                Sign up for a PRO or Enterprise account to access API keys from your dashboard settings.
              </p>
            </div>
            <div className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-6">
              <div className="bg-blue-500/10 p-3 rounded-xl w-fit mb-4">
                <Terminal className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="text-xl font-bold mb-2">2. Make Request</h3>
              <p className="text-gray-400 text-sm">
                Include your API key in the Authorization header of every request to authenticate.
              </p>
            </div>
            <div className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-6">
              <div className="bg-green-500/10 p-3 rounded-xl w-fit mb-4">
                <Zap className="w-6 h-6 text-green-400" />
              </div>
              <h3 className="text-xl font-bold mb-2">3. Get Data</h3>
              <p className="text-gray-400 text-sm">
                Receive real-time insider trades, congressional data, and AI insights in JSON format.
              </p>
            </div>
          </div>

          {/* Example Request */}
          <div className="mt-12">
            <h3 className="text-2xl font-bold mb-6">Example Request</h3>
            <div className="bg-[#0f0f1a] border border-white/10 rounded-2xl overflow-hidden">
              <div className="bg-black/40 px-6 py-4 border-b border-white/5 flex items-center justify-between">
                <span className="text-sm font-mono text-gray-400">cURL</span>
                <button
                  onClick={() => copyToClipboard(`curl -X GET "${import.meta.env.VITE_API_URL}/api/v1/trades?limit=10" -H "Authorization: Bearer YOUR_API_KEY"`, 'curl')}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  {copiedEndpoint === 'curl' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
              <div className="p-6 font-mono text-sm overflow-x-auto">
                <pre className="text-green-400">
{`curl -X GET "${import.meta.env.VITE_API_URL}/api/v1/trades?limit=10" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json"`}
                </pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Endpoints */}
      <section className="py-16 px-4 bg-[#0f0f1a]">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold mb-8">API Endpoints</h2>
          <div className="space-y-12">
            {endpoints.map((category, index) => (
              <div key={index}>
                <h3 className="text-2xl font-bold mb-2">{category.category}</h3>
                <p className="text-gray-400 mb-6">{category.description}</p>
                <div className="space-y-3">
                  {category.items.map((endpoint, endpointIndex) => (
                    <div
                      key={endpointIndex}
                      className="bg-[#0a0a0a] border border-white/10 rounded-xl p-4 hover:border-purple-500/30 transition-all"
                    >
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                              endpoint.method === 'GET' ? 'bg-green-500/20 text-green-400' :
                              endpoint.method === 'POST' ? 'bg-blue-500/20 text-blue-400' :
                              endpoint.method === 'PUT' ? 'bg-yellow-500/20 text-yellow-400' :
                              'bg-red-500/20 text-red-400'
                            }`}>
                              {endpoint.method}
                            </span>
                            <code className="text-purple-400 font-mono text-sm">{endpoint.path}</code>
                          </div>
                          <p className="text-gray-400 text-sm">{endpoint.description}</p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap ${
                          endpoint.tier === 'Free' ? 'bg-gray-500/20 text-gray-400' :
                          endpoint.tier === 'Plus' ? 'bg-blue-500/20 text-blue-400' :
                          endpoint.tier === 'PRO' ? 'bg-purple-500/20 text-purple-400' :
                          'bg-orange-500/20 text-orange-400'
                        }`}>
                          {endpoint.tier}+
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Rate Limits */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold mb-8">Rate Limits</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {rateLimit.map((tier, index) => (
              <div key={index} className="bg-[#0f0f1a] border border-white/10 rounded-2xl p-6">
                <h3 className="text-lg font-bold mb-4">{tier.tier}</h3>
                <div className="space-y-3">
                  <div>
                    <span className="text-gray-500 text-sm">Hourly Limit</span>
                    <p className="text-white font-mono text-lg">{tier.limit}</p>
                  </div>
                  <div>
                    <span className="text-gray-500 text-sm">Burst Rate</span>
                    <p className="text-white font-mono text-lg">{tier.burst}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Authentication */}
      <section className="py-16 px-4 bg-[#0f0f1a]">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-3 mb-6">
            <Lock className="w-8 h-8 text-purple-400" />
            <h2 className="text-3xl font-bold">Authentication</h2>
          </div>
          <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-8">
            <p className="text-gray-400 mb-6">
              All API requests require authentication using a Bearer token. Include your API key in the Authorization header:
            </p>
            <div className="bg-black/40 rounded-xl p-4 font-mono text-sm">
              <code className="text-green-400">Authorization: Bearer YOUR_API_KEY</code>
            </div>
            <p className="text-gray-500 text-sm mt-4">
              Get your API key from Settings {'>'} API Access after upgrading to PRO or Enterprise tier.
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-[#0f0f1a] border border-purple-500/20 rounded-3xl p-12">
            <Code className="w-12 h-12 text-purple-400 mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-4">Ready to Build?</h2>
            <p className="text-gray-400 mb-8">
              Upgrade to PRO or Enterprise to access our full API with real-time insider trading data
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/pricing"
                className="inline-flex items-center justify-center gap-2 bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-200 transition-all"
              >
                View Pricing
              </Link>
              <a
                href={`${import.meta.env.VITE_API_URL}/docs`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 bg-white/5 border border-white/10 text-white px-8 py-4 rounded-full font-bold hover:bg-white/10 transition-all"
              >
                <BookOpen className="w-5 h-5" />
                Explore Full API Docs
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default APIDocsPage;
