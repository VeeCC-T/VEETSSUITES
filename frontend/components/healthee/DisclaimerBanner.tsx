'use client';

import { useState } from 'react';

interface DisclaimerBannerProps {
  /**
   * Whether the disclaimer can be dismissed by the user
   * @default true
   */
  dismissible?: boolean;
  /**
   * Custom className for styling
   */
  className?: string;
  /**
   * Whether to show the disclaimer in a compact format
   * @default false
   */
  compact?: boolean;
}

export function DisclaimerBanner({ 
  dismissible = true, 
  className = '',
  compact = false 
}: DisclaimerBannerProps) {
  const [isDismissed, setIsDismissed] = useState(false);

  // Don't render if dismissed (but keep persistent across page reloads)
  if (isDismissed && dismissible) {
    return null;
  }

  const handleDismiss = () => {
    if (dismissible) {
      setIsDismissed(true);
      // Store dismissal in sessionStorage (not localStorage to make it session-persistent)
      sessionStorage.setItem('healthee-disclaimer-dismissed', 'true');
    }
  };

  // Check if previously dismissed in this session
  if (dismissible && typeof window !== 'undefined') {
    const wasDismissed = sessionStorage.getItem('healthee-disclaimer-dismissed');
    if (wasDismissed && !isDismissed) {
      setIsDismissed(true);
      return null;
    }
  }

  return (
    <div 
      className={`bg-yellow-50 border border-yellow-200 rounded-2xl p-4 mb-8 ${className}`}
      role="alert"
      aria-labelledby="medical-disclaimer-title"
    >
      <div className="flex">
        <div className="flex-shrink-0">
          <svg 
            className="h-5 w-5 text-yellow-400" 
            viewBox="0 0 20 20" 
            fill="currentColor"
            aria-hidden="true"
          >
            <path 
              fillRule="evenodd" 
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" 
              clipRule="evenodd" 
            />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 
            id="medical-disclaimer-title"
            className="text-sm font-medium text-yellow-800"
          >
            Medical Disclaimer
          </h3>
          <div className="mt-2 text-sm text-yellow-700">
            {compact ? (
              <p>
                <strong>HEALTHEE is a guide only.</strong> This service provides general health information 
                and is not a substitute for professional medical advice. Always consult your physician 
                for medical conditions.
              </p>
            ) : (
              <p>
                This service provides general health information and is not a substitute for professional 
                medical advice, diagnosis, or treatment. Always seek the advice of your physician or other 
                qualified health provider with any questions you may have regarding a medical condition. 
                Never disregard professional medical advice or delay in seeking it because of something 
                you have read here. <strong>HEALTHEE is a guide only - contact a physician for medical advice.</strong>
              </p>
            )}
          </div>
        </div>
        {dismissible && (
          <div className="ml-auto pl-3">
            <div className="-mx-1.5 -my-1.5">
              <button
                type="button"
                onClick={handleDismiss}
                className="inline-flex rounded-md bg-yellow-50 p-1.5 text-yellow-500 hover:bg-yellow-100 focus:outline-none focus:ring-2 focus:ring-yellow-600 focus:ring-offset-2 focus:ring-offset-yellow-50"
                aria-label="Dismiss medical disclaimer"
              >
                <span className="sr-only">Dismiss</span>
                <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
                </svg>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}