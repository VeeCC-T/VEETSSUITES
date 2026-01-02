// API mocks for testing
export const mockApiResponses = {
  // Auth API mocks
  auth: {
    login: { token: 'mock-token', user: { id: 1, username: 'testuser' } },
    register: { token: 'mock-token', user: { id: 1, username: 'testuser' } },
    profile: { id: 1, username: 'testuser', email: 'test@example.com' },
  },
  
  // Portfolio API mocks
  portfolio: {
    list: [{ id: 1, title: 'Test Portfolio', user: 1 }],
    detail: { id: 1, title: 'Test Portfolio', user: 1, items: [] },
  },
  
  // PHARMXAM API mocks
  pharmxam: {
    exams: [{ id: 1, title: 'Test Exam', questions: [] }],
    results: { score: 85, passed: true },
  },
  
  // HUB3660 API mocks
  hub3660: {
    courses: [{ id: 1, title: 'Test Course', instructor: 'Test Instructor' }],
    sessions: [{ id: 1, title: 'Test Session', course: 1 }],
  },
  
  // HEALTHEE API mocks
  healthee: {
    consultations: [{ id: 1, type: 'general', status: 'active' }],
    messages: [{ id: 1, content: 'Test message', is_ai_response: false }],
  },
};

export const mockApiError = {
  response: {
    status: 400,
    data: { error: 'Mock API error' },
  },
};