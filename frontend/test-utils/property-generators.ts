import fc from 'fast-check';

// Basic data generators
export const validEmail = () => fc.emailAddress();
export const validPassword = () => fc.string({ minLength: 8, maxLength: 128 });
export const validUsername = () => fc.string({ minLength: 3, maxLength: 30 }).filter(s => /^[a-zA-Z0-9_]+$/.test(s));
export const validName = () => fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0);
export const validPhoneNumber = () => fc.string({ minLength: 10, maxLength: 15 }).filter(s => /^\+?[\d\s-()]+$/.test(s));

// User data generators
export const validUserData = () => fc.record({
  username: validUsername(),
  email: validEmail(),
  password: validPassword(),
  firstName: validName(),
  lastName: validName(),
  role: fc.constantFrom('student', 'instructor', 'admin')
});

export const studentUserData = () => fc.record({
  username: validUsername(),
  email: validEmail(),
  password: validPassword(),
  firstName: validName(),
  lastName: validName(),
  role: fc.constant('student')
});

export const instructorUserData = () => fc.record({
  username: validUsername(),
  email: validEmail(),
  password: validPassword(),
  firstName: validName(),
  lastName: validName(),
  role: fc.constant('instructor')
});

// Course data generators
export const validCourseData = () => fc.record({
  title: fc.string({ minLength: 5, maxLength: 200 }),
  description: fc.string({ minLength: 10, maxLength: 1000 }),
  price: fc.float({ min: 0, max: 10000, noNaN: true }),
  duration: fc.integer({ min: 1, max: 52 }),
  isPublished: fc.boolean()
});

// Question data generators
export const validQuestionData = () => fc.record({
  text: fc.string({ minLength: 10, maxLength: 500 }),
  optionA: fc.string({ minLength: 1, maxLength: 200 }),
  optionB: fc.string({ minLength: 1, maxLength: 200 }),
  optionC: fc.string({ minLength: 1, maxLength: 200 }),
  optionD: fc.string({ minLength: 1, maxLength: 200 }),
  correctAnswer: fc.constantFrom('A', 'B', 'C', 'D'),
  category: fc.string({ minLength: 3, maxLength: 50 }),
  difficulty: fc.constantFrom('easy', 'medium', 'hard')
});

export const validMCQImportData = () => fc.array(validQuestionData(), { minLength: 1, maxLength: 100 });

// Exam data generators
export const validExamAnswers = () => fc.array(
  fc.record({
    questionId: fc.integer({ min: 1, max: 1000 }),
    selectedAnswer: fc.constantFrom('A', 'B', 'C', 'D')
  }),
  { minLength: 1, maxLength: 50 }
);

// Portfolio data generators
export const validPortfolioData = () => fc.record({
  title: fc.string({ minLength: 5, maxLength: 100 }),
  description: fc.string({ minLength: 10, maxLength: 500 }),
  isPublic: fc.boolean(),
  skills: fc.array(fc.string({ minLength: 2, maxLength: 30 }), { maxLength: 20 }),
  experience: fc.string({ minLength: 10, maxLength: 2000 })
});

export const validPDFContent = () => fc.string({ minLength: 100, maxLength: 5000 });

// Payment data generators
export const validPaymentData = () => fc.record({
  amount: fc.float({ min: 1, max: 10000, noNaN: true }),
  currency: fc.constantFrom('USD', 'NGN', 'GHS', 'KES'),
  provider: fc.constantFrom('stripe', 'paystack'),
  metadata: fc.record({
    courseId: fc.integer({ min: 1, max: 1000 }),
    userId: fc.integer({ min: 1, max: 1000 })
  })
});

// Session data generators
export const validSessionData = () => fc.record({
  title: fc.string({ minLength: 5, maxLength: 200 }),
  description: fc.string({ minLength: 10, maxLength: 1000 }),
  scheduledTime: fc.date({ min: new Date(), max: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000) }),
  duration: fc.integer({ min: 30, max: 480 }),
  maxParticipants: fc.integer({ min: 1, max: 1000 })
});

// Consultation data generators
export const validConsultationData = () => fc.record({
  type: fc.constantFrom('ai', 'human'),
  message: fc.string({ minLength: 10, maxLength: 1000 }),
  urgency: fc.constantFrom('low', 'medium', 'high'),
  category: fc.constantFrom('general', 'prescription', 'symptoms', 'dosage')
});

export const validChatMessage = () => fc.record({
  content: fc.string({ minLength: 1, maxLength: 1000 }),
  sender: fc.constantFrom('user', 'ai', 'pharmacist'),
  timestamp: fc.date()
});

// UI component generators
export const validButtonProps = () => fc.record({
  variant: fc.constantFrom('primary', 'secondary', 'danger', 'outline'),
  size: fc.constantFrom('sm', 'md', 'lg'),
  disabled: fc.boolean(),
  loading: fc.boolean(),
  children: fc.string({ minLength: 1, maxLength: 50 })
});

