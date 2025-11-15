/**
 * Cookie Consent Banner Component
 *
 * GDPR-compliant cookie consent banner.
 * Based on TRUTH_FREE.md Phase 2.4 specifications.
 */

import { useState, useEffect } from 'react';

export const CookieConsent = () => {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem('cookieConsent');
    if (!consent) {
      // Show banner after a short delay
      setTimeout(() => setShow(true), 1000);
    }
  }, []);

  const acceptCookies = () => {
    localStorage.setItem('cookieConsent', 'accepted');
    localStorage.setItem('cookieConsentDate', new Date().toISOString());
    setShow(false);
    // Enable analytics here if needed
    console.log('Cookies accepted');
  };

  const declineCookies = () => {
    localStorage.setItem('cookieConsent', 'declined');
    localStorage.setItem('cookieConsentDate', new Date().toISOString());
    setShow(false);
    // Disable analytics if declined
    console.log('Cookies declined');
  };

  if (!show) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900 text-white p-4 z-50 shadow-2xl border-t border-gray-700">
      <div className="max-w-7xl mx-auto flex items-center justify-between flex-wrap gap-4">
        <div className="flex-1 min-w-[300px]">
          <div className="flex items-start">
            <span className="text-2xl mr-3">🍪</span>
            <div>
              <p className="text-sm font-medium mb-1">
                We use cookies to improve your experience
              </p>
              <p className="text-xs text-gray-300">
                By continuing to use this site, you agree to our use of cookies.
                See our{' '}
                <a
                  href="/privacy"
                  className="underline hover:text-white"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Privacy Policy
                </a>
                {' '}for details.
              </p>
            </div>
          </div>
        </div>
        <div className="flex gap-3">
          <button
            onClick={declineCookies}
            className="px-4 py-2 bg-gray-700 rounded hover:bg-gray-600 text-sm font-medium transition-colors duration-200"
            aria-label="Decline cookies"
          >
            Decline
          </button>
          <button
            onClick={acceptCookies}
            className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-500 text-sm font-medium transition-colors duration-200"
            aria-label="Accept cookies"
          >
            Accept
          </button>
        </div>
      </div>
    </div>
  );
};

export default CookieConsent;
