import LegalHeroSection from '../components/legal/LegalHeroSection';
import LegalContentSection from '../components/legal/LegalContentSection';
import Section from '../components/legal/Section';

const PrivacyPolicyPage = () => {
  return (
    <>
      <LegalHeroSection 
        title="Privacy Policy" 
        intro="At TradeSignal, your privacy matters. This policy outlines how we collect, use, and protect your information when you use our services." 
      />
      <LegalContentSection>
        <Section title="1. Information We Collect">
          <ul className="list-disc ml-6 space-y-2">
            <li><strong>Personal Information:</strong> Email address, username, payment details (processed securely by Stripe).</li>
            <li><strong>Trading Data:</strong> Watchlists, alert configurations, and user preferences.</li>
            <li><strong>Usage Data:</strong> Pages visited, features accessed, time spent, and interaction logs.</li>
            <li><strong>Device Data:</strong> IP address, browser type, operating system, and device identifiers.</li>
            <li><strong>Communication Data:</strong> Support tickets, feedback, and inquiries sent to us.</li>
          </ul>
        </Section>

        <Section title="2. How We Use Your Information">
          <ul className="list-disc ml-6 space-y-2">
            <li>To provide and maintain our insider trading intelligence platform (Alpha release).</li>
            <li>To process your subscription payments and manage your account status via Stripe.</li>
            <li>To send you real-time trade alerts via email, push notifications, Discord, Slack, SMS, and webhooks.</li>
            <li>To provide AI-powered insights and analysis (Beta feature, requires API key configuration).</li>
            <li>To improve our services and algorithms based on aggregated, anonymized usage patterns.</li>
            <li>To provide customer support and respond to your inquiries through our ticket system.</li>
            <li>To detect and prevent fraud, abuse, and security incidents.</li>
            <li>To comply with legal obligations and enforce our Terms of Service.</li>
          </ul>
        </Section>

        <Section title="3. Sharing of Information">
          <p>We do not sell your personal information. We may share information with:</p>
          <ul className="list-disc ml-6 space-y-2 mt-4">
            <li><strong>Service Providers:</strong> Third-party vendors who assist in our operations, including:
              <ul className="list-disc ml-6 mt-2 space-y-1">
                <li><strong>Stripe</strong> - Payment processing for subscriptions</li>
                <li><strong>PostgreSQL</strong> - Database hosting and data storage</li>
                <li><strong>Redis</strong> - Caching and session management</li>
                <li><strong>Email Services</strong> - Resend, Brevo, or SendGrid for email notifications</li>
                <li><strong>Twilio</strong> - SMS notifications (Pro/Enterprise tiers only)</li>
                <li><strong>Discord & Slack</strong> - Webhook notifications (Pro/Enterprise tiers only)</li>
                <li><strong>Market Data Providers</strong> - Finnhub, Alpha Vantage, CoinGecko, FRED API for financial data</li>
                <li><strong>AI Services</strong> - Google Gemini or OpenAI for AI-powered insights (optional, requires API key)</li>
              </ul>
            </li>
            <li><strong>Legal Requirements:</strong> If required by law, court order, or government regulation.</li>
            <li><strong>Business Transfers:</strong> In connection with a merger, sale, or asset transfer, though we will notify you before your data is transferred.</li>
          </ul>
        </Section>

        <Section title="4. Cookies & Tracking Technologies">
          <p>We use cookies and similar technologies to enhance your experience:</p>
          <ul className="list-disc ml-6 space-y-2 mt-4">
             <li><strong>Essential Cookies:</strong> Required for authentication and session management.</li>
             <li><strong>Preference Cookies:</strong> To remember your settings (e.g., theme, chart preferences).</li>
             <li><strong>Analytics Cookies:</strong> To understand how users interact with our platform (e.g., Google Analytics).</li>
          </ul>
          <p className="mt-4">You can control cookie settings through your browser, but some features may not function properly without them.</p>
        </Section>

        <Section title="5. Data Security">
          <p>We implement industry-standard security measures to protect your data, including encryption in transit (HTTPS) and at rest. However, no method of transmission over the internet is 100% secure, and we cannot guarantee absolute security.</p>
        </Section>

        <Section title="6. Third-Party Links">
          <p>Our Service may contain links to third-party websites (e.g., SEC EDGAR, news sites). We are not responsible for the privacy practices or content of these external sites.</p>
        </Section>

        <Section title="7. Changes to This Policy">
          <p>We may update this Privacy Policy from time to time. We will notify you of significant changes via email or a prominent notice on our Service. Your continued use of TradeSignal after changes constitutes acceptance of the new policy.</p>
          <p className="mt-4"><strong>Last Updated:</strong> {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
        </Section>

        <Section title="8. Contact Us">
          <p>If you have any questions about this Privacy Policy, please contact us at:</p>
          <a href="mailto:support@tradesignal.com" className="text-purple-600 hover:text-purple-800 font-semibold block mt-2">
            support@tradesignal.com
          </a>
        </Section>
      </LegalContentSection>
    </>
  );
};

export default PrivacyPolicyPage;