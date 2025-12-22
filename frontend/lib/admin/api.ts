/**
 * Admin API client for VEETSSUITES platform
 */

import { apiClient } from '../auth/api';

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: 'student' | 'instructor' | 'pharmacist' | 'admin';
  is_active: boolean;
  date_joined: string;
  last_login: string | null;
}

export interface Analytics {
  users: {
    total: number;
    active: number;
    new_30d: number;
    new_7d: number;
    by_role: Record<string, number>;
    growth: Array<{ date: string; new_users: number }>;
  };
  courses: {
    total: number;
    published: number;
    top_courses: Array<{
      id: number;
      title: string;
      instructor: string;
      enrollment_count: number;
      price: number;
      currency: string;
    }>;
  };
  enrollments: {
    total: number;
    completed: number;
    pending: number;
    failed: number;
    new_30d: number;
    new_7d: number;
  };
  revenue: {
    total: number;
    last_30d: number;
    last_7d: number;
    by_provider: Array<{
      provider: string;
      count: number;
      revenue: number;
    }>;
  };
  exams: {
    total_attempts: number;
    completed: number;
    attempts_30d: number;
  };
}

export interface SystemHealth {
  status: 'healthy' | 'warning' | 'unhealthy';
  timestamp: string;
  checks: Record<string, {
    status: string;
    message?: string;
    [key: string]: any;
  }>;
}

export const adminApi = {
  // User Management
  async getUsers(params?: {
    role?: string;
    is_active?: boolean;
    search?: string;
    page?: number;
  }) {
    const searchParams = new URLSearchParams();
    if (params?.role) searchParams.append('role', params.role);
    if (params?.is_active !== undefined) searchParams.append('is_active', params.is_active.toString());
    if (params?.search) searchParams.append('search', params.search);
    if (params?.page) searchParams.append('page', params.page.toString());

    const response = await apiClient.get(`/accounts/admin/users/?${searchParams}`);
    return response.data;
  },

  async updateUser(userId: number, data: { role?: string; is_active?: boolean }) {
    const response = await apiClient.patch(`/accounts/admin/users/${userId}/`, data);
    return response.data;
  },

  // Analytics
  async getAnalytics(): Promise<Analytics> {
    const response = await apiClient.get('/accounts/admin/analytics/');
    return response.data;
  },

  // System Health
  async getSystemHealth(): Promise<SystemHealth> {
    const response = await apiClient.get('/accounts/admin/health/');
    return response.data;
  },

  // MCQ Import
  async importMCQs(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/exams/questions/import/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};