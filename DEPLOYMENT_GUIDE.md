# VEETSSUITES Deployment Guide

This guide covers deploying the VEETSSUITES platform to production environments.

## 🚀 Quick Deployment Options

### Option 1: Vercel + Render (Recommended)
- **Frontend**: Vercel (automatic deployments)
- **Backend**: Render (managed PostgreSQL + Redis)
- **Storage**: AWS S3
- **Estimated Setup Time**: 30 minutes

### Option 2: AWS Full Stack
- **Frontend**: AWS Amplify or S3 + CloudFront
- **Backend**: AWS ECS or EC2
- **Database**: AWS RDS PostgreSQL
- **Cache**: AWS ElastiCache Redis
- **Estimated Setup Time**: 2-3 hours

### Option 3: Self-Hosted
- **Frontend**: Nginx + PM2
- **Backend**: Gunicorn + Nginx
- **Database**: PostgreSQL
- **Cache**: Redis
- **Estimated Setup Time**: 4-6 hours

## 📋 Pre-Deployment Checklist

### Environment Setup
- [ ] Domain name registered and DNS configured
- [ ] SSL certificates obtained (Let's Encrypt recommended)
- [ ] Production database created (PostgreSQL 13+)
- [ ] Redis instance configured
- [ ] AWS S3 bucket created with proper IAM permissions
- [ ] Email service configured (SendGrid, AWS SES, etc.)

### API Keys and Services
- [ ] Stripe production keys obtained
- [ ] Paystack production keys obtained
- [ ] Zoom API credentials configured
- [ ] AI service API keys (OpenAI, etc.)
- [ ] Monitoring service setup (Sentry, DataDog, etc.)

### Security Configuration
- [ ] Environment variables secured
- [ ] CORS origins configured
- [ ] Rate limiting configured
- [ ] Security headers enabled
- [ ] Backup strategy implemented

## 🔧 Option 1: Vercel + Render Deployment

### Step 1: Backend Deployment (Render)

1. **Create Render Account**
   ```bash
   # Visit https://render.com and create account
   # Connect your GitHub repository
   ```

2. **Create PostgreSQL Database**
   - Go to Render Dashboard → New → PostgreSQL
   - Choose plan (Starter $7/month recommended)
   - Note the connection string

3. **Create Redis Instance**
   - Go to Render Dashboard → New → Redis
   - Choose plan (Starter $7/month recommended)
   - Note the connection string

4. **Deploy Backend Service**
   - Go to Render Dashboard → New → Web Service
   - Connect GitHub repository
   - Configure settings:
     ```
     Name: veetssuites-backend
     Environment: Python 3
     Build Command: pip install -r requirements.txt
     Start Command: gunicorn veetssuites.wsgi:application
     ```

5. **Configure Environment Variables**
   ```bash
   # Required environment variables
   DEBUG=False
   SECRET_KEY=your-production-secret-key-here
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   REDIS_URL=redis://user:pass@host:port
   ALLOWED_HOSTS=your-backend-domain.onrender.com
   
   # AWS S3
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   AWS_STORAGE_BUCKET_NAME=your-s3-bucket
   AWS_S3_REGION_NAME=us-east-1
   
   # Payment Services
   STRIPE_SECRET_KEY=sk_live_your-stripe-secret-key
   STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
   PAYSTACK_SECRET_KEY=sk_live_your-paystack-secret-key
   
   # External Services
   ZOOM_API_KEY=your-zoom-api-key
   ZOOM_API_SECRET=your-zoom-api-secret
   AI_API_KEY=your-ai-api-key
   
   # Email
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_PORT=587
   EMAIL_HOST_USER=apikey
   EMAIL_HOST_PASSWORD=your-sendgrid-api-key
   
   # CORS
   CORS_ALLOWED_ORIGINS=https://your-domain.com
   ```

6. **Deploy and Verify**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Visit `https://your-backend.onrender.com/api/health/` to verify

### Step 2: Frontend Deployment (Vercel)

1. **Create Vercel Account**
   ```bash
   # Visit https://vercel.com and create account
   # Install Vercel CLI (optional)
   npm i -g vercel
   ```

2. **Connect Repository**
   - Go to Vercel Dashboard → New Project
   - Import your GitHub repository
   - Select `frontend` as root directory

3. **Configure Build Settings**
   ```
   Framework Preset: Next.js
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

4. **Configure Environment Variables**
   ```bash
   # Production environment variables
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   NEXT_PUBLIC_SITE_URL=https://your-domain.com
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your-stripe-public-key
   NEXT_PUBLIC_PAYSTACK_PUBLIC_KEY=pk_live_your-paystack-public-key
   ```

5. **Deploy and Configure Domain**
   - Click "Deploy"
   - Add custom domain in Vercel dashboard
   - Configure DNS records as instructed

### Step 3: Post-Deployment Configuration

1. **Database Migration**
   ```bash
   # SSH into Render service or use Render Shell
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic --noinput
   ```

2. **Configure Webhooks**
   - **Stripe**: Add webhook endpoint `https://your-backend.onrender.com/api/payments/stripe/webhook/`
   - **Paystack**: Add webhook endpoint `https://your-backend.onrender.com/api/payments/paystack/webhook/`
   - **Zoom**: Configure webhook URL if using meeting events

3. **Test Payment Flows**
   ```bash
   # Test Stripe integration
   curl -X POST https://your-backend.onrender.com/api/payments/stripe/create-intent/ \
     -H "Authorization: Bearer your-jwt-token" \
     -H "Content-Type: application/json" \
     -d '{"amount": 1000, "currency": "usd"}'
   ```

## 🔧 Option 2: AWS Full Stack Deployment

### Step 1: Infrastructure Setup

1. **Create AWS Resources**
   ```bash
   # Using AWS CLI
   aws rds create-db-instance \
     --db-instance-identifier veetssuites-prod \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username admin \
     --master-user-password your-secure-password \
     --allocated-storage 20
   
   aws elasticache create-cache-cluster \
     --cache-cluster-id veetssuites-redis \
     --cache-node-type cache.t3.micro \
     --engine redis \
     --num-cache-nodes 1
   ```

2. **Create ECS Cluster**
   ```bash
   aws ecs create-cluster --cluster-name veetssuites-cluster
   ```

### Step 2: Backend Deployment (ECS)

1. **Create Dockerfile** (if not exists)
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 8000
   CMD ["gunicorn", "veetssuites.wsgi:application", "--bind", "0.0.0.0:8000"]
   ```

2. **Build and Push to ECR**
   ```bash
   # Create ECR repository
   aws ecr create-repository --repository-name veetssuites-backend
   
   # Build and push image
   docker build -t veetssuites-backend ./backend
   docker tag veetssuites-backend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/veetssuites-backend:latest
   docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/veetssuites-backend:latest
   ```

3. **Create ECS Task Definition**
   ```json
   {
     "family": "veetssuites-backend",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "256",
     "memory": "512",
     "executionRoleArn": "arn:aws:iam::123456789:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "backend",
         "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/veetssuites-backend:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {"name": "DEBUG", "value": "False"},
           {"name": "DATABASE_URL", "value": "postgresql://admin:password@rds-endpoint:5432/veetssuites"}
         ]
       }
     ]
   }
   ```

### Step 3: Frontend Deployment (S3 + CloudFront)

1. **Build Frontend**
   ```bash
   cd frontend
   npm run build
   npm run export  # If using static export
   ```

2. **Deploy to S3**
   ```bash
   aws s3 sync out/ s3://your-frontend-bucket --delete
   ```

3. **Configure CloudFront**
   ```bash
   aws cloudfront create-distribution \
     --distribution-config file://cloudfront-config.json
   ```

## 🔧 Option 3: Self-Hosted Deployment

### Step 1: Server Setup

1. **Provision Server** (Ubuntu 20.04+ recommended)
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install dependencies
   sudo apt install -y python3 python3-pip nodejs npm nginx postgresql redis-server
   ```

