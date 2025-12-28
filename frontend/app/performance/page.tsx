'use client';

import React from 'react'
import PerformanceDemo from '@/components/performance/PerformanceDemo'

// Disable static generation for this page
export const dynamic = 'force-dynamic'

export default function PerformancePage() {
  return <PerformanceDemo />
}