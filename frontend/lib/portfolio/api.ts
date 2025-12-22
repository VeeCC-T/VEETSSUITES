import axios from 'axios';
import { tokenStorage } from '@/lib/auth/storage';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = tokenStorage.getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface Portfolio {
  id: number;
  user: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
  };
  cv_file: string;
  cv_file_url: string | null;
  parsed_content: any;
  is_public: boolean;
  public_url: string;
  created_at: string;
  updated_at: string;
}

export interface PortfolioUploadData {
  cv_file: File;
  is_public: boolean;
}

export interface PortfolioUpdateData {
  cv_file?: File;
  is_public?: boolean;
}

/**
 * Portfolio API functions
 * Validates: Requirements 3.1, 3.2, 3.3, 3.4
 */
export const portfolioApi = {
  async uploadPortfolio(data: PortfolioUploadData): Promise<Portfolio> {
    const formData = new FormData();
    formData.append('cv_file', data.cv_file);
    formData.append('is_public', data.is_public.toString());

    const response = await api.post('/api/portfolio/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getMyPortfolio(): Promise<Portfolio> {
    const response = await api.get('/api/portfolio/me/');
    return response.data;
  },

  async getPortfolio(userId: number): Promise<Portfolio> {
    const response = await api.get(`/api/portfolio/${userId}/`);
    return response.data;
  },

  async updatePortfolio(userId: number, data: PortfolioUpdateData): Promise<Portfolio> {
    const formData = new FormData();
    
    if (data.cv_file) {
      formData.append('cv_file', data.cv_file);
    }
    
    if (data.is_public !== undefined) {
      formData.append('is_public', data.is_public.toString());
    }

    const response = await api.put(`/api/portfolio/${userId}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async deletePortfolio(userId: number): Promise<void> {
    await api.delete(`/api/portfolio/${userId}/`);
  },
};