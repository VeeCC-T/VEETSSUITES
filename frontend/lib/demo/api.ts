/**
 * Demo API service for frontend-only deployment
 * Provides mock data when backend is not available
 */

// Mock data for demo mode
const DEMO_USER = {
  id: 1,
  email: 'demo@veetssuites.com',
  firstName: 'Demo',
  lastName: 'User',
  role: 'student',
};

const DEMO_EXAMS = [
  {
    id: 1,
    title: 'Pharmacology Basics',
    description: 'Fundamental concepts in pharmacology',
    duration: 60,
    totalQuestions: 50,
    passingScore: 70,
    category: 'pharmacology',
    difficulty: 'intermediate',
  },
  {
    id: 2,
    title: 'Clinical Pharmacy',
    description: 'Clinical pharmacy practice and patient care',
    duration: 90,
    totalQuestions: 75,
    passingScore: 75,
    category: 'clinical',
    difficulty: 'advanced',
  },
];

const DEMO_COURSES = [
  {
    id: 1,
    title: 'Advanced Web Development',
    description: 'Learn modern web development with React and Node.js',
    instructor: 'Dr. Jane Smith',
    price: 299.99,
    duration: 12,
    level: 'advanced',
    enrollmentCount: 45,
    rating: 4.8,
  },
  {
    id: 2,
    title: 'Database Design Fundamentals',
    description: 'Master database design principles and SQL',
    instructor: 'Prof. John Doe',
    price: 199.99,
    duration: 8,
    level: 'intermediate',
    enrollmentCount: 32,
    rating: 4.6,
  },
];

const DEMO_PORTFOLIO = {
  id: 1,
  title: 'John Doe - Software Developer',
  description: 'Experienced full-stack developer with 5+ years in web development',
  skills: ['JavaScript', 'React', 'Node.js', 'Python', 'Django', 'PostgreSQL'],
  experience: [
    {
      title: 'Senior Software Developer',
      company: 'Tech Solutions Inc.',
      duration: '2021 - Present',
      description: 'Lead development of web applications using React and Django',
    },
    {
      title: 'Full Stack Developer',
      company: 'StartupXYZ',
      duration: '2019 - 2021',
      description: 'Built scalable web applications from scratch',
    },
  ],
  projects: [
    {
      name: 'E-commerce Platform',
      description: 'Full-featured e-commerce solution with payment integration',
      technologies: ['React', 'Node.js', 'MongoDB', 'Stripe'],
      url: 'https://github.com/demo/ecommerce',
    },
    {
      name: 'Task Management App',
      description: 'Collaborative task management with real-time updates',
      technologies: ['Vue.js', 'Express', 'Socket.io', 'PostgreSQL'],
      url: 'https://github.com/demo/taskmanager',
    },
  ],
};

// Demo API functions
export const demoApi = {
  // Authentication
  login: async (credentials: any) => {
    await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API delay
    return {
      access: 'demo_access_token',
      refresh: 'demo_refresh_token',
      user: DEMO_USER,
    };
  },

  register: async (userData: any) => {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return {
      access: 'demo_access_token',
      refresh: 'demo_refresh_token',
      user: { ...DEMO_USER, ...userData, id: Math.random() },
    };
  },

  // Exams
  getExams: async () => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return { results: DEMO_EXAMS };
  },

  startExam: async (examId: number) => {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return {
      sessionId: `demo_session_${examId}`,
      exam: DEMO_EXAMS.find(e => e.id === examId),
      questions: [
        {
          id: 1,
          questionText: 'What is the primary mechanism of action for ACE inhibitors?',
          options: [
            { id: 'a', text: 'Block calcium channels' },
            { id: 'b', text: 'Inhibit angiotensin-converting enzyme' },
            { id: 'c', text: 'Block beta receptors' },
            { id: 'd', text: 'Inhibit sodium channels' },
          ],
        },
        {
          id: 2,
          questionText: 'Which drug class is first-line treatment for hypertension?',
          options: [
            { id: 'a', text: 'Beta blockers' },
            { id: 'b', text: 'ACE inhibitors' },
            { id: 'c', text: 'Calcium channel blockers' },
            { id: 'd', text: 'Diuretics' },
          ],
        },
      ],
      startedAt: new Date().toISOString(),
    };
  },

  // Courses
  getCourses: async () => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return { results: DEMO_COURSES };
  },

  // Portfolio
  getPortfolio: async (userId: number) => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return DEMO_PORTFOLIO;
  },

  // Health consultation
  startConsultation: async (data: any) => {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return {
      consultationId: 'demo_consultation_123',
      sessionToken: 'demo_session_token',
      estimatedWaitTime: 5,
      disclaimer: 'This is a demo consultation. Not for actual medical advice.',
    };
  },

  // System health (for admin)
  getSystemHealth: async () => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return {
      database: 'healthy',
      cache: 'healthy',
      storage: 'healthy',
      externalServices: {
        stripe: 'demo',
        zoom: 'demo',
        email: 'demo',
      },
      performance: {
        avgResponseTime: 120,
        activeUsers: 45,
        memoryUsage: 65,
      },
    };
  },
};

// Check if we're in demo mode
export const isDemoMode = () => {
  return process.env.NEXT_PUBLIC_DEMO_MODE === 'true';
};

// Demo notification component
export const DemoNotification = () => {
  if (!isDemoMode()) return null;

  return (
    <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
      <div className="flex">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <p className="text-sm text-yellow-700">
            <strong>Demo Mode:</strong> This is a demonstration version with mock data. 
            Features like payments, file uploads, and real-time chat are simulated.
          </p>
        </div>
      </div>
    </div>
  );
};