export const validCardProps = () => fc.record({
  title: fc.option(fc.string({ minLength: 1, maxLength: 100 })),
  className: fc.option(fc.string({ maxLength: 100 })),
  children: fc.string({ minLength: 1, maxLength: 500 })
});

export const validModalProps = () => fc.record({
  isOpen: fc.boolean(),
  title: fc.string({ minLength: 1, maxLength: 100 }),
  children: fc.string({ minLength: 1, maxLength: 500 }),
  onClose: fc.constant(() => {})
});

// Navigation generators
export const validNavigationItem = () => fc.record({
  label: fc.string({ minLength: 1, maxLength: 50 }),
  href: fc.string({ minLength: 1, maxLength: 100 }),
  active: fc.boolean(),
  icon: fc.option(fc.string({ minLength: 1, maxLength: 20 }))
});

export const validScreenSize = () => fc.record({
  width: fc.integer({ min: 320, max: 2560 }),
  height: fc.integer({ min: 240, max: 1440 })
});

// SEO generators
export const validSEOMetadata = () => fc.record({
  title: fc.string({ minLength: 10, maxLength: 60 }),
  description: fc.string({ minLength: 50, maxLength: 160 }),
  keywords: fc.array(fc.string({ minLength: 2, maxLength: 30 }), { maxLength: 10 }),
  ogImage: fc.option(fc.webUrl()),
  canonicalUrl: fc.option(fc.webUrl())
});

// Accessibility generators
export const validARIAAttributes = () => fc.record({
  'aria-label': fc.option(fc.string({ minLength: 1, maxLength: 100 })),
  'aria-describedby': fc.option(fc.string({ minLength: 1, maxLength: 50 })),
  'aria-expanded': fc.option(fc.boolean()),
  'aria-hidden': fc.option(fc.boolean()),
  role: fc.option(fc.constantFrom('button', 'link', 'heading', 'banner', 'navigation', 'main', 'complementary'))
});

// Performance generators
export const validPerformanceMetrics = () => fc.record({
  loadTime: fc.float({ min: 0.1, max: 10.0, noNaN: true }),
  bundleSize: fc.integer({ min: 1000, max: 10000000 }),
  renderTime: fc.float({ min: 0.01, max: 5.0, noNaN: true }),
  memoryUsage: fc.integer({ min: 1000000, max: 1000000000 })
});

// Error generators
export const validErrorResponse = () => fc.record({
  status: fc.integer({ min: 400, max: 599 }),
  message: fc.string({ minLength: 5, maxLength: 200 }),
  code: fc.option(fc.string({ minLength: 3, maxLength: 20 })),
  details: fc.option(fc.record({
    field: fc.string({ minLength: 1, maxLength: 50 }),
    error: fc.string({ minLength: 5, maxLength: 100 })
  }))
});

// File upload generators
export const validFileData = () => fc.record({
  name: fc.string({ minLength: 1, maxLength: 255 }).filter(s => s.includes('.')),
  size: fc.integer({ min: 1, max: 10 * 1024 * 1024 }), // Up to 10MB
  type: fc.constantFrom('application/pdf', 'image/jpeg', 'image/png', 'text/plain'),
  lastModified: fc.date()
});

// Admin generators
export const validAdminAction = () => fc.record({
  action: fc.constantFrom('promote', 'demote', 'deactivate', 'activate', 'delete'),
  targetUserId: fc.integer({ min: 1, max: 10000 }),
  reason: fc.option(fc.string({ minLength: 10, maxLength: 500 }))
});

export const validSystemHealth = () => fc.record({
  database: fc.constantFrom('healthy', 'warning', 'error'),
  redis: fc.constantFrom('healthy', 'warning', 'error'),
  storage: fc.constantFrom('healthy', 'warning', 'error'),
  apiResponse: fc.float({ min: 0.1, max: 5.0, noNaN: true }),
  uptime: fc.integer({ min: 0, max: 365 * 24 * 60 * 60 })
});

// Utility generators
export const validDateRange = () => fc.record({
  start: fc.date(),
  end: fc.date()
}).filter(({ start, end }) => start <= end);

export const validPagination = () => fc.record({
  page: fc.integer({ min: 1, max: 1000 }),
  limit: fc.integer({ min: 1, max: 100 }),
  total: fc.integer({ min: 0, max: 100000 })
});

export const validSearchQuery = () => fc.record({
  query: fc.string({ minLength: 1, maxLength: 100 }),
  filters: fc.record({
    category: fc.option(fc.string({ minLength: 1, maxLength: 50 })),
    dateRange: fc.option(validDateRange()),
    sortBy: fc.option(fc.constantFrom('date', 'name', 'relevance', 'price')),
    sortOrder: fc.option(fc.constantFrom('asc', 'desc'))
  })
});