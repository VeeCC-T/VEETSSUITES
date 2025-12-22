/**
 * HEALTHEE UI Property-Based Tests
 * Tests for health guidance disclaimer property
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import * as fc from 'fast-check';
import { DisclaimerBanner } from '@/components/healthee';
import ConsultationInterface from '@/components/healthee/ConsultationInterface';
import { Consultation, ConsultationMessage } from '@/lib/healthee/types';

// Mock Next.js router
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
  useSearchParams: () => ({
    get: jest.fn(),
  }),
  useParams: () => ({}),
}));

// Mock the healthee API
jest.mock('@/lib/healthee/api', () => ({
  healtheeApi: {
    createConsultation: jest.fn(),
    getConsultation: jest.fn(),
    getMessages: jest.fn(),
    sendMessage: jest.fn(),
    requestPharmacist: jest.fn(),
  },
}));

// Mock auth hook
const mockAuthContext = {
  user: {
    id: 1,
    email: 'test@example.com',
    first_name: 'Test',
    last_name: 'User',
    role: 'student' as const,
  },
  tokens: {
    access: 'mock-access-token',
    refresh: 'mock-refresh-token',
  },
  isAuthenticated: true,
  isLoading: false,
  login: jest.fn(),
  register: jest.fn(),
  logout: jest.fn(),
  refreshAuth: jest.fn(),
};

jest.mock('@/lib/auth', () => ({
  useAuth: () => mockAuthContext,
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// Generators for property testing
const consultationGenerator = fc.record({
  id: fc.integer({ min: 1, max: 1000 }),
  consultation_type: fc.constantFrom('ai', 'human'),
  status: fc.constantFrom('active', 'waiting', 'completed'),
  pharmacist: fc.option(fc.record({
    id: fc.integer({ min: 1, max: 100 }),
    first_name: fc.constantFrom('John', 'Jane', 'Alice', 'Bob', 'Carol'),
    last_name: fc.constantFrom('Doe', 'Smith', 'Johnson', 'Wilson', 'Brown'),
    email: fc.emailAddress(),
  }), { nil: null }),
  created_at: fc.integer({ min: Date.now() - 365 * 24 * 60 * 60 * 1000, max: Date.now() }).map(timestamp => new Date(timestamp).toISOString()),
  completed_at: fc.option(fc.integer({ min: Date.now() - 365 * 24 * 60 * 60 * 1000, max: Date.now() }).map(timestamp => new Date(timestamp).toISOString()), { nil: null }),
});

const disclaimerPropsGenerator = fc.record({
  dismissible: fc.boolean(),
  compact: fc.boolean(),
  className: fc.option(fc.constantFrom('', 'mb-4', 'mt-8', 'custom-class'), { nil: '' }),
});

describe('HEALTHEE UI Property Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    const { healtheeApi } = require('@/lib/healthee/api');
    healtheeApi.getMessages.mockResolvedValue([]);
    healtheeApi.sendMessage.mockResolvedValue({
      id: 1,
      message: 'Test message',
      sender: mockAuthContext.user,
      is_ai_response: false,
      created_at: new Date().toISOString(),
    });
    healtheeApi.requestPharmacist.mockResolvedValue({ success: true });
    healtheeApi.getConsultation.mockResolvedValue({
      id: 1,
      consultation_type: 'ai',
      status: 'active',
      pharmacist: null,
      created_at: new Date().toISOString(),
      completed_at: null,
    });

    // Clear sessionStorage before each test
    Object.defineProperty(window, 'sessionStorage', {
      value: {
        getItem: jest.fn(() => null),
        setItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn(),
      },
      writable: true,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // Feature: veetssuites-platform, Property 40: Health guidance includes disclaimer
  describe('Property 40: Health guidance includes disclaimer', () => {
    it('should display medical disclaimer with required content on all health guidance pages', () => {
      fc.assert(fc.property(disclaimerPropsGenerator, (props) => {
        const { unmount } = render(<DisclaimerBanner {...props} />);
        
        // Should display "Medical Disclaimer" title
        expect(screen.getAllByText('Medical Disclaimer')[0]).toBeInTheDocument();
        
        // Should include the key disclaimer text about HEALTHEE being a guide only
        expect(screen.getAllByText(/HEALTHEE is a guide only/i)[0]).toBeInTheDocument();
        
        // Should include warning about not substituting professional medical advice
        expect(screen.getAllByText(/not a substitute for professional medical advice/i)[0]).toBeInTheDocument();
        
        // Should include instruction to contact physician (different text for compact vs full)
        const physicianText = screen.queryAllByText(/contact.*physician.*medical advice/i);
        const consultText = screen.queryAllByText(/consult.*physician/i);
        expect(physicianText.length > 0 || consultText.length > 0).toBe(true);
        
        // Should have proper ARIA attributes for accessibility
        const disclaimerElements = screen.getAllByRole('alert');
        expect(disclaimerElements[0]).toHaveAttribute('aria-labelledby', 'medical-disclaimer-title');
        
        // Should have warning icon
        const warningIcon = disclaimerElements[0].querySelector('svg');
        expect(warningIcon).toBeInTheDocument();
        expect(warningIcon).toHaveAttribute('aria-hidden', 'true');
        
        // Should have proper styling (yellow background for warning)
        expect(disclaimerElements[0]).toHaveClass('bg-yellow-50', 'border-yellow-200');
        
        unmount();
      }), { numRuns: 50 });
    });

    it('should display disclaimer in both compact and full formats with required content', () => {
      fc.assert(fc.property(fc.boolean(), (compact) => {
        const { unmount } = render(<DisclaimerBanner compact={compact} />);
        
        // Both formats should include the essential disclaimer content
        expect(screen.getByText('Medical Disclaimer')).toBeInTheDocument();
        expect(screen.getByText(/HEALTHEE is a guide only/i)).toBeInTheDocument();
        
        if (compact) {
          // Compact format should still include key warning
          expect(screen.getByText(/not a substitute for professional medical advice/i)).toBeInTheDocument();
          expect(screen.getByText(/consult your physician/i)).toBeInTheDocument();
        } else {
          // Full format should include comprehensive disclaimer
          expect(screen.getByText(/seek the advice of your physician/i)).toBeInTheDocument();
          expect(screen.getByText(/Never disregard professional medical advice/i)).toBeInTheDocument();
          expect(screen.getByText(/contact a physician for medical advice/i)).toBeInTheDocument();
        }
        
        unmount();
      }), { numRuns: 30 });
    });

    it('should maintain disclaimer visibility and accessibility regardless of dismissible state', () => {
      fc.assert(fc.property(fc.boolean(), (dismissible) => {
        const { unmount } = render(<DisclaimerBanner dismissible={dismissible} />);
        
        // Should always display disclaimer content initially
        expect(screen.getByText('Medical Disclaimer')).toBeInTheDocument();
        expect(screen.getByText(/HEALTHEE is a guide only/i)).toBeInTheDocument();
        
        // Should have proper accessibility attributes
        const disclaimerElements = screen.getAllByRole('alert');
        expect(disclaimerElements[0]).toBeInTheDocument();
        
        if (dismissible) {
          // Should have dismiss button when dismissible
          const dismissButton = screen.getByLabelText('Dismiss medical disclaimer');
          expect(dismissButton).toBeInTheDocument();
          expect(dismissButton).toHaveAttribute('type', 'button');
          
          // Dismiss button should have proper accessibility
          expect(screen.getByText('Dismiss')).toBeInTheDocument(); // Screen reader text
        } else {
          // Should not have dismiss button when not dismissible
          expect(screen.queryByLabelText('Dismiss medical disclaimer')).not.toBeInTheDocument();
        }
        
        unmount();
      }), { numRuns: 30 });
    });

    it('should display disclaimer prominently in health guidance contexts', () => {
      fc.assert(fc.property(disclaimerPropsGenerator, (props) => {
        const { unmount } = render(
          <div>
            <DisclaimerBanner {...props} />
            <div data-testid="health-content">
              <h2>Health Guidance Content</h2>
              <p>This is sample health guidance content that should be accompanied by a disclaimer.</p>
            </div>
          </div>
        );
        
        // Disclaimer should be present alongside health content
        expect(screen.getAllByText('Medical Disclaimer')[0]).toBeInTheDocument();
        expect(screen.getAllByText(/HEALTHEE is a guide only/i)[0]).toBeInTheDocument();
        
        // Health content should also be present
        expect(screen.getByTestId('health-content')).toBeInTheDocument();
        expect(screen.getByText('Health Guidance Content')).toBeInTheDocument();
        
        unmount();
      }), { numRuns: 30 });
    });

    it('should ensure disclaimer content is semantically structured for screen readers', () => {
      fc.assert(fc.property(disclaimerPropsGenerator, (props) => {
        const { unmount } = render(<DisclaimerBanner {...props} />);
        
        // Should have proper heading structure
        const headings = screen.getAllByRole('heading', { name: /medical disclaimer/i });
        expect(headings[0]).toBeInTheDocument();
        expect(headings[0]).toHaveAttribute('id', 'medical-disclaimer-title');
        
        // Should have alert role for screen readers
        const alertElements = screen.getAllByRole('alert');
        expect(alertElements[0]).toBeInTheDocument();
        expect(alertElements[0]).toHaveAttribute('aria-labelledby', 'medical-disclaimer-title');
        
        // Should have proper text hierarchy
        expect(screen.getByText(/HEALTHEE is a guide only/i)).toBeInTheDocument();
        
        // Warning icon should be hidden from screen readers
        const warningIcon = alertElements[0].querySelector('svg');
        expect(warningIcon).toHaveAttribute('aria-hidden', 'true');
        
        unmount();
      }), { numRuns: 40 });
    });

    it('should display disclaimer with consistent styling across different configurations', () => {
      fc.assert(fc.property(disclaimerPropsGenerator, (props) => {
        const { unmount } = render(<DisclaimerBanner {...props} />);
        
        const disclaimerElements = screen.getAllByRole('alert');
        
        // Should always have warning-style background and border
        expect(disclaimerElements[0]).toHaveClass('bg-yellow-50');
        expect(disclaimerElements[0]).toHaveClass('border-yellow-200');
        expect(disclaimerElements[0]).toHaveClass('rounded-2xl');
        
        // Should have proper spacing
        expect(disclaimerElements[0]).toHaveClass('p-4');
        
        // Text should have proper warning colors
        const heading = screen.getByText('Medical Disclaimer');
        expect(heading).toHaveClass('text-yellow-800');
        
        // Should include custom className if provided
        if (props.className) {
          expect(disclaimerElements[0]).toHaveClass(props.className);
        }
        
        unmount();
      }), { numRuns: 40 });
    });
  });
});