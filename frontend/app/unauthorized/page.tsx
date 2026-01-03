'use client';

import React from 'react';
import Link from 'next/link';
import { Card, Button } from '@/components/ui';

export default function UnauthorizedPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <Card className="max-w-md mx-auto">
        <div className="p-8 text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Access Denied
          </h1>
          <p className="text-gray-600 mb-6">
            You don't have permission to access this page. Please contact an administrator if you believe this is an error.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-3">
            <Link href="/" className="flex-1">
              <Button variant="secondary" className="w-full">
                Go Home
              </Button>
            </Link>
            <Link href="/auth-demo" className="flex-1">
              <Button className="w-full">
                Login
              </Button>
            </Link>
          </div>
        </div>
      </Card>
    </div>
  );
}