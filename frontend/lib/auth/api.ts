import axios from 'axios';
import { User, AuthTokens, LoginCredentials, RegisterData } from './types';
import { tokenStorage } from './storage';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const api = apiClient;

// Add token to requests
api.interceptors.request.use((config) => {
  const token = tokenStorage.getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * Authentication API functions
 * Validates: Requirements 1.1, 1.2, 1.3, 1.5
 */
export const authApi = {
  async login(credentials: LoginCredentials): Promise<{ user: User; tokens: AuthTokens }> {
    const response = await api.post('/api/auth/login/', credentials);
    return response.data;
  },

  async register(data: RegisterData): Promise<{ user: User; tokens: AuthTokens }> {
    const response = await api.post('/api/auth/register/', data);
    return response.data;
  },

  async logout(): Promise<void> {
    const refreshToken = tokenStorage.getRefreshToken();
    if (refreshToken) {
      await api.post('/api/auth/logout/', { refresh: refreshToken });
    }
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/api/auth/me/');
    return response.data;
  },

  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    const response = await api.post('/api/auth/token/refresh/', {
      refresh: refreshToken,
    });
    return {
      access: response.data.access,
      refresh: refreshToken,
    };
  },

  async requestPasswordReset(email: string): Promise<void> {
    await api.post('/api/auth/password-reset/', { email });
  },

  async confirmPasswordReset(token: string, password: string): Promise<void> {
    await api.post('/api/auth/password-reset-confirm/', { token, password });
  },
};
