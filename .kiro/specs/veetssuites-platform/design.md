# Design Document

## Overview

VEETSSUITES is a multi-tenant platform architecture that separates concerns across four distinct subsites while sharing common infrastructure for authentication, payments, and media storage. The system uses a modern JAMstack approach with Next.js for the frontend and Django REST Framework for the backend API, enabling independent scaling and deployment of client and server components.

The architecture prioritizes:
- **Modularity**: Each subsite operates as a distinct module with clear boundaries
- **Security**: Role-based access control, encrypted credentials, and secure payment processing
- **Scalability**: Stateless API design, CDN-delivered frontend, and cloud object storage
- **Maintainability**: Clear separation of concerns, comprehensive testing, and API-first design

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Portfolio │  │ PHARMXAM │  │  HUB3660 │  │ HEALTHEE │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│              Shared: Auth, Navigation, UI Components        │
└─────────────────────────────────────────────────────────────┘
                            │
                    HTTPS/REST API
                            │
┌─────────────────────────────────────────────────────────────┐
│              Backend API (Django REST Framework)             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Portfolio │  │ PHARMXAM │  │  HUB3660 │  │ HEALTHEE │   │
│  │  API     │  │   API    │  │   API    │  │   API    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│         Shared: Auth, Payments, File Storage, Users         │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐      ┌──────▼──────┐    ┌──────▼──────┐
   │  MySQL  │      │  AWS S3     │    │  External   │
   │Database │      │  Storage    │    │  Services   │
   └─────────┘      └─────────────┘    └─────────────┘
                                        │ Stripe
                                        │ Paystack
                                        │ Zoom API
                                        │ AI API
