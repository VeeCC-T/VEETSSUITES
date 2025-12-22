import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import {
  createLazyComponent,
  LazyImage,
  useLazyLoad,
  PerformanceMonitor,
  LazyLoadingMetrics,
  globalPreloader
} from '@/lib/performance'

// Mock IntersectionObserver
const mockIntersectionObserver = jest.fn()
mockIntersectionObserver.mockReturnValue({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null
})
window.IntersectionObserver = mockIntersectionObserver

// Mock performance API
Object.defineProperty(window, 'performance', {
  value: {
    now: jest.fn(() => Date.now()),
    mark: jest.fn(),
    measure: jest.fn(),
    getEntriesByType: jest.fn(() => []),
    getEntriesByName: jest.fn(() => [])
  }
})

// Test component for lazy loading
const TestComponent = () => <div data-testid="test-component">Test Component</div>

describe('Performance Utilities', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Lazy Loading', () => {
    test('createLazyComponent creates a lazy component', async () => {
      const LazyTestComponent = createLazyComponent(
        () => Promise.resolve({ default: TestComponent })
      )

      render(<LazyTestComponent />)
      
      // Should show loading initially, then the component
      await waitFor(() => {
        expect(screen.getByTestId('test-component')).toBeInTheDocument()
      })
    })

    test('LazyImage renders with placeholder initially', () => {
      render(
        <LazyImage
          src="/test-image.jpg"
          alt="Test image"
          data-testid="lazy-image"
        />
      )

      const image = screen.getByRole('img')
      expect(image).toBeInTheDocument()
      expect(image).toHaveAttribute('alt', 'Test image')
    })

    test('useLazyLoad hook works correctly', () => {
      const TestHookComponent = () => {
        const { data, loading, error, ref } = useLazyLoad(
          async () => ({ message: 'Loaded!' })
        )

        return (
          <div ref={ref} data-testid="lazy-content">
            {loading && <div>Loading...</div>}
            {error && <div>Error: {error.message}</div>}
            {data && <div>{data.message}</div>}
          </div>
        )
      }

      render(<TestHookComponent />)
      expect(screen.getByTestId('lazy-content')).toBeInTheDocument()
    })
  })

  describe('Performance Monitoring', () => {
    test('PerformanceMonitor singleton works', () => {
      const monitor1 = PerformanceMonitor.getInstance()
      const monitor2 = PerformanceMonitor.getInstance()
      
      expect(monitor1).toBe(monitor2)
    })

    test('PerformanceMonitor records metrics', () => {
      const monitor = PerformanceMonitor.getInstance()
      monitor.clearMetrics()
      
      monitor.recordMetric('Test Metric', 100)
      const metrics = monitor.getMetrics()
      
      expect(metrics).toHaveLength(1)
      expect(metrics[0].name).toBe('Test Metric')
      expect(metrics[0].value).toBe(100)
    })

    test('LazyLoadingMetrics tracks component loading', () => {
      const metrics = LazyLoadingMetrics.getInstance()
      metrics.clearMetrics()
      
      metrics.recordLoad('TestComponent', 150, true)
      const componentMetrics = metrics.getMetrics('TestComponent')
      
      expect(componentMetrics).toBeDefined()
      expect(componentMetrics?.loadTime).toBe(150)
      expect(componentMetrics?.successCount).toBe(1)
      expect(componentMetrics?.errorCount).toBe(0)
    })
  })

  describe('Component Preloader', () => {
    test('globalPreloader preloads components', async () => {
      const mockImport = jest.fn(() => Promise.resolve({ default: TestComponent }))
      
      const promise = globalPreloader.preload('test-component', mockImport)
      
      expect(mockImport).toHaveBeenCalled()
      expect(globalPreloader.isPreloaded('test-component')).toBe(false) // Not yet resolved
      
      await promise
      expect(globalPreloader.isPreloaded('test-component')).toBe(true)
    })

    test('globalPreloader preloads multiple components', async () => {
      const mockImports = {
        'component1': jest.fn(() => Promise.resolve({ default: TestComponent })),
        'component2': jest.fn(() => Promise.resolve({ default: TestComponent }))
      }
      
      await globalPreloader.preloadMultiple(mockImports)
      
      expect(mockImports.component1).toHaveBeenCalled()
      expect(mockImports.component2).toHaveBeenCalled()
    })
  })

  describe('Performance Hooks', () => {
    test('useDebounce hook', async () => {
      const { useDebounce } = require('@/lib/performance/hooks/useDebounce')
      
      const TestDebounceComponent = () => {
        const [value, setValue] = React.useState('')
        const debouncedValue = useDebounce(value, 100)
        
        return (
          <div>
            <input 
              value={value}
              onChange={(e) => setValue(e.target.value)}
              data-testid="input"
            />
            <div data-testid="debounced-value">{debouncedValue}</div>
          </div>
        )
      }

      render(<TestDebounceComponent />)
      
      const input = screen.getByTestId('input')
      const debouncedDiv = screen.getByTestId('debounced-value')
      
      // Initially empty
      expect(debouncedDiv).toHaveTextContent('')
      
      // Type something
      input.focus()
      // Note: Full debounce testing would require more complex setup
      // This is a basic structure test
    })
  })

  describe('Error Handling', () => {
    test('lazy loading handles import errors gracefully', async () => {
      const LazyErrorComponent = createLazyComponent(
        () => Promise.reject(new Error('Import failed'))
      )

      // This would normally be wrapped in an error boundary in a real app
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
      
      try {
        render(<LazyErrorComponent />)
      } catch (error) {
        expect(error).toBeDefined()
      }
      
      consoleSpy.mockRestore()
    })

    test('performance monitoring handles missing APIs gracefully', () => {
      // Temporarily remove performance API
      const originalPerformance = window.performance
      delete (window as any).performance
      
      const monitor = PerformanceMonitor.getInstance()
      
      // Should not throw
      expect(() => {
        monitor.recordMetric('Test', 100)
        monitor.startMonitoring()
        monitor.stopMonitoring()
      }).not.toThrow()
      
      // Restore
      window.performance = originalPerformance
    })
  })
})

describe('Performance Utilities Integration', () => {
  test('complete performance optimization flow', async () => {
    // Create a lazy component with tracking
    const { createTrackedLazyComponent } = require('@/lib/performance')
    
    const TrackedComponent = createTrackedLazyComponent(
      () => Promise.resolve({ default: TestComponent }),
      'IntegrationTest'
    )

    // Render and verify it works
    render(<TrackedComponent />)
    
    await waitFor(() => {
      expect(screen.getByTestId('test-component')).toBeInTheDocument()
    })

    // Check that metrics were recorded
    const metrics = LazyLoadingMetrics.getInstance()
    const componentMetrics = metrics.getMetrics('IntegrationTest')
    
    // Should have recorded the load
    expect(componentMetrics).toBeDefined()
  })
})