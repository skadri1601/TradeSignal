import { createContext, useContext, useState, useEffect, ReactNode, useCallback, useRef } from 'react';
import { useUser, useAuth as useClerkAuth, useClerk } from '@clerk/clerk-react';

interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_verified: boolean;
  is_superuser: boolean;
  role?: string;
  full_name?: string | null;
  date_of_birth?: string | null;
  phone_number?: string | null;
  bio?: string | null;
  avatar_url?: string | null;
  stripe_subscription_tier?: string | null;
}

export type SyncErrorType = 'network' | 'database' | 'auth' | 'server';

export interface SyncError {
  type: SyncErrorType;
  message: string;
  retryable: boolean;
}

export interface AuthContextType {
  user: User | null;
  tokens: null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isDegraded: boolean;
  syncError: SyncError | null;
  autoRetryCountdown: number;
  retrySync: () => void;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const MAX_FETCH_RETRIES = 3;
const RETRY_DELAY_MS = 1500;
const CACHE_KEY_PREFIX = 'ts_user_cache_';

let cachedToken: string | null = null;

function getCachedUser(clerkUserId: string): User | null {
  try {
    const raw = sessionStorage.getItem(`${CACHE_KEY_PREFIX}${clerkUserId}`);
    return raw ? JSON.parse(raw) : null;
  } catch { return null; }
}

function setCachedUser(clerkUserId: string, user: User) {
  try {
    sessionStorage.setItem(`${CACHE_KEY_PREFIX}${clerkUserId}`, JSON.stringify(user));
  } catch { /* quota exceeded */ }
}

function clearCachedUser(clerkUserId: string) {
  try {
    sessionStorage.removeItem(`${CACHE_KEY_PREFIX}${clerkUserId}`);
  } catch { /* ignore */ }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const { isSignedIn, user: clerkUser, isLoaded: isClerkLoaded } = useUser();
  const { getToken } = useClerkAuth();
  const clerk = useClerk();
  const [backendUser, setBackendUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasSynced, setHasSynced] = useState(false);
  const [syncError, setSyncError] = useState<SyncError | null>(null);
  const [isDegraded, setIsDegraded] = useState(false);
  const [autoRetryCountdown, setAutoRetryCountdown] = useState(0);
  const retryTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fetchBackendUser = useCallback(async () => {
    if (!isSignedIn || !clerkUser) return;

    const token = await getToken();
    if (!token) return;
    cachedToken = token;

    for (let attempt = 0; attempt < MAX_FETCH_RETRIES; attempt++) {
      try {
        const response = await fetch(`${API_URL}/api/v1/auth/me`, {
          headers: { 'Authorization': `Bearer ${token}` },
        });

        if (response.ok) {
          const userData = await response.json();
          setBackendUser(userData);
          setSyncError(null);
          setIsDegraded(false);
          setIsLoading(false);
          setHasSynced(true);
          setCachedUser(clerkUser.id, userData);
          return;
        }

        if (response.status === 401 || response.status === 404) {
          // User not provisioned yet -- fall back to clerk-sync to create them
          const syncResp = await fetch(`${API_URL}/api/v1/auth/clerk-sync`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          if (syncResp.ok) {
            const userData = await syncResp.json();
            setBackendUser(userData);
            setSyncError(null);
            setIsDegraded(false);
            setIsLoading(false);
            setHasSynced(true);
            setCachedUser(clerkUser.id, userData);
            return;
          }
        }

        if (attempt === MAX_FETCH_RETRIES - 1) {
          const cached = getCachedUser(clerkUser.id);
          if (cached) {
            setBackendUser(cached);
            setIsDegraded(true);
            setSyncError(null);
          } else {
            setSyncError({
              type: response.status === 503 ? 'database' : 'server',
              message: response.status === 503
                ? 'Database temporarily unavailable.'
                : 'An unexpected server error occurred.',
              retryable: true,
            });
          }
          setIsLoading(false);
          setHasSynced(true);
          return;
        }

        await new Promise(r => { retryTimerRef.current = setTimeout(r, RETRY_DELAY_MS * (attempt + 1)); });
      } catch {
        if (attempt === MAX_FETCH_RETRIES - 1) {
          const cached = getCachedUser(clerkUser.id);
          if (cached) {
            setBackendUser(cached);
            setIsDegraded(true);
            setSyncError(null);
          } else {
            setSyncError({ type: 'network', message: 'Cannot reach the server.', retryable: true });
          }
          setIsLoading(false);
          setHasSynced(true);
          return;
        }
        await new Promise(r => { retryTimerRef.current = setTimeout(r, RETRY_DELAY_MS * (attempt + 1)); });
      }
    }
  }, [isSignedIn, clerkUser, getToken]);

  useEffect(() => {
    return () => { if (retryTimerRef.current) clearTimeout(retryTimerRef.current); };
  }, []);

  useEffect(() => {
    if (!isClerkLoaded) return;

    if (isSignedIn && !hasSynced) {
      fetchBackendUser();
    } else if (!isSignedIn) {
      setBackendUser(null);
      cachedToken = null;
      setIsLoading(false);
      setHasSynced(false);
      setSyncError(null);
      setIsDegraded(false);
      setAutoRetryCountdown(0);
    }
  }, [isClerkLoaded, isSignedIn, hasSynced, fetchBackendUser]);

  // Auto-retry countdown when showing error
  useEffect(() => {
    if (!syncError?.retryable) {
      setAutoRetryCountdown(0);
      return;
    }

    let remaining = 15;
    setAutoRetryCountdown(remaining);

    const interval = setInterval(() => {
      remaining -= 1;
      setAutoRetryCountdown(remaining);
      if (remaining <= 0) {
        clearInterval(interval);
        setSyncError(null);
        setHasSynced(false);
        setIsLoading(true);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [syncError]);

  // Re-fetch when tab regains focus if in error or degraded state
  useEffect(() => {
    const handleVisibility = () => {
      if (document.visibilityState === 'visible' && (syncError || isDegraded)) {
        setSyncError(null);
        setIsDegraded(false);
        setHasSynced(false);
        setIsLoading(true);
      }
    };
    document.addEventListener('visibilitychange', handleVisibility);
    return () => document.removeEventListener('visibilitychange', handleVisibility);
  }, [syncError, isDegraded]);

  // Periodic token refresh
  useEffect(() => {
    if (!isSignedIn) return;

    const refreshToken = async () => {
      const token = await getToken();
      cachedToken = token;
    };

    refreshToken();
    const interval = setInterval(refreshToken, 50000);
    return () => clearInterval(interval);
  }, [isSignedIn, getToken]);

  const logout = useCallback(() => {
    if (clerkUser) clearCachedUser(clerkUser.id);
    cachedToken = null;
    setBackendUser(null);
    setHasSynced(false);
    setSyncError(null);
    setIsDegraded(false);
    clerk.signOut();
  }, [clerk, clerkUser]);

  const login = async () => { clerk.openSignIn(); };
  const register = async () => { clerk.openSignUp(); };

  const refreshAccessToken = async () => {
    const token = await getToken();
    cachedToken = token;
  };

  const retrySync = useCallback(() => {
    if (retryTimerRef.current) clearTimeout(retryTimerRef.current);
    setSyncError(null);
    setIsDegraded(false);
    setHasSynced(false);
    setIsLoading(true);
    setAutoRetryCountdown(0);
  }, []);

  const value: AuthContextType = {
    user: backendUser,
    tokens: null,
    isAuthenticated: !!isSignedIn && !!backendUser,
    isLoading: !isClerkLoaded || isLoading,
    isDegraded,
    syncError,
    autoRetryCountdown,
    retrySync,
    login,
    register,
    logout,
    refreshAccessToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export function getAccessToken(): string | null {
  return cachedToken;
}
