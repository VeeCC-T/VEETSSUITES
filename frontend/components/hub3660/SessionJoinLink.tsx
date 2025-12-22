'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui';
import { hub3660Api, type Session } from '@/lib/hub3660';
import { useAuth } from '@/lib/auth';

interface SessionJoinLinkProps {
  session: Session;
  courseId: number;
  className?: string;
  onError?: (error: string) => void;
}

export default function SessionJoinLink({ 
  session, 
  courseId, 
  className = '',
  onError 
}: SessionJoinLinkProps) {
  const [canJoin, setCanJoin] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLive, setIsLive] = useState(false);
  
  const { user } = useAuth();

  useEffect(() => {
    const checkSessionStatus = () => {
      const now = new Date().getTime();
      const sessionTime = new Date(session.scheduled_at).getTime();
      const timeDiff = sessionTime - now;
      
      // Session is considered live from 15 minutes before to 2 hours after start time
      const isCurrentlyLive = timeDiff <= 900000 && timeDiff > -7200000; // 15 min before, 2 hours after
      setIsLive(isCurrentlyLive);
    };

    checkSessionStatus();
    const interval = setInterval(checkSessionStatus, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, [session.scheduled_at]);

  useEffect(() => {
    if (user && isLive) {
      checkAccess();
    }
  }, [user, isLive, courseId]);

  const checkAccess = async () => {
    if (!user) {
      setError('Please log in to join live sessions.');
      setCanJoin(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Check enrollment status
      const enrollmentStatus = await hub3660Api.checkEnrollmentStatus(courseId);
      
      if (!enrollmentStatus.is_enrolled) {
        setError('You must be enrolled in this course to join live sessions.');
        setCanJoin(false);
        return;
      }

      // If enrolled and session has join URL, allow joining
      if (session.zoom_join_url) {
        setCanJoin(true);
      } else {
        setError('Join link is not available for this session.');
        setCanJoin(false);
      }
    } catch (err: any) {
      console.error('Failed to check access:', err);
      setError('Failed to verify access permissions.');
      setCanJoin(false);
      
      if (onError) {
        onError('Failed to verify access permissions.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleJoinSession = async () => {
    if (!canJoin || !session.zoom_join_url) return;

    try {
      // Register for session if not already registered
      await hub3660Api.registerForSession(session.id);
    } catch (err) {
      // Registration might fail if already registered, which is fine
      console.log('Registration status:', err);
    }

    // Open Zoom meeting in new window
    window.open(session.zoom_join_url, '_blank', 'noopener,noreferrer');
  };

  const getTimeUntilSession = () => {
    const now = new Date().getTime();
    const sessionTime = new Date(session.scheduled_at).getTime();
    const timeDiff = sessionTime - now;

    if (timeDiff <= 0) return null;

    const minutes = Math.floor(timeDiff / (1000 * 60));
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) {
      return `Starts in ${days} ${days === 1 ? 'day' : 'days'}`;
    } else if (hours > 0) {
      return `Starts in ${hours} ${hours === 1 ? 'hour' : 'hours'}`;
    } else if (minutes > 15) {
      return `Starts in ${minutes} minutes`;
    } else if (minutes > 0) {
      return `Starting in ${minutes} minutes`;
    } else {
      return 'Starting now';
    }
  };

  const getJoinButtonText = () => {
    if (loading) return 'Checking Access...';
    if (!user) return 'Log In to Join';
    if (!isLive) return 'Not Live Yet';
    if (error) return 'Cannot Join';
    if (canJoin) return 'Join Live Session';
    return 'Join Session';
  };

  const getJoinButtonVariant = () => {
    if (isLive && canJoin) return 'primary';
    if (error) return 'secondary';
    return 'secondary';
  };

  const shouldShowJoinButton = () => {
    // Always show button, but with different states
    return true;
  };

  const handleButtonClick = () => {
    if (!user) {
      window.location.href = '/auth-demo';
      return;
    }

    if (!isLive) {
      // Show info about when session starts
      return;
    }

    if (error && error.includes('enroll')) {
      window.location.href = `/hub3660/courses/${courseId}`;
      return;
    }

    if (canJoin) {
      handleJoinSession();
    }
  };

  return (
    <div className={`${className}`}>
      {/* Session status indicator */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          {isLive ? (
            <>
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium text-red-600">LIVE NOW</span>
            </>
          ) : (
            <>
              <div className="w-3 h-3 bg-gray-400 rounded-full" />
              <span className="text-sm text-gray-600">
                {getTimeUntilSession() || 'Session Ended'}
              </span>
            </>
          )}
        </div>

        {session.zoom_join_url && (
          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
            Zoom Meeting
          </span>
        )}
      </div>

      {/* Join button */}
      {shouldShowJoinButton() && (
        <div className="space-y-2">
          <Button
            onClick={handleButtonClick}
            disabled={loading || (!isLive && !!user) || (isLive && !canJoin && !error?.includes('enroll'))}
            variant={getJoinButtonVariant()}
            className="w-full"
            size="sm"
          >
            {isLive && canJoin && (
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            )}
            {getJoinButtonText()}
          </Button>

          {/* Error message */}
          {error && (
            <p className="text-xs text-red-600 text-center">
              {error}
            </p>
          )}

          {/* Info message */}
          {!error && !isLive && user && (
            <p className="text-xs text-gray-500 text-center">
              Join button will be active when the session starts
            </p>
          )}

          {/* Not logged in message */}
          {!user && (
            <p className="text-xs text-blue-600 text-center">
              Log in to join live sessions
            </p>
          )}
        </div>
      )}

      {/* Session info */}
      <div className="mt-3 pt-3 border-t border-gray-200">
        <div className="text-xs text-gray-500 space-y-1">
          <div className="flex justify-between">
            <span>Scheduled:</span>
            <span>
              {new Date(session.scheduled_at).toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </span>
          </div>
          
          {session.zoom_join_url && (
            <div className="flex justify-between">
              <span>Platform:</span>
              <span>Zoom Meeting</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}