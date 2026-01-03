'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'student' | 'instructor' | 'admin';
  redirectTo?: string;
}

/**
 * ProtectedRoute HOC for route protection based on authentication and roles
 * Validates: Requirements 1.4, 2.3
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
  redirectTo = '/auth-demo',
}) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        router.push(redirectTo);
        return;
      }

      if (requiredRole && user?.role !== requiredRole) {
        // Check role hierarchy: admin > instructor > student
        const roleHierarchy = { student: 0, instructor: 1, admin: 2 };
        const userRoleLevel = roleHierarchy[user?.role || 'student'];
        const requiredRoleLevel = roleHierarchy[requiredRole];

        if (userRoleLevel < requiredRoleLevel) {
          router.push('/unauthorized');
        }
      }
    }
  }, [isAuthenticated, isLoading, user, requiredRole, redirectTo, router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  if (requiredRole && user?.role !== requiredRole) {
    const roleHierarchy = { student: 0, instructor: 1, admin: 2 };
    const userRoleLevel = roleHierarchy[user?.role || 'student'];
    const requiredRoleLevel = roleHierarchy[requiredRole];

    if (userRoleLevel < requiredRoleLevel) {
      return null;
    }
  }

  return <>{children}</>;
};
