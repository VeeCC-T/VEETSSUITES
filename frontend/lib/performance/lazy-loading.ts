import React, { lazy, ComponentType, Suspense, useEffect, useState, useRef } from 'react'

// Default loading component
const DefaultLoadingSpinner = () => {
  return React.createElement('div', 
    { className: 'flex items-center justify-center p-4' },
    React.createElement('div', { 
      className: 'animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600' 
    })
  )
}

/**
 * Creates a lazy-loaded component with a loading fallback
 */
export function createLazyComponent<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  fallback: ComponentType = DefaultLoadingSpinner
) {
  const LazyComponent = lazy(importFn)
  const FallbackComponent = fallback
  
  return function LazyWrapper(props: any) {
    return React.createElement(Suspense, 
      { fallback: React.createElement(FallbackComponent) },
      React.createElement(LazyComponent, props)
    )
  }
}

/**
 * Preloads a component for better performance
 */
export function preloadComponent(importFn: () => Promise<any>) {
  const componentImport = importFn()
  return componentImport
}

/**
 * Hook for intersection observer-based lazy loading
 */
export function useIntersectionObserver(
  ref: React.RefObject<Element>,
  options: IntersectionObserverInit = {
    threshold: 0.1,
    rootMargin: '50px'
  }
): boolean {
  const [isIntersecting, setIsIntersecting] = useState(false)

  useEffect(() => {
    const element = ref.current
    if (!element) return

    const observer = new IntersectionObserver(([entry]) => {
      setIsIntersecting(entry.isIntersecting)
    }, options)

    observer.observe(element)

    return () => {
      observer.unobserve(element)
    }
  }, [ref, options])

  return isIntersecting
}

/**
 * Hook for lazy loading content when element becomes visible
 */
export function useLazyLoad<T>(
  loadFn: () => Promise<T>,
  dependencies: any[] = []
): {
  data: T | null
  loading: boolean
  error: Error | null
  ref: React.RefObject<HTMLDivElement>
} {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const ref = useRef<HTMLDivElement>(null)
  const isVisible = useIntersectionObserver(ref)

  useEffect(() => {
    if (isVisible && !data && !loading) {
      setLoading(true)
      setError(null)
      
      loadFn()
        .then(setData)
        .catch(setError)
        .finally(() => setLoading(false))
    }
  }, [isVisible, data, loading, ...dependencies])

  return { data, loading, error, ref }
}

/**
 * Component for lazy loading images with placeholder
 */
interface LazyImageProps {
  src: string
  alt: string
  placeholder?: string
  className?: string
  onLoad?: () => void
  onError?: (error: Error) => void
}

export function LazyImage({ 
  src, 
  alt, 
  placeholder = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkxvYWRpbmcuLi48L3RleHQ+PC9zdmc+',
  className = '',
  onLoad,
  onError
}: LazyImageProps) {
  const [imageSrc, setImageSrc] = useState(placeholder)
  const [imageRef, setImageRef] = useState<HTMLImageElement | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const isVisible = useIntersectionObserver(containerRef)

  useEffect(() => {
    if (isVisible && imageSrc === placeholder) {
      const img = new Image()
      img.onload = () => {
        setImageSrc(src)
        onLoad?.()
      }
      img.onerror = () => {
        const error = new Error(`Failed to load image: ${src}`)
        onError?.(error)
      }
      img.src = src
      setImageRef(img)
    }
  }, [isVisible, src, placeholder, imageSrc, onLoad, onError])

  return React.createElement('div', 
    { ref: containerRef, className },
    React.createElement('img', {
      src: imageSrc,
      alt,
      className: 'w-full h-full object-cover transition-opacity duration-300',
      style: { opacity: imageSrc === placeholder ? 0.7 : 1 }
    })
  )
}

/**
 * Higher-order component for lazy loading any component
 */
