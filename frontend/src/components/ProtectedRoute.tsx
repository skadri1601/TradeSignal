/**
 * Protected Route Component
 * Redirects to login if user is not authenticated
 *
 * PORTFOLIO MODE: Tier restrictions bypassed for portfolio showcase
 */

import { Navigate, useLocation } from 'react-router-dom';
import { useAuth, SyncErrorType } from '../contexts/AuthContext';
import { Loader2, WifiOff, Database, ShieldAlert, ServerCrash, RefreshCw, LogOut, X } from 'lucide-react';
import { useState } from 'react';

// PORTFOLIO MODE: Set to true to bypass all tier restrictions
const PORTFOLIO_MODE = true;

// Define tier hierarchy
const TIER_LEVELS: Record<string, number> = {
  'free': 0,
  'basic': 1,
  'plus': 2,
  'pro': 3,
  'enterprise': 4
};

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireVerified?: boolean;
  requireSuperuser?: boolean;
  redirectAdmin?: boolean; // If true, redirect admins to /admin
  requireTier?: string; // Minimum tier required
}

export function ProtectedRoute({
  children,
  requireVerified = false,
  requireSuperuser = false,
  redirectAdmin = false,
  requireTier
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user, syncError, isDegraded, autoRetryCountdown, retrySync, logout } = useAuth();
  const location = useLocation();
  const [bannerDismissed, setBannerDismissed] = useState(false);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-gray-900 via-gray-900 to-black">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-purple-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (syncError) {
    const errorConfig: Record<SyncErrorType, {
      icon: React.ReactNode;
      title: string;
      description: string;
      iconBg: string;
    }> = {
      network: {
        icon: <WifiOff className="w-8 h-8 text-red-400" />,
        title: 'Cannot Reach Server',
        description: 'Please check that the backend is running and try again.',
        iconBg: 'bg-red-500/20 border-red-500/30',
      },
      database: {
        icon: <Database className="w-8 h-8 text-amber-400" />,
        title: 'Database Temporarily Unavailable',
        description: 'The server is running but the database is temporarily unavailable. This usually resolves in a few moments.',
        iconBg: 'bg-amber-500/20 border-amber-500/30',
      },
      auth: {
        icon: <ShieldAlert className="w-8 h-8 text-orange-400" />,
        title: 'Authentication Error',
        description: 'There was a problem verifying your session. Please sign out and try again.',
        iconBg: 'bg-orange-500/20 border-orange-500/30',
      },
      server: {
        icon: <ServerCrash className="w-8 h-8 text-red-400" />,
        title: 'Server Error',
        description: 'An unexpected server error occurred. Please try again.',
        iconBg: 'bg-red-500/20 border-red-500/30',
      },
    };

    const config = errorConfig[syncError.type];

    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-gray-900 via-gray-900 to-black">
        <div className="text-center max-w-md">
          <div className={`rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4 border ${config.iconBg}`}>
            {config.icon}
          </div>
          <p className="text-red-400 text-lg font-semibold mb-2">{config.title}</p>
          <p className="text-gray-400 mb-6">{config.description}</p>
          <div className="space-y-3">
            {syncError.retryable && (
              <>
                <button
                  onClick={retrySync}
                  className="bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors w-full"
                >
                  Retry Now
                </button>
                {autoRetryCountdown > 0 && (
                  <p className="text-gray-500 text-sm">
                    Retrying automatically in {autoRetryCountdown}s...
                  </p>
                )}
              </>
            )}
            {syncError.type === 'auth' && (
              <button
                onClick={logout}
                className="flex items-center justify-center gap-2 bg-gray-700 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-600 transition-colors w-full"
              >
                <LogOut className="w-4 h-4" />
                Sign Out
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check for verified user requirement
  if (requireVerified && user && !user.is_verified) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-gray-900 via-gray-900 to-black px-4">
        <div className="max-w-md w-full bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-2xl shadow-2xl p-8 text-center border border-gray-700/50 backdrop-blur-sm">
          <div className="bg-yellow-500/20 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4 border border-yellow-500/30">
            <span className="text-3xl">⚠️</span>
          </div>
          <h2 className="text-2xl font-bold text-white mb-4">
            Email Verification Required
          </h2>
          <p className="text-gray-400 mb-6">
            Please verify your email address to access this feature.
          </p>
          <button
            onClick={() => window.location.href = '/profile'}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
          >
            Go to Profile
          </button>
        </div>
      </div>
    );
  }

  // Check for superuser requirement
  if (requireSuperuser && user) {
    const isAdmin = user.is_superuser || user.role === 'super_admin' || user.role === 'support';

    if (!isAdmin) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-gray-900 via-gray-900 to-black px-4">
          <div className="max-w-md w-full bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-2xl shadow-2xl p-8 text-center border border-gray-700/50 backdrop-blur-sm">
            <div className="bg-red-500/20 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4 border border-red-500/30">
              <span className="text-3xl">🚫</span>
            </div>
            <h2 className="text-2xl font-bold text-white mb-4">
              Access Denied
            </h2>
            <p className="text-gray-400 mb-6">
              You don't have permission to access this page. Admin privileges are required.
            </p>
            <button
              onClick={() => window.location.href = '/'}
              className="bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
            >
              Go to Dashboard
            </button>
          </div>
        </div>
      );
    }
  }

  // Check for subscription tier requirement
  // PORTFOLIO MODE: Skip tier checks entirely
  if (!PORTFOLIO_MODE && requireTier && user) {
    const userTier = user.stripe_subscription_tier || 'free';
    const requiredLevel = TIER_LEVELS[requireTier.toLowerCase()] || 0;
    const userLevel = TIER_LEVELS[userTier.toLowerCase()] || 0;

    if (userLevel < requiredLevel) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-gray-900 via-gray-900 to-black px-4">
          <div className="max-w-md w-full bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-2xl shadow-2xl p-8 text-center border border-gray-700/50 backdrop-blur-sm">
            <div className="bg-purple-500/20 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4 border border-purple-500/30">
              <span className="text-3xl">💎</span>
            </div>
            <h2 className="text-2xl font-bold text-white mb-4">
              Future Enhancement
            </h2>
            <p className="text-gray-400 mb-6">
              This feature is planned for future development.
              All features are currently free for portfolio showcase.
            </p>
            <div className="space-y-3">
              <button
                onClick={() => window.location.href = '/dashboard'}
                className="w-full bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      );
    }
  }

  // Redirect admins away from user pages to admin dashboard
  if (redirectAdmin && user) {
    const isAdmin = user.is_superuser || user.role === 'super_admin' || user.role === 'support';
    if (isAdmin) {
      return <Navigate to="/admin" replace />;
    }
  }

  // User is authenticated and meets all requirements
  return (
    <>
      {isDegraded && !bannerDismissed && (
        <div className="bg-amber-500/10 border-b border-amber-500/30 px-4 py-2.5">
          <div className="max-w-7xl mx-auto flex items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-amber-300 text-sm">
              <Database className="w-4 h-4 flex-shrink-0" />
              <span>Running in offline mode &mdash; some features may be limited.</span>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <button
                onClick={retrySync}
                className="flex items-center gap-1 text-amber-300 hover:text-amber-200 text-sm font-medium transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Reconnect
              </button>
              <button
                onClick={() => setBannerDismissed(true)}
                className="text-amber-400/60 hover:text-amber-300 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
      {children}
    </>
  );
}