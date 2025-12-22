'use client';

import React from 'react';
import { Navigation } from './Navigation';
import { Footer } from './Footer';

interface MainLayoutProps {
  children: React.ReactNode;
}

/**
 * Main layout component with navigation and footer
 * Implements responsive breakpoints (mobile, tablet, desktop)
 * Validates: Requirements 10.3, 10.4, 10.5
 */
export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Skip to main content link for keyboard navigation */}
      <a href="#main-content" className="skip-to-main">
        Skip to main content
      </a>
      
      <Navigation />
      
      <main id="main-content" className="flex-grow" role="main">
        {children}
      </main>
      
      <Footer />
    </div>
  );
};
