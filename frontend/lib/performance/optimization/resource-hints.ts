import React from 'react'

/**
 * Resource hints utilities for performance optimization
 */

export type ResourceHintType = 'preload' | 'prefetch' | 'preconnect' | 'dns-prefetch' | 'modulepreload'

export interface ResourceHint {
  href: string
  as?: string
  type?: string
  crossorigin?: 'anonymous' | 'use-credentials'
  media?: string
}

/**
 * Resource hints manager
 */
export class ResourceHintsManager {
  private static instance: ResourceHintsManager
  private addedHints = new Set<string>()

  static getInstance(): ResourceHintsManager {
    if (!ResourceHintsManager.instance) {
      ResourceHintsManager.instance = new ResourceHintsManager()
    }
    return ResourceHintsManager.instance
  }

  /**
   * Add a resource hint to the document head
   */
  addResourceHint(type: ResourceHintType, hint: ResourceHint): void {
    if (typeof document === 'undefined') return

    const key = `${type}-${hint.href}`
    if (this.addedHints.has(key)) return

    const link = document.createElement('link')
    link.rel = type
    link.href = hint.href

    if (hint.as) link.setAttribute('as', hint.as)
    if (hint.type) link.setAttribute('type', hint.type)
    if (hint.crossorigin) link.setAttribute('crossorigin', hint.crossorigin)
    if (hint.media) link.setAttribute('media', hint.media)

    document.head.appendChild(link)
    this.addedHints.add(key)
  }

  /**
   * Preload critical resources
   */
  preloadCriticalResources(resources: ResourceHint[]): void {
    resources.forEach(resource => {
      this.addResourceHint('preload', resource)
    })
  }

  /**
   * Prefetch resources for future navigation
   */
  prefetchResources(resources: ResourceHint[]): void {
    resources.forEach(resource => {
      this.addResourceHint('prefetch', resource)
    })
  }

  /**
   * Preconnect to external domains
   */
  preconnectToDomains(domains: string[]): void {
    domains.forEach(domain => {
      this.addResourceHint('preconnect', { href: domain })
    })
  }

  /**
   * DNS prefetch for external domains
   */
  dnsPrefetchDomains(domains: string[]): void {
    domains.forEach(domain => {
      this.addResourceHint('dns-prefetch', { href: domain })
    })
  }

  /**
   * Preload JavaScript modules
   */
  preloadModules(modules: string[]): void {
    modules.forEach(module => {
      this.addResourceHint('modulepreload', { href: module })
    })
  }

  /**
   * Smart resource hints based on user behavior
   */
  addSmartHints(): void {
    // Preconnect to common external domains
    this.preconnectToDomains([
      'https://fonts.googleapis.com',
      'https://fonts.gstatic.com',
      'https://api.example.com'
    ])

    // DNS prefetch for analytics and other third-party services
    this.dnsPrefetchDomains([
      'https://www.google-analytics.com',
      'https://www.googletagmanager.com'
    ])
  }

  /**
   * Remove resource hint
   */
  removeResourceHint(type: ResourceHintType, href: string): void {
    if (typeof document === 'undefined') return

    const key = `${type}-${href}`
    if (!this.addedHints.has(key)) return

    const link = document.querySelector(`link[rel="${type}"][href="${href}"]`)
    if (link) {
      document.head.removeChild(link)
      this.addedHints.delete(key)
    }
  }

  /**
   * Clear all added hints
   */
  clearHints(): void {
    if (typeof document === 'undefined') return

    this.addedHints.forEach(key => {
      const [type, href] = key.split('-', 2)
      const link = document.querySelector(`link[rel="${type}"][href="${href}"]`)
      if (link) {
        document.head.removeChild(link)
      }
    })

    this.addedHints.clear()
  }

  /**
   * Get performance metrics for resource hints
   */
  getHintMetrics(): {
    totalHints: number
    hintsByType: Record<ResourceHintType, number>
    unusedHints: string[]
  } {
    const hintsByType: Record<ResourceHintType, number> = {
      preload: 0,
      prefetch: 0,
      preconnect: 0,
      'dns-prefetch': 0,
      modulepreload: 0
    }

    const unusedHints: string[] = []

    this.addedHints.forEach(key => {
      const [type] = key.split('-', 2) as [ResourceHintType, string]
      hintsByType[type]++

      // Check if resource was actually used (simplified check)
      if (typeof window !== 'undefined' && window.performance) {
        const [, href] = key.split('-', 2)
        const resourceEntries = performance.getEntriesByName(href)
        if (resourceEntries.length === 0) {
          unusedHints.push(key)
        }
      }
    })

    return {
      totalHints: this.addedHints.size,
      hintsByType,
      unusedHints
    }
  }
}

