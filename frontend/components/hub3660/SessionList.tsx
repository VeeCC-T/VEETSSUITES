'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui';
import { hub3660Api, type Session } from '@/lib/hub3660';
import { useAuth } from '@/lib/auth';
import SessionCountdown from './SessionCountdown';
import SessionPlayer from './SessionPlayer';
import SessionJoinLink from './SessionJoinLink';

interface SessionListProps {
  courseId: number;
  className?: string;
}

export default function SessionList({ courseId, className = '' }: SessionListProps) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEnrolled, setIsEnrolled] = useState(false);
  
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      checkEnrollmentAndLoadSessions();
    } else {
      setLoading(false);
      setError('Please log in to view course sessions.');
    }
  }, [courseId, user]);

  const checkEnrollmentAndLoadSessions = async () => {
    try {
      setLoading(true);
      setError(null);

      // Check enrollment status first
      const enrollmentStatus = await hub3660Api.checkEnrollmentStatus(courseId);
      setIsEnrolled(enrollmentStatus.is_enrolled);

      if (!enrollmentStatus.is_enrolled) {
        setError('You must be enrolled in this course to view sessions.');
        return;
      }

      // Load sessions if enrolled
      const sessionsData = await hub3660Api.getCourseSessions(courseId);
      setSessions(sessionsData);
    } catch (err: any) {
      console.error('Failed to load sessions:', err);
      
      if (err.response?.status === 403) {
        setError('You do not have permission to view these sessions.');
      } else {
        setError('Failed to load course sessions. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
  };

  const categorizeSession = (session: Session) => {
    const now = new Date();
    const sessionDate = new Date(session.scheduled_at);
    const timeDiff = sessionDate.getTime() - now.getTime();
    
    // Live: within 15 minutes before to 2 hours after
    if (timeDiff <= 900000 && timeDiff > -7200000) {
      return 'live';
    }
    
    // Upcoming: more than 15 minutes in the future
    if (timeDiff > 900000) {
      return 'upcoming';
    }
    
    // Past: more than 2 hours ago
    return 'past';
  };

  const groupSessionsByCategory = () => {
    const grouped = {
      live: [] as Session[],
      upcoming: [] as Session[],
      past: [] as Session[]
    };

    sessions.forEach(session => {
      const category = categorizeSession(session);
      grouped[category].push(session);
    });

    // Sort each category
    grouped.live.sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime());
    grouped.upcoming.sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime());
    grouped.past.sort((a, b) => new Date(b.scheduled_at).getTime() - new Date(a.scheduled_at).getTime());

    return grouped;
  };

  const renderSessionCard = (session: Session, category: 'live' | 'upcoming' | 'past') => {
    return (
      <Card key={session.id} className="overflow-hidden">
        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Session countdown (for upcoming and live sessions) */}
            <div className="lg:col-span-2">
              {(category === 'upcoming' || category === 'live') && (
                <SessionCountdown session={session} />
              )}
              
              {category === 'past' && (
                <div className="bg-gray-50 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {session.title}
                  </h3>
                  <p className="text-sm text-gray-600 mb-2">
                    {session.course_title}
                  </p>
                  <p className="text-sm text-gray-500">
                    Completed: {new Date(session.scheduled_at).toLocaleString('en-US', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                  
                  {session.has_recording && (
                    <div className="mt-4">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M8 5v10l7-5-7-5z" />
                        </svg>
                        Recording Available
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Session actions */}
            <div className="space-y-4">
              {/* Join link for live and upcoming sessions */}
              {(category === 'live' || category === 'upcoming') && (
                <SessionJoinLink
                  session={session}
                  courseId={courseId}
                  onError={handleError}
                />
              )}

              {/* Recording player for past sessions */}
              {category === 'past' && session.has_recording && (
                <div className="bg-white border border-gray-200 rounded-xl p-4">
                  <h4 className="font-medium text-gray-900 mb-3">Session Recording</h4>
                  <SessionPlayer
                    session={session}
                    courseId={courseId}
                    onError={handleError}
                  />
                </div>
              )}

              {/* No recording available */}
              {category === 'past' && !session.has_recording && (
                <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-center">
                  <svg className="w-8 h-8 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <p className="text-sm text-gray-600">No recording available</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </Card>
    );
  };

  if (loading) {
    return (
      <div className={`${className}`}>
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading course sessions...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className={`${className}`}>
        <Card>
          <div className="p-8 text-center">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Login Required</h3>
            <p className="text-gray-600 mb-4">Please log in to view course sessions.</p>
            <button
              onClick={() => window.location.href = '/auth-demo'}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Log In
            </button>
          </div>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${className}`}>
        <Card>
          <div className="p-8 text-center">
            <svg className="w-16 h-16 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Access Denied</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            {error.includes('enroll') && (
              <button
                onClick={() => window.location.href = `/hub3660/courses/${courseId}`}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                View Course Details
              </button>
            )}
          </div>
        </Card>
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className={`${className}`}>
        <Card>
          <div className="p-8 text-center">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3a4 4 0 118 0v4m-4 8a2 2 0 100-4 2 2 0 000 4zm0 0v4a2 2 0 002 2h6a2 2 0 002-2v-4a2 2 0 00-2-2h-6a2 2 0 00-2 2z" />
            </svg>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Sessions Scheduled</h3>
            <p className="text-gray-600">
              No sessions have been scheduled for this course yet. Check back later for updates.
            </p>
          </div>
        </Card>
      </div>
    );
  }

  const groupedSessions = groupSessionsByCategory();

  return (
    <div className={`space-y-8 ${className}`}>
      {/* Live Sessions */}
      {groupedSessions.live.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse mr-3" />
            Live Sessions
          </h2>
          <div className="space-y-4">
            {groupedSessions.live.map(session => renderSessionCard(session, 'live'))}
          </div>
        </div>
      )}

      {/* Upcoming Sessions */}
      {groupedSessions.upcoming.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
            <svg className="w-6 h-6 text-blue-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Upcoming Sessions
          </h2>
          <div className="space-y-4">
            {groupedSessions.upcoming.map(session => renderSessionCard(session, 'upcoming'))}
          </div>
        </div>
      )}

      {/* Past Sessions */}
      {groupedSessions.past.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
            <svg className="w-6 h-6 text-gray-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            Past Sessions
          </h2>
          <div className="space-y-4">
            {groupedSessions.past.map(session => renderSessionCard(session, 'past'))}
          </div>
        </div>
      )}
    </div>
  );
}