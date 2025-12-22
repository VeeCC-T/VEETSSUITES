/**
 * Instructor Dashboard Component
 * 
 * Main dashboard for instructors to manage their courses, sessions, and view statistics.
 * Requirements: 5.1, 7.1
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { useToast } from '@/components/ui/Toast';
import { CourseCreateForm } from './CourseCreateForm';
import { CourseEditForm } from './CourseEditForm';
import SessionScheduleForm from './SessionScheduleForm';
import { EnrollmentStats } from './EnrollmentStats';
import { hub3660Api } from '@/lib/hub3660/api';
import type { Course, Session } from '@/lib/hub3660/types';

interface InstructorDashboardProps {
  className?: string;
}

export function InstructorDashboard({ className = '' }: InstructorDashboardProps) {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showSessionModal, setShowSessionModal] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const { addToast } = useToast();

  useEffect(() => {
    loadInstructorCourses();
  }, []);

  const loadInstructorCourses = async () => {
    try {
      setLoading(true);
      setError(null);
      const instructorCourses = await hub3660Api.getInstructorCourses();
      setCourses(instructorCourses);
    } catch (err) {
      console.error('Failed to load instructor courses:', err);
      setError('Failed to load your courses. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCourse = () => {
    setShowCreateModal(true);
  };

  const handleEditCourse = (course: Course) => {
    setSelectedCourse(course);
    setShowEditModal(true);
  };

  const handleScheduleSession = (course: Course) => {
    setSelectedCourse(course);
    setShowSessionModal(true);
  };

  const handleCourseCreated = (newCourse: Course) => {
    setCourses(prev => [newCourse, ...prev]);
    setShowCreateModal(false);
    addToast('Course created successfully!', 'success');
  };

  const handleCourseUpdated = (updatedCourse: Course) => {
    setCourses(prev => prev.map(course => 
      course.id === updatedCourse.id ? updatedCourse : course
    ));
    setShowEditModal(false);
    setSelectedCourse(null);
    addToast('Course updated successfully!', 'success');
  };

  const handleSessionCreated = (newSession: Session) => {
    // Refresh courses to get updated session data
    loadInstructorCourses();
    setShowSessionModal(false);
    setSelectedCourse(null);
    addToast('Session scheduled successfully!', 'success');
  };

  const handleCloseModals = () => {
    setShowCreateModal(false);
    setShowEditModal(false);
    setShowSessionModal(false);
    setSelectedCourse(null);
  };

  if (loading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-64 bg-gray-200 rounded-2xl"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`space-y-6 ${className}`}>
        <Card className="p-6 text-center">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Dashboard</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={loadInstructorCourses}>
            Try Again
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Instructor Dashboard</h1>
          <p className="text-gray-600">Manage your courses and sessions</p>
        </div>
        <Button onClick={handleCreateCourse} className="sm:w-auto">
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Create Course
        </Button>
      </div>

      {/* Statistics Overview */}
      <EnrollmentStats courses={courses} />

      {/* Courses Grid */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Your Courses</h2>
        
        {courses.length === 0 ? (
          <Card className="p-8 text-center">
            <div className="text-gray-400 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Courses Yet</h3>
            <p className="text-gray-600 mb-4">Create your first course to get started with teaching on HUB3660.</p>
            <Button onClick={handleCreateCourse}>
              Create Your First Course
            </Button>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map(course => (
              <Card key={course.id} className="p-6 hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                      {course.title}
                    </h3>
                    <p className="text-gray-600 text-sm line-clamp-3 mb-3">
                      {course.description}
                    </p>
                  </div>
                  <div className="flex items-center space-x-1 ml-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEditCourse(course)}
                      className="p-2"
                      ariaLabel="Edit course"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </Button>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Price:</span>
                    <span className="font-medium text-gray-900">
                      {parseFloat(course.price) === 0 ? 'Free' : `${course.currency} ${course.price}`}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Enrolled:</span>
                    <span className="font-medium text-gray-900">
                      {course.enrollment_count} student{course.enrollment_count !== 1 ? 's' : ''}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Sessions:</span>
                    <span className="font-medium text-gray-900">
                      {course.sessions?.length || 0} scheduled
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Status:</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      course.is_published 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {course.is_published ? 'Published' : 'Draft'}
                    </span>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-200">
                  <Button
                    onClick={() => handleScheduleSession(course)}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    Schedule Session
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Modals */}
      <Modal
        isOpen={showCreateModal}
        onClose={handleCloseModals}
        title="Create New Course"
        className="max-w-2xl"
      >
        <CourseCreateForm
          onSuccess={handleCourseCreated}
          onCancel={handleCloseModals}
        />
      </Modal>

      <Modal
        isOpen={showEditModal}
        onClose={handleCloseModals}
        title="Edit Course"
        className="max-w-2xl"
      >
        {selectedCourse && (
          <CourseEditForm
            course={selectedCourse}
            onSuccess={handleCourseUpdated}
            onCancel={handleCloseModals}
          />
        )}
      </Modal>

      <Modal
        isOpen={showSessionModal}
        onClose={handleCloseModals}
        title="Schedule Session"
        className="max-w-2xl"
      >
        {selectedCourse && (
          <SessionScheduleForm
            course={selectedCourse}
            onSuccess={handleSessionCreated}
            onCancel={handleCloseModals}
          />
        )}
      </Modal>


    </div>
  );
}