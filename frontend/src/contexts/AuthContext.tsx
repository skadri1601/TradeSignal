/**
 * Authentication Context
 * Manages user authentication state and JWT tokens
 */

import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';

interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_verified: boolean;
  is_superuser: boolean;
  role?: string; // 'customer', 'support', 'super_admin'
  full_name?: string | null;
  date_of_birth?: string | null;
  phone_number?: string | null;
  bio?: string | null;
  avatar_url?: string | null;
  stripe_subscription_tier?: string | null;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

export interface AuthContextType {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback((): void => {
    setUser(null);
    setTokens(null);
    localStorage.removeItem('auth_tokens');
  }, []);

  // Fetch current user info
  const fetchCurrentUser = useCallback(
    async (
      accessToken: string,
      options?: {
        onUnauthorized?: () => Promise<void>;
      }
    ) => {
      try {
        const response = await fetch(`${API_URL}/api/v1/auth/me`, {
          headers: {
            'Authorization': `Bearer ${accessToken}`
          }
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else if (response.status === 401 && options?.onUnauthorized) {
          await options.onUnauthorized();
        } else {
          console.error('Failed to fetch user, status:', response.status);
          logout();
        }
      } catch (error) {
        console.error('Failed to fetch user:', error);
      } finally {
        setIsLoading(false);
      }
    },
    [logout]
  );

  // Login function
  const login = async (email: string, password: string) => {
    try {
      const formData = new FormData();
      formData.append('username', email); // OAuth2PasswordRequestForm uses 'username' field
      formData.append('password', password);

      let response: Response;
      try {
        response = await fetch(`${API_URL}/api/v1/auth/login`, {
          method: 'POST',
          body: formData
        });
      } catch (networkError: any) {
        // Handle network errors (CORS, connection refused, etc.)
        console.error('Network error during login:', networkError);
        throw new Error('Unable to connect to server. Please check your internet connection and try again.');
      }

      if (!response.ok) {
        // Try to parse error response, but handle non-JSON responses
        let errorMessage = 'Login failed. Please check your credentials.';
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
          try {
            const error = await response.json();
            errorMessage = error.detail || error.message || errorMessage;
          } catch (parseError) {
            console.error('Failed to parse error response:', parseError);
            // Use status-based error messages
            if (response.status === 401) {
              errorMessage = 'Incorrect email or password. Please try again.';
            } else if (response.status === 403) {
              errorMessage = 'Your account is inactive. Please contact support.';
            } else if (response.status >= 500) {
              errorMessage = 'Server error. Please try again later.';
            } else {
              errorMessage = `Login failed (${response.status}). Please try again.`;
            }
          }
        } else {
          // Non-JSON error response
          try {
            const text = await response.text();
            console.error('Non-JSON error response:', text);
            if (response.status === 401) {
              errorMessage = 'Incorrect email or password. Please try again.';
            } else if (response.status === 403) {
              errorMessage = 'Your account is inactive. Please contact support.';
            } else if (response.status >= 500) {
              errorMessage = 'Server error. Please try again later.';
            } else {
              errorMessage = `Login failed (${response.status}). Please try again.`;
            }
          } catch (textError) {
            console.error('Failed to read error response:', textError);
            // Fallback to status-based message
            if (response.status === 401) {
              errorMessage = 'Incorrect email or password. Please try again.';
            } else if (response.status === 403) {
              errorMessage = 'Your account is inactive. Please contact support.';
            } else if (response.status >= 500) {
              errorMessage = 'Server error. Please try again later.';
            } else {
              errorMessage = `Login failed (${response.status}). Please try again.`;
            }
          }
        }
        
        console.error('Login failed:', {
          status: response.status,
          statusText: response.statusText,
          message: errorMessage
        });
        throw new Error(errorMessage);
      }

      // Parse successful response
      let authTokens: AuthTokens;
      try {
        authTokens = await response.json();
      } catch (parseError) {
        console.error('Failed to parse login response:', parseError);
        throw new Error('Invalid response from server. Please try again.');
      }

      setTokens(authTokens);
      localStorage.setItem('auth_tokens', JSON.stringify(authTokens));

      // Fetch user data - don't fail login if this fails
      try {
        await fetchCurrentUser(authTokens.access_token);
      } catch (userError) {
        console.error('Failed to fetch user data after login:', userError);
        // Login is still successful, user just needs to refresh or we'll fetch on next page load
        // Don't throw - tokens are saved and user is logged in
      }
    } catch (error: any) {
      console.error('Login error:', {
        error,
        message: error?.message,
        stack: error?.stack,
        name: error?.name
      });
      // Re-throw with a user-friendly message if it's not already an Error with message
      if (error instanceof Error) {
        throw error;
      } else {
        throw new Error('An unexpected error occurred during login. Please try again.');
      }
    }
  };

  // Register function
  const register = async (email: string, username: string, password: string) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, username, password })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Registration failed');
      }

      // Auto-login after registration
      await login(email, password);
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  // Refresh access token
  const refreshAccessToken = useCallback(async (): Promise<void> => {
    if (!tokens?.refresh_token) {
      logout();
      return Promise.resolve();
    }

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refresh_token: tokens.refresh_token })
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const newTokens: AuthTokens = await response.json();
      setTokens(newTokens);
      localStorage.setItem('auth_tokens', JSON.stringify(newTokens));

      // Fetch user data with new token
      await fetchCurrentUser(newTokens.access_token, { onUnauthorized: async () => logout() });
    } catch (error) {
      console.error('Token refresh error:', error);
      logout();
    }
  }, [fetchCurrentUser, logout, tokens?.refresh_token]);

  // Load tokens from localStorage on mount
  useEffect(() => {
    const storedTokens = localStorage.getItem('auth_tokens');
    if (storedTokens) {
      try {
        const parsedTokens = JSON.parse(storedTokens);
        setTokens(parsedTokens);
        fetchCurrentUser(parsedTokens.access_token, { onUnauthorized: refreshAccessToken });
      } catch (error) {
        console.error('Invalid auth tokens in localStorage:', error);
        localStorage.removeItem('auth_tokens');
        setIsLoading(false);
      }
    } else {
      setIsLoading(false);
    }
  }, [fetchCurrentUser, refreshAccessToken]);

  const value: AuthContextType = {
    user,
    tokens,
    isAuthenticated: !!user && !!tokens,
    isLoading,
    login,
    register,
    logout,
    refreshAccessToken
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

// Helper function to get access token
export function getAccessToken(): string | null {
  const stored = localStorage.getItem('auth_tokens');
  if (stored) {
    const tokens = JSON.parse(stored);
    return tokens.access_token;
  }
  return null;
}
