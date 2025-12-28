'use client';

import React, { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Card, Button } from '@/components/ui';
import { hub3660Api, type Course } from '@/lib/hub3660';
import { useAuth } from '@/lib/auth';

export function EnrollmentSuccessContent() {
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const searchParams = useSearchParams();
  const router = useRouter();
  const { user } = useAuth();
  
  const courseId = searchParams.get('course_id');

  useEffect(() => {
    if (!user) {
      router.push('/auth-demo');
      return;
    }

    if (!courseId) {
      setError('Course ID not provided');
      setLoading(false);
      return;
    }

    loadCourse();
  }, [user, courseId, router]);

  const loadCourse = async () => {
    try {
      setLoading(true);
      const courseData = await hub3660Api.getCourse(parseInt(courseId!));
      setCourse(courseData);
    } catch (err) {
      console.error('Failed to load course:', err);
      setError('Failed to load course information');
    } finally {
      setLoading(false);
    }
  };

  const handleContinueToCourse = () => {
    if (course) {
      router.push(`/hub3660/courses/${course.id}`);
    }
  };

  const handleBackToCatalog = () => {
    router.push('/hub3660');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading course information...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="max-w-md mx-auto">
          <div className="p-8 text-center">
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h1 className="text-xl font-semibold text-gray-900 mb-2">Error</h1>
            <p className="text-gray-600 mb-6">{error}</p>
            <Button onClick={handleBackToCatalog} className="w-full">
              Back to Course Catalog
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <Card className="max-w-lg mx-auto">
        <div className="p-8 text-center">
          {/* Success Icon */}
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>

          {/* Success Message */}
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Enrollment Successful!
          </h1>
          <p className="text-gray-600 mb-6">
            Congratulations! You have successfully enrolled in{' '}
            <span className="font-semibold text-gray-900">{course?.title}</span>.
          </p>

          {/* Course Info */}
          {course && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 text-left">
              <h3 className="font-semibold text-blue-900 mb-2">What's Next?</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li className="flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Access course materials and sessions
                </li>
                <li className="flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Join live Zoom sessions when scheduled
                </li>
                <li className="flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Watch recorded sessions anytime
                </li>
              </ul>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              onClick={handleBackToCatalog}
              variant="secondary"
              className="flex-1"
            >
              Browse More Courses
            </Button>
            <Button
              onClick={handleContinueToCourse}
              className="flex-1"
            >
              Go to Course
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}