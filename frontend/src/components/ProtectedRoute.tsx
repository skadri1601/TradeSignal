/**
 * Protected Route Component
 * Redirects to login if user is not authenticated
 */

import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Loader2 } from 'lucide-react';

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
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check for verified user requirement
  if (requireVerified && user && !user.is_verified) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="bg-yellow-100 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">⚠️</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Email Verification Required
          </h2>
          <p className="text-gray-600 mb-6">
            Please verify your email address to access this feature.
          </p>
          <button
            onClick={() => window.location.href = '/profile'}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
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
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="bg-red-100 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">🚫</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Access Denied
            </h2>
            <p className="text-gray-600 mb-6">
              You don't have permission to access this page. Admin privileges are required.
            </p>
            <button
              onClick={() => window.location.href = '/'}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Go to Dashboard
            </button>
          </div>
        </div>
      );
    }
  }

  // Check for subscription tier requirement
  if (requireTier && user) {
    const userTier = user.stripe_subscription_tier || 'free';
    const requiredLevel = TIER_LEVELS[requireTier.toLowerCase()] || 0;
    const userLevel = TIER_LEVELS[userTier.toLowerCase()] || 0;

    if (userLevel < requiredLevel) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="bg-purple-100 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">💎</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Premium Feature
            </h2>
            <p className="text-gray-600 mb-6">
              This feature requires a {requireTier.toUpperCase()} subscription.
              Please upgrade your plan to access this page.
            </p>
            <div className="space-y-3">
              <button
                onClick={() => window.location.href = '/pricing'}
                className="w-full bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
              >
                View Pricing
              </button>
              <button
                onClick={() => window.location.href = '/dashboard'}
                className="w-full bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
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
  return <>{children}</>;
}