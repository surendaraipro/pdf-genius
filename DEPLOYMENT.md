# PDF Genius Deployment Guide

## 🚀 Production Deployment Options

### Option 1: Railway.app (Recommended for MVP)
**Easiest deployment, free tier available**

```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login to Railway
railway login

# 3. Initialize project
railway init

# 4. Deploy
railway up
```

**Railway Services:**
- PostgreSQL database
- Redis cache
- Backend service (FastAPI)
- Frontend service (Next.js)

**Cost:** ~$5-20/month for basic usage

### Option 2: DigitalOcean App Platform
**Simple, managed platform**

```bash
# 1. Create app in DigitalOcean dashboard
# 2. Connect GitHub repository
# 3. Configure services:
#    - Backend: Python service
#    - Frontend: Static site
#    - Database: Managed PostgreSQL
#    - Redis: Managed Redis
```

**Cost:** ~$15-30/month

### Option 3: Self-hosted with Docker
**Full control, most cost-effective**

```bash
# 1. Clone repository on your server
git clone https://github.com/yourusername/pdf-genius.git
cd pdf-genius

# 2. Set up environment variables
cp .env.example .env
# Edit .env with production values

# 3. Start with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# 4. Set up reverse proxy (nginx)
# See nginx.conf.example
```

**Cost:** VPS starting at $5/month (DigitalOcean, Linode, Vultr)

## 📋 Production Checklist

### 1. Security
- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Set up firewall rules
- [ ] Regular security updates

### 2. Database
- [ ] Regular backups
- [ ] Performance optimization
- [ ] Connection pooling
- [ ] Monitoring

### 3. Storage
- [ ] Configure S3/Backblaze for file storage
- [ ] Set up CDN for static assets
- [ ] Implement file cleanup policy

### 4. Monitoring
- [ ] Application logs
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring
- [ ] Uptime monitoring

### 5. Scaling
- [ ] Load balancing
- [ ] Database replication
- [ ] Cache strategy
- [ ] Queue workers

## 🔧 Environment Variables (Production)

Create `.env.production`:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/pdf_genius_prod

# Redis
REDIS_URL=redis://host:6379/0

# Security
SECRET_KEY=your-very-secure-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Storage
STORAGE_TYPE=s3
S3_BUCKET=your-bucket-name
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_ENDPOINT=https://s3.amazonaws.com

# AI Services
OPENAI_API_KEY=your-openai-api-key
USE_LOCAL_LLM=false  # Use OpenAI in production for reliability

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Application
DEBUG=false
APP_NAME=PDF Genius
APP_VERSION=1.0.0
MAX_UPLOAD_SIZE_MB=100
RATE_LIMIT_PER_MINUTE=100

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Domain
DOMAIN=https://pdfgenius.com
ALLOWED_ORIGINS=https://pdfgenius.com,https://www.pdfgenius.com
```

## 🐳 Docker Compose Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - pdf_genius_network

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    networks:
      - pdf_genius_network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - STORAGE_TYPE=${STORAGE_TYPE}
      - S3_BUCKET=${S3_BUCKET}
      - S3_ACCESS_KEY=${S3_ACCESS_KEY}
      - S3_SECRET_KEY=${S3_SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    volumes:
      - pdf_storage:/app/storage
    restart: unless-stopped
    networks:
      - pdf_genius_network
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
    restart: unless-stopped
    networks:
      - pdf_genius_network
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    restart: unless-stopped
    networks:
      - pdf_genius_network
    depends_on:
      - backend
      - frontend

networks:
  pdf_genius_network:
    driver: bridge

volumes:
  postgres_data:
  pdf_storage:
```

## 📈 Scaling Strategies

### Small Scale (< 1000 users)
- Single server with Docker Compose
- Basic monitoring
- Manual backups

### Medium Scale (1000-10,000 users)
- Separate database server
- Load balancer
- Automated backups
- CDN for static files

### Large Scale (10,000+ users)
- Microservices architecture
- Database replication
- Multiple app servers
- Redis cluster
- Queue system (RabbitMQ/Celery)

## 💰 Cost Optimization

### Free/Cheap Options:
1. **Railway** - Free tier + $5/month for database
2. **Render** - Free tier with limitations
3. **Fly.io** - Free allowances
4. **Oracle Cloud** - Always free tier

### Cost Breakdown (Estimated):
- **Basic:** $10-20/month (VPS + domain)
- **Standard:** $30-50/month (managed services)
- **Business:** $100+/month (high availability)

## 🚨 Emergency Procedures

### Database Backup:
```bash
# Backup
docker-compose exec postgres pg_dump -U postgres pdf_genius > backup.sql

# Restore
cat backup.sql | docker-compose exec -T postgres psql -U postgres pdf_genius
```

### Rollback Deployment:
```bash
# Revert to previous version
git checkout previous-commit
docker-compose up --build -d
```

### Monitor Logs:
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend

# Error logs only
docker-compose logs --tail=100 | grep ERROR
```

## 📊 Performance Monitoring

### Key Metrics to Track:
1. **Response Time:** < 500ms for API calls
2. **Uptime:** > 99.9%
3. **Error Rate:** < 1%
4. **Conversion Rate:** Free → Paid
5. **User Growth:** Month-over-month

### Tools:
- **Uptime Robot** - Free monitoring
- **Google Analytics** - User tracking
- **Sentry** - Error tracking
- **Datadog** - Advanced monitoring (paid)

## 🎯 Go-to-Market Strategy

### Launch Plan:
1. **Week 1:** Soft launch to friends & family
2. **Week 2:** Product Hunt launch
3. **Week 3:** Reddit communities
4. **Week 4:** Content marketing (blog posts)
5. **Month 2:** Paid ads (Google/Facebook)
6. **Month 3:** Affiliate program

### Pricing Strategy:
- **Free tier:** Lead generation
- **Pro plan:** Main revenue stream
- **Business plan:** Upsell opportunity
- **Enterprise:** Custom deals

## 📞 Support Setup

### Essential:
- [ ] Documentation website
- [ ] FAQ page
- [ ] Contact form
- [ ] Email support

### Advanced:
- [ ] Live chat (Crisp/Intercom)
- [ ] Help desk (Zendesk)
- [ ] Community forum
- [ ] Video tutorials

---

**Remember:** Start simple, validate with users, then scale based on demand. The MVP should be live within 7 days, then iterate based on feedback.

Good luck with your launch! 🚀