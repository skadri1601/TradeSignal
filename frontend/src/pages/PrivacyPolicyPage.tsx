/**
 * Privacy Policy Page
 *
 * Privacy policy and data handling practices for TradeSignal.
 * Compliant with GDPR and CCPA requirements.
 * Based on TRUTH_FREE.md Phase 2.4 specifications.
 */

export const PrivacyPolicyPage = () => (
  <div className="max-w-4xl mx-auto p-6 py-12">
    <h1 className="text-4xl font-bold mb-8 text-gray-900">Privacy Policy</h1>

    <div className="prose prose-lg max-w-none">
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">1. Information We Collect</h2>
        <p className="text-gray-700 leading-relaxed">
          TradeSignal collects minimal information necessary to provide the Service:
        </p>

        <h3 className="text-xl font-semibold mt-4 mb-2 text-gray-800">Information You Provide:</h3>
        <ul className="list-disc ml-6 space-y-2 text-gray-700">
          <li><strong>Account Information:</strong> Email address (if you create an account)</li>
          <li><strong>Watchlists:</strong> Stock tickers you add to your personal watchlists</li>
          <li><strong>Alerts:</strong> Alert configurations you create</li>
          <li><strong>Preferences:</strong> User settings and preferences</li>
        </ul>

        <h3 className="text-xl font-semibold mt-4 mb-2 text-gray-800">Automatically Collected Information:</h3>
        <ul className="list-disc ml-6 space-y-2 text-gray-700">
          <li><strong>Usage Data:</strong> Pages visited, features used, time spent</li>
          <li><strong>Device Information:</strong> Browser type, operating system, IP address</li>
          <li><strong>Cookies:</strong> Session cookies, preference cookies (see Cookie Policy below)</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">2. How We Use Your Information</h2>
        <p className="text-gray-700 leading-relaxed">
          We use collected information to:
        </p>
        <ul className="list-disc ml-6 mt-3 space-y-2 text-gray-700">
          <li>Provide and maintain the Service</li>
          <li>Send alert notifications (if enabled)</li>
          <li>Improve and optimize the Service</li>
          <li>Respond to support requests</li>
          <li>Detect and prevent abuse or security issues</li>
        </ul>
        <div className="bg-green-50 border-l-4 border-green-500 p-4 mt-4">
          <p className="text-green-800 font-semibold">
            We DO NOT sell your personal information to third parties.
          </p>
        </div>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">3. Data Storage and Security</h2>
        <p className="text-gray-700 leading-relaxed">
          Your data is stored securely using industry-standard practices:
        </p>
        <ul className="list-disc ml-6 mt-3 space-y-2 text-gray-700">
          <li><strong>Encryption:</strong> Data is encrypted in transit (HTTPS) and at rest</li>
          <li><strong>Access Control:</strong> Strict access controls and authentication</li>
          <li><strong>Database:</strong> Hosted on secure cloud infrastructure (Supabase/PostgreSQL)</li>
          <li><strong>Passwords:</strong> Hashed using bcrypt (if authentication is implemented)</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">4. Third-Party Services</h2>
        <p className="text-gray-700 leading-relaxed">
          We use the following third-party services which may collect data:
        </p>
        <ul className="list-disc ml-6 mt-3 space-y-2 text-gray-700">
          <li>
            <strong>Yahoo Finance:</strong> Stock price data (subject to Yahoo's privacy policy)
          </li>
          <li>
            <strong>Google Gemini:</strong> AI-powered insights (subject to Google's privacy policy)
          </li>
          <li>
            <strong>Supabase:</strong> Database hosting (subject to Supabase's privacy policy)
          </li>
        </ul>
        <p className="text-gray-700 leading-relaxed mt-3">
          We are not responsible for the privacy practices of third-party services.
          Please review their respective privacy policies.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">5. Cookies and Tracking</h2>
        <p className="text-gray-700 leading-relaxed">
          We use cookies and similar tracking technologies for:
        </p>
        <ul className="list-disc ml-6 mt-3 space-y-2 text-gray-700">
          <li><strong>Essential Cookies:</strong> Required for the Service to function (session management)</li>
          <li><strong>Preference Cookies:</strong> Remember your settings and preferences</li>
          <li><strong>Analytics Cookies:</strong> Help us understand how users interact with the Service (opt-in only)</li>
        </ul>
        <p className="text-gray-700 leading-relaxed mt-3">
          You can control cookies through your browser settings. Disabling essential cookies
          may prevent some features from working properly.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">6. Your Rights (GDPR & CCPA)</h2>
        <p className="text-gray-700 leading-relaxed">
          You have the following rights regarding your personal data:
        </p>

        <h3 className="text-xl font-semibold mt-4 mb-2 text-gray-800">GDPR Rights (EU Users):</h3>
        <ul className="list-disc ml-6 space-y-2 text-gray-700">
          <li><strong>Right to Access:</strong> Request a copy of your data</li>
          <li><strong>Right to Rectification:</strong> Request corrections to inaccurate data</li>
          <li><strong>Right to Erasure:</strong> Request deletion of your data ("right to be forgotten")</li>
          <li><strong>Right to Data Portability:</strong> Download your data in a machine-readable format</li>
          <li><strong>Right to Object:</strong> Object to processing of your data</li>
          <li><strong>Right to Restrict Processing:</strong> Request limited processing of your data</li>
        </ul>

        <h3 className="text-xl font-semibold mt-4 mb-2 text-gray-800">CCPA Rights (California Users):</h3>
        <ul className="list-disc ml-6 space-y-2 text-gray-700">
          <li><strong>Right to Know:</strong> What personal information we collect and how it's used</li>
          <li><strong>Right to Delete:</strong> Request deletion of your personal information</li>
          <li><strong>Right to Opt-Out:</strong> Opt-out of sale of personal information (we don't sell data)</li>
          <li><strong>Right to Non-Discrimination:</strong> Equal service regardless of privacy choices</li>
        </ul>

        <div className="bg-blue-50 border border-blue-300 rounded p-4 mt-4">
          <p className="text-blue-800 font-semibold mb-2">
            Exercise Your Rights:
          </p>
          <p className="text-blue-700">
            To exercise any of these rights, please contact us via GitHub Issues or use the
            data export/deletion tools in your account settings (if available).
          </p>
        </div>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">7. Data Retention</h2>
        <p className="text-gray-700 leading-relaxed">
          We retain your data for as long as necessary to provide the Service:
        </p>
        <ul className="list-disc ml-6 mt-3 space-y-2 text-gray-700">
          <li><strong>Account Data:</strong> Retained until you delete your account</li>
          <li><strong>Watchlists & Alerts:</strong> Retained until you delete them</li>
          <li><strong>Usage Logs:</strong> Retained for 90 days for security and debugging</li>
          <li><strong>Deleted Data:</strong> Permanently deleted within 30 days of deletion request</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">8. Children's Privacy</h2>
        <p className="text-gray-700 leading-relaxed">
          TradeSignal is not intended for children under 13 years of age.
          We do not knowingly collect personal information from children.
          If you believe we have collected information from a child, please contact us immediately.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">9. Changes to Privacy Policy</h2>
        <p className="text-gray-700 leading-relaxed">
          We may update this Privacy Policy from time to time.
          We will notify you of significant changes by posting a notice on the Service
          or sending an email (if you have provided one).
          Continued use of the Service after changes constitutes acceptance of the updated policy.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3 text-gray-800">10. Contact Us</h2>
        <p className="text-gray-700 leading-relaxed">
          For privacy-related questions or requests, please contact us via GitHub Issues
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

export default PrivacyPolicyPage;