```

### Technology Stack

**Frontend:**
- Next.js 14+ (App Router)
- React 18+
- Tailwind CSS 3+
- TypeScript
- Axios for API calls
- React Query for state management
- Vercel for hosting

**Backend:**
- Python 3.11+
- Django 5.0+
- Django REST Framework 3.14+
- MySQL 8.0+
- Celery for async tasks
- Redis for caching and task queue
- Render or AWS for hosting

**External Services:**
- Stripe (global payments)
- Paystack or Flutterwave (Nigerian payments)
- Zoom API (video conferencing)
- AWS S3 (file and video storage)
- AI API (health consultation chatbot)

**DevOps:**
- Git for version control
- GitHub Actions for CI/CD
- pytest for backend testing
- Jest and React Testing Library for frontend testing
- Docker for local development

## Components and Interfaces

### Frontend Components

#### 1. Authentication Module
- **LoginForm**: Handles user login with email/password
- **RegisterForm**: Handles new user registration
- **PasswordResetForm**: Initiates password reset flow
- **AuthProvider**: React context for managing authentication state
- **ProtectedRoute**: HOC for route protection based on authentication and roles

#### 2. Portfolio Module
- **PortfolioUpload**: CV file upload component with drag-and-drop
- **PortfolioDisplay**: Renders parsed CV content in structured format
- **PortfolioPublicView**: Public-facing portfolio page

#### 3. PHARMXAM Module
- **ExamList**: Displays available practice exams
- **ExamSession**: Interactive exam-taking interface
- **QuestionCard**: Individual MCQ display with answer options
- **ExamResults**: Score display and performance breakdown
- **ExamHistory**: Past exam attempts with review capability

#### 4. HUB3660 Module
- **CourseCatalog**: Grid display of available courses
- **CourseDetail**: Detailed course information with enrollment CTA
- **EnrollmentCheckout**: Payment flow integration
- **SessionCountdown**: Live session countdown timer widget
- **SessionPlayer**: Video player for recorded sessions
- **InstructorDashboard**: Course management interface for instructors

#### 5. HEALTHEE Module
- **ConsultationInterface**: Chat interface for AI and human consultations
- **ChatMessage**: Individual message display component
- **DisclaimerBanner**: Prominent medical disclaimer display
- **PharmacistQueue**: Interface for pharmacists to accept consultations

#### 6. Shared Components
- **Navigation**: Main navigation bar with subsite links
- **Card**: Reusable 2xl rounded card with shadow
- **Button**: Accessible button with loading states
- **Modal**: Accessible modal dialog
- **Toast**: Notification system for user feedback

### Backend API Endpoints

#### Authentication API (`/api/auth/`)
- `POST /register/` - Create new user account
- `POST /login/` - Authenticate user and return token
- `POST /logout/` - Invalidate user session
- `POST /password-reset/` - Initiate password reset
- `POST /password-reset-confirm/` - Complete password reset
- `GET /me/` - Get current user profile

#### Portfolio API (`/api/portfolio/`)
- `POST /upload/` - Upload CV file
- `GET /{user_id}/` - Get portfolio data
- `PUT /{user_id}/` - Update portfolio
- `DELETE /{user_id}/` - Delete portfolio

#### PHARMXAM API (`/api/pharmxam/`)
- `POST /questions/import/` - Import MCQ dataset (admin only)
- `GET /exams/` - List available exams
- `POST /exams/{exam_id}/start/` - Start exam session
- `POST /exams/{exam_id}/submit-answer/` - Submit answer
- `POST /exams/{exam_id}/complete/` - Complete exam and get results
- `GET /exams/history/` - Get user's exam history

#### HUB3660 API (`/api/hub3660/`)
- `GET /courses/` - List all courses
- `POST /courses/` - Create course (instructor only)
- `GET /courses/{course_id}/` - Get course details
- `PUT /courses/{course_id}/` - Update course (instructor only)
- `POST /courses/{course_id}/enroll/` - Initiate enrollment
- `GET /courses/{course_id}/sessions/` - List course sessions
- `POST /sessions/` - Create session with Zoom link (instructor only)
- `GET /sessions/{session_id}/recording/` - Get recording URL

#### Payment API (`/api/payments/`)
- `POST /create-checkout/` - Create payment session
- `POST /webhook/stripe/` - Handle Stripe webhooks
- `POST /webhook/paystack/` - Handle Paystack webhooks
- `GET /transactions/` - List user transactions

#### HEALTHEE API (`/api/healthee/`)
- `POST /consultations/` - Start new consultation
- `POST /consultations/{id}/messages/` - Send message
- `GET /consultations/{id}/messages/` - Get conversation history
- `POST /consultations/{id}/request-pharmacist/` - Request human pharmacist
- `GET /consultations/queue/` - Get pharmacist queue (pharmacist only)

#### Zoom Integration API (`/api/zoom/`)
- `POST /create-meeting/` - Create Zoom meeting
- `POST /register-participant/` - Register user for meeting
- `POST /webhook/` - Handle Zoom webhooks for recordings

## Data Models

### User Model
```python
class User(AbstractUser):
    email = EmailField(unique=True)
    role = CharField(choices=['student', 'instructor', 'admin'])
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Portfolio Model
```python
class Portfolio:
    user = OneToOneField(User)
    cv_file = FileField(upload_to='portfolios/')
    parsed_content = JSONField()
    is_public = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Course Model
```python
class Course:
    title = CharField(max_length=200)
    description = TextField()
    instructor = ForeignKey(User)
    price = DecimalField(max_digits=10, decimal_places=2)
    currency = CharField(max_length=3, default='USD')
    is_published = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Enrollment Model
```python
class Enrollment:
    student = ForeignKey(User)
    course = ForeignKey(Course)
    payment_status = CharField(choices=['pending', 'completed', 'failed'])
    payment_id = CharField(max_length=200)
    enrolled_at = DateTimeField(auto_now_add=True)
```

### Session Model
```python
class Session:
    course = ForeignKey(Course)
    title = CharField(max_length=200)
    scheduled_at = DateTimeField()
    zoom_meeting_id = CharField(max_length=100)
    zoom_join_url = URLField()
    recording_url = URLField(null=True)
    created_at = DateTimeField(auto_now_add=True)
```

