# Performance Optimization Utilities

A comprehensive suite of performance optimization utilities for React applications, including lazy loading, performance monitoring, bundle analysis, and resource optimization.

## Features

### 🚀 Lazy Loading
- **Component Lazy Loading**: Lazy load React components with customizable fallbacks
- **Image Lazy Loading**: Intersection Observer-based image lazy loading with placeholders
- **Content Lazy Loading**: Load content when elements become visible
- **Smart Preloading**: Preload components on hover or visibility

### 📊 Performance Monitoring
- **Web Vitals Tracking**: Monitor CLS, FID, FCP, LCP, TTFB
- **Resource Timing**: Track navigation and resource loading performance
- **Long Task Detection**: Identify performance bottlenecks
- **Custom Metrics**: Record and analyze custom performance metrics

### 📦 Bundle Analysis
- **Bundle Size Analysis**: Analyze JavaScript bundle sizes and load times
- **Code Splitting Effectiveness**: Measure code splitting performance
- **Chunk Loading Tracking**: Monitor dynamic import performance
- **Optimization Recommendations**: Get actionable performance recommendations

### 🔗 Resource Optimization
- **Resource Hints**: Preload, prefetch, preconnect, and DNS prefetch
- **Smart Resource Loading**: Automatic resource hint detection
- **Performance Metrics**: Track resource hint effectiveness

## Quick Start

```typescript
import { 
  createLazyComponent,
  LazyImage,
  useLazyLoad,
  usePerformanceMonitoring,
  useResourceHints
} from '@/lib/performance'

// Lazy load a component
const LazyChart = createLazyComponent(
  () => import('./Chart'),
  'Chart'
)

// Use in your component
function MyComponent() {
  const { preload, prefetch } = useResourceHints()
  const { recordMetric } = usePerformanceMonitoring()
  
  // Preload critical resources
  useEffect(() => {
    preload([
      { href: '/api/data', as: 'fetch' },
      { href: '/hero-image.jpg', as: 'image' }
    ])
  }, [])

  return (
    <div>
      <LazyImage 
        src="/hero-image.jpg" 
        alt="Hero" 
        onLoad={() => recordMetric('Hero Image Load', performance.now())}
      />
      <LazyChart />
    </div>
  )
}
```

## API Reference

### Lazy Loading

#### `createLazyComponent(importFn, fallback?)`
Creates a lazy-loaded React component with Suspense boundary.

```typescript
const LazyComponent = createLazyComponent(
  () => import('./MyComponent'),
  CustomLoadingSpinner
)
```

#### `createTrackedLazyComponent(importFn, componentName, fallback?)`
Creates a lazy component with performance tracking.

```typescript
const TrackedComponent = createTrackedLazyComponent(
  () => import('./MyComponent'),
  'MyComponent'
)
```

#### `useLazyLoad(loadFn, dependencies?)`
Hook for lazy loading content when element becomes visible.

```typescript
const { data, loading, error, ref } = useLazyLoad(
  async () => {
    const response = await fetch('/api/data')
    return response.json()
  }
)
```

#### `LazyImage`
Component for lazy loading images with intersection observer.

```typescript
<LazyImage
  src="/image.jpg"
  alt="Description"
  placeholder="/placeholder.jpg"
  onLoad={() => console.log('Image loaded')}
  onError={(error) => console.error('Image failed', error)}
/>
```

#### `withLazyLoading(Component, fallback?)`
Higher-order component for lazy loading any component.

```typescript
const LazyWrappedComponent = withLazyLoading(MyComponent)
```

### Performance Monitoring

#### `usePerformanceMonitoring()`
Hook for performance monitoring in React components.

```typescript
const { recordMetric, getMetrics, generateReport } = usePerformanceMonitoring()

// Record custom metric
recordMetric('API Call Duration', 150)

// Generate performance report
const report = generateReport()
```

#### `PerformanceMonitor`
Singleton class for global performance monitoring.

```typescript
const monitor = PerformanceMonitor.getInstance()
monitor.startMonitoring()

// Record metrics
monitor.recordMetric('Custom Metric', 100)

// Get all metrics
const metrics = monitor.getMetrics()
```

#### `withPerformanceMonitoring(Component, componentName)`
HOC for automatic component performance tracking.

```typescript
const MonitoredComponent = withPerformanceMonitoring(MyComponent, 'MyComponent')
```

### Bundle Analysis

#### `useBundleAnalysis()`
Hook for bundle analysis in React components.

```typescript
const { 
  analyzeBundleLoading, 
  analyzeCodeSplitting, 
  generateOptimizationReport 
} = useBundleAnalysis()

// Analyze bundle performance
const bundleReport = await analyzeBundleLoading()
const optimizationReport = generateOptimizationReport()
```

#### `BundleAnalyzer`
Singleton class for bundle analysis.

```typescript
const analyzer = BundleAnalyzer.getInstance()
analyzer.monitorWebpackChunks()

const report = analyzer.generateOptimizationReport()
```

### Resource Optimization

#### `useResourceHints()`
Hook for managing resource hints.

```typescript
const { preload, prefetch, preconnect, dnsPrefetch } = useResourceHints()

// Preload critical resources
preload([
  { href: '/critical.css', as: 'style' },
  { href: '/hero.jpg', as: 'image' }
])

// Prefetch next page resources
prefetch([{ href: '/next-page' }])

// Preconnect to external domains
preconnect(['https://api.example.com'])
```

#### `ResourceHintsManager`
Singleton class for resource hint management.

