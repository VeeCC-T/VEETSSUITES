'use client';

import React, { useState, useEffect } from 'react';
import { Card, Button, Modal } from '@/components/ui';
import { hub3660Api, type Course } from '@/lib/hub3660';
import { useAuth } from '@/lib/auth';
import EnrollmentCheckout from './EnrollmentCheckout';
import SessionList from './SessionList';

interface CourseDetailProps {
  course: Course;
  onEnroll?: (course: Course) => void;
  onBack?: () => void;
}

export default function CourseDetail({ course, onBack }: CourseDetailProps) {
  const [error, setError] = useState<string | null>(null);
  const [showEnrollModal, setShowEnrollModal] = useState(false);
  const [showCheckout, setShowCheckout] = useState(false);
  
  const { user } = useAuth();

  const handleEnroll = () => {
    setShowEnrollModal(false);
    setShowCheckout(true);
  };

  const handleEnrollmentSuccess = () => {
    // Refresh the page to show updated enrollment status
    window.location.reload();
  };

  const handleEnrollmentError = (errorMessage: string) => {
    setError(errorMessage);
  };

  const formatPrice = (price: string, currency: string) => {
    const numPrice = parseFloat(price);
    if (numPrice === 0) {
      return 'Free';
    }
    return `${currency} ${numPrice.toFixed(2)}`;
  };

  const getEnrollmentCTA = () => {
    if (!user) {
      return {
        text: 'Login to Enroll',
        disabled: false,
        variant: 'primary' as const
      };
    }

    if (course.is_enrolled) {
      return {
        text: 'Already Enrolled',
        disabled: true,
        variant: 'secondary' as const
      };
    }

    if (course.enrollment_status === 'pending') {
      return {
        text: 'Enrollment Pending',
        disabled: true,
        variant: 'secondary' as const
      };
    }

    const price = parseFloat(course.price);
    return {
      text: price === 0 ? 'Enroll for Free' : `Enroll for ${formatPrice(course.price, course.currency)}`,
      disabled: false,
      variant: 'primary' as const
    };
  };

  const enrollmentCTA = getEnrollmentCTA();

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back Button */}
      {onBack && (
        <button
          onClick={onBack}
          className="flex items-center text-blue-600 hover:text-blue-800 mb-6 transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Catalog
        </button>
      )}

      {/* Course Header */}
      <Card className="mb-8">
        <div className="p-8">
          <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">{course.title}</h1>
              
              <div className="flex flex-wrap items-center gap-4 mb-6 text-sm text-gray-600">
                <div className="flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  Instructor: {course.instructor_name}
                </div>
                
                <div className="flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                  </svg>
                  {course.enrollment_count} students enrolled
                </div>

                {course.is_enrolled && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    ✓ Enrolled
                  </span>
                )}
              </div>

              <p className="text-gray-700 text-lg leading-relaxed">{course.description}</p>
            </div>

            <div className="lg:w-80">
              <Card className="bg-gray-50">
                <div className="p-6">
                  <div className="text-center mb-6">
                    <div className="text-3xl font-bold text-blue-600 mb-2">
                      {formatPrice(course.price, course.currency)}
                    </div>
                    {parseFloat(course.price) > 0 && (
                      <p className="text-sm text-gray-600">One-time payment</p>
                    )}
                  </div>

                  <Button
                    onClick={() => {
                      if (!user) {
                        // Redirect to login
                        window.location.href = '/auth-demo';
                        return;
                      }
                      if (!course.is_enrolled && course.enrollment_status !== 'pending') {
                        setShowEnrollModal(true);
                      }
                    }}
                    className="w-full mb-4"
                    variant={enrollmentCTA.variant}
                    disabled={enrollmentCTA.disabled}
                  >
                    {enrollmentCTA.text}
                  </Button>

                  {error && (
                    <div className="text-red-600 text-sm text-center mb-4">
                      {error}
                    </div>
                  )}

                  <div className="text-sm text-gray-600 space-y-2">
                    <div className="flex items-center">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      Live Zoom sessions
                    </div>
                    <div className="flex items-center">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h4a1 1 0 011 1v1a1 1 0 01-1 1v9a2 2 0 01-2 2H5a2 2 0 01-2-2V7a1 1 0 01-1-1V5a1 1 0 011-1h4z" />
                      </svg>
                      Session recordings
                    </div>
                    <div className="flex items-center">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Lifetime access
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </Card>

      {/* Course Sessions */}
      {course.is_enrolled && (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Course Sessions</h2>
          <SessionList courseId={course.id} />
        </div>
      )}

      {/* Enrollment Confirmation Modal */}
      <Modal
        isOpen={showEnrollModal}
        onClose={() => setShowEnrollModal(false)}
        title="Confirm Enrollment"
      >
        <div className="p-6">
          <p className="text-gray-700 mb-6">
            Are you sure you want to enroll in <strong>{course.title}</strong>?
          </p>
          
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Course Price:</span>
              <span className="font-bold text-lg">
                {formatPrice(course.price, course.currency)}
              </span>
            </div>
          </div>

          {error && (
            <div className="text-red-600 text-sm mb-4">
              {error}
            </div>
          )}

          <div className="flex gap-3">
            <Button
              onClick={() => setShowEnrollModal(false)}
              variant="secondary"
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={handleEnroll}
              className="flex-1"
            >
              Confirm Enrollment
            </Button>
          </div>
        </div>
      </Modal>

      {/* Enrollment Checkout Flow */}
      <EnrollmentCheckout
        course={course}
        isOpen={showCheckout}
        onClose={() => setShowCheckout(false)}
        onSuccess={handleEnrollmentSuccess}
        onError={handleEnrollmentError}
      />
    </div>
  );
}