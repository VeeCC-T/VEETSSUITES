import { useState, useEffect, useMemo } from 'react'

interface VirtualizationOptions {
  itemHeight: number
  containerHeight: number
  overscan?: number
}

interface VirtualizationResult {
  startIndex: number
  endIndex: number
  visibleItems: number
  totalHeight: number
  offsetY: number
}

/**
 * Hook for virtualizing large lists to improve performance
 */
export default function useVirtualization(
  itemCount: number,
  scrollTop: number,
  options: VirtualizationOptions
): VirtualizationResult {
  const { itemHeight, containerHeight, overscan = 5 } = options

  return useMemo(() => {
    const visibleItems = Math.ceil(containerHeight / itemHeight)
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan)
    const endIndex = Math.min(
      itemCount - 1,
      startIndex + visibleItems + overscan * 2
    )

    return {
      startIndex,
      endIndex,
      visibleItems,
      totalHeight: itemCount * itemHeight,
      offsetY: startIndex * itemHeight
    }
  }, [itemCount, scrollTop, itemHeight, containerHeight, overscan])
}