/**
 * Hook for using resource hints in React components
 */
export function useResourceHints() {
  const manager = ResourceHintsManager.getInstance()

  React.useEffect(() => {
    manager.addSmartHints()
  }, [])

  return {
    preload: (resources: ResourceHint[]) => manager.preloadCriticalResources(resources),
    prefetch: (resources: ResourceHint[]) => manager.prefetchResources(resources),
    preconnect: (domains: string[]) => manager.preconnectToDomains(domains),
    dnsPrefetch: (domains: string[]) => manager.dnsPrefetchDomains(domains),
    preloadModules: (modules: string[]) => manager.preloadModules(modules),
    getMetrics: () => manager.getHintMetrics()
  }
}

/**
 * Automatic resource hint detection
 */
export class AutoResourceHints {
  private manager: ResourceHintsManager
  private observer?: MutationObserver

  constructor() {
    this.manager = ResourceHintsManager.getInstance()
  }

  /**
   * Start automatic detection of resources that should be hinted
   */
  startAutoDetection(): void {
    if (typeof document === 'undefined') return

    // Observe DOM changes to detect new resources
    this.observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            this.analyzeElement(node as Element)
          }
        })
      })
    })

    this.observer.observe(document.body, {
      childList: true,
      subtree: true
    })

    // Analyze existing elements
    this.analyzeExistingElements()
  }

  /**
   * Stop automatic detection
   */
  stopAutoDetection(): void {
    if (this.observer) {
      this.observer.disconnect()
      this.observer = undefined
    }
  }

  /**
   * Analyze existing elements for resource hints
   */
  private analyzeExistingElements(): void {
    // Analyze images for preloading
    const images = document.querySelectorAll('img[data-preload="true"]')
    images.forEach(img => {
      const src = img.getAttribute('src')
      if (src) {
        this.manager.addResourceHint('preload', { href: src, as: 'image' })
      }
    })

    // Analyze links for prefetching
    const links = document.querySelectorAll('a[data-prefetch="true"]')
    links.forEach(link => {
      const href = link.getAttribute('href')
      if (href) {
        this.manager.addResourceHint('prefetch', { href })
      }
    })
  }

  /**
   * Analyze a single element for resource hints
   */
  private analyzeElement(element: Element): void {
    // Check for images that should be preloaded
    if (element.tagName === 'IMG' && element.getAttribute('data-preload') === 'true') {
      const src = element.getAttribute('src')
      if (src) {
        this.manager.addResourceHint('preload', { href: src, as: 'image' })
      }
    }

    // Check for links that should be prefetched
    if (element.tagName === 'A' && element.getAttribute('data-prefetch') === 'true') {
      const href = element.getAttribute('href')
      if (href) {
        this.manager.addResourceHint('prefetch', { href })
      }
    }

    // Check for external scripts/stylesheets
    if (element.tagName === 'SCRIPT' || element.tagName === 'LINK') {
      const src = element.getAttribute('src') || element.getAttribute('href')
      if (src && this.isExternalResource(src)) {
        const domain = new URL(src).origin
        this.manager.addResourceHint('preconnect', { href: domain })
      }
    }
  }

  /**
   * Check if resource is external
   */
  private isExternalResource(url: string): boolean {
    try {
      const resourceUrl = new URL(url, window.location.href)
      return resourceUrl.origin !== window.location.origin
    } catch {
      return false
    }
  }
}

// Global auto resource hints instance
export const autoResourceHints = new AutoResourceHints()

/**
 * Initialize resource hints optimization
 */
export function initializeResourceHints(): void {
  const manager = ResourceHintsManager.getInstance()
  
  // Add smart hints
  manager.addSmartHints()
  
  // Start auto detection
  autoResourceHints.startAutoDetection()
  
  // Cleanup on page unload
  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', () => {
      autoResourceHints.stopAutoDetection()
    })
  }
}