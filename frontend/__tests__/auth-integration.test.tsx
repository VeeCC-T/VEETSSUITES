/**
 * Integration tests for authentication flow
 * Validates: Requirements 1.1, 1.2, 1.5
 * 
 * Tests:
 * - Complete registration flow
 * - Login and token storage
 * - Protected route access
 * - Logout and token cleanup
 */

import '@testing-library/jest-dom';
import React from 'react';
import { render, act } from '@testing-library/react';
import { screen, waitFor, fireEvent } from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from '@/lib/auth/AuthContext';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import * as authApiModule from '@/lib/auth/api';

// Mock Next.js router
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
}));

// Mock the auth API module
jest.mock('@/lib/auth/api', () => ({
  authApi: {
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
    getCurrentUser: jest.fn(),
    refreshToken: jest.fn(),
    requestPasswordReset: jest.fn(),
    confirmPasswordReset: jest.fn(),
  },
}));

// Test component that uses auth
const TestAuthComponent = () => {
  const { user, isAuthenticated, isLoading, login, register, logout } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  const handleLogin = async () => {
    try {
      await login({ email: 'test@example.com', password: 'password123' });
    } catch (error) {
      // Error handled - test can verify auth state remains unchanged
    }
  };

  const handleRegister = async () => {
    try {
      await register({
        email: 'newuser@example.com',
        password: 'password123',
        name: 'Test User',
      });
    } catch (error) {
      // Error handled - test can verify auth state remains unchanged
    }
  };

  return (
    <div>
      <div data-testid="auth-status">
        {isAuthenticated ? 'Authenticated' : 'Not Authenticated'}
      </div>
      {user && (
        <div>
          <div data-testid="user-email">{user.email}</div>
          <div data-testid="user-role">{user.role}</div>
        </div>
      )}
      <button data-testid="login-btn" onClick={handleLogin}>
        Login
      </button>
      <button data-testid="register-btn" onClick={handleRegister}>
        Register
      </button>
      <button data-testid="logout-btn" onClick={logout}>
        Logout
      </button>
    </div>
  );
};

// Test component for protected routes
const ProtectedContent = () => {
  return <div data-testid="protected-content">Protected Content</div>;
};

