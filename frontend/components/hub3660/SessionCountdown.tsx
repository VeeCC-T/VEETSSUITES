'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui';
import type { Session } from '@/lib/hub3660';

interface SessionCountdownProps {
  session: Session;
  className?: string;
}

interface TimeRemaining {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  total: number;
}

export default function SessionCountdown({ session, className = '' }: SessionCountdownProps) {
  const [timeRemaining, setTimeRemaining] = useState<TimeRemaining>({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
    total: 0
  });
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    const calculateTimeRemaining = (): TimeRemaining => {
      const now = new Date().getTime();
      const sessionTime = new Date(session.scheduled_at).getTime();
      const difference = sessionTime - now;

      if (difference <= 0) {
        return {
          days: 0,
          hours: 0,
          minutes: 0,
          seconds: 0,
          total: 0
        };
      }

      const days = Math.floor(difference / (1000 * 60 * 60 * 24));
      const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((difference % (1000 * 60)) / 1000);

      return {
        days,
        hours,
        minutes,
        seconds,
        total: difference
      };
    };

    const updateCountdown = () => {
      const remaining = calculateTimeRemaining();
      setTimeRemaining(remaining);
      
      // Check if session is live (within 5 minutes of start time)
      const now = new Date().getTime();
      const sessionTime = new Date(session.scheduled_at).getTime();
      const timeDiff = sessionTime - now;
      setIsLive(timeDiff <= 0 && timeDiff > -300000); // Live for 5 minutes after start
    };

    // Initial calculation
    updateCountdown();

    // Update every second
    const interval = setInterval(updateCountdown, 1000);

    return () => clearInterval(interval);
  }, [session.scheduled_at]);

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
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

  const getStatusColor = () => {
    if (isLive) return 'bg-red-500';
    if (timeRemaining.total <= 0) return 'bg-gray-500';
    if (timeRemaining.days === 0 && timeRemaining.hours < 1) return 'bg-orange-500';
    if (timeRemaining.days === 0) return 'bg-yellow-500';
    return 'bg-blue-500';
  };

  const getStatusText = () => {
    if (isLive) return 'LIVE NOW';
    if (timeRemaining.total <= 0) return 'SESSION ENDED';
    return 'UPCOMING';
  };

  return (
    <Card className={`relative overflow-hidden ${className}`}>
      {/* Status indicator */}
      <div className={`absolute top-0 left-0 right-0 h-1 ${getStatusColor()}`} />
      
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
              {formatDateTime(session.scheduled_at)}
            </p>
          </div>
          
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold text-white ${getStatusColor()}`}>
            {getStatusText()}
          </span>
        </div>

        {/* Countdown display */}
        {timeRemaining.total > 0 && !isLive && (
          <div className="grid grid-cols-4 gap-4 text-center">
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-2xl font-bold text-gray-900">
                {timeRemaining.days}
              </div>
              <div className="text-xs text-gray-600 uppercase tracking-wide">
                {timeRemaining.days === 1 ? 'Day' : 'Days'}
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-2xl font-bold text-gray-900">
                {timeRemaining.hours}
              </div>
              <div className="text-xs text-gray-600 uppercase tracking-wide">
                {timeRemaining.hours === 1 ? 'Hour' : 'Hours'}
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-2xl font-bold text-gray-900">
                {timeRemaining.minutes}
              </div>
              <div className="text-xs text-gray-600 uppercase tracking-wide">
                {timeRemaining.minutes === 1 ? 'Min' : 'Mins'}
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-2xl font-bold text-gray-900">
                {timeRemaining.seconds}
              </div>
              <div className="text-xs text-gray-600 uppercase tracking-wide">
                {timeRemaining.seconds === 1 ? 'Sec' : 'Secs'}
              </div>
            </div>
          </div>
        )}

        {/* Live session indicator */}
        {isLive && (
          <div className="text-center py-4">
            <div className="inline-flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
              <span className="text-lg font-semibold text-red-600">
                Session is Live Now!
              </span>
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
            </div>
          </div>
        )}

        {/* Session ended */}
        {timeRemaining.total <= 0 && !isLive && (
          <div className="text-center py-4">
            <span className="text-gray-600">
              This session has ended
            </span>
            {session.has_recording && (
              <p className="text-sm text-blue-600 mt-1">
                Recording may be available
              </p>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}