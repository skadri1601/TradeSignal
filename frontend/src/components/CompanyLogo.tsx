/**
 * Company Logo Component
 * Displays company logos using multiple sources with fallbacks
 * Primary source: Backend API (Yahoo Finance)
 * Fallbacks: UI Avatars, Ticker initials
 */

import { useState, useEffect } from 'react';
import { companiesApi } from '../api/companies';

interface CompanyLogoProps {
  ticker: string;
  companyName?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const sizeMap = {
  sm: 'w-8 h-8',
  md: 'w-10 h-10',
  lg: 'w-12 h-12',
  xl: 'w-16 h-16',
};

export default function CompanyLogo({
  ticker,
  companyName,
  size = 'md',
  className = ''
}: CompanyLogoProps) {
  const [currentSourceIndex, setCurrentSourceIndex] = useState(0);
  const [imageError, setImageError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [timeoutReached, setTimeoutReached] = useState(false);
  const [logoUrl, setLogoUrl] = useState<string | null>(null);

  // Fetch logo from backend API (Yahoo Finance)
  useEffect(() => {
    let cancelled = false;

    const fetchLogo = async () => {
      try {
        const url = await companiesApi.getCompanyLogo(ticker);
        if (!cancelled && url) {
          setLogoUrl(url);
          setLoading(false);
          setImageError(false);
        } else if (!cancelled) {
          // No logo from backend, use fallback
          setImageError(true);
        }
      } catch (error) {
        if (!cancelled) {
          console.warn(`Failed to fetch logo for ${ticker}:`, error);
          setImageError(true);
        }
      }
    };

    fetchLogo();

    return () => {
      cancelled = true;
    };
  }, [ticker]);

  // Fallback sources if backend doesn't have logo
  const getLogoSources = (): string[] => {
    const sources: string[] = [];
    
    // Primary: Backend API logo (already fetched, stored in logoUrl state)
    if (logoUrl) {
      sources.push(logoUrl);
    }
    
    // Secondary: Use UI Avatars as fallback (always works, no API needed)
    sources.push(`https://ui-avatars.com/api/?name=${encodeURIComponent(ticker)}&background=3B82F6&color=fff&bold=true&size=128`);
    
    return sources;
  };

  const logoSources = getLogoSources();
  const currentLogoUrl = logoSources[currentSourceIndex] || logoUrl || undefined;

  useEffect(() => {
    // Reset when ticker changes
    setCurrentSourceIndex(0);
    setImageError(false);
    setLoading(true);
    setTimeoutReached(false);
    setLogoUrl(null);

    // Set timeout for image loading (3 seconds per source)
    const timeoutId = setTimeout(() => {
      setTimeoutReached(true);
      // Trigger error handler to try next source or show fallback
      const sources = getLogoSources();
      setCurrentSourceIndex(prev => {
        if (prev < sources.length - 1) {
          setLoading(true);
          setTimeoutReached(false);
          return prev + 1;
        } else {
          setLoading(false);
          setImageError(true);
          return prev;
        }
      });
    }, 3000);

    return () => clearTimeout(timeoutId);
  }, [ticker]);

  const handleImageLoad = () => {
    setLoading(false);
    setImageError(false);
    setTimeoutReached(false);
  };

  const handleImageError = () => {
    // Try next source
    const sources = getLogoSources();
    setCurrentSourceIndex(prev => {
      if (prev < sources.length - 1) {
        setLoading(true);
        setTimeoutReached(false);
        return prev + 1;
      } else {
        // All sources failed, show fallback immediately
        setLoading(false);
        setImageError(true);
        return prev;
      }
    });
  };

  // Fallback UI with ticker initial or letters
  // Show fallback if error, no ticker, or timeout reached
  if (imageError || !ticker || timeoutReached) {
    const tickerText = ticker?.toUpperCase().slice(0, 2) || 'N/A';
    return (
      <div className={`${sizeMap[size]} ${className} bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center flex-shrink-0 shadow-sm`}>
        <span className="text-white font-bold text-xs">
          {tickerText}
        </span>
      </div>
    );
  }

  return (
    <div className={`${sizeMap[size]} ${className} bg-white rounded-lg flex items-center justify-center flex-shrink-0 overflow-hidden border border-gray-200 shadow-sm relative`}>
      {loading && (
        <div className="absolute inset-0 animate-pulse bg-gray-200 rounded-lg"></div>
      )}
      {currentLogoUrl ? (
        <img
          src={currentLogoUrl || undefined}
          alt={`${companyName || ticker} logo`}
          className={`w-full h-full object-contain p-1 ${loading ? 'opacity-0' : 'opacity-100'} transition-opacity duration-200`}
          onLoad={handleImageLoad}
          onError={handleImageError}
          loading="lazy"
        />
      ) : null}
    </div>
  );
}
