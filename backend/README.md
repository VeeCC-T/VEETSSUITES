# VEETSSUITES Backend

Django REST Framework backend for the VEETSSUITES platform.

## Setup

### Prerequisites

- Python 3.11+
- MySQL 8.0+ (for production) or SQLite (for development)
- Redis (for Celery tasks)

### Installation

1. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env with your configuration
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## Project Structure

```
backend/
├── veetssuites/          # Main project settings
│   ├── settings.py       # Django settings with environment variables
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── accounts/             # User authentication and management
│   ├── models.py         # Custom User model with role-based access
│   ├── admin.py          # Admin interface configuration
│   └── migrations/       # Database migrations
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not in git)
└── .env.example          # Example environment configuration
```

## Features Implemented

### Task 2.1: Django Project Initialization ✅
- Django 5.0+ with REST Framework
- Environment variable management with python-decouple
- CORS configuration for frontend communication
- JWT authentication setup
- Development and production settings separation

### Task 2.2: Database Configuration ✅
- MySQL database support (production)
- SQLite fallback (development)
- Environment-based database configuration
- Initial migration structure

### Task 2.3: Custom User Model ✅
- Custom User model extending AbstractUser
- Role-based access control (student, instructor, admin)
- Email as primary identifier with uniqueness constraint
- Role promotion/demotion methods
- Admin interface with bulk actions

## User Roles

The platform supports three user roles:

1. **Student** (default)
   - Access to courses and consultations
   - Can enroll in courses
   - Can take exams

2. **Instructor**
   - All student permissions
   - Can create and manage courses
   - Can schedule sessions

3. **Admin**
   - Full system access
   - User management
   - System configuration

## Environment Variables

Key environment variables (see `.env.example` for full list):

- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `DB_ENGINE`: Database engine (sqlite3 or mysql)
- `DB_NAME`: Database name
- `CORS_ALLOWED_ORIGINS`: Allowed frontend origins
- `JWT_ACCESS_TOKEN_LIFETIME`: JWT token lifetime in minutes

## Database

See [README_DATABASE.md](README_DATABASE.md) for detailed database setup instructions.

## API Documentation

API documentation will be available at `/api/docs/` once implemented in subsequent tasks.

## Testing

```bash
# Run all tests
python manage.py test

# Run with coverage
pytest --cov=. --cov-report=html
```

## Next Steps

The following modules will be implemented in subsequent tasks:
- Authentication API (login, register, password reset)
- Portfolio subsite
- PHARMXAM exam system
- HUB3660 course management
- HEALTHEE consultation system
- Payment integration
- Zoom integration

## License

MIT License - See LICENSE file for details
