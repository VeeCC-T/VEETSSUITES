import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock providers for testing
export const MockQueryProvider = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        staleTime: Infinity,
      },
      mutations: {
        retry: false,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

export const MockAuthProvider = ({ children, value }: { children: React.ReactNode; value: any }) => {
  // This would be replaced with actual auth context mock
  return <div data-testid="mock-auth-provider">{children}</div>;
};