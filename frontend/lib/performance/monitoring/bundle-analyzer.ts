/**
 * Bundle analysis utilities for performance optimization
 */

interface BundleInfo {
  name: string
  size: number
  gzipSize?: number
  modules: string[]
  loadTime?: number
}

interface ChunkInfo {
  id: string
  name: string
  size: number
  modules: ModuleInfo[]
  isAsync: boolean
}

interface ModuleInfo {
  id: string
  name: string
  size: number
  reasons: string[]
}

export class BundleAnalyzer {
  private static instance: BundleAnalyzer
  private bundles: Map<string, BundleInfo> = new Map()
  private chunks: Map<string, ChunkInfo> = new Map()

  static getInstance(): BundleAnalyzer {
    if (!BundleAnalyzer.instance) {
      BundleAnalyzer.instance = new BundleAnalyzer()
    }
    return BundleAnalyzer.instance
  }

  /**
   * Analyze bundle loading performance
   */
  analyzeBundleLoading(): Promise<{
    totalSize: number
    loadTime: number
    recommendations: string[]
  }> {
    return new Promise((resolve) => {
      if (typeof window === 'undefined') {
        resolve({ totalSize: 0, loadTime: 0, recommendations: [] })
        return
      }

      const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[]
      const jsResources = resources.filter(resource => 
        resource.name.includes('.js') || resource.name.includes('chunk')
      )

      let totalSize = 0
      let totalLoadTime = 0
      const recommendations: string[] = []

      jsResources.forEach(resource => {
        totalSize += resource.transferSize || 0
        totalLoadTime += resource.duration
      })

      // Generate recommendations
      if (totalSize > 1024 * 1024) { // > 1MB
        recommendations.push('Consider code splitting to reduce initial bundle size')
      }

      if (totalLoadTime > 3000) { // > 3 seconds
        recommendations.push('Optimize bundle loading with resource hints and compression')
      }

      const largeResources = jsResources.filter(r => (r.transferSize || 0) > 100 * 1024)
      if (largeResources.length > 0) {
        recommendations.push(`Large bundles detected: ${largeResources.map(r => r.name).join(', ')}`)
      }

      resolve({
        totalSize,
        loadTime: totalLoadTime,
        recommendations
      })
    })
  }

  /**
   * Track chunk loading performance
   */
  trackChunkLoad(chunkId: string, startTime: number): void {
    const endTime = performance.now()
    const loadTime = endTime - startTime

    const existingChunk = this.chunks.get(chunkId)
    if (existingChunk) {
      // Update load time
      this.chunks.set(chunkId, {
        ...existingChunk,
        // Add load time tracking if needed
      })
    }

    // Record metric
    if (typeof window !== 'undefined' && window.performance) {
      performance.mark(`chunk-${chunkId}-loaded`)
      performance.measure(`chunk-${chunkId}-load-time`, `chunk-${chunkId}-start`, `chunk-${chunkId}-loaded`)
    }
  }

  /**
   * Analyze code splitting effectiveness
   */
  analyzeCodeSplitting(): {
    totalChunks: number
    asyncChunks: number
    averageChunkSize: number
    recommendations: string[]
  } {
    const chunks = Array.from(this.chunks.values())
    const asyncChunks = chunks.filter(chunk => chunk.isAsync)
    const totalSize = chunks.reduce((sum, chunk) => sum + chunk.size, 0)
    const averageChunkSize = chunks.length > 0 ? totalSize / chunks.length : 0

    const recommendations: string[] = []

    if (asyncChunks.length === 0) {
      recommendations.push('No async chunks detected. Consider implementing code splitting.')
    }

    if (averageChunkSize > 500 * 1024) { // > 500KB
      recommendations.push('Average chunk size is large. Consider further splitting.')
    }

    const largeChunks = chunks.filter(chunk => chunk.size > 1024 * 1024) // > 1MB
    if (largeChunks.length > 0) {
      recommendations.push(`Large chunks detected: ${largeChunks.map(c => c.name).join(', ')}`)
    }

    return {
      totalChunks: chunks.length,
      asyncChunks: asyncChunks.length,
      averageChunkSize,
      recommendations
    }
  }

  /**
   * Generate bundle optimization report
   */
  generateOptimizationReport(): {
    bundleAnalysis: any
    codeSplittingAnalysis: any
    recommendations: string[]
  } {
    const bundleAnalysis = this.analyzeBundleLoading()
    const codeSplittingAnalysis = this.analyzeCodeSplitting()

    const allRecommendations = [
      ...codeSplittingAnalysis.recommendations
    ]

    return {
      bundleAnalysis,
      codeSplittingAnalysis,
      recommendations: allRecommendations
    }
  }

  /**
   * Monitor webpack chunk loading (if available)
   */
  monitorWebpackChunks(): void {
    if (typeof window === 'undefined') return

    // Hook into webpack's chunk loading if available
    const webpackChunkName = '__webpack_require__'
    if ((window as any)[webpackChunkName]) {
      const originalChunkLoad = (window as any)[webpackChunkName].e
      if (originalChunkLoad) {
        (window as any)[webpackChunkName].e = (chunkId: string) => {
          const startTime = performance.now()
          performance.mark(`chunk-${chunkId}-start`)
          
          return originalChunkLoad(chunkId).then((result: any) => {
            this.trackChunkLoad(chunkId, startTime)
            return result
          })
        }
      }
    }
  }

  /**
   * Detect unused code (dead code elimination opportunities)
   */
  detectUnusedCode(): {
    unusedModules: string[]
    recommendations: string[]
  } {
    const recommendations: string[] = []
    const unusedModules: string[] = []

    // This would require build-time analysis in a real implementation
    // For now, provide general recommendations
    recommendations.push('Use tree shaking to eliminate unused code')
    recommendations.push('Analyze bundle with webpack-bundle-analyzer')
    recommendations.push('Consider dynamic imports for rarely used features')

    return {
      unusedModules,
      recommendations
    }
  }
}

/**
 * Hook for bundle analysis in React components
 */
export function useBundleAnalysis() {
  const analyzer = BundleAnalyzer.getInstance()

  React.useEffect(() => {
    analyzer.monitorWebpackChunks()
  }, [])

  return {
    analyzeBundleLoading: analyzer.analyzeBundleLoading.bind(analyzer),
    analyzeCodeSplitting: analyzer.analyzeCodeSplitting.bind(analyzer),
    generateOptimizationReport: analyzer.generateOptimizationReport.bind(analyzer)
  }
}