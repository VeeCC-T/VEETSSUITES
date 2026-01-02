# 🚀 VEETSSUITES Demo Credentials

## Local Development Testing

The VEETSSUITES platform is now running locally with sample data! 

### 🌐 URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin/

### 👤 Demo User Accounts

#### Student Account
- **Email**: demo@veetssuites.com
- **Password**: demo123
- **Role**: Student
- **Access**: All subsites, can enroll in courses

#### Alternative Student Account  
- **Email**: student@veetssuites.com
- **Password**: student123
- **Role**: Student

#### Instructor Account
- **Email**: instructor@veetssuites.com  
- **Password**: instructor123
- **Role**: Instructor
- **Access**: Can create/manage courses

#### Admin Account
- **Email**: admin@veetssuites.com
- **Password**: admin123  
- **Role**: Admin
- **Access**: Full admin dashboard, Django admin

### 🎯 What to Test

#### 1. Portfolio Subsite (http://localhost:3000/portfolio)
- Login with demo account
- Upload CV/resume (demo mode - no actual file upload)
- View portfolio display

#### 2. PHARMXAM Subsite (http://localhost:3000/pharmxam)  
- Login with demo account
- Start practice exams
- View exam history and results
- **Sample Questions**: 15 pharmacy questions loaded

#### 3. HUB3660 Subsite (http://localhost:3000/hub3660)
- Browse course catalog
- View course details  
- **Sample Courses**: 3 pharmacy courses with sessions
- Test enrollment flow (demo mode)

#### 4. HEALTHEE Subsite (http://localhost:3000/healthee)
- Login with demo account
- Start AI consultation
- Test chat interface (demo responses)

#### 5. Admin Dashboard (http://localhost:3000/admin)
- Login with admin account
- View system health
- Manage users and content

### 🔧 Backend Data

- **Courses**: 3 sample pharmacy courses
- **Sessions**: 9 total sessions (3 per course)  
- **Questions**: 15 sample pharmacy exam questions
- **Users**: 5 test accounts with different roles

### 🚨 Demo Mode Features

- Mock API responses for external services
- Simulated file uploads
- Demo payment flows (no real transactions)
- AI chat responses (simulated)
- All features functional for testing

### 🛠️ Development Notes

- Frontend runs on Next.js 14.2.35
- Backend runs on Django 5.0.14
- Database: SQLite (local development)
- All migrations applied
- Sample data loaded automatically

**Ready for full testing of all 4 subsites! 🎉**