// Performance optimization utilities
export * from './lazy-loading'

// Additional performance utilities
export { default as useDebounce } from './hooks/useDebounce'
export { default as useThrottle } from './hooks/useThrottle'
export { default as useMemoizedCallback } from './hooks/useMemoizedCallback'
export { default as useVirtualization } from './hooks/useVirtualization'

// Performance monitoring
export * from './monitoring/performance-monitor'
export * from './monitoring/bundle-analyzer'

// Optimization helpers
export * from './optimization/code-splitting'
export * from './optimization/resource-hints'

// Re-export React for components that need it
export { default as React } from 'react'