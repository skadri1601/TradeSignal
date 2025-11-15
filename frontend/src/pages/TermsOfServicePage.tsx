/**
 * Terms of Service Page
 *
 * Legal terms and conditions for using TradeSignal.
 * Based on TRUTH_FREE.md Phase 2.1 specifications.
 */

export const TermsOfServicePage = () => (
  <div className="max-w-4xl mx-auto p-6 py-12">
    <h1 className="text-4xl font-bold mb-8 text-gray-900">Terms of Service</h1>

    <div className="prose prose-lg max-w-none">
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">1. Acceptance of Terms</h2>
        <p className="text-gray-700 leading-relaxed">
          By accessing or using TradeSignal ("the Service"), you agree to be bound by these Terms of Service.
          If you do not agree to these terms, do not use this Service.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">2. Description of Service</h2>
        <p className="text-gray-700 leading-relaxed">
          TradeSignal provides stock market information, including insider trading data from SEC filings,
          stock prices, and AI-generated insights for <strong>educational purposes only</strong>.
          This is NOT professional financial advice, investment advice, or trading recommendations.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">3. Not Financial Advice</h2>
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
          <p className="text-red-800 font-bold text-lg">
            ⚠️ IMPORTANT: WE ARE NOT FINANCIAL ADVISORS
          </p>
        </div>
        <p className="text-gray-700 leading-relaxed">
          Nothing on this site should be construed as investment advice, financial advice, trading advice,
          or any other sort of advice. We do not recommend buying, selling, or holding any securities.
          Always consult a licensed financial professional before making investment decisions.
        </p>
        <p className="text-gray-700 leading-relaxed mt-3">
          <strong>You are solely responsible for your own investment decisions and any resulting profits or losses.</strong>
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">4. Data Accuracy and Timeliness</h2>
        <p className="text-gray-700 leading-relaxed">
          Stock prices and other data may be delayed, inaccurate, or incomplete.
          We do not guarantee the accuracy, completeness, or timeliness of any information displayed on this Service.
        </p>
        <ul className="list-disc ml-6 mt-3 space-y-2 text-gray-700">
          <li>Stock prices may be delayed by up to 15 seconds or more</li>
          <li>SEC filing data is scraped from public sources and may contain errors</li>
          <li>AI-generated insights are experimental and may be incorrect or misleading</li>
          <li>Market data is provided "as is" without warranty of any kind</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">5. Limitation of Liability</h2>
        <div className="bg-yellow-50 border border-yellow-300 rounded p-4 mb-4">
          <p className="text-gray-800 font-semibold">
            TO THE FULLEST EXTENT PERMITTED BY LAW:
          </p>
        </div>
        <p className="text-gray-700 leading-relaxed">
          We shall NOT be liable for any losses, damages, injuries, or financial harm arising from:
        </p>
        <ul className="list-disc ml-6 mt-3 space-y-2 text-gray-700">
          <li>Your use of this Service</li>
          <li>Reliance on any information provided by this Service</li>
          <li>Investment decisions made based on data from this Service</li>
          <li>Errors, inaccuracies, or delays in data</li>
          <li>Service downtime, data loss, or technical issues</li>
          <li>Third-party data sources or APIs</li>
        </ul>
        <p className="text-gray-700 leading-relaxed mt-3 font-semibold">
          YOU USE THIS SERVICE ENTIRELY AT YOUR OWN RISK.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">6. Educational Use Only</h2>
        <p className="text-gray-700 leading-relaxed">
          This Service is provided for <strong>educational and informational purposes only</strong>.
          It is designed to help users learn about:
        </p>
        <ul className="list-disc ml-6 mt-3 space-y-2 text-gray-700">
          <li>How SEC insider trading filings work</li>
          <li>How to analyze public company data</li>
          <li>Basic stock market concepts</li>
          <li>Software engineering and web development</li>
        </ul>
        <p className="text-gray-700 leading-relaxed mt-3">
          This Service is NOT intended for commercial use or professional trading purposes.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">7. User Conduct</h2>
        <p className="text-gray-700 leading-relaxed">
          You agree NOT to:
        </p>
        <ul className="list-disc ml-6 mt-3 space-y-2 text-gray-700">
          <li>Use the Service for illegal purposes</li>
          <li>Scrape, harvest, or abuse the API</li>
          <li>Attempt to hack, exploit, or disrupt the Service</li>
          <li>Violate any applicable laws or regulations</li>
          <li>Share false or misleading information</li>
          <li>Impersonate others or provide false identity information</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">8. Third-Party Data Sources</h2>
        <p className="text-gray-700 leading-relaxed">
          This Service uses data from third-party sources including:
        </p>
        <ul className="list-disc ml-6 mt-3 space-y-2 text-gray-700">
          <li><strong>SEC EDGAR:</strong> Public company filings (public domain)</li>
          <li><strong>Yahoo Finance:</strong> Stock prices (educational use only)</li>
          <li><strong>Google Gemini:</strong> AI-generated insights (experimental)</li>
        </ul>
        <p className="text-gray-700 leading-relaxed mt-3">
          We are not responsible for the accuracy, availability, or reliability of third-party data.
          Each data provider has its own terms of service which you must comply with.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">9. Modifications to Service</h2>
        <p className="text-gray-700 leading-relaxed">
          We reserve the right to modify, suspend, or discontinue the Service at any time without notice.
          We may also modify these Terms of Service at any time. Continued use of the Service after
          changes constitutes acceptance of the new terms.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">10. Privacy</h2>
        <p className="text-gray-700 leading-relaxed">
          Your use of the Service is also governed by our{' '}
          <a href="/privacy" className="text-blue-600 hover:text-blue-800 underline">
            Privacy Policy
          </a>
          .
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">11. Contact Information</h2>
        <p className="text-gray-700 leading-relaxed">
          If you have questions about these Terms of Service, please contact us via GitHub Issues
          at the TradeSignal repository.
        </p>
      </section>

      <div className="border-t border-gray-300 pt-6 mt-8">
        <p className="text-sm text-gray-500">
          <strong>Last Updated:</strong> {new Date().toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })}
        </p>
        <p className="text-sm text-gray-500 mt-2">
          <strong>Version:</strong> 1.0
        </p>
      </div>
    </div>
  </div>
);

export default TermsOfServicePage;
