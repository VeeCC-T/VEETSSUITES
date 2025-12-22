/**
 * Instructor Dashboard Page
 * 
 * Main page for instructors to manage their courses and sessions.
 * Requirements: 5.1, 7.1
 */

import { Metadata } from 'next';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { InstructorDashboard } from '@/components/hub3660/InstructorDashboard';
import { SEO } from '@/components/seo/SEO';

export const metadata: Metadata = {
  title: 'Instructor Dashboard - HUB3660 | VEETSSUITES',
  description: 'Manage your courses, schedule sessions, and track student enrollments on HUB3660.',
  keywords: ['instructor', 'dashboard', 'course management', 'HUB3660', 'teaching'],
  openGraph: {
    title: 'Instructor Dashboard - HUB3660',
    description: 'Manage your courses, schedule sessions, and track student enrollments on HUB3660.',
    type: 'website',
  },
  twitter: {
    card: 'summary',
    title: 'Instructor Dashboard - HUB3660',
    description: 'Manage your courses, schedule sessions, and track student enrollments on HUB3660.',
  },
};

export default function InstructorDashboardPage() {
  return (
    <>
      <SEO
        title="Instructor Dashboard - HUB3660"
        description="Manage your courses, schedule sessions, and track student enrollments on HUB3660."
        keywords={['instructor', 'dashboard', 'course management', 'HUB3660', 'teaching']}
        ogType="website"
      />
      
      <ProtectedRoute requiredRole="instructor">
        <div className="min-h-screen bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <InstructorDashboard />
          </div>
        </div>
      </ProtectedRoute>
    </>
  );
}