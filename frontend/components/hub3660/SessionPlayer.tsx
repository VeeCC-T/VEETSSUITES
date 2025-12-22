'use client';

import React, { useState, useEffect } from 'react';
import { Card, Button } from '@/components/ui';
import { hub3660Api, type Session } from '@/lib/hub3660';
import { useAuth } from '@/lib/auth';

interface SessionPlayerProps {
  session: Session;
  courseId: number;
  className?: string;
  onError?: (error: string) => void;
}

interface RecordingData {
  recording_url: string;
  session_title: string;
  course_title: string;
  expires_in_hours: number | null;
  storage_type: 's3' | 'zoom';
}

export default function SessionPlayer({ 
  session, 
  courseId, 
  className = '',
  onError 
}: SessionPlayerProps) {
  const [recording, setRecording] = useState<RecordingData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [accessGranted, setAccessGranted] = useState(false);
  
  const { user } = useAuth();

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const checkAccess = async () => {
    if (!user) {
      setError('Please log in to access session recordings.');
      return false;
    }

    try {
      // Check enrollment status
      const enrollmentStatus = await hub3660Api.checkEnrollmentStatus(courseId);
      
      if (!enrollmentStatus.is_enrolled) {
        setError('You must be enrolled in this course to access recordings.');
        return false;
      }

      return true;
    } catch (err) {
      console.error('Failed to check access:', err);
      setError('Failed to verify access permissions.');
      return false;
    }
  };

  const loadRecording = async () => {
    if (!session.has_recording) {
      setError('No recording is available for this session.');
      return;
    }

    const hasAccess = await checkAccess();
    if (!hasAccess) return;

    try {
      setLoading(true);
      setError(null);
      
      const recordingData = await hub3660Api.getSessionRecording(session.id);
      setRecording(recordingData);
      setAccessGranted(true);
    } catch (err: any) {
      console.error('Failed to load recording:', err);
      
      if (err.response?.status === 403) {
        setError('You do not have permission to access this recording.');
      } else if (err.response?.status === 404) {
        setError('Recording not found or not yet available.');
      } else {
        setError('Failed to load recording. Please try again later.');
      }
      
      if (onError) {
        onError(error || 'Failed to load recording');
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePlayRecording = () => {
    if (recording?.recording_url) {
      // Open recording in new tab/window
      window.open(recording.recording_url, '_blank', 'noopener,noreferrer');
    }
  };

  const getExpirationText = () => {
    if (!recording?.expires_in_hours) return null;
    
    if (recording.expires_in_hours <= 1) {
      return 'Access expires in less than 1 hour';
    } else if (recording.expires_in_hours < 24) {
      return `Access expires in ${recording.expires_in_hours} hours`;
    } else {
      const days = Math.floor(recording.expires_in_hours / 24);
      return `Access expires in ${days} ${days === 1 ? 'day' : 'days'}`;
    }
  };

  return (
    <Card className={`${className}`}>
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {session.title}
            </h3>
            <p className="text-sm text-gray-600 mb-2">
              {session.course_title}
            </p>
            <p className="text-sm text-gray-500">
              Recorded: {formatDateTime(session.scheduled_at)}
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            {session.has_recording && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M8 5v10l7-5-7-5z" />
                </svg>
                Recording Available
              </span>
            )}
          </div>
        </div>

        {/* Recording not available */}
        {!session.has_recording && (
          <div className="text-center py-8 bg-gray-50 rounded-lg">
            <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <p className="text-gray-600 mb-2">No recording available</p>
            <p className="text-sm text-gray-500">
              This session was not recorded or the recording is still being processed.
            </p>
          </div>
        )}

        {/* Access control - not logged in */}
        {session.has_recording && !user && (
          <div className="text-center py-8 bg-blue-50 rounded-lg">
            <svg className="w-12 h-12 text-blue-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            <p className="text-gray-700 mb-4">Please log in to access session recordings</p>
            <Button
              onClick={() => window.location.href = '/auth-demo'}
              size="sm"
            >
              Log In
            </Button>
          </div>
        )}

        {/* Access control - need to load recording */}
        {session.has_recording && user && !accessGranted && !loading && !error && (
          <div className="text-center py-8">
            <Button
              onClick={loadRecording}
              disabled={loading}
              className="mb-4"
            >
              {loading ? 'Checking Access...' : 'Access Recording'}
            </Button>
            <p className="text-sm text-gray-500">
              Click to verify enrollment and access the recording
            </p>
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading recording...</p>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="text-center py-8 bg-red-50 rounded-lg">
            <svg className="w-12 h-12 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p className="text-red-700 mb-4">{error}</p>
            {error.includes('enroll') && (
              <Button
                onClick={() => window.location.href = `/hub3660/courses/${courseId}`}
                size="sm"
                variant="secondary"
              >
                View Course
              </Button>
            )}
          </div>
        )}

        {/* Recording ready to play */}
        {recording && accessGranted && !error && (
          <div className="space-y-4">
            {/* Recording info */}
            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M8 5v10l7-5-7-5z" />
                  </svg>
                  <span className="text-green-800 font-medium">Recording Ready</span>
                </div>
                
                {recording.storage_type === 's3' && (
                  <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded">
                    Secure Access
                  </span>
                )}
              </div>
              
              {getExpirationText() && (
                <p className="text-sm text-green-700 mt-2">
                  ⏰ {getExpirationText()}
                </p>
              )}
            </div>

            {/* Play button */}
            <div className="text-center">
              <Button
                onClick={handlePlayRecording}
                size="lg"
                className="inline-flex items-center space-x-2"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M8 5v10l7-5-7-5z" />
                </svg>
                <span>Play Recording</span>
              </Button>
              
              <p className="text-sm text-gray-500 mt-2">
                Recording will open in a new window
              </p>
            </div>

            {/* Technical info */}
            <div className="text-xs text-gray-500 space-y-1 pt-4 border-t border-gray-200">
              <div className="flex justify-between">
                <span>Storage:</span>
                <span className="capitalize">{recording.storage_type}</span>
              </div>
              {recording.expires_in_hours && (
                <div className="flex justify-between">
                  <span>Access Duration:</span>
                  <span>{recording.expires_in_hours} hours</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}