/**
 * Test data generators and fixtures for frontend tests
 */

export const mockUser = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
  role: 'student' as const,
  is_active: true,
};

export const mockInstructor = {
  ...mockUser,
  id: 2,
  username: 'instructor',
  email: 'instructor@example.com',
  role: 'instructor' as const,
};

export const mockAdmin = {
  ...mockUser,
  id: 3,
  username: 'admin',
  email: 'admin@example.com',
  role: 'admin' as const,
};

export const mockCourse = {
  id: 1,
  title: 'Test Course',
  description: 'A test course for learning',
  price: 99.99,
  instructor: mockInstructor,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

export const mockExam = {
  id: 1,
  title: 'Test Exam',
  description: 'A test exam',
  questions_count: 10,
  time_limit: 60,
  created_at: '2024-01-01T00:00:00Z',
};

export const mockQuestion = {
  id: 1,
  text: 'What is the capital of France?',
  options: ['London', 'Berlin', 'Paris', 'Madrid'],
  correct_answer: 2,
  explanation: 'Paris is the capital of France',
};

export const mockPortfolio = {
  id: 1,
  user: mockUser,
  cv_file: 'portfolios/test-cv.pdf',
  parsed_content: {
    name: 'Test User',
    email: 'test@example.com',
    skills: ['JavaScript', 'Python', 'React'],
    experience: ['Software Developer at Tech Corp'],
  },
  is_public: true,
  created_at: '2024-01-01T00:00:00Z',
};

export const mockConsultation = {
  id: 1,
  user: mockUser,
  consultation_type: 'ai' as const,
  status: 'active' as const,
  created_at: '2024-01-01T00:00:00Z',
};

export const mockMessage = {
  id: 1,
  consultation: mockConsultation,
  sender: 'user' as const,
  content: 'Hello, I need help with my medication',
  timestamp: '2024-01-01T00:00:00Z',
};

export const mockTransaction = {
  id: 1,
  user: mockUser,
  amount: 99.99,
  currency: 'USD',
  provider: 'stripe' as const,
  status: 'completed' as const,
  created_at: '2024-01-01T00:00:00Z',
};

export const mockSession = {
  id: 1,
  course: mockCourse,
  title: 'Introduction Session',
  scheduled_time: '2024-12-20T10:00:00Z',
  zoom_meeting_id: '123456789',
  zoom_join_url: 'https://zoom.us/j/123456789',
  recording_url: null,
};

// Factory functions for generating test data
export const createMockUser = (overrides: Partial<typeof mockUser> = {}) => ({
  ...mockUser,
  ...overrides,
});

export const createMockCourse = (overrides: Partial<typeof mockCourse> = {}) => ({
  ...mockCourse,
  ...overrides,
});

export const createMockExam = (overrides: Partial<typeof mockExam> = {}) => ({
  ...mockExam,
  ...overrides,
});

export const createMockQuestion = (overrides: Partial<typeof mockQuestion> = {}) => ({
  ...mockQuestion,
  ...overrides,
});

export const createMockPortfolio = (overrides: Partial<typeof mockPortfolio> = {}) => ({
  ...mockPortfolio,
  ...overrides,
});

export const createMockConsultation = (overrides: Partial<typeof mockConsultation> = {}) => ({
  ...mockConsultation,
  ...overrides,
});

export const createMockTransaction = (overrides: Partial<typeof mockTransaction> = {}) => ({
  ...mockTransaction,
  ...overrides,
});

export const createMockSession = (overrides: Partial<typeof mockSession> = {}) => ({
  ...mockSession,
  ...overrides,
});