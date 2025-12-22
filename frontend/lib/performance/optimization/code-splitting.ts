/**
 * Code splitting utilities and helpers
 */

import { lazy, ComponentType } from 'react'

/**
 * Route-based code splitting helper
 */
export function createRouteComponent<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  routeName: string
) {
  const LazyComponent = lazy(async () => {
    const startTime = performance.now()
    try {
      const component = await importFn()
      const loadTime = performance.now() - startTime
      
      // Log performance metrics
      if (typeof window !== 'undefined') {
        console.log(`Route "${routeName}" loaded in ${loadTime.toFixed(2)}ms`)
        performance.mark(`route-${routeName}-loaded`)
      }
      
      return component
    } catch (error) {
      console.error(`Failed to load route "${routeName}":`, error)
      throw error
    }
  })

  LazyComponent.displayName = `LazyRoute(${routeName})`
  return LazyComponent
}

/**
 * Feature-based code splitting helper
 */
export function createFeatureComponent<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  featureName: string,
  fallback?: ComponentType
) {
  const LazyComponent = lazy(async () => {
    const startTime = performance.now()
    try {
      const component = await importFn()
      const loadTime = performance.now() - startTime
      
      if (typeof window !== 'undefined') {
        console.log(`Feature "${featureName}" loaded in ${loadTime.toFixed(2)}ms`)
        performance.mark(`feature-${featureName}-loaded`)
      }
      
      return component
    } catch (error) {
      console.error(`Failed to load feature "${featureName}":`, error)
      throw error
    }
  })

  LazyComponent.displayName = `LazyFeature(${featureName})`
  return LazyComponent
}

/**
 * Vendor library code splitting helper
 */
export function createVendorComponent<T>(
  importFn: () => Promise<T>,
  vendorName: string
): Promise<T> {
  const startTime = performance.now()
  
  return importFn().then(
    (module) => {
      const loadTime = performance.now() - startTime
      if (typeof window !== 'undefined') {
        console.log(`Vendor "${vendorName}" loaded in ${loadTime.toFixed(2)}ms`)
        performance.mark(`vendor-${vendorName}-loaded`)
      }
      return module
    },
    (error) => {
      console.error(`Failed to load vendor "${vendorName}":`, error)
      throw error
    }
  )
}

/**
 * Dynamic import with retry logic
 */
export async function dynamicImportWithRetry<T>(
  importFn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  let lastError: Error

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await importFn()
    } catch (error) {
      lastError = error as Error
      
      if (attempt === maxRetries) {
        throw lastError
      }
      
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay * attempt))
    }
  }
  
  throw lastError!
}

/**
 * Preload strategy for code splitting
 */
export class CodeSplittingPreloader {
  private preloadedModules = new Set<string>()
  private preloadPromises = new Map<string, Promise<any>>()

  /**
   * Preload a module
   */
  preload<T>(
    key: string,
    importFn: () => Promise<T>
  ): Promise<T> {
    if (this.preloadPromises.has(key)) {
      return this.preloadPromises.get(key)!
    }

    const promise = importFn().then(module => {
      this.preloadedModules.add(key)
      return module
    })

    this.preloadPromises.set(key, promise)
    return promise
  }

  /**
   * Check if module is preloaded
   */
  isPreloaded(key: string): boolean {
    return this.preloadedModules.has(key)
  }

  /**
   * Preload multiple modules
   */
  preloadMultiple(modules: Record<string, () => Promise<any>>): Promise<any[]> {
    const promises = Object.entries(modules).map(([key, importFn]) =>
      this.preload(key, importFn)
    )
    return Promise.all(promises)
  }

  /**
   * Clear preloaded modules
   */
  clear(): void {
    this.preloadedModules.clear()
    this.preloadPromises.clear()
  }
}

// Global preloader instance
export const globalCodeSplittingPreloader = new CodeSplittingPreloader()

/**
 * Smart preloading based on user behavior
 */
