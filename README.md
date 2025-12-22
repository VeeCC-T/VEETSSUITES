# VEETSSUITES Platform

A comprehensive multi-subsite platform providing professional portfolio showcase, pharmacy exam preparation (PHARMXAM), AI-powered health consultation (HEALTHEE ANYWHERE), and technology education with live instruction (HUB3660).

## Overview

VEETSSUITES is a modern JAMstack platform that integrates four distinct services:

- **Portfolio Subsite**: Professional CV showcase with PDF upload and parsing
- **PHARMXAM**: Pharmacy examination preparation with MCQ practice tests
- **HEALTHEE ANYWHERE**: AI and human pharmacist health consultation service
- **HUB3660**: Technology education platform with live Zoom sessions and recordings

## Architecture

### Technology Stack

**Frontend:**
- Next.js 14+ (App Router)
- React 18+
- Tailwind CSS 3+
- TypeScript
- Axios & React Query
- Hosted on Vercel

**Backend:**
- Python 3.11+
- Django 5.0+
- Django REST Framework 3.14+
- MySQL 8.0+
- Celery & Redis
- Hosted on Render or AWS

**External Services:**
- Stripe (global payments)
- Paystack/Flutterwave (Nigerian payments)
- Zoom API (video conferencing)
- AWS S3 (file and video storage)
- AI API (health consultation chatbot)

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

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- MySQL 8.0+
- Git

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Configure environment variables in .env.local
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Configure environment variables in .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The backend API will be available at `http://localhost:8000`

### Environment Variables

**Frontend (.env.local):**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLIC_KEY=your_stripe_key
NEXT_PUBLIC_PAYSTACK_PUBLIC_KEY=your_paystack_key
```

**Backend (.env):**
```
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=mysql://user:password@localhost:3306/veetssuites
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_STORAGE_BUCKET_NAME=your_bucket_name
STRIPE_SECRET_KEY=your_stripe_secret
PAYSTACK_SECRET_KEY=your_paystack_secret
ZOOM_API_KEY=your_zoom_key
ZOOM_API_SECRET=your_zoom_secret
AI_API_KEY=your_ai_api_key
```

## Development

### Running Tests

**Frontend:**
```bash
cd frontend
npm test
npm run test:coverage
```

**Backend:**
```bash
cd backend
pytest
pytest --cov=. --cov-report=html
```

### Code Quality

**Frontend:**
```bash
npm run lint
npm run type-check
```

**Backend:**
```bash
flake8
black .
mypy .
```

## Deployment

### Frontend (Vercel)

1. Connect your GitHub repository to Vercel
2. Configure environment variables in Vercel dashboard
3. Deploy from main branch

### Backend (Render/AWS)

1. Configure production database
2. Set up environment variables
3. Run migrations: `python manage.py migrate`
4. Collect static files: `python manage.py collectstatic`
5. Deploy using your hosting provider's process

## API Documentation

API documentation is available at `/api/docs/` when running the backend server.

## Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please open an issue in the GitHub repository.

## Roadmap

See [project-checklist.json](project-checklist.json) for current development status and upcoming features.
