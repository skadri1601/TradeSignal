import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from '../ProtectedRoute';
import { AuthContext } from '../../contexts/AuthContext';
import type { AuthContextType } from '../../contexts/AuthContext';

// Mock user object
const mockUser = {
  id: 1,
  email: 'test@example.com',
  username: 'testuser',
  is_active: true,
  is_verified: true,
  is_superuser: false,
  stripe_subscription_tier: 'free',
};

const mockSuperUser = {
  ...mockUser,
  is_superuser: true,
};

// Helper to render with auth context
const renderWithAuth = (
  ui: React.ReactElement,
  {
    user = null,
    loading = false,
    isAuthenticated = false,
  }: {
    user?: typeof mockUser | null;
    loading?: boolean;
    isAuthenticated?: boolean;
  } = {}
) => {
  const mockAuthContext: AuthContextType = {
    user,
    tokens: null,
    isLoading: loading,
    isAuthenticated,
    isDegraded: false,
    syncError: null,
    autoRetryCountdown: 0,
    retrySync: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
    register: vi.fn(),
    refreshAccessToken: vi.fn(),
  };

  return render(
    <AuthContext.Provider value={mockAuthContext}>
      <MemoryRouter>
        {ui}
      </MemoryRouter>
    </AuthContext.Provider>
  );
};

describe('ProtectedRoute', () => {
  it('shows loading spinner while loading', () => {
    renderWithAuth(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>,
      { loading: true }
    );

    // Should show loading, not content
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('redirects to login when not authenticated', () => {
    renderWithAuth(
      <Routes>
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <div>Protected Content</div>
            </ProtectedRoute>
          }
        />
        <Route path="/login" element={<div>Login Page</div>} />
      </Routes>,
      { isAuthenticated: false }
    );

    // Content should not be visible
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('shows content when authenticated', () => {
    renderWithAuth(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>,
      { user: mockUser, isAuthenticated: true }
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('blocks non-superusers from superuser routes', () => {
    renderWithAuth(
      <Routes>
        <Route
          path="/"
          element={
            <ProtectedRoute requireSuperuser>
              <div>Admin Content</div>
            </ProtectedRoute>
          }
        />
      </Routes>,
      { user: mockUser, isAuthenticated: true }
    );

    // Should not show admin content
    expect(screen.queryByText('Admin Content')).not.toBeInTheDocument();
  });

  it('allows superusers to access superuser routes', () => {
    renderWithAuth(
      <ProtectedRoute requireSuperuser>
        <div>Admin Content</div>
      </ProtectedRoute>,
      { user: mockSuperUser, isAuthenticated: true }
    );

    expect(screen.getByText('Admin Content')).toBeInTheDocument();
  });
});
