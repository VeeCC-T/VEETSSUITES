'use client';

import React from 'react';
import Link from 'next/link';

/**
 * Footer component for the application
 * Validates: Requirements 10.1, 10.3
 */
export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-50 border-t border-gray-200 mt-auto" role="contentinfo">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* About section */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
              About VEETSSUITES
            </h3>
            <p className="text-sm text-gray-600">
              A comprehensive multi-subsite platform providing professional services, education, and health consultation.
            </p>
          </div>

          {/* Subsites */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
              Subsites
            </h3>
            <ul className="space-y-2">
              <li>
                <Link href="/portfolio" className="text-sm text-gray-600 hover:text-blue-600 transition-colors">
                  Portfolio
                </Link>
              </li>
              <li>
                <Link href="/pharmxam" className="text-sm text-gray-600 hover:text-blue-600 transition-colors">
                  PHARMXAM
                </Link>
              </li>
              <li>
                <Link href="/hub3660" className="text-sm text-gray-600 hover:text-blue-600 transition-colors">
                  HUB3660
                </Link>
              </li>
              <li>
                <Link href="/healthee" className="text-sm text-gray-600 hover:text-blue-600 transition-colors">
                  HEALTHEE
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
              Resources
            </h3>
            <ul className="space-y-2">
              <li>
                <Link href="/about" className="text-sm text-gray-600 hover:text-blue-600 transition-colors">
                  About Us
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-sm text-gray-600 hover:text-blue-600 transition-colors">
                  Contact
                </Link>
              </li>
              <li>
                <Link href="/help" className="text-sm text-gray-600 hover:text-blue-600 transition-colors">
                  Help Center
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
              Legal
            </h3>
            <ul className="space-y-2">
              <li>
                <Link href="/privacy" className="text-sm text-gray-600 hover:text-blue-600 transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-sm text-gray-600 hover:text-blue-600 transition-colors">
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-8 pt-8 border-t border-gray-200">
          <p className="text-sm text-gray-500 text-center">
            © {currentYear} VEETSSUITES. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};