describe('Authentication Integration Tests', () => {
  const mockAuthApi = authApiModule.authApi as jest.Mocked<typeof authApiModule.authApi>;

  beforeEach(() => {
    // Clear localStorage
    localStorage.clear();
    
    // Reset all mocks
    jest.clearAllMocks();
    mockPush.mockClear();
  });

  describe('Registration Flow', () => {
    it('should complete registration flow successfully', async () => {
      // Mock registration API response
      const mockUser = {
        id: 1,
        email: 'newuser@example.com',
        name: 'Test User',
        role: 'student' as const,
      };
      const mockTokens = {
        access: 'mock-access-token',
        refresh: 'mock-refresh-token',
      };

      mockAuthApi.register.mockResolvedValue({
        user: mockUser,
        tokens: mockTokens,
      });

      // Render component
      render(
        <AuthProvider>
          <TestAuthComponent />
        </AuthProvider>
      );

      // Wait for initial loading to complete
      await waitFor(() => {
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      });

      // Initially not authenticated
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');

      // Click register button
      const registerBtn = screen.getByTestId('register-btn');
      await act(async () => {
        await userEvent.click(registerBtn);
      });

      // Wait for registration to complete
      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      });

      // Verify user data is displayed
      expect(screen.getByTestId('user-email')).toHaveTextContent('newuser@example.com');
      expect(screen.getByTestId('user-role')).toHaveTextContent('student');

      // Verify tokens are stored in localStorage
      expect(localStorage.getItem('veetssuites_access_token')).toBe('mock-access-token');
      expect(localStorage.getItem('veetssuites_refresh_token')).toBe('mock-refresh-token');
    });

    it('should handle registration errors', async () => {
      // Suppress console.error for this test
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      // Mock registration API error
      mockAuthApi.register.mockRejectedValueOnce(new Error('User with this email already exists.'));

      render(
        <AuthProvider>
          <TestAuthComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      });

      const registerBtn = screen.getByTestId('register-btn');
      
      // Registration should fail
      await userEvent.click(registerBtn);

      // Wait a bit for the error to be processed
      await new Promise(resolve => setTimeout(resolve, 100));

      // Should remain unauthenticated
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
      
      consoleErrorSpy.mockRestore();
    });
  });

  describe('Login and Token Storage', () => {
    it('should complete login flow and store tokens', async () => {
      // Mock login API response
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        name: 'Test User',
        role: 'student' as const,
      };
      const mockTokens = {
        access: 'mock-access-token-login',
        refresh: 'mock-refresh-token-login',
      };

      mockAuthApi.login.mockResolvedValue({
        user: mockUser,
        tokens: mockTokens,
      });

      render(
        <AuthProvider>
          <TestAuthComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      });

      // Click login button
      const loginBtn = screen.getByTestId('login-btn');
      await act(async () => {
        await userEvent.click(loginBtn);
      });

      // Wait for login to complete
      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      });

      // Verify user data
      expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com');

      // Verify tokens are stored
      expect(localStorage.getItem('veetssuites_access_token')).toBe('mock-access-token-login');
      expect(localStorage.getItem('veetssuites_refresh_token')).toBe('mock-refresh-token-login');
    });

    it('should restore session from stored tokens on mount', async () => {
      // Set up stored tokens
      localStorage.setItem('veetssuites_access_token', 'stored-access-token');
      localStorage.setItem('veetssuites_refresh_token', 'stored-refresh-token');

      // Mock token refresh
      mockAuthApi.refreshToken.mockResolvedValue({
        access: 'new-access-token',
        refresh: 'stored-refresh-token',
      });

      // Mock get current user
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        name: 'Test User',
        role: 'student' as const,
      };
      mockAuthApi.getCurrentUser.mockResolvedValue(mockUser);

      render(
        <AuthProvider>
          <TestAuthComponent />
        </AuthProvider>
      );

      // Should restore session
      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      });

      expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com');
    });

    it('should handle invalid credentials', async () => {
      // Suppress console.error for this test
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      // Mock login API error
      mockAuthApi.login.mockRejectedValueOnce(new Error('Invalid email or password'));

      render(
        <AuthProvider>
          <TestAuthComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      });

      const loginBtn = screen.getByTestId('login-btn');
      
      // Login should fail
      await userEvent.click(loginBtn);

      // Wait a bit for the error to be processed
      await new Promise(resolve => setTimeout(resolve, 100));

      // Should remain unauthenticated
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
      
      consoleErrorSpy.mockRestore();
    });
  });

  describe('Protected Route Access', () => {
    it('should allow access to protected routes when authenticated', async () => {
      // Set up authenticated state
      localStorage.setItem('veetssuites_access_token', 'valid-access-token');
      localStorage.setItem('veetssuites_refresh_token', 'valid-refresh-token');

      mockAuthApi.refreshToken.mockResolvedValue({
        access: 'new-access-token',
        refresh: 'valid-refresh-token',
      });
      
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        name: 'Test User',
        role: 'student' as const,
      };
      mockAuthApi.getCurrentUser.mockResolvedValue(mockUser);

      render(
        <AuthProvider>
          <ProtectedRoute>
            <ProtectedContent />
          </ProtectedRoute>
        </AuthProvider>
      );

      // Should show protected content
      await waitFor(() => {
        expect(screen.getByTestId('protected-content')).toBeInTheDocument();
      });
    });

    it('should redirect to login when accessing protected routes unauthenticated', async () => {
      // No tokens in storage
      mockAuthApi.refreshToken.mockRejectedValue(new Error('No refresh token'));

      render(
        <AuthProvider>
          <ProtectedRoute>
            <ProtectedContent />
          </ProtectedRoute>
        </AuthProvider>
      );

      // Should not show protected content
      await waitFor(() => {
        expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
      });

      // Should redirect to login
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/login');
      });
    });

    it('should deny access when token is expired', async () => {
      // Set up expired token
      localStorage.setItem('veetssuites_access_token', 'expired-token');
      localStorage.setItem('veetssuites_refresh_token', 'expired-refresh');

      // Mock refresh failure
      mockAuthApi.refreshToken.mockRejectedValue(new Error('Token is invalid or expired'));

      render(
        <AuthProvider>
          <ProtectedRoute>
            <ProtectedContent />
          </ProtectedRoute>
        </AuthProvider>
      );

      // Should not show protected content
      await waitFor(() => {
        expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
      });

      // Tokens should be cleared
      await waitFor(() => {
        expect(localStorage.getItem('veetssuites_access_token')).toBeNull();
        expect(localStorage.getItem('veetssuites_refresh_token')).toBeNull();
      });
    });
  });

  describe('Logout and Token Cleanup', () => {
    it('should complete logout flow and clear tokens', async () => {
      // Set up authenticated state
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        name: 'Test User',
        role: 'student' as const,
      };
      const mockTokens = {
        access: 'valid-access-token',
        refresh: 'valid-refresh-token',
      };

      mockAuthApi.login.mockResolvedValue({
        user: mockUser,
        tokens: mockTokens,
      });
      mockAuthApi.logout.mockResolvedValue();

      render(
        <AuthProvider>
          <TestAuthComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      });

      // Login first
      const loginBtn = screen.getByTestId('login-btn');
      await act(async () => {
        await userEvent.click(loginBtn);
      });

      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      });

      // Now logout
      const logoutBtn = screen.getByTestId('logout-btn');
      await act(async () => {
        await userEvent.click(logoutBtn);
      });

      // Should be logged out
      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
      });

      // Tokens should be cleared
      expect(localStorage.getItem('veetssuites_access_token')).toBeNull();
      expect(localStorage.getItem('veetssuites_refresh_token')).toBeNull();

      // User data should be cleared
      expect(screen.queryByTestId('user-email')).not.toBeInTheDocument();
    });

    it('should clear tokens even if logout API fails', async () => {
      // Set up authenticated state
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        name: 'Test User',
        role: 'student' as const,
      };
      const mockTokens = {
        access: 'valid-access-token',
        refresh: 'valid-refresh-token',
      };

      mockAuthApi.login.mockResolvedValue({
        user: mockUser,
        tokens: mockTokens,
      });
      
      // Mock logout API failure
      mockAuthApi.logout.mockRejectedValue(new Error('Server error'));

      render(
        <AuthProvider>
          <TestAuthComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      });

      // Login first
      const loginBtn = screen.getByTestId('login-btn');
      await act(async () => {
        await userEvent.click(loginBtn);
      });

      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      });

      // Logout (API will fail but should still clear local state)
      const logoutBtn = screen.getByTestId('logout-btn');
      await act(async () => {
        await userEvent.click(logoutBtn);
      });

      // Should still be logged out locally
      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
      });

      // Tokens should still be cleared
      expect(localStorage.getItem('veetssuites_access_token')).toBeNull();
      expect(localStorage.getItem('veetssuites_refresh_token')).toBeNull();
    });

    it('should invalidate session after logout', async () => {
      // Set up authenticated state
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        name: 'Test User',
        role: 'student' as const,
      };
      const mockTokens = {
        access: 'valid-access-token',
        refresh: 'valid-refresh-token',
      };

      mockAuthApi.login.mockResolvedValue({
        user: mockUser,
        tokens: mockTokens,
      });
      mockAuthApi.logout.mockResolvedValue();

      render(
        <AuthProvider>
          <TestAuthComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      });

      // Login
      const loginBtn = screen.getByTestId('login-btn');
      await act(async () => {
        await userEvent.click(loginBtn);
      });

      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      });

      // Logout
      const logoutBtn = screen.getByTestId('logout-btn');
      await act(async () => {
        await userEvent.click(logoutBtn);
      });

      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
      });

      // Verify logout API was called
      expect(mockAuthApi.logout).toHaveBeenCalled();
    });
  });

  describe('Complete Authentication Journey', () => {
    it('should handle complete user journey: register -> login -> access protected -> logout', async () => {
      // Mock all API calls
      const mockUser = {
        id: 1,
        email: 'journey@example.com',
        name: 'Journey User',
        role: 'student' as const,
      };
      const mockTokens = {
        access: 'journey-access-token',
        refresh: 'journey-refresh-token',
      };

      mockAuthApi.register.mockResolvedValue({
        user: mockUser,
        tokens: mockTokens,
      });
      mockAuthApi.logout.mockResolvedValue();

      // Render both test component and protected route
      const { rerender } = render(
        <AuthProvider>
          <TestAuthComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      });

      // Step 1: Register
      const registerBtn = screen.getByTestId('register-btn');
      await act(async () => {
        await userEvent.click(registerBtn);
      });

      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      });

      // Verify tokens stored
      expect(localStorage.getItem('veetssuites_access_token')).toBe('journey-access-token');

      // Step 2: Access protected content
      rerender(
        <AuthProvider>
          <ProtectedRoute>
            <ProtectedContent />
          </ProtectedRoute>
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('protected-content')).toBeInTheDocument();
      });

      // Step 3: Logout
      rerender(
        <AuthProvider>
          <TestAuthComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('logout-btn')).toBeInTheDocument();
      });

      const logoutBtn = screen.getByTestId('logout-btn');
      await act(async () => {
        await userEvent.click(logoutBtn);
      });

      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
      });

      // Verify tokens cleared
      expect(localStorage.getItem('veetssuites_access_token')).toBeNull();
      expect(localStorage.getItem('veetssuites_refresh_token')).toBeNull();
    });
  });
});