### Question Model
```python
class Question:
    text = TextField()
    option_a = CharField(max_length=500)
    option_b = CharField(max_length=500)
    option_c = CharField(max_length=500)
    option_d = CharField(max_length=500)
    correct_answer = CharField(max_length=1, choices=['A', 'B', 'C', 'D'])
    category = CharField(max_length=100)
    difficulty = CharField(choices=['easy', 'medium', 'hard'])
    created_at = DateTimeField(auto_now_add=True)
```

### ExamAttempt Model
```python
class ExamAttempt:
    student = ForeignKey(User)
    questions = ManyToManyField(Question, through='ExamAnswer')
    score = IntegerField()
    total_questions = IntegerField()
    started_at = DateTimeField(auto_now_add=True)
    completed_at = DateTimeField(null=True)
```

### ExamAnswer Model
```python
class ExamAnswer:
    attempt = ForeignKey(ExamAttempt)
    question = ForeignKey(Question)
    selected_answer = CharField(max_length=1)
    is_correct = BooleanField()
    answered_at = DateTimeField(auto_now_add=True)
```

### Consultation Model
```python
class Consultation:
    user = ForeignKey(User)
    consultation_type = CharField(choices=['ai', 'human'])
    pharmacist = ForeignKey(User, null=True, related_name='pharmacist_consultations')
    status = CharField(choices=['active', 'waiting', 'completed'])
    created_at = DateTimeField(auto_now_add=True)
    completed_at = DateTimeField(null=True)
```

### ConsultationMessage Model
```python
class ConsultationMessage:
    consultation = ForeignKey(Consultation)
    sender = ForeignKey(User)
    message = TextField()
    is_ai_response = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
```

