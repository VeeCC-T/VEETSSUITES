/**
 * Session Schedule Form Component
 * 
 * Form for instructors to schedule live Zoom sessions for their courses.
 * Requirements: 7.1
 */

'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { hub3660Api } from '@/lib/hub3660/api';
import type { Course, Session, SessionCreateData } from '@/lib/hub3660/types';

interface SessionScheduleFormProps {
  course: Course;
  onSuccess: (session: Session) => void;
  onCancel: () => void;
}

function SessionScheduleForm({ course, onSuccess, onCancel }: SessionScheduleFormProps) {
  const [formData, setFormData] = useState<SessionCreateData>({
    course: course.id,
    title: '',
    scheduled_at: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Session title is required';
    } else if (formData.title.length > 200) {
      newErrors.title = 'Session title must be 200 characters or less';
    }

    if (!formData.scheduled_at) {
      newErrors.scheduled_at = 'Session date and time is required';
    } else {
      const scheduledDate = new Date(formData.scheduled_at);
      const now = new Date();
      
      if (scheduledDate <= now) {
        newErrors.scheduled_at = 'Session must be scheduled in the future';
      }
      
      // Check if it's at least 1 hour in the future to allow for preparation
      const oneHourFromNow = new Date(now.getTime() + 60 * 60 * 1000);
      if (scheduledDate < oneHourFromNow) {
        newErrors.scheduled_at = 'Session must be scheduled at least 1 hour in advance';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      setErrors({});
      
      const newSession = await hub3660Api.createSession(formData);
      onSuccess(newSession);
    } catch (error: any) {
      console.error('Failed to create session:', error);
      
      if (error.response?.data) {
        // Handle validation errors from backend
        const backendErrors = error.response.data;
        if (typeof backendErrors === 'object') {
          setErrors(backendErrors);
        } else {
          setErrors({ general: 'Failed to schedule session. Please try again.' });
        }
      } else {
        setErrors({ general: 'Failed to schedule session. Please check your connection and try again.' });
      }
    } finally {
      setLoading(false);
    }
  };

  // Get minimum datetime (1 hour from now)
  const getMinDateTime = () => {
    const now = new Date();
    const oneHourFromNow = new Date(now.getTime() + 60 * 60 * 1000);
    return oneHourFromNow.toISOString().slice(0, 16);
  };

  // Format datetime for display
  const formatDateTime = (dateTimeString: string) => {
    if (!dateTimeString) return '';
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZoneName: 'short'
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {errors.general && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{errors.general}</p>
            </div>
          </div>
        </div>
      )}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-blue-800">
              Scheduling session for: <strong>{course.title}</strong>
            </p>
            <p className="text-sm text-blue-700 mt-1">
              A Zoom meeting will be automatically created and all enrolled students will be registered.
            </p>
          </div>
        </div>
      </div>

      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
          Session Title *
        </label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleInputChange}
          className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
            errors.title ? 'border-red-300' : 'border-gray-300'
          }`}
          placeholder="e.g., Introduction to React Hooks"
          maxLength={200}
          required
        />
        {errors.title && (
          <p className="mt-1 text-sm text-red-600">{errors.title}</p>
        )}
        <p className="mt-1 text-sm text-gray-500">
          Choose a descriptive title that helps students understand the session content
        </p>
      </div>

      <div>
        <label htmlFor="scheduled_at" className="block text-sm font-medium text-gray-700 mb-2">
          Session Date & Time *
        </label>
        <input
          type="datetime-local"
          id="scheduled_at"
          name="scheduled_at"
          value={formData.scheduled_at}
          onChange={handleInputChange}
          min={getMinDateTime()}
          className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
            errors.scheduled_at ? 'border-red-300' : 'border-gray-300'
          }`}
          required
        />
        {errors.scheduled_at && (
          <p className="mt-1 text-sm text-red-600">{errors.scheduled_at}</p>
        )}
        {formData.scheduled_at && (
          <p className="mt-1 text-sm text-gray-600">
            Scheduled for: {formatDateTime(formData.scheduled_at)}
          </p>
        )}
        <p className="mt-1 text-sm text-gray-500">
          Sessions must be scheduled at least 1 hour in advance
        </p>
      </div>

      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2">What happens next?</h4>
        <ul className="text-sm text-gray-600 space-y-1">
          <li className="flex items-start">
            <svg className="w-4 h-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            A Zoom meeting will be created automatically
          </li>
          <li className="flex items-start">
            <svg className="w-4 h-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            All enrolled students will be registered for the meeting
          </li>
          <li className="flex items-start">
            <svg className="w-4 h-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            Students will see a countdown timer before the session
          </li>
          <li className="flex items-start">
            <svg className="w-4 h-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            Recording will be automatically stored after the session
          </li>
        </ul>
      </div>

      <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={loading}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          loading={loading}
          disabled={loading}
        >
          {loading ? 'Scheduling...' : 'Schedule Session'}
        </Button>
      </div>
    </form>
  );
}

export default SessionScheduleForm;