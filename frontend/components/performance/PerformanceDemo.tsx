'use client'

import React, { useState, useRef } from 'react'
import { 
  useLazyLoad, 
  LazyImage, 
  usePerformanceMonitoring,
  useBundleAnalysis,
  useResourceHints,
  globalPreloader,
  LazyLoadingMetrics
} from '@/lib/performance'

// Lazy loaded components for demo
const LazyChart = React.lazy(() => import('./LazyChart'))
const LazyTable = React.lazy(() => import('./LazyTable'))

export default function PerformanceDemo() {
  const [activeTab, setActiveTab] = useState('lazy-loading')
  const { recordMetric, getMetrics, generateReport } = usePerformanceMonitoring()
  const { analyzeBundleLoading, generateOptimizationReport } = useBundleAnalysis()
  const { preload, prefetch, getMetrics: getHintMetrics } = useResourceHints()

  // Lazy loading demo
  const { data: lazyData, loading, error, ref } = useLazyLoad(
    async () => {
      await new Promise(resolve => setTimeout(resolve, 1000))
      return { message: 'Lazy loaded content!', timestamp: Date.now() }
    }
  )

  // Performance metrics
  const [performanceReport, setPerformanceReport] = useState<any>(null)
  const [bundleReport, setBundleReport] = useState<any>(null)

  const handleGenerateReport = async () => {
    const report = generateReport()
    setPerformanceReport(report)
  }

  const handleBundleAnalysis = async () => {
    const bundleAnalysis = await analyzeBundleLoading()
    const optimizationReport = generateOptimizationReport()
    setBundleReport({ bundleAnalysis, optimizationReport })
  }

  const handlePreloadDemo = () => {
    // Preload some resources
    preload([
      { href: '/api/data', as: 'fetch' },
      { href: '/images/hero.jpg', as: 'image' }
    ])

    // Prefetch next page
    prefetch([
      { href: '/next-page' }
    ])

    // Preload components
    globalPreloader.preload('chart', () => import('./LazyChart'))
    globalPreloader.preload('table', () => import('./LazyTable'))
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8">Performance Optimization Demo</h1>

      {/* Tab Navigation */}
      <div className="flex space-x-4 mb-8 border-b">
        {[
          { id: 'lazy-loading', label: 'Lazy Loading' },
          { id: 'performance', label: 'Performance Monitoring' },
          { id: 'bundle', label: 'Bundle Analysis' },
          { id: 'resource-hints', label: 'Resource Hints' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 font-medium ${
              activeTab === tab.id
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Lazy Loading Demo */}
      {activeTab === 'lazy-loading' && (
        <div className="space-y-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Intersection Observer Lazy Loading</h2>
            <div ref={ref} className="min-h-[200px] border-2 border-dashed border-gray-300 rounded p-4">
              {loading && <div className="text-center">Loading lazy content...</div>}
              {error && <div className="text-red-600">Error: {error.message}</div>}
              {lazyData && (
                <div className="text-center">
                  <p className="text-green-600 font-medium">{lazyData.message}</p>
                  <p className="text-sm text-gray-500">Loaded at: {new Date(lazyData.timestamp).toLocaleTimeString()}</p>
                </div>
              )}
              {!loading && !error && !lazyData && (
                <div className="text-center text-gray-500">Scroll this element into view to load content</div>
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Lazy Image Loading</h2>
            <div className="grid grid-cols-2 gap-4">
              <LazyImage
                src="https://picsum.photos/400/300?random=1"
                alt="Lazy loaded image 1"
                className="rounded"
                onLoad={() => recordMetric('Image Load', performance.now())}
              />
              <LazyImage
                src="https://picsum.photos/400/300?random=2"
                alt="Lazy loaded image 2"
                className="rounded"
                onLoad={() => recordMetric('Image Load', performance.now())}
              />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Lazy Components</h2>
            <div className="space-y-4">
              <React.Suspense fallback={<div className="text-center py-8">Loading Chart...</div>}>
                <LazyChart />
              </React.Suspense>
              <React.Suspense fallback={<div className="text-center py-8">Loading Table...</div>}>
                <LazyTable />
              </React.Suspense>
            </div>
          </div>
        </div>
      )}

      {/* Performance Monitoring Demo */}
      {activeTab === 'performance' && (
        <div className="space-y-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Performance Monitoring</h2>
            <div className="space-y-4">
              <button
                onClick={handleGenerateReport}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Generate Performance Report
              </button>
              
              {performanceReport && (
                <div className="mt-4">
                  <h3 className="font-medium mb-2">Performance Summary</h3>
                  <div className="bg-gray-50 p-4 rounded">
                    <pre className="text-sm overflow-auto">
                      {JSON.stringify(performanceReport, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Lazy Loading Metrics</h2>
            <button
              onClick={() => {
                const metrics = LazyLoadingMetrics.getInstance().getMetrics()
                console.log('Lazy Loading Metrics:', metrics)
              }}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Log Lazy Loading Metrics
            </button>
          </div>
        </div>
      )}

      {/* Bundle Analysis Demo */}
      {activeTab === 'bundle' && (
        <div className="space-y-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Bundle Analysis</h2>
            <div className="space-y-4">
              <button
                onClick={handleBundleAnalysis}
                className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
              >
                Analyze Bundle Performance
              </button>
              
              {bundleReport && (
                <div className="mt-4">
                  <h3 className="font-medium mb-2">Bundle Analysis Report</h3>
                  <div className="bg-gray-50 p-4 rounded">
                    <pre className="text-sm overflow-auto">
                      {JSON.stringify(bundleReport, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Resource Hints Demo */}
      {activeTab === 'resource-hints' && (
        <div className="space-y-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Resource Hints</h2>
            <div className="space-y-4">
              <button
                onClick={handlePreloadDemo}
                className="bg-orange-600 text-white px-4 py-2 rounded hover:bg-orange-700"
              >
                Demo Resource Preloading
              </button>
              
              <button
                onClick={() => {
                  const metrics = getHintMetrics()
                  console.log('Resource Hint Metrics:', metrics)
                }}
                className="bg-teal-600 text-white px-4 py-2 rounded hover:bg-teal-700 ml-2"
              >
                Log Resource Hint Metrics
              </button>
            </div>
            
            <div className="mt-4 text-sm text-gray-600">
              <p>Check the Network tab in DevTools to see preloaded resources.</p>
              <p>Check the Console for logged metrics.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}