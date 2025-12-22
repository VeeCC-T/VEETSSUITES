'use client'

import React from 'react'

export default function LazyChart() {
  // Simulate a heavy chart component
  const data = Array.from({ length: 12 }, (_, i) => ({
    month: new Date(2024, i).toLocaleDateString('en', { month: 'short' }),
    value: Math.floor(Math.random() * 100) + 20
  }))

  return (
    <div className="bg-white border rounded-lg p-4">
      <h3 className="text-lg font-medium mb-4">Performance Chart (Lazy Loaded)</h3>
      <div className="h-64 flex items-end space-x-2">
        {data.map((item, index) => (
          <div key={index} className="flex-1 flex flex-col items-center">
            <div
              className="bg-blue-500 w-full rounded-t transition-all duration-1000 ease-out"
              style={{ 
                height: `${(item.value / 120) * 100}%`,
                animationDelay: `${index * 100}ms`
              }}
            />
            <span className="text-xs mt-2 text-gray-600">{item.month}</span>
          </div>
        ))}
      </div>
      <p className="text-sm text-gray-500 mt-4">
        This chart was lazy loaded when the component became visible.
      </p>
    </div>
  )
}