export function withLazyLoading<P extends object>(
  Component: ComponentType<P>,
  fallback: ComponentType = DefaultLoadingSpinner
) {
  return function LazyLoadedComponent(props: P) {
    const containerRef = useRef<HTMLDivElement>(null)
    const isVisible = useIntersectionObserver(containerRef)
    const FallbackComponent = fallback

    return React.createElement('div',
      { ref: containerRef },
      isVisible 
        ? React.createElement(Component, props)
        : React.createElement(FallbackComponent)
    )
  }
}

/**
 * Utility for batch preloading components
 */
export class ComponentPreloader {
  private preloadedComponents = new Map<string, Promise<any>>()

  preload(key: string, importFn: () => Promise<any>): Promise<any> {
    if (!this.preloadedComponents.has(key)) {
      this.preloadedComponents.set(key, importFn())
    }
    return this.preloadedComponents.get(key)!
  }

  preloadMultiple(components: Record<string, () => Promise<any>>): Promise<any[]> {
    const promises = Object.entries(components).map(([key, importFn]) => 
      this.preload(key, importFn)
    )
    return Promise.all(promises)
  }

  isPreloaded(key: string): boolean {
    return this.preloadedComponents.has(key)
  }

  clear(key?: string): void {
    if (key) {
      this.preloadedComponents.delete(key)
    } else {
      this.preloadedComponents.clear()
    }
  }
}

// Global preloader instance
export const globalPreloader = new ComponentPreloader()

/**
 * Hook for preloading components on user interaction
 */
export function usePreloadOnHover(importFn: () => Promise<any>) {
  const preloadRef = useRef<(() => Promise<any>) | null>(null)
  
  const handleMouseEnter = () => {
    if (!preloadRef.current) {
      preloadRef.current = importFn
      importFn()
    }
  }

  return { onMouseEnter: handleMouseEnter }
}

/**
 * Performance monitoring for lazy loading
 */
export class LazyLoadingMetrics {
  private static instance: LazyLoadingMetrics
  private metrics: Map<string, {
    loadTime: number
    errorCount: number
    successCount: number
  }> = new Map()

  static getInstance(): LazyLoadingMetrics {
    if (!LazyLoadingMetrics.instance) {
      LazyLoadingMetrics.instance = new LazyLoadingMetrics()
    }
    return LazyLoadingMetrics.instance
  }

  recordLoad(componentName: string, loadTime: number, success: boolean): void {
    const existing = this.metrics.get(componentName) || {
      loadTime: 0,
      errorCount: 0,
      successCount: 0
    }

    this.metrics.set(componentName, {
      loadTime: (existing.loadTime + loadTime) / (existing.successCount + existing.errorCount + 1),
      errorCount: success ? existing.errorCount : existing.errorCount + 1,
      successCount: success ? existing.successCount + 1 : existing.successCount
    })
  }

  getMetrics(componentName?: string) {
    if (componentName) {
      return this.metrics.get(componentName)
    }
    return Object.fromEntries(this.metrics)
  }

  clearMetrics(): void {
    this.metrics.clear()
  }
}

/**
 * Enhanced lazy component with performance tracking
 */
export function createTrackedLazyComponent<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  componentName: string,
  fallback: ComponentType = DefaultLoadingSpinner
) {
  const LazyComponent = lazy(async () => {
    const startTime = performance.now()
    try {
      const component = await importFn()
      const loadTime = performance.now() - startTime
      LazyLoadingMetrics.getInstance().recordLoad(componentName, loadTime, true)
      return component
    } catch (error) {
      const loadTime = performance.now() - startTime
      LazyLoadingMetrics.getInstance().recordLoad(componentName, loadTime, false)
      throw error
    }
  })

  const FallbackComponent = fallback

  return function TrackedLazyWrapper(props: any) {
    return React.createElement(Suspense,
      { fallback: React.createElement(FallbackComponent) },
      React.createElement(LazyComponent, props)
    )
  }
}