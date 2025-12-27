# VEETSSUITES Platform

A comprehensive multi-subsite platform providing professional portfolio showcase, pharmacy exam preparation (PHARMXAM), AI-powered health consultation (HEALTHEE ANYWHERE), and technology education with live instruction (HUB3660).

## 🚀 Current Status

**Implementation Complete**: All core features are fully implemented with comprehensive property-based testing (52+ test properties). The platform is ready for production deployment with final polishing in progress.

**Live Demo**: [https://veetssuites.com](https://veetssuites.com) (Coming Soon)
**GitHub Repository**: [https://github.com/VeeCC-T/VEETSSUITES](https://github.com/VeeCC-T/VEETSSUITES)

## Overview

VEETSSUITES is a modern JAMstack platform that integrates four distinct services:

- **Portfolio Subsite**: Professional CV showcase with PDF upload and parsing
- **PHARMXAM**: Pharmacy examination preparation with MCQ practice tests
- **HEALTHEE ANYWHERE**: AI and human pharmacist health consultation service
- **HUB3660**: Technology education platform with live Zoom sessions and recordings

## 🏗️ Architecture

### Technology Stack

**Frontend:**
- Next.js 14+ (App Router) with TypeScript
- React 18+ with modern hooks and context
- Tailwind CSS 3+ for responsive design
- Axios & React Query for API management
- Jest & Playwright for testing
- Property-based testing with fast-check
- Hosted on Vercel

**Backend:**
- Python 3.11+ with Django 5.0+
- Django REST Framework 3.14+ for APIs
- MySQL 8.0+ with optimized queries
- Celery & Redis for background tasks
- Comprehensive property-based testing with Hypothesis
- JWT authentication with role-based access
- Hosted on Render or AWS

**External Services:**
- Stripe (global payments) & Paystack (Nigerian payments)
- Zoom API (video conferencing and recordings)
- AWS S3 (file and video storage)
- AI API integration (health consultation chatbot)
- Email services for notifications

### Key Features Implemented

✅ **Authentication System**: JWT-based auth with role management (student, instructor, pharmacist, admin)
✅ **Portfolio Subsite**: PDF upload, parsing, and professional showcase
✅ **PHARMXAM**: MCQ exam system with categories, scoring, and progress tracking
✅ **HEALTHEE**: AI + human pharmacist consultation with real-time chat
✅ **HUB3660**: Course management, Zoom integration, and video storage
✅ **Payment Integration**: Stripe and Paystack with webhook handling
✅ **Admin Dashboard**: User management, system health, and MCQ import
✅ **Performance Optimization**: Caching, lazy loading, and bundle optimization
✅ **Security**: Input validation, rate limiting, and error handling
✅ **Testing**: 52+ property-based tests covering all critical functionality

## Project Structure

```
veetssuites/
├── frontend/          # Next.js frontend application
│   ├── app/          # Next.js App Router pages
│   ├── components/   # React components
│   ├── lib/          # Utilities and API clients
│   └── public/       # Static assets
│
├── backend/          # Django backend API
│   ├── config/       # Django project settings
│   ├── apps/         # Django applications
│   │   ├── authentication/
│   │   ├── portfolio/
│   │   ├── pharmxam/
│   │   ├── hub3660/
│   │   └── healthee/
│   ├── manage.py
│   └── requirements.txt
│
└── docs/             # Additional documentation
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- MySQL 8.0+
- Git

### 1. Clone and Setup

```bash
git clone https://github.com/VeeCC-T/VEETSSUITES.git
cd VEETSSUITES
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database and API keys

# Setup database
python manage.py migrate
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json

# Start development server
python manage.py runserver
```

Backend API available at: `http://localhost:8000`
Admin panel available at: `http://localhost:8000/admin/`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your API URLs and keys

# Start development server
npm run dev
```

Frontend available at: `http://localhost:3000`

### 4. Verify Setup

1. Visit `http://localhost:3000` - should show the VEETSSUITES homepage
2. Visit `http://localhost:8000/api/docs/` - should show API documentation
3. Create a test account and explore the subsites

## ⚙️ Environment Variables

### Frontend (.env.local)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# Payment Keys (Public)
NEXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
NEXT_PUBLIC_PAYSTACK_PUBLIC_KEY=pk_test_your_paystack_public_key

# Analytics (Optional)
NEXT_PUBLIC_GA_ID=your_google_analytics_id
```

### Backend (.env)

```bash
# Django Configuration
DEBUG=True
SECRET_KEY=your-super-secret-django-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=mysql://username:password@localhost:3306/veetssuites
# Alternative format:
DB_NAME=veetssuites
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306

# AWS S3 Storage
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_STORAGE_BUCKET_NAME=your_s3_bucket_name
AWS_S3_REGION_NAME=us-east-1

# Payment Services
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_stripe_webhook_secret
PAYSTACK_SECRET_KEY=sk_test_your_paystack_secret_key

# Zoom Integration
ZOOM_API_KEY=your_zoom_api_key
ZOOM_API_SECRET=your_zoom_api_secret
ZOOM_WEBHOOK_SECRET_TOKEN=your_zoom_webhook_secret

# AI Service
AI_API_KEY=your_ai_service_api_key
AI_API_URL=https://api.your-ai-service.com

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=True

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# Security
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com
```

### Required API Keys

1. **Stripe**: Get from [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. **Paystack**: Get from [Paystack Dashboard](https://dashboard.paystack.com/#/settings/developer)
3. **Zoom**: Create app at [Zoom Marketplace](https://marketplace.zoom.us/)
4. **AWS S3**: Create bucket and IAM user with S3 permissions
5. **AI Service**: Configure your preferred AI API (OpenAI, Anthropic, etc.)

## 🧪 Development & Testing

### Running Tests

**Frontend Tests:**
```bash
cd frontend

# Unit and integration tests
npm test

# E2E tests with Playwright
npm run test:e2e

# Coverage report
npm run test:coverage

# Property-based tests
npm run test:properties
```

**Backend Tests:**
```bash
cd backend

# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Property-based tests only
pytest -m "property"

# Specific test modules
pytest accounts/tests.py
pytest exams/test_properties.py
```

### Code Quality & Linting

**Frontend:**
```bash
npm run lint          # ESLint
npm run lint:fix      # Auto-fix issues
npm run type-check    # TypeScript checking
npm run format        # Prettier formatting
```

**Backend:**
```bash
flake8               # Python linting
black .              # Code formatting
mypy .               # Type checking
isort .              # Import sorting
```

### Performance Testing

**Frontend:**
```bash
npm run build        # Production build
npm run analyze      # Bundle analysis
npm run lighthouse   # Performance audit
```

**Backend:**
```bash
python manage.py test_performance    # Performance tests
python manage.py profile_views       # View profiling
```

## 🚀 Deployment

### Frontend Deployment (Vercel)

1. **Connect Repository**:
   - Link your GitHub repository to Vercel
   - Select the `frontend` directory as the root

2. **Environment Variables**:
   ```bash
   NEXT_PUBLIC_API_URL=https://your-api-domain.com
   NEXT_PUBLIC_SITE_URL=https://your-domain.com
   NEXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_live_your_live_key
   NEXT_PUBLIC_PAYSTACK_PUBLIC_KEY=pk_live_your_live_key
   ```

3. **Build Settings**:
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

4. **Deploy**: Push to main branch for automatic deployment

### Backend Deployment (Render/Railway/AWS)

1. **Database Setup**:
   ```bash
   # Create production database
   mysql -u root -p
   CREATE DATABASE veetssuites_prod;
   ```

2. **Environment Variables** (Production):
   ```bash
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   DATABASE_URL=mysql://user:pass@host:port/veetssuites_prod
   ALLOWED_HOSTS=your-domain.com,api.your-domain.com
   # ... other production keys
   ```

3. **Deployment Steps**:
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Run migrations
   python manage.py migrate
   
   # Collect static files
   python manage.py collectstatic --noinput
   
   # Create superuser (optional)
   python manage.py createsuperuser
   
   # Start production server
   gunicorn veetssuites.wsgi:application
   ```

4. **Background Tasks**:
   ```bash
   # Start Celery worker
   celery -A veetssuites worker -l info
   
   # Start Celery beat (scheduler)
   celery -A veetssuites beat -l info
   ```

### Domain Configuration

1. **Frontend**: Point your domain to Vercel
2. **Backend**: Point API subdomain to your backend host
3. **SSL**: Enable HTTPS on both domains
4. **CORS**: Update `CORS_ALLOWED_ORIGINS` in backend settings

### Production Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] SSL certificates installed
- [ ] Domain DNS configured
- [ ] Monitoring and logging setup
- [ ] Backup strategy implemented
- [ ] Performance testing completed

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: `http://localhost:8000/api/docs/` (Development)
- **ReDoc**: `http://localhost:8000/api/redoc/` (Alternative view)
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

### Key API Endpoints

**Authentication:**
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh
- `POST /api/auth/logout/` - User logout

**Portfolio:**
- `GET /api/portfolio/` - List portfolios
- `POST /api/portfolio/` - Create portfolio
- `POST /api/portfolio/upload/` - Upload CV PDF

**PHARMXAM:**
- `GET /api/exams/` - List available exams
- `POST /api/exams/{id}/start/` - Start exam session
- `POST /api/exams/sessions/{id}/submit/` - Submit answers

**HEALTHEE:**
- `POST /api/healthee/consultations/` - Start consultation
- `POST /api/healthee/consultations/{id}/messages/` - Send message
- `GET /api/healthee/pharmacist-queue/` - Pharmacist queue

**HUB3660:**
- `GET /api/hub3660/courses/` - List courses
- `POST /api/hub3660/courses/{id}/enroll/` - Enroll in course
- `GET /api/hub3660/sessions/{id}/join/` - Join live session

### Authentication

All protected endpoints require JWT token in header:
```bash
Authorization: Bearer your_jwt_token_here
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

### Development Workflow

1. **Fork & Clone**:
   ```bash
   git clone https://github.com/your-username/VEETSSUITES.git
   cd VEETSSUITES
   ```

2. **Create Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**:
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

4. **Test Your Changes**:
   ```bash
   # Frontend tests
   cd frontend && npm test
   
   # Backend tests
   cd backend && pytest
   ```

5. **Commit & Push**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**:
   - Describe your changes
   - Link any related issues
   - Ensure all tests pass

### Code Standards

- **Frontend**: ESLint + Prettier configuration
- **Backend**: PEP 8 with Black formatting
- **Commits**: Follow [Conventional Commits](https://conventionalcommits.org/)
- **Testing**: Maintain >80% code coverage

### Areas for Contribution

- 🐛 Bug fixes and improvements
- 📝 Documentation enhancements
- 🧪 Additional test coverage
- 🎨 UI/UX improvements
- 🚀 Performance optimizations
- 🌐 Internationalization (i18n)
- ♿ Accessibility improvements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Community

- **Issues**: [GitHub Issues](https://github.com/VeeCC-T/VEETSSUITES/issues)
- **Discussions**: [GitHub Discussions](https://github.com/VeeCC-T/VEETSSUITES/discussions)
- **Email**: support@veetssuites.com
- **Documentation**: [Wiki](https://github.com/VeeCC-T/VEETSSUITES/wiki)

## 🗺️ Roadmap & Status

### Current Implementation Status

✅ **Completed (Ready for Production)**:
- Core authentication and authorization
- All four subsites fully functional
- Payment processing (Stripe + Paystack)
- File upload and storage (AWS S3)
- Zoom integration for live sessions
- AI-powered health consultations
- Admin dashboard and management
- Comprehensive testing suite (52+ properties)
- Performance optimizations
- Security hardening

🔄 **In Progress (Final Polish)**:
- Test configuration fixes
- Documentation completion
- CI/CD pipeline setup
- Production deployment preparation

📋 **Upcoming Features**:
- Mobile app (React Native)
- Advanced analytics dashboard
- Multi-language support (i18n)
- Advanced AI features
- Integration with more payment providers
- Enhanced video streaming capabilities

### Development Progress

See [project-checklist.json](project-checklist.json) for detailed task tracking and completion status.

---

**Built with ❤️ by the VEETSSUITES Team**

*Empowering education, health, and professional growth through technology.*
