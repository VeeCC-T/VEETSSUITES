import { useCallback, useRef } from 'react'

/**
 * Hook for creating memoized callbacks with stable references
 */
export default function useMemoizedCallback<T extends (...args: any[]) => any>(
  callback: T,
  dependencies: any[]
): T {
  const callbackRef = useRef<T>(callback)
  const dependenciesRef = useRef(dependencies)

  // Update callback if dependencies changed
  if (
    dependencies.length !== dependenciesRef.current.length ||
    dependencies.some((dep, index) => dep !== dependenciesRef.current[index])
  ) {
    callbackRef.current = callback
    dependenciesRef.current = dependencies
  }

  return useCallback(
    ((...args) => callbackRef.current(...args)) as T,
    []
  )
}