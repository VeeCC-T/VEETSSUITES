import { AuthTokens } from './types';

const ACCESS_TOKEN_KEY = 'veetssuites_access_token';
const REFRESH_TOKEN_KEY = 'veetssuites_refresh_token';

/**
 * Token storage utilities for localStorage
 * Validates: Requirements 1.2, 1.5
 */
export const tokenStorage = {
  getTokens(): AuthTokens | null {
    if (typeof window === 'undefined') return null;
    
    const access = localStorage.getItem(ACCESS_TOKEN_KEY);
    const refresh = localStorage.getItem(REFRESH_TOKEN_KEY);
    
    if (access && refresh) {
      return { access, refresh };
    }
    
    return null;
  },

  setTokens(tokens: AuthTokens): void {
    if (typeof window === 'undefined') return;
    
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh);
  },

  clearTokens(): void {
    if (typeof window === 'undefined') return;
    
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },

  getAccessToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  },

  getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  },
};

/**
 * Get the current auth token for API requests
 */
export const getAuthToken = (): string | null => {
  return tokenStorage.getAccessToken();
};
