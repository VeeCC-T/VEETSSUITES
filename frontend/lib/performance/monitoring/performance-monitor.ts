/**
 * Performance monitoring utilities
 */

interface PerformanceMetric {
  name: string
  value: number
  timestamp: number
  type: 'timing' | 'counter' | 'gauge'
}

interface WebVitalsMetric {
  name: 'CLS' | 'FID' | 'FCP' | 'LCP' | 'TTFB'
  value: number
  rating: 'good' | 'needs-improvement' | 'poor'
}

export class PerformanceMonitor {
  private static instance: PerformanceMonitor
  private metrics: PerformanceMetric[] = []
  private observers: PerformanceObserver[] = []

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor()
    }
    return PerformanceMonitor.instance
  }

  /**
   * Start monitoring performance metrics
   */
  startMonitoring(): void {
    this.monitorNavigationTiming()
    this.monitorResourceTiming()
    this.monitorLongTasks()
    this.monitorWebVitals()
  }

  /**
   * Stop monitoring and cleanup observers
   */
  stopMonitoring(): void {
    this.observers.forEach(observer => observer.disconnect())
    this.observers = []
  }

  /**
   * Record a custom performance metric
   */
  recordMetric(name: string, value: number, type: PerformanceMetric['type'] = 'timing'): void {
    this.metrics.push({
      name,
      value,
      timestamp: Date.now(),
      type
    })
  }

  /**
   * Get all recorded metrics
   */
  getMetrics(): PerformanceMetric[] {
    return [...this.metrics]
  }

  /**
   * Get metrics by name
   */
  getMetricsByName(name: string): PerformanceMetric[] {
    return this.metrics.filter(metric => metric.name === name)
  }

  /**
   * Clear all metrics
   */
  clearMetrics(): void {
    this.metrics = []
  }

  /**
   * Monitor navigation timing
   */
  private monitorNavigationTiming(): void {
    if (typeof window === 'undefined' || !window.performance) return

    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
    if (navigation) {
      this.recordMetric('DNS Lookup', navigation.domainLookupEnd - navigation.domainLookupStart)
      this.recordMetric('TCP Connection', navigation.connectEnd - navigation.connectStart)
      this.recordMetric('Request', navigation.responseStart - navigation.requestStart)
      this.recordMetric('Response', navigation.responseEnd - navigation.responseStart)
      this.recordMetric('DOM Processing', navigation.domComplete - navigation.domLoading)
      this.recordMetric('Load Complete', navigation.loadEventEnd - navigation.loadEventStart)
    }
  }

  /**
   * Monitor resource timing
   */
  private monitorResourceTiming(): void {
    if (typeof window === 'undefined' || !window.PerformanceObserver) return

    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.entryType === 'resource') {
          const resource = entry as PerformanceResourceTiming
          this.recordMetric(`Resource: ${resource.name}`, resource.duration)
        }
      })
    })

    observer.observe({ entryTypes: ['resource'] })
    this.observers.push(observer)
  }

  /**
   * Monitor long tasks that block the main thread
   */
  private monitorLongTasks(): void {
    if (typeof window === 'undefined' || !window.PerformanceObserver) return

    try {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          this.recordMetric('Long Task', entry.duration)
        })
      })

      observer.observe({ entryTypes: ['longtask'] })
      this.observers.push(observer)
    } catch (e) {
      // Long task observer not supported
    }
  }

  /**
   * Monitor Web Vitals metrics
   */
  private monitorWebVitals(): void {
    if (typeof window === 'undefined') return

    // Monitor Largest Contentful Paint (LCP)
    this.observeWebVital('largest-contentful-paint', (entry: any) => {
      const value = entry.startTime
      this.recordMetric('LCP', value)
      return {
        name: 'LCP' as const,
        value,
        rating: value <= 2500 ? 'good' : value <= 4000 ? 'needs-improvement' : 'poor'
      }
    })

    // Monitor First Input Delay (FID)
    this.observeWebVital('first-input', (entry: any) => {
      const value = entry.processingStart - entry.startTime
      this.recordMetric('FID', value)
      return {
        name: 'FID' as const,
        value,
        rating: value <= 100 ? 'good' : value <= 300 ? 'needs-improvement' : 'poor'
      }
    })

    // Monitor Cumulative Layout Shift (CLS)
    this.observeWebVital('layout-shift', (entry: any) => {
      if (!entry.hadRecentInput) {
        const value = entry.value
        this.recordMetric('CLS', value)
        return {
          name: 'CLS' as const,
          value,
          rating: value <= 0.1 ? 'good' : value <= 0.25 ? 'needs-improvement' : 'poor'
        }
      }
    })
  }

  /**
   * Observe specific web vital metrics
   */
  private observeWebVital(type: string, callback: (entry: any) => WebVitalsMetric | undefined): void {
    if (!window.PerformanceObserver) return

    try {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach(callback)
      })

      observer.observe({ entryTypes: [type] })
      this.observers.push(observer)
    } catch (e) {
      // Observer type not supported
    }
  }

  /**
   * Generate performance report
   */
  generateReport(): {
    summary: Record<string, number>
    webVitals: WebVitalsMetric[]
    recommendations: string[]
  } {
    const summary: Record<string, number> = {}
    const webVitals: WebVitalsMetric[] = []
    const recommendations: string[] = []

    // Calculate averages for each metric type
    const metricGroups = this.metrics.reduce((groups, metric) => {
      if (!groups[metric.name]) {
        groups[metric.name] = []
      }
      groups[metric.name].push(metric.value)
      return groups
    }, {} as Record<string, number[]>)

    Object.entries(metricGroups).forEach(([name, values]) => {
      summary[name] = values.reduce((sum, val) => sum + val, 0) / values.length
    })

    // Generate recommendations based on metrics
    if (summary['Long Task'] > 50) {
      recommendations.push('Consider code splitting to reduce long tasks')
    }
    if (summary['LCP'] > 2500) {
      recommendations.push('Optimize Largest Contentful Paint by optimizing images and critical resources')
    }
    if (summary['FID'] > 100) {
      recommendations.push('Reduce First Input Delay by minimizing JavaScript execution time')
    }

    return { summary, webVitals, recommendations }
  }
}

/**
 * Hook for using performance monitoring in React components
 */
export function usePerformanceMonitoring() {
  const monitor = PerformanceMonitor.getInstance()

  return {
    recordMetric: monitor.recordMetric.bind(monitor),
    getMetrics: monitor.getMetrics.bind(monitor),
    generateReport: monitor.generateReport.bind(monitor)
  }
}

/**
 * Higher-order component for performance monitoring
 */
export function withPerformanceMonitoring<P extends object>(
  Component: React.ComponentType<P>,
  componentName: string
) {
  return function PerformanceMonitoredComponent(props: P) {
    const monitor = PerformanceMonitor.getInstance()
    
    React.useEffect(() => {
      const startTime = performance.now()
      
      return () => {
        const endTime = performance.now()
        monitor.recordMetric(`${componentName} Render Time`, endTime - startTime)
      }
    }, [])

    return React.createElement(Component, props)
  }
}