'use client';

import React from 'react';
import { AdminDashboard } from '../../components/admin';
import { ProtectedRoute } from '../../components/auth/ProtectedRoute';
import { SEO } from '../../components/seo/SEO';

export default function AdminPage() {
  return (
    <ProtectedRoute requiredRole="admin">
      <SEO
        title="Admin Dashboard - VEETSSUITES"
        description="Admin dashboard for managing users, courses, and system health"
        noIndex={true}
      />
      <div className="min-h-screen bg-gray-50">
        <AdminDashboard />
      </div>
    </ProtectedRoute>
  );
}