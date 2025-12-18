/**
 * First-Time Disclaimer Modal Component
 *
 * Forces users to accept terms on first visit.
 * Based on TRUTH_FREE.md Phase 2.1 specifications.
 */

import { useState } from 'react';
import { useCustomAlert } from '../hooks/useCustomAlert';
import CustomAlert from './common/CustomAlert';
import { AlertTriangle, CheckCircle, Info } from 'lucide-react';

interface FirstTimeDisclaimerModalProps {
  onAccept: () => void;
}

export const FirstTimeDisclaimerModal = ({ onAccept }: FirstTimeDisclaimerModalProps) => {
  const [termsAccepted, setTermsAccepted] = useState(false);
  const { alertState, showAlert, hideAlert } = useCustomAlert();

  const handleAccept = () => {
    if (!termsAccepted) {
      showAlert(
        'Please check the box to confirm you have read and agree to the terms.',
        { type: 'warning', title: 'TradeSignal' }
      );
      return;
    }
    onAccept();
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 z-50">
      <div className="bg-[#0f0f1a] border border-white/10 rounded-2xl max-w-2xl max-h-[85vh] overflow-y-auto p-8 shadow-2xl relative">
        {/* Glow Effect */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-1 bg-gradient-to-r from-transparent via-purple-500 to-transparent opacity-50"></div>

        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-6 text-white flex items-center gap-3">
            <AlertTriangle className="w-8 h-8 text-yellow-500" />
            Important Disclaimer
          </h2>

          <div className="space-y-6 text-gray-300 leading-relaxed">
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-5 flex gap-4 items-start">
              <Info className="w-6 h-6 text-red-400 shrink-0 mt-0.5" />
              <div>
                <p className="font-bold text-red-400 text-lg mb-1">
                  THIS IS NOT FINANCIAL ADVICE
                </p>
                <p className="text-sm text-red-200/80">
                  TradeSignal is for <strong>educational purposes only</strong>.
                  We do not provide investment advice, financial advice, or trading recommendations.
                  Always consult a licensed financial advisor before making investment decisions.
                </p>
              </div>
            </div>

            <p className="text-lg">
              By clicking "I Understand", you acknowledge that:
            </p>

            <ul className="space-y-3 bg-white/5 border border-white/5 p-6 rounded-xl text-sm">
              <li className="flex items-start gap-3">
                <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-2 shrink-0"></span>
                This is not professional financial advice
              </li>
              <li className="flex items-start gap-3">
                <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-2 shrink-0"></span>
                You will not rely on this information for investment decisions
              </li>
              <li className="flex items-start gap-3">
                <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-2 shrink-0"></span>
                Trading stocks involves substantial risk of loss
              </li>
              <li className="flex items-start gap-3">
                <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-2 shrink-0"></span>
                Data may be delayed or inaccurate
              </li>
              <li className="flex items-start gap-3">
                <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-2 shrink-0"></span>
                You use this service at your own risk
              </li>
              <li className="flex items-start gap-3">
                <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-2 shrink-0"></span>
                Past performance does not guarantee future results
              </li>
            </ul>

            <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4 text-sm text-yellow-200/80">
              <p>
                <strong className="text-yellow-400">Data Sources:</strong> Stock prices are provided by third-party feeds
                and may be delayed. SEC filings are scraped from public sources.
                AI insights are experimental and may be incorrect.
              </p>
            </div>
          </div>

          <div className="border-t border-white/10 pt-6 mt-8 mb-6">
            <label className="flex items-start cursor-pointer group">
              <div className="relative flex items-center">
                <input
                  type="checkbox"
                  checked={termsAccepted}
                  onChange={(e) => setTermsAccepted(e.target.checked)}
                  className="peer h-5 w-5 cursor-pointer appearance-none rounded-md border border-white/30 bg-black/50 checked:border-purple-500 checked:bg-purple-500 transition-all"
                  id="terms-checkbox"
                />
                <CheckCircle className="absolute pointer-events-none opacity-0 peer-checked:opacity-100 text-white w-3.5 h-3.5 left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 transition-opacity" />
              </div>
              <span className="ml-3 text-sm text-gray-400 group-hover:text-gray-300 transition-colors">
                I have read and agree to the{' '}
                <a
                  href="/terms"
                  className="text-purple-400 hover:text-purple-300 underline underline-offset-2"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Terms of Service
                </a>
                {' '}and{' '}
                <a
                  href="/privacy"
                  className="text-purple-400 hover:text-purple-300 underline underline-offset-2"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Privacy Policy
                </a>
                . I understand that this is not financial advice.
              </span>
            </label>
          </div>

          <button
            onClick={handleAccept}
            className={`w-full py-4 rounded-xl font-bold text-lg tracking-wide transition-all duration-300 shadow-lg ${
              termsAccepted
                ? 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white shadow-purple-900/30 transform hover:scale-[1.02]'
                : 'bg-white/10 text-gray-500 cursor-not-allowed border border-white/5'
            }`}
            disabled={!termsAccepted}
          >
            {termsAccepted ? 'I Understand and Accept' : 'Please Accept Terms to Continue'}
          </button>

          <p className="text-xs text-gray-600 text-center mt-4">
            You must accept these terms to use TradeSignal
          </p>
        </div>
      </div>

      {/* Custom Alert Modal */}
      <CustomAlert
        show={alertState.show}
        message={alertState.message}
        title={alertState.title || 'TradeSignal'}
        type={alertState.type}
        onClose={hideAlert}
      />
    </div>
  );
};

export default FirstTimeDisclaimerModal;