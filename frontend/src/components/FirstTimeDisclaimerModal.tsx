/**
 * First-Time Disclaimer Modal Component
 *
 * Forces users to accept terms on first visit.
 * Based on TRUTH_FREE.md Phase 2.1 specifications.
 */

import { useState } from 'react';

interface FirstTimeDisclaimerModalProps {
  onAccept: () => void;
}

export const FirstTimeDisclaimerModal = ({ onAccept }: FirstTimeDisclaimerModalProps) => {
  const [termsAccepted, setTermsAccepted] = useState(false);

  const handleAccept = () => {
    if (!termsAccepted) {
      alert('Please check the box to confirm you have read and agree to the terms.');
      return;
    }
    onAccept();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
      <div className="bg-white rounded-lg max-w-2xl max-h-[80vh] overflow-y-auto p-6 shadow-2xl">
        <div className="mb-6">
          <h2 className="text-2xl font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-3xl mr-2">⚠️</span>
            Important Disclaimer
          </h2>

          <div className="mb-6 text-gray-700 space-y-3">
            <div className="bg-red-50 border-l-4 border-red-500 p-4">
              <p className="font-bold text-red-800 text-lg">
                THIS IS NOT FINANCIAL ADVICE
              </p>
            </div>

            <p>
              TradeSignal is for <strong>educational purposes only</strong>.
              We do not provide investment advice, financial advice, or trading recommendations.
              Always consult a licensed financial advisor before making investment decisions.
            </p>

            <p className="font-semibold text-gray-900">
              By clicking "I Understand", you acknowledge that:
            </p>

            <ul className="list-disc ml-6 space-y-2 bg-gray-50 p-4 rounded">
              <li>This is not professional financial advice</li>
              <li>You will not rely on this information for investment decisions</li>
              <li>Trading stocks involves substantial risk of loss</li>
              <li>Data may be delayed or inaccurate</li>
              <li>You use this service at your own risk</li>
              <li>Past performance does not guarantee future results</li>
              <li>We are not responsible for your investment decisions</li>
            </ul>

            <div className="bg-yellow-50 border border-yellow-300 rounded p-4">
              <p className="text-sm text-yellow-800">
                <strong>Data Sources:</strong> Stock prices are provided by Yahoo Finance
                and may be delayed. SEC filings are scraped from public sources.
                AI insights are experimental and may be incorrect.
              </p>
            </div>
          </div>

          <div className="border-t border-gray-300 pt-4 mb-4">
            <label className="flex items-start cursor-pointer">
              <input
                type="checkbox"
                checked={termsAccepted}
                onChange={(e) => setTermsAccepted(e.target.checked)}
                className="mt-1 mr-3 h-5 w-5 cursor-pointer"
                id="terms-checkbox"
              />
              <span className="text-sm text-gray-700">
                I have read and agree to the{' '}
                <a
                  href="/terms"
                  className="text-blue-600 underline hover:text-blue-800"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Terms of Service
                </a>
                {' '}and{' '}
                <a
                  href="/privacy"
                  className="text-blue-600 underline hover:text-blue-800"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Privacy Policy
                </a>
                . I understand that this is not financial advice and I will not make
                investment decisions based solely on information from this site.
              </span>
            </label>
          </div>

          <button
            onClick={handleAccept}
            className={`w-full py-3 rounded-lg font-semibold transition-colors duration-200 ${
              termsAccepted
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
            disabled={!termsAccepted}
          >
            {termsAccepted ? 'I Understand and Accept' : 'Please Accept Terms to Continue'}
          </button>

          <p className="text-xs text-gray-500 text-center mt-3">
            You must accept these terms to use TradeSignal
          </p>
        </div>
      </div>
    </div>
  );
};

export default FirstTimeDisclaimerModal;