```typescript
const manager = ResourceHintsManager.getInstance()

manager.preloadCriticalResources([
  { href: '/app.js', as: 'script' }
])

manager.preconnectToDomains([
  'https://fonts.googleapis.com'
])
```

#### `initializeResourceHints()`
Initialize automatic resource hint optimization.

```typescript
import { initializeResourceHints } from '@/lib/performance'

// Call once in your app initialization
initializeResourceHints()
```

### Code Splitting

#### `createRouteComponent(importFn, routeName)`
Create route-based lazy components with performance tracking.

```typescript
const HomePage = createRouteComponent(
  () => import('./pages/Home'),
  'Home'
)
```

#### `createFeatureComponent(importFn, featureName, fallback?)`
Create feature-based lazy components.

```typescript
const ChatFeature = createFeatureComponent(
  () => import('./features/Chat'),
  'Chat'
)
```

#### `dynamicImportWithRetry(importFn, maxRetries?, delay?)`
Dynamic import with retry logic for better reliability.

```typescript
const module = await dynamicImportWithRetry(
  () => import('./unreliable-module'),
  3, // max retries
  1000 // delay between retries
)
```

#### `CodeSplittingManager`
Manage code splitting configuration and strategies.

```typescript
const manager = new CodeSplittingManager({
  routes: {
    home: () => import('./pages/Home'),
    about: () => import('./pages/About')
  },
  features: {
    chat: () => import('./features/Chat')
  },
  preloadStrategy: 'hover'
})

manager.initialize()
```

## Performance Hooks

### `useDebounce(value, delay)`
Debounce values to reduce unnecessary re-renders.

```typescript
const debouncedSearchTerm = useDebounce(searchTerm, 300)
```

### `useThrottle(callback, delay)`
Throttle function calls to improve performance.

```typescript
const throttledScroll = useThrottle(handleScroll, 100)
```

### `useVirtualization(itemCount, scrollTop, options)`
Virtualize large lists for better performance.

```typescript
const { startIndex, endIndex, totalHeight, offsetY } = useVirtualization(
  1000, // item count
  scrollTop,
  { itemHeight: 50, containerHeight: 400 }
)
```

## Best Practices

### 1. Lazy Loading Strategy
- Use route-based splitting for different pages
- Implement feature-based splitting for large features
- Preload components on user interaction (hover, focus)
- Use intersection observer for content below the fold

### 2. Performance Monitoring
- Monitor Web Vitals continuously
- Set up alerts for performance regressions
- Track custom metrics relevant to your application
- Generate regular performance reports

### 3. Bundle Optimization
- Analyze bundle sizes regularly
- Implement code splitting for large dependencies
- Use tree shaking to eliminate dead code
- Monitor chunk loading performance

### 4. Resource Optimization
- Preload critical resources
- Prefetch resources for likely next navigation
- Preconnect to external domains
- Use appropriate resource hints based on priority

## Examples

### Complete Performance Setup

```typescript
// app/layout.tsx
import { initializeResourceHints } from '@/lib/performance'

export default function RootLayout({ children }) {
  useEffect(() => {
    // Initialize performance optimizations
    initializeResourceHints()
    
    // Start performance monitoring
    const monitor = PerformanceMonitor.getInstance()
    monitor.startMonitoring()
    
    return () => {
      monitor.stopMonitoring()
    }
  }, [])

  return (
    <html>
      <body>{children}</body>
    </html>
  )
}
```

### Lazy Loading with Performance Tracking

```typescript
// components/Dashboard.tsx
import { 
  createTrackedLazyComponent,
  usePerformanceMonitoring,
  LazyImage 
} from '@/lib/performance'

const LazyChart = createTrackedLazyComponent(
  () => import('./Chart'),
  'Dashboard Chart'
)

export default function Dashboard() {
  const { recordMetric } = usePerformanceMonitoring()
  
  useEffect(() => {
    const startTime = performance.now()
    
    return () => {
      const renderTime = performance.now() - startTime
      recordMetric('Dashboard Render Time', renderTime)
    }
  }, [])

  return (
    <div>
      <LazyImage 
        src="/dashboard-hero.jpg"
        alt="Dashboard"
        onLoad={() => recordMetric('Dashboard Hero Load', performance.now())}
      />
      <LazyChart />
    </div>
  )
}
```

### Smart Resource Preloading

```typescript
// components/Navigation.tsx
import { useResourceHints, usePreloadOnHover } from '@/lib/performance'

export default function Navigation() {
  const { prefetch } = useResourceHints()
  const preloadProps = usePreloadOnHover(
    () => import('../pages/Dashboard')
  )

  return (
    <nav>
      <Link 
        href="/dashboard" 
        {...preloadProps}
        onFocus={() => prefetch([{ href: '/dashboard' }])}
      >
        Dashboard
      </Link>
    </nav>
  )
}
```

## Demo

Visit `/performance` to see a comprehensive demo of all performance utilities in action, including:

- Lazy loading components and images
- Performance monitoring and reporting
- Bundle analysis and optimization recommendations
- Resource hint management and metrics

## Browser Support

- Modern browsers with IntersectionObserver support
- Fallbacks provided for older browsers
- Performance API features gracefully degrade

## Contributing

When adding new performance utilities:

1. Follow the existing patterns and naming conventions
2. Include TypeScript types and JSDoc comments
3. Add comprehensive error handling
4. Include performance metrics and monitoring
5. Update this README with new features
6. Add examples to the demo page