export class SmartPreloader {
  private intersectionObserver?: IntersectionObserver
  private hoverTimeouts = new Map<string, NodeJS.Timeout>()

  constructor(private preloader: CodeSplittingPreloader = globalCodeSplittingPreloader) {}

  /**
   * Preload on hover with delay
   */
  preloadOnHover<T>(
    element: HTMLElement,
    key: string,
    importFn: () => Promise<T>,
    delay: number = 200
  ): void {
    const handleMouseEnter = () => {
      const timeout = setTimeout(() => {
        this.preloader.preload(key, importFn)
      }, delay)
      
      this.hoverTimeouts.set(key, timeout)
    }

    const handleMouseLeave = () => {
      const timeout = this.hoverTimeouts.get(key)
      if (timeout) {
        clearTimeout(timeout)
        this.hoverTimeouts.delete(key)
      }
    }

    element.addEventListener('mouseenter', handleMouseEnter)
    element.addEventListener('mouseleave', handleMouseLeave)

    // Cleanup function
    return () => {
      element.removeEventListener('mouseenter', handleMouseEnter)
      element.removeEventListener('mouseleave', handleMouseLeave)
      const timeout = this.hoverTimeouts.get(key)
      if (timeout) {
        clearTimeout(timeout)
        this.hoverTimeouts.delete(key)
      }
    }
  }

  /**
   * Preload when element becomes visible
   */
  preloadOnVisible<T>(
    element: HTMLElement,
    key: string,
    importFn: () => Promise<T>,
    rootMargin: string = '50px'
  ): void {
    if (!this.intersectionObserver) {
      this.intersectionObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              const elementKey = entry.target.getAttribute('data-preload-key')
              if (elementKey) {
                // Trigger preload for this element
                // This would need to be connected to the import function
              }
            }
          })
        },
        { rootMargin }
      )
    }

    element.setAttribute('data-preload-key', key)
    this.intersectionObserver.observe(element)
  }

  /**
   * Cleanup observers
   */
  cleanup(): void {
    if (this.intersectionObserver) {
      this.intersectionObserver.disconnect()
    }
    this.hoverTimeouts.forEach(timeout => clearTimeout(timeout))
    this.hoverTimeouts.clear()
  }
}

/**
 * Code splitting configuration
 */
export interface CodeSplittingConfig {
  routes: Record<string, () => Promise<{ default: ComponentType<any> }>>
  features: Record<string, () => Promise<{ default: ComponentType<any> }>>
  vendors: Record<string, () => Promise<any>>
  preloadStrategy: 'hover' | 'visible' | 'immediate' | 'none'
  retryConfig: {
    maxRetries: number
    delay: number
  }
}

/**
 * Code splitting manager
 */
export class CodeSplittingManager {
  private config: CodeSplittingConfig
  private preloader: SmartPreloader

  constructor(config: CodeSplittingConfig) {
    this.config = config
    this.preloader = new SmartPreloader()
  }

  /**
   * Initialize code splitting
   */
  initialize(): void {
    // Preload based on strategy
    if (this.config.preloadStrategy === 'immediate') {
      this.preloadAll()
    }
  }

  /**
   * Preload all modules
   */
  private preloadAll(): void {
    const allModules = {
      ...this.config.routes,
      ...this.config.features,
      ...this.config.vendors
    }

    globalCodeSplittingPreloader.preloadMultiple(allModules)
  }

  /**
   * Get route component
   */
  getRouteComponent(routeName: string): ComponentType<any> | null {
    const importFn = this.config.routes[routeName]
    if (!importFn) return null

    return createRouteComponent(importFn, routeName)
  }

  /**
   * Get feature component
   */
  getFeatureComponent(featureName: string): ComponentType<any> | null {
    const importFn = this.config.features[featureName]
    if (!importFn) return null

    return createFeatureComponent(importFn, featureName)
  }

  /**
   * Cleanup
   */
  cleanup(): void {
    this.preloader.cleanup()
  }
}