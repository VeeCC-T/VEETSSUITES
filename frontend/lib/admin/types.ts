/**
 * Admin dashboard types
 */

export interface DashboardMetrics {
  totalUsers: number;
  activeUsers: number;
  totalCourses: number;
  totalRevenue: number;
  newUsersThisMonth: number;
  enrollmentsThisMonth: number;
}

export interface UserRole {
  value: 'student' | 'instructor' | 'pharmacist' | 'admin';
  label: string;
}

export const USER_ROLES: UserRole[] = [
  { value: 'student', label: 'Student' },
  { value: 'instructor', label: 'Instructor' },
  { value: 'pharmacist', label: 'Pharmacist' },
  { value: 'admin', label: 'Admin' },
];

export interface HealthStatus {
  status: 'healthy' | 'warning' | 'unhealthy' | 'unknown';
  color: string;
  icon: string;
}

export const HEALTH_STATUS_MAP: Record<string, HealthStatus> = {
  healthy: { status: 'healthy', color: 'text-green-600', icon: '✓' },
  warning: { status: 'warning', color: 'text-yellow-600', icon: '⚠' },
  unhealthy: { status: 'unhealthy', color: 'text-red-600', icon: '✗' },
  unknown: { status: 'unknown', color: 'text-gray-600', icon: '?' },
};