'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { User, AuthTokens, LoginCredentials, RegisterData, AuthState } from './types';
import { authApi } from './api';
import { tokenStorage } from './storage';

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider with React Context for managing authentication state
 * Validates: Requirements 1.2, 1.5
 */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    tokens: null,
    isAuthenticated: false,
    isLoading: true,
  });

  // Automatic token refresh logic
  const refreshAuth = useCallback(async () => {
    const tokens = tokenStorage.getTokens();
    
    if (!tokens?.refresh) {
      setAuthState({
        user: null,
        tokens: null,
        isAuthenticated: false,
        isLoading: false,
      });
      return;
    }

    try {
      // Refresh the access token
      const newTokens = await authApi.refreshToken(tokens.refresh);
      tokenStorage.setTokens(newTokens);

      // Get current user
      const user = await authApi.getCurrentUser();

      setAuthState({
        user,
        tokens: newTokens,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      // If refresh fails, clear tokens and log out
      tokenStorage.clearTokens();
      setAuthState({
        user: null,
        tokens: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  }, []);

  // Initialize auth state on mount
  useEffect(() => {
    refreshAuth();
  }, [refreshAuth]);

  // Set up automatic token refresh every 14 minutes (tokens typically expire in 15 minutes)
  useEffect(() => {
    if (!authState.isAuthenticated) return;

    const refreshInterval = setInterval(() => {
      refreshAuth();
    }, 14 * 60 * 1000); // 14 minutes

    return () => clearInterval(refreshInterval);
  }, [authState.isAuthenticated, refreshAuth]);

  const login = useCallback(async (credentials: LoginCredentials) => {
    try {
      const { user, tokens } = await authApi.login(credentials);
      
      tokenStorage.setTokens(tokens);
      
      setAuthState({
        user,
        tokens,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      throw error;
    }
  }, []);

  const register = useCallback(async (data: RegisterData) => {
    try {
      const { user, tokens } = await authApi.register(data);
      
      tokenStorage.setTokens(tokens);
      
      setAuthState({
        user,
        tokens,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      throw error;
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch (error) {
      // Continue with logout even if API call fails
      console.error('Logout API call failed:', error);
    } finally {
      tokenStorage.clearTokens();
      setAuthState({
        user: null,
        tokens: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        ...authState,
        login,
        register,
        logout,
        refreshAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

/**
 * useAuth hook for accessing auth state
 * Validates: Requirements 1.2, 1.5
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
