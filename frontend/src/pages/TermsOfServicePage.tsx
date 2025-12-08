import React from 'react';
import LegalHeroSection from '../components/legal/LegalHeroSection';
import LegalContentSection from '../components/legal/LegalContentSection';
import Section from '../components/legal/Section';

const TermsOfServicePage = () => {
  return (
    <>
      <LegalHeroSection 
        title="Terms & Conditions" 
        intro="Welcome to TradeSignal. By accessing or using our website, products, or services, you agree to these Terms & Conditions. Please read them carefully." 
      />
      <LegalContentSection>
        <Section title="1. Acceptance of Terms">
          <p>By accessing or using TradeSignal ("the Service"), you agree to be bound by these Terms. If you disagree with any part of the terms, you may not access the Service.</p>
          <p className="mt-4">You must be at least 18 years old to use this Service.</p>
        </Section>

        <Section title="2. Use of Services">
           <ul className="list-disc ml-6 space-y-2">
            <li><strong>Informational Purposes Only:</strong> TradeSignal provides financial data and AI insights for educational and informational purposes only. We are <strong>NOT</strong> financial advisors, and nothing on this site constitutes investment advice.</li>
            <li><strong>No Automated Scraping:</strong> You agree not to use automated bots, scrapers, or spiders to access or extract data from our Service without express written permission.</li>
            <li><strong>Lawful Use:</strong> You agree to use the Service only for lawful purposes and not to violate any applicable laws or regulations.</li>
           </ul>
        </Section>

        <Section title="3. Accounts & Registration">
          <ul className="list-disc ml-6 space-y-2">
            <li>You must provide accurate and complete information when creating an account.</li>
            <li>You are responsible for maintaining the confidentiality of your account and password.</li>
            <li>You agree to accept responsibility for all activities that occur under your account.</li>
            <li>We reserve the right to terminate accounts that violate these Terms.</li>
          </ul>
        </Section>

        <Section title="4. Purchases & Payments">
          <ul className="list-disc ml-6 space-y-2">
            <li><strong>Subscriptions:</strong> Some parts of the Service are billed on a subscription basis (Free, Plus, Pro, Enterprise).</li>
            <li><strong>Billing:</strong> You will be billed in advance on a recurring and periodic basis (monthly or annually).</li>
            <li><strong>Cancellation:</strong> You may cancel your subscription at any time. Your access will continue until the end of the current billing period.</li>
            <li><strong>Refunds:</strong> Refunds are handled on a case-by-case basis and are generally not provided for partial months.</li>
          </ul>
        </Section>

        <Section title="5. Intellectual Property">
          <p>The Service and its original content (excluding SEC public data), features, and functionality are and will remain the exclusive property of TradeSignal and its licensors. The Service is protected by copyright, trademark, and other laws.</p>
        </Section>

        <Section title="6. Limitation of Liability">
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
             <p className="font-bold text-yellow-800">DISCLAIMER:</p>
             <p className="text-yellow-700">TradeSignal is not responsible for any financial losses or damages resulting from your investment decisions.</p>
          </div>
          <p>In no event shall TradeSignal, nor its directors, employees, partners, agents, suppliers, or affiliates, be liable for any indirect, incidental, special, consequential or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses, resulting from your access to or use of or inability to access or use the Service.</p>
        </Section>

        <Section title="7. Termination">
          <p>We may terminate or suspend your account and bar access to the Service immediately, without prior notice or liability, under our sole discretion, for any reason whatsoever and without limitation, including but not limited to a breach of the Terms.</p>
        </Section>

        <Section title="8. Changes to Terms">
          <p>We reserve the right, at our sole discretion, to modify or replace these Terms at any time. If a revision is material we will provide at least 30 days' notice prior to any new terms taking effect. What constitutes a material change will be determined at our sole discretion.</p>
          <p className="mt-4"><strong>Last Updated:</strong> {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
        </Section>

        <Section title="9. Contact Us">
          <p>If you have any questions about these Terms, please contact us at:</p>
          <a href="mailto:support@tradesignal.com" className="text-purple-600 hover:text-purple-800 font-semibold block mt-2">
            support@tradesignal.com
          </a>
        </Section>
      </LegalContentSection>
    </>
  );
};

export default TermsOfServicePage;