/**
 * Enrollment Statistics Component
 * 
 * Displays enrollment statistics and key metrics for instructors.
 * Requirements: 5.1
 */

'use client';

import React from 'react';
import { Card } from '@/components/ui/Card';
import type { Course } from '@/lib/hub3660/types';

interface EnrollmentStatsProps {
  courses: Course[];
  className?: string;
}

export function EnrollmentStats({ courses, className = '' }: EnrollmentStatsProps) {
  // Calculate statistics
  const totalCourses = courses.length;
  const publishedCourses = courses.filter(course => course.is_published).length;
  const totalEnrollments = courses.reduce((sum, course) => sum + course.enrollment_count, 0);
  const totalSessions = courses.reduce((sum, course) => sum + (course.sessions?.length || 0), 0);
  
  // Calculate revenue (approximate, since we don't have actual payment data)
  const estimatedRevenue = courses.reduce((sum, course) => {
    const price = parseFloat(course.price) || 0;
    return sum + (price * course.enrollment_count);
  }, 0);

  // Find most popular course
  const mostPopularCourse = courses.reduce((prev, current) => {
    return (current.enrollment_count > prev.enrollment_count) ? current : prev;
  }, courses[0]);

  const stats = [
    {
      title: 'Total Courses',
      value: totalCourses,
      subtitle: `${publishedCourses} published`,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      ),
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      title: 'Total Students',
      value: totalEnrollments,
      subtitle: 'across all courses',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
        </svg>
      ),
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      title: 'Scheduled Sessions',
      value: totalSessions,
      subtitle: 'live sessions planned',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      ),
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      title: 'Estimated Revenue',
      value: `$${estimatedRevenue.toFixed(2)}`,
      subtitle: 'from enrollments',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
        </svg>
      ),
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100'
    }
  ];

  if (totalCourses === 0) {
    return (
      <div className={`space-y-4 ${className}`}>
        <h2 className="text-lg font-semibold text-gray-900">Statistics</h2>
        <Card className="p-6 text-center">
          <div className="text-gray-400 mb-2">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <p className="text-gray-600">Create your first course to see statistics</p>
        </Card>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      <h2 className="text-lg font-semibold text-gray-900">Statistics Overview</h2>
      
      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => (
          <Card key={index} className="p-4">
            <div className="flex items-center">
              <div className={`p-2 rounded-lg ${stat.bgColor} ${stat.color}`}>
                {stat.icon}
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-xs text-gray-500">{stat.subtitle}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Additional Insights */}
      {mostPopularCourse && totalEnrollments > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card className="p-4">
            <h3 className="text-sm font-medium text-gray-600 mb-2">Most Popular Course</h3>
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="font-semibold text-gray-900 line-clamp-1">{mostPopularCourse.title}</p>
                <p className="text-sm text-gray-600">
                  {mostPopularCourse.enrollment_count} student{mostPopularCourse.enrollment_count !== 1 ? 's' : ''} enrolled
                </p>
              </div>
              <div className="ml-4">
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                  mostPopularCourse.is_published 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {mostPopularCourse.is_published ? 'Published' : 'Draft'}
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="text-sm font-medium text-gray-600 mb-2">Course Performance</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Average enrollments per course:</span>
                <span className="font-medium text-gray-900">
                  {publishedCourses > 0 ? (totalEnrollments / publishedCourses).toFixed(1) : '0'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Published courses:</span>
                <span className="font-medium text-gray-900">
                  {publishedCourses} of {totalCourses} ({totalCourses > 0 ? Math.round((publishedCourses / totalCourses) * 100) : 0}%)
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Sessions per course:</span>
                <span className="font-medium text-gray-900">
                  {totalCourses > 0 ? (totalSessions / totalCourses).toFixed(1) : '0'}
                </span>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}