### Transaction Model
```python
class Transaction:
    user = ForeignKey(User)
    amount = DecimalField(max_digits=10, decimal_places=2)
    currency = CharField(max_length=3)
    provider = CharField(choices=['stripe', 'paystack', 'flutterwave'])
    provider_transaction_id = CharField(max_length=200)
    status = CharField(choices=['pending', 'completed', 'failed', 'refunded'])
    metadata = JSONField()
    created_at = DateTimeField(auto_now_add=True)
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Authentication and Authorization Properties

**Property 1: Registration creates encrypted accounts**
*For any* valid registration data (email, password, name), when submitted to the registration endpoint, the system should create a user account where the password is encrypted and not stored in plaintext.
**Validates: Requirements 1.1**

**Property 2: Valid credentials return tokens**
*For any* existing user with valid credentials, when login is attempted, the system should return a valid JWT token that can be used for subsequent authenticated requests.
**Validates: Requirements 1.2**

**Property 3: Password reset sends secure links**
*For any* registered user email, when password reset is requested, the system should generate a unique, time-limited reset token and send it to the user's email.
**Validates: Requirements 1.3**

**Property 4: Protected resources require valid authentication**
*For any* protected API endpoint, when accessed without a valid token or with insufficient role permissions, the system should return a 401 or 403 error and deny access.
**Validates: Requirements 1.4**

**Property 5: Logout invalidates tokens**
*For any* authenticated session, when logout is performed, the session token should become invalid and subsequent requests with that token should be rejected.
**Validates: Requirements 1.5**

**Property 6: New accounts default to Student role**
*For any* newly created user account, the role field should be set to "student" by default.
**Validates: Requirements 2.1**

**Property 7: Role promotion updates user permissions**
*For any* user promoted by an admin, the user's role should be updated to the new role (instructor or admin) and subsequent permission checks should reflect the new role.
**Validates: Requirements 2.2**

**Property 8: Students cannot access instructor features**
*For any* user with student role, when attempting to access instructor-only endpoints (course creation, session scheduling), the system should deny access with a 403 error.
**Validates: Requirements 2.3**

**Property 9: Course content is associated with creator**
*For any* course created by an instructor, the course's instructor field should reference the creating user's ID.
**Validates: Requirements 2.4**

**Property 10: Admins have full access**
*For any* user with admin role, when accessing any system endpoint, the system should grant access without authorization errors.
**Validates: Requirements 2.5**

### Portfolio Properties

**Property 11: PDF upload stores and extracts content**
*For any* valid PDF file up to 10MB, when uploaded to the portfolio endpoint, the system should store the file in S3 and extract text content into the parsed_content field.
**Validates: Requirements 3.1**

**Property 12: Portfolio display shows parsed content**
*For any* portfolio with parsed_content, when the portfolio page is rendered, the display should include all sections from the parsed content in a structured format.
**Validates: Requirements 3.2**

**Property 13: Public portfolios accessible without auth**
*For any* portfolio marked as public, when accessed via its public URL without authentication, the system should return the portfolio data without requiring login.
**Validates: Requirements 3.3**

**Property 14: CV update replaces previous version**
*For any* existing portfolio, when a new CV is uploaded, the old CV file should be replaced and the parsed_content should be updated with the new file's content.
**Validates: Requirements 3.4**

### PHARMXAM Properties

**Property 15: MCQ import parses and stores questions**
*For any* valid MCQ dataset in the expected format, when imported by an admin, all questions should be parsed and stored with their options and correct answers intact.
**Validates: Requirements 4.1**

**Property 16: Exam questions are randomized**
*For any* exam with multiple questions, when started by different students or at different times, the question order should vary (not always the same sequence).
**Validates: Requirements 4.2**

**Property 17: Answer submission provides immediate feedback**
*For any* answer submitted during an exam, the system should immediately validate it against the correct answer and return feedback indicating correctness.
**Validates: Requirements 4.3**

**Property 18: Exam completion calculates accurate scores**
*For any* completed exam, the displayed score should equal the count of correct answers divided by total questions, and the performance breakdown should accurately categorize questions by correctness.
**Validates: Requirements 4.4**

**Property 19: Exam history shows marked answers**
*For any* past exam attempt, when reviewed, each question should display the student's selected answer and the correct answer, with visual indicators for correct/incorrect.
**Validates: Requirements 4.5**

### HUB3660 Course Properties

**Property 20: Course creation stores all details**
*For any* course created by an instructor, all provided fields (title, description, price, schedule) should be stored and retrievable via the course detail endpoint.
**Validates: Requirements 5.1**

**Property 21: Course catalog shows enrollment status**
*For any* student viewing the course catalog, each course should display whether the student is enrolled, not enrolled, or enrollment is pending.
**Validates: Requirements 5.2**

**Property 22: Enrollment requires payment completion**
*For any* enrollment attempt, the system should not grant course access until a payment confirmation webhook is received with status "completed".
**Validates: Requirements 5.3**

**Property 23: Scheduled sessions display countdowns**
*For any* course with future scheduled sessions, the session list should display countdown timers showing time remaining until each session starts.
**Validates: Requirements 5.4**

**Property 24: Course content requires enrollment**
*For any* course content or recording, when accessed by a user, the system should verify enrollment exists before returning the content.
**Validates: Requirements 5.5**

### Payment Properties

**Property 25: Payment provider routing by location**
*For any* enrollment initiation, the system should redirect to Stripe for non-Nigerian users and to Paystack/Flutterwave for Nigerian users based on detected or specified location.
**Validates: Requirements 6.1**

**Property 26: Payment webhooks trigger access grants**
*For any* successful payment webhook received, the system should create or update an enrollment record with status "completed" and grant the student access to the course.
**Validates: Requirements 6.3**

**Property 27: Payment failures allow retry**
*For any* failed payment, the frontend should display an error message and maintain the enrollment flow state to allow the user to retry without re-entering information.
**Validates: Requirements 6.4**

### Zoom Integration Properties

**Property 28: Session scheduling creates Zoom meetings**
*For any* session scheduled by an instructor, the system should call the Zoom API to create a meeting and store the meeting ID and join URL.
**Validates: Requirements 7.1**

**Property 29: Enrollment auto-registers for Zoom**
*For any* course enrollment, the system should automatically register the student for all scheduled Zoom sessions associated with that course.
**Validates: Requirements 7.2**

**Property 30: Session countdown displays correctly**
*For any* scheduled session, the countdown widget should display the time remaining in a human-readable format (days, hours, minutes) and update in real-time.
**Validates: Requirements 7.3**

**Property 31: Session start provides join links**
*For any* live session that has started, enrolled students should see an active join link that redirects to the Zoom meeting.
**Validates: Requirements 7.4**

**Property 32: Session end stores recordings**
*For any* completed Zoom session, when the recording becomes available, the system should retrieve the recording URL and upload it to S3 with appropriate access controls.
**Validates: Requirements 7.5**

### Recording Access Properties

**Property 33: Recording URLs stored with permissions**
*For any* recording uploaded to S3, the system should store the S3 URL along with a reference to the course, enabling enrollment-based access control.
**Validates: Requirements 8.1**

**Property 34: Recording access requires enrollment**
*For any* recording request, the system should verify the requesting user is enrolled in the associated course before generating an access URL.
**Validates: Requirements 8.2**

**Property 35: Unenrolled users denied recording access**
*For any* user not enrolled in a course, when attempting to access a recording from that course, the system should return a 403 error.
**Validates: Requirements 8.3**

**Property 36: Recording URLs are time-limited**
*For any* authorized recording access, the generated signed URL should include an expiration timestamp set to 24 hours from generation time.
**Validates: Requirements 8.4**

### HEALTHEE Consultation Properties

**Property 37: Consultation initiation presents options**
*For any* new consultation, the interface should display both AI chatbot and human pharmacist options before the user sends their first message.
**Validates: Requirements 9.1**

**Property 38: AI messages forwarded and returned**
*For any* message sent to the AI chatbot, the system should forward it to the configured AI API and return the AI's response to the user within the consultation interface.
**Validates: Requirements 9.2**

**Property 39: Human consultation creates requests**
*For any* human pharmacist consultation request, the system should create a consultation record with status "waiting" and send notifications to available pharmacists.
**Validates: Requirements 9.3**

**Property 40: Health guidance includes disclaimer**
*For any* page displaying health guidance or consultation interface, the UI should include a prominent disclaimer stating that HEALTHEE is a guide only and users should contact a physician for medical advice.
**Validates: Requirements 9.4**

**Property 41: Consultation history is stored**
*For any* completed consultation, all messages should be stored and retrievable by the user for future reference.
**Validates: Requirements 9.5**

### UI and Accessibility Properties

**Property 42: Content uses 2xl rounded cards**
*For any* content container in the frontend, the CSS should include classes for 2xl border radius and soft shadow effects.
**Validates: Requirements 10.1**

**Property 43: Navigation shows current section**
*For any* subsite navigation, the current section should have a visual indicator (active state) distinguishing it from other navigation items.
**Validates: Requirements 10.2**

**Property 44: Responsive design adapts to screen sizes**
*For any* page, when viewed at different viewport widths (mobile: <768px, tablet: 768-1024px, desktop: >1024px), the layout should adapt appropriately without horizontal scrolling or broken layouts.
**Validates: Requirements 10.3**

**Property 45: Accessibility standards compliance**
*For any* page, when tested with automated accessibility tools (axe, Lighthouse), the page should pass WCAG 2.1 Level AA criteria with no critical violations.
**Validates: Requirements 10.4**

**Property 46: Interactive elements provide feedback**
*For any* button or link, when focused or hovered, the element should display visual feedback (color change, outline, or other indicator).
**Validates: Requirements 10.5**

### SEO Properties

**Property 47: Semantic HTML with heading hierarchy**
*For any* page, the HTML should use semantic elements (header, nav, main, article, footer) and maintain proper heading hierarchy (single h1, nested h2-h6).
**Validates: Requirements 11.1**

**Property 48: Meta tags present on all pages**
*For any* page, the HTML head should include title, description, and keywords meta tags with content relevant to that page.
**Validates: Requirements 11.2**

**Property 49: Social sharing metadata implemented**
*For any* page, the HTML head should include Open Graph and Twitter Card meta tags for proper social media sharing previews.
**Validates: Requirements 11.3**

**Property 50: Structured data for content types**
*For any* course, article, or organization page, the HTML should include valid JSON-LD structured data markup.
**Validates: Requirements 11.5**

### Security Properties

**Property 51: No hardcoded secrets**
*For any* configuration file or source code file, there should be no hardcoded API keys, passwords, or other sensitive credentials - all should use environment variables.
**Validates: Requirements 12.5**

**Property 52: Code comments for complex logic**
*For any* function or module with complex business logic (cyclomatic complexity > 10), the code should include comments explaining the algorithm and key decision points.
**Validates: Requirements 14.5**

## Error Handling

### Authentication Errors
- **Invalid Credentials**: Return 401 with message "Invalid email or password"
- **Expired Token**: Return 401 with message "Session expired, please login again"
- **Insufficient Permissions**: Return 403 with message "You do not have permission to access this resource"
- **Account Locked**: Return 403 with message "Account temporarily locked due to multiple failed login attempts"

### Validation Errors
- **Missing Required Fields**: Return 400 with specific field names and "This field is required"
- **Invalid Format**: Return 400 with field name and format requirements (e.g., "Email must be a valid email address")
- **File Too Large**: Return 413 with message "File size exceeds maximum allowed size of 10MB"
- **Unsupported File Type**: Return 415 with message "File type not supported. Please upload a PDF file"

### Payment Errors
- **Payment Failed**: Display user-friendly message "Payment could not be processed. Please check your payment details and try again"
- **Payment Timeout**: Return 408 with message "Payment session expired. Please try again"
- **Webhook Verification Failed**: Log error and return 400 to payment provider
- **Duplicate Payment**: Detect duplicate transaction IDs and return existing enrollment without double-charging

### External Service Errors
- **Zoom API Failure**: Log error, notify admin, and display to user "Unable to create meeting at this time. Please try again later"
- **AI API Timeout**: Return cached response or fallback message "AI service temporarily unavailable. Please try again or request human pharmacist"
- **S3 Upload Failure**: Retry up to 3 times with exponential backoff, then return 500 with message "File upload failed. Please try again"
- **Email Service Failure**: Queue email for retry and log error for admin review

### Database Errors
- **Connection Failure**: Retry connection with exponential backoff, return 503 if unable to connect
- **Constraint Violation**: Return 409 with user-friendly message (e.g., "Email already registered")
- **Transaction Rollback**: Log error details and return 500 with generic message to user

### Rate Limiting
- **Too Many Requests**: Return 429 with message "Too many requests. Please try again in X seconds" and include Retry-After header

### Error Logging
- All errors should be logged with:
  - Timestamp
  - User ID (if authenticated)
  - Request path and method
  - Error type and message
  - Stack trace (for 500 errors)
- Critical errors (payment failures, data loss risks) should trigger admin notifications

## Testing Strategy

### Unit Testing

**Backend (pytest)**
- Test all model methods and properties
- Test serializer validation logic
- Test business logic in service layer
- Test utility functions and helpers
- Target: 80% code coverage minimum
- Run with: `pytest --cov=. --cov-report=html`

**Frontend (Jest + React Testing Library)**
- Test component rendering with various props
- Test user interactions (clicks, form submissions)
- Test conditional rendering logic
- Test custom hooks
- Target: 70% code coverage minimum
- Run with: `npm test -- --coverage`

### Property-Based Testing

**Framework**: Hypothesis (Python) for backend, fast-check (TypeScript) for frontend

**Configuration**: Each property test should run minimum 100 iterations to ensure thorough coverage of input space.

**Test Tagging**: Each property-based test MUST include a comment with this exact format:
```python
# Feature: veetssuites-platform, Property 1: Registration creates encrypted accounts
```

**Key Properties to Test**:
- Authentication: Properties 1-10 (registration, login, logout, role-based access)
- Portfolio: Properties 11-14 (upload, display, public access, updates)
- PHARMXAM: Properties 15-19 (import, randomization, scoring)
- HUB3660: Properties 20-24 (course management, enrollment, access control)
- Payments: Properties 25-27 (routing, webhooks, error handling)
- Zoom: Properties 28-32 (meeting creation, registration, recordings)
- Recordings: Properties 33-36 (storage, access control, URL generation)
- HEALTHEE: Properties 37-41 (consultation flow, AI integration, history)
- UI/Accessibility: Properties 42-46 (responsive design, accessibility)
- SEO: Properties 47-50 (meta tags, structured data)
- Security: Properties 51-52 (no secrets, documentation)

**Example Property Test**:
```python
from hypothesis import given, strategies as st

