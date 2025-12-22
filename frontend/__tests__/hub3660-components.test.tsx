/**
 * HUB3660 Components Tests
 * Tests for course catalog and detail components
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CourseCatalog, CourseDetail } from '@/components/hub3660';
import type { Course } from '@/lib/hub3660';

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

// Mock fetch API
global.fetch = jest.fn();

// Mock the hub3660 API
jest.mock('@/lib/hub3660', () => ({
  hub3660Api: {
    getCourses: jest.fn(),
    getCourseSessions: jest.fn(),
    enrollInCourse: jest.fn(),
    getSessionRecording: jest.fn(),
    checkEnrollmentStatus: jest.fn(),
    registerForSession: jest.fn(),
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

// Mock the useAuth hook
jest.mock('@/lib/auth', () => ({
  useAuth: () => mockAuthContext,
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

const mockCourses: Course[] = [
  {
    id: 1,
    title: 'Introduction to React',
    description: 'Learn the basics of React development',
    instructor_name: 'John Doe',
    price: '99.99',
    currency: 'USD',
    enrollment_count: 25,
    is_enrolled: false,
    enrollment_status: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    title: 'Advanced JavaScript',
    description: 'Master advanced JavaScript concepts',
    instructor_name: 'Jane Smith',
    price: '0.00',
    currency: 'USD',
    enrollment_count: 15,
    is_enrolled: true,
    enrollment_status: 'completed',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

const renderWithAuth = (component: React.ReactElement) => {
  return render(component);
};

describe('CourseCatalog Component', () => {
  beforeEach(() => {
    const { hub3660Api } = require('@/lib/hub3660');
    hub3660Api.getCourses.mockResolvedValue(mockCourses);
    hub3660Api.checkEnrollmentStatus.mockResolvedValue({
      is_enrolled: false,
      enrollment_status: null,
      enrolled_at: null
    });
    hub3660Api.getCourseSessions.mockResolvedValue([]);
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders course catalog with grid layout', async () => {
    renderWithAuth(<CourseCatalog />);

    // Wait for loading to complete and content to appear
    await waitFor(() => {
      expect(screen.getByText('Course Catalog')).toBeInTheDocument();
    });
    
    await waitFor(() => {
      expect(screen.getByText('Introduction to React')).toBeInTheDocument();
      expect(screen.getByText('Advanced JavaScript')).toBeInTheDocument();
    });

    // Check grid layout classes are present
    const courseGrid = screen.getByText('Introduction to React').closest('.grid');
    expect(courseGrid).toHaveClass('grid-cols-1', 'md:grid-cols-2', 'lg:grid-cols-3');
  });

  it('shows enrollment status per course', async () => {
    renderWithAuth(<CourseCatalog />);

    await waitFor(() => {
      // Should show "Enrolled" badge for enrolled course
      expect(screen.getByText('Enrolled')).toBeInTheDocument();
      
      // Should show different button text based on enrollment
      expect(screen.getByText('View Course')).toBeInTheDocument(); // For enrolled course
      expect(screen.getByText('Learn More')).toBeInTheDocument(); // For non-enrolled course
    });
  });

  it('implements course filtering and search', async () => {
    renderWithAuth(<CourseCatalog />);

    await waitFor(() => {
      expect(screen.getByText('Introduction to React')).toBeInTheDocument();
    });

    // Test search functionality
    const searchInput = screen.getByPlaceholderText(/search by title/i);
    fireEvent.change(searchInput, { target: { value: 'React' } });

    await waitFor(() => {
      expect(screen.getByText('Introduction to React')).toBeInTheDocument();
      expect(screen.queryByText('Advanced JavaScript')).not.toBeInTheDocument();
    });

    // Test price filter
    const priceFilter = screen.getByLabelText('Price');
    fireEvent.change(priceFilter, { target: { value: 'free' } });

    await waitFor(() => {
      // Should show only free courses
      expect(screen.queryByText('Introduction to React')).not.toBeInTheDocument();
    });
  });

  it('displays course count and results', async () => {
    renderWithAuth(<CourseCatalog />);

    await waitFor(() => {
      expect(screen.getByText(/showing \d+ of \d+ courses/i)).toBeInTheDocument();
    });
  });
});

describe('CourseDetail Component', () => {
  const mockCourse = mockCourses[0];

  beforeEach(() => {
    const { hub3660Api } = require('@/lib/hub3660');
    hub3660Api.getCourseSessions.mockResolvedValue([]);
    hub3660Api.checkEnrollmentStatus.mockResolvedValue({
      is_enrolled: false,
      enrollment_status: null,
      enrolled_at: null
    });
    hub3660Api.enrollInCourse.mockResolvedValue({
      message: 'Enrollment successful',
      enrollment_id: 1,
      payment_required: true,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders course detail with enrollment CTA', () => {
    const mockOnEnroll = jest.fn();
    const mockOnBack = jest.fn();

    renderWithAuth(
      <CourseDetail 
        course={mockCourse} 
        onBack={mockOnBack}
      />
    );

    // Check course details are displayed
    expect(screen.getByText('Introduction to React')).toBeInTheDocument();
    expect(screen.getByText('Learn the basics of React development')).toBeInTheDocument();
    expect(screen.getByText('Instructor: John Doe')).toBeInTheDocument();
    expect(screen.getByText('25 students enrolled')).toBeInTheDocument();

    // Check enrollment CTA
    expect(screen.getByText('Enroll for USD 99.99')).toBeInTheDocument();
  });

  it('shows different CTA based on enrollment status', () => {
    const enrolledCourse = { ...mockCourse, is_enrolled: true };
    
    renderWithAuth(
      <CourseDetail course={enrolledCourse} />
    );

    expect(screen.getByText('Already Enrolled')).toBeInTheDocument();
  });

  it('handles back navigation', () => {
    const mockOnBack = jest.fn();

    renderWithAuth(
      <CourseDetail 
        course={mockCourse} 
        onBack={mockOnBack}
      />
    );

    const backButton = screen.getByText('Back to Catalog');
    fireEvent.click(backButton);

    expect(mockOnBack).toHaveBeenCalled();
  });

  it('handles enrollment flow', async () => {
    renderWithAuth(
      <CourseDetail 
        course={mockCourse} 
      />
    );

    const enrollButton = screen.getByText('Enroll for USD 99.99');
    fireEvent.click(enrollButton);

    // Should open confirmation modal
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    const confirmButton = screen.getByRole('button', { name: 'Confirm Enrollment' });
    fireEvent.click(confirmButton);

    // Should trigger enrollment checkout flow
    await waitFor(() => {
      expect(screen.getByText('Course Enrollment')).toBeInTheDocument();
    });
  });

  it('displays free course pricing correctly', () => {
    const freeCourse = { ...mockCourse, price: '0.00' };

    renderWithAuth(
      <CourseDetail course={freeCourse} />
    );

    expect(screen.getByText('Free')).toBeInTheDocument();
    expect(screen.getByText('Enroll for Free')).toBeInTheDocument();
  });
});