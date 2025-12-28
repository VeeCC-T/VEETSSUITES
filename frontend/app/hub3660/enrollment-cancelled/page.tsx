'use client';

import React, { Suspense } from 'react';
import { EnrollmentCancelledContent } from './EnrollmentCancelledContent';

function LoadingFallback() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading...</p>
      </div>
    </div>
  );
}

export default function EnrollmentCancelledPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <EnrollmentCancelledContent />
    </Suspense>
  );
}