# Feature: veetssuites-platform, Property 1: Registration creates encrypted accounts
@given(
    email=st.emails(),
    password=st.text(min_size=8, max_size=128),
    name=st.text(min_size=1, max_size=100)
)
def test_registration_encrypts_password(email, password, name):
    response = client.post('/api/auth/register/', {
        'email': email,
        'password': password,
        'name': name
    })
    assert response.status_code == 201
    user = User.objects.get(email=email)
    assert user.password != password  # Password should be hashed
    assert user.check_password(password)  # But should verify correctly
```

### Integration Testing

**Critical User Flows**:
1. **Authentication Flow**: Register → Login → Access Protected Resource → Logout
2. **Course Enrollment Flow**: Browse Catalog → View Course → Initiate Payment → Complete Payment → Access Course Content
3. **Exam Flow**: Start Exam → Answer Questions → Submit Exam → View Results → Review History
4. **Live Session Flow**: Enroll in Course → View Session Schedule → Join Live Session → Access Recording
5. **Consultation Flow**: Initiate Consultation → Send Messages → Receive Responses → View History

**Tools**: pytest-django for backend, Cypress or Playwright for frontend

### End-to-End Testing

**Framework**: Playwright or Cypress

**Test Scenarios**:
- Complete student journey: Register → Enroll in course → Attend session → Take exam
- Instructor journey: Create course → Schedule session → View enrollments
- Admin journey: Import questions → Manage users → View analytics
- Payment scenarios: Successful payment, failed payment, refund
- Multi-device testing: Desktop, tablet, mobile viewports

### Accessibility Testing

**Tools**: 
- axe-core for automated testing
- Lighthouse CI for continuous monitoring
- Manual testing with screen readers (NVDA, JAWS)

**Criteria**: WCAG 2.1 Level AA compliance

### Performance Testing

**Metrics**:
- Page load time < 3 seconds
- Time to Interactive < 5 seconds
- API response time < 500ms (p95)
- Database query time < 100ms (p95)

**Tools**: Lighthouse, WebPageTest, k6 for load testing

### Security Testing

**Automated Scans**:
- OWASP ZAP for vulnerability scanning
- npm audit / pip-audit for dependency vulnerabilities
- Bandit for Python security issues
- ESLint security plugins for JavaScript

**Manual Testing**:
- SQL injection attempts
- XSS attempts
- CSRF protection verification
- Authentication bypass attempts
- Authorization escalation attempts

### Continuous Integration

**GitHub Actions Workflow**:
1. Run linters (flake8, ESLint)
2. Run unit tests with coverage
3. Run integration tests
4. Run property-based tests
5. Run security scans
6. Build Docker images
7. Deploy to staging (on main branch)

**Quality Gates**:
- All tests must pass
- Code coverage must meet minimums (80% backend, 70% frontend)
- No critical security vulnerabilities
- No accessibility violations on key pages

### Test Data Management

**Fixtures**: Use factory_boy (Python) and faker (JavaScript) to generate realistic test data

**Database**: Use separate test database that is reset between test runs

**External Services**: Mock external APIs (Stripe, Zoom, AI) in unit/integration tests, use sandbox environments for E2E tests

### Monitoring and Observability

**Production Monitoring**:
- Error tracking: Sentry
- Performance monitoring: New Relic or DataDog
- Uptime monitoring: Pingdom or UptimeRobot
- Log aggregation: CloudWatch or Papertrail

**Alerts**:
- Error rate > 1%
- Response time > 2 seconds (p95)
- Payment failure rate > 5%
- Service downtime > 1 minute
