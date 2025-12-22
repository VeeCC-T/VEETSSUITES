'use client';

import React from 'react';

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  ariaLabel?: string;
  role?: string;
}

/**
 * Card component with 2xl rounded corners and soft shadows
 * Validates: Requirements 10.1, 10.4, 10.5
 */
export const Card: React.FC<CardProps> = ({ 
  children, 
  className = '', 
  onClick,
  ariaLabel,
  role,
}) => {
  const baseClasses = 'rounded-2xl shadow-md bg-white p-6';
  const interactiveClasses = onClick 
    ? 'cursor-pointer hover:shadow-lg transition-shadow focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2' 
    : '';
  const combinedClasses = `${baseClasses} ${interactiveClasses} ${className}`.trim();

  // If interactive, make it keyboard accessible
  if (onClick) {
    const handleKeyDown = (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        onClick();
      }
    };

    return (
      <div 
        className={combinedClasses} 
        onClick={onClick}
        onKeyDown={handleKeyDown}
        role={role || 'button'}
        tabIndex={0}
        aria-label={ariaLabel}
      >
        {children}
      </div>
    );
  }

  return (
    <div className={combinedClasses} role={role}>
      {children}
    </div>
  );
};