2. **Configure PostgreSQL**
   ```bash
   sudo -u postgres createuser --interactive
   sudo -u postgres createdb veetssuites
   ```

3. **Configure Nginx**
   ```nginx
   # /etc/nginx/sites-available/veetssuites
   server {
       listen 80;
       server_name your-domain.com;
       
       location /api/ {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location / {
           proxy_pass http://127.0.0.1:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Step 2: Application Deployment

1. **Deploy Backend**
   ```bash
   # Clone repository
   git clone https://github.com/VeeCC-T/VEETSSUITES.git
   cd VEETSSUITES/backend
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env with production values
   
   # Run migrations
   python manage.py migrate
   python manage.py collectstatic --noinput
   
   # Start with Gunicorn
   gunicorn veetssuites.wsgi:application --bind 127.0.0.1:8000 --daemon
   ```

2. **Deploy Frontend**
   ```bash
   cd ../frontend
   npm install
   npm run build
   npm start &  # Or use PM2 for process management
   ```

### Step 3: Process Management with PM2

1. **Install PM2**
   ```bash
   npm install -g pm2
   ```

2. **Create PM2 Configuration**
   ```json
   {
     "apps": [
       {
         "name": "veetssuites-backend",
         "cwd": "/path/to/VEETSSUITES/backend",
         "script": "venv/bin/gunicorn",
         "args": "veetssuites.wsgi:application --bind 127.0.0.1:8000",
         "env": {
           "DEBUG": "False"
         }
       },
       {
         "name": "veetssuites-frontend",
         "cwd": "/path/to/VEETSSUITES/frontend",
         "script": "npm",
         "args": "start"
       }
     ]
   }
   ```

3. **Start Services**
   ```bash
   pm2 start ecosystem.json
   pm2 startup
   pm2 save
   ```

## 🔒 SSL Configuration

### Using Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring Setup

### 1. Application Monitoring (Sentry)

```python
# backend/veetssuites/settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
)
```

### 2. Server Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Setup log rotation
sudo nano /etc/logrotate.d/veetssuites
```

