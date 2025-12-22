import React, { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/lib/auth/AuthContext'

// Create a custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        {children}
      </AuthProvider>
    </QueryClientProvider>
  )
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

export * from '@testing-library/react'
export { customRender as render }

// Custom render with specific auth state
export const renderWithAuth = (
  ui: ReactElement,
  authState: {
    isAuthenticated?: boolean
    user?: any
    token?: string
  } = {},
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  const MockAuthProvider = ({ children }: { children: React.ReactNode }) => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    })

    // Mock the auth context value
    const mockAuthValue = {
      isAuthenticated: authState.isAuthenticated ?? false,
      user: authState.user ?? null,
      token: authState.token ?? null,
      login: jest.fn(),
      logout: jest.fn(),
      register: jest.fn(),
      loading: false,
    }

    return (
      <QueryClientProvider client={queryClient}>
        <AuthProvider value={mockAuthValue}>
          {children}
        </AuthProvider>
      </QueryClientProvider>
    )
  }

  return render(ui, { wrapper: MockAuthProvider, ...options })
}

// Utility to wait for loading states to complete
export const waitForLoadingToFinish = () => 
  new Promise(resolve => setTimeout(resolve, 0))

// Utility to create a mock query client
export const createMockQueryClient = () => 
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  })