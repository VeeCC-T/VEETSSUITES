import PerformanceDemo from '@/components/performance/PerformanceDemo'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Performance Optimization Demo - VeetsSuites',
  description: 'Demonstration of performance optimization utilities including lazy loading, performance monitoring, and resource hints.',
}

export default function PerformancePage() {
  return <PerformanceDemo />
}