### 3. Database Monitoring

```sql
-- Enable PostgreSQL logging
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();
```

## 🔄 Backup Strategy

### 1. Database Backup

```bash
#!/bin/bash
# backup-db.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump veetssuites > /backups/db_backup_$DATE.sql
aws s3 cp /backups/db_backup_$DATE.sql s3://your-backup-bucket/
```

### 2. File Backup

```bash
#!/bin/bash
# backup-files.sh
tar -czf /backups/files_$(date +%Y%m%d).tar.gz /path/to/media/files
aws s3 sync /backups/ s3://your-backup-bucket/backups/
```

### 3. Automated Backups

```bash
# Add to crontab
0 2 * * * /path/to/backup-db.sh
0 3 * * * /path/to/backup-files.sh
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Check connection
   psql -h localhost -U username -d veetssuites
   ```

2. **Redis Connection Issues**
   ```bash
   # Check Redis status
   sudo systemctl status redis
   
   # Test connection
   redis-cli ping
   ```

3. **Static Files Not Loading**
   ```bash
   # Collect static files
   python manage.py collectstatic --noinput
   
   # Check Nginx configuration
   sudo nginx -t
   ```

4. **SSL Certificate Issues**
   ```bash
   # Check certificate status
   sudo certbot certificates
   
   # Renew if needed
   sudo certbot renew --dry-run
   ```

### Performance Optimization

1. **Database Optimization**
   ```sql
   -- Add indexes for frequently queried fields
   CREATE INDEX idx_user_email ON accounts_user(email);
   CREATE INDEX idx_exam_category ON exams_exam(category);
   ```

2. **Nginx Optimization**
   ```nginx
   # Enable gzip compression
   gzip on;
   gzip_types text/plain text/css application/json application/javascript;
   
   # Enable caching
   location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

3. **Application Optimization**
   ```python
   # Use connection pooling
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'OPTIONS': {
               'MAX_CONNS': 20,
               'CONN_MAX_AGE': 600,
           }
       }
   }
   ```

## 📞 Support

For deployment support:
- **Documentation**: Check this guide and README.md
- **Issues**: Create GitHub issue with deployment logs
- **Email**: support@veetssuites.com

## 🎯 Post-Deployment Checklist

- [ ] All services running and accessible
- [ ] SSL certificates installed and auto-renewing
- [ ] Database migrations applied
- [ ] Static files serving correctly
- [ ] Payment webhooks configured and tested
- [ ] Email delivery working
- [ ] Monitoring and logging configured
- [ ] Backup strategy implemented and tested
- [ ] Performance testing completed
- [ ] Security scan passed
- [ ] Domain DNS configured correctly

---

**Congratulations! Your VEETSSUITES platform is now live! 🎉**