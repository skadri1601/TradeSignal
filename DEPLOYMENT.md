# TradeSignal Deployment Runbook

Complete guide for deploying TradeSignal to production.

## Pre-Deployment Checklist

### Required Services
- [ ] PostgreSQL database (Supabase/Railway/managed service)
- [ ] Redis instance (Redis Cloud/Upstash free tier)
- [ ] Domain name configured
- [ ] SSL certificate (Let's Encrypt via Caddy/Nginx)
- [ ] Email service (SendGrid account)
- [ ] API keys obtained (Gemini, Alpha Vantage)
- [ ] Sentry account (optional, for error tracking)
- [ ] Stripe account (for payments)

### Environment Variables
- [ ] All secrets rotated (new JWT_SECRET, etc.)
- [ ] Production DATABASE_URL configured
- [ ] CORS_ORIGINS set to production domains
- [ ] ENVIRONMENT=production
- [ ] DEBUG=false
- [ ] Sentry DSN configured
- [ ] Stripe keys added

## Deployment Options

### Option 1: Railway + Vercel (Recommended for MVP)

**Backend (Railway)**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Add PostgreSQL
railway add postgresql

# Add Redis
railway add redis

# Set environment variables
railway variables set ENVIRONMENT=production
railway variables set JWT_SECRET=$(openssl rand -hex 32)
railway variables set GEMINI_API_KEY=your-key
railway variables set STRIPE_SECRET_KEY=your-key
# ... add all other env vars

# Deploy backend
cd backend
railway up

# Get deployment URL
railway domain
```

**Frontend (Vercel)**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod

# Set environment variables in Vercel dashboard
# VITE_API_URL=https://your-backend-url.railway.app
```

**Database Migration**
```bash
# SSH into Railway container or run locally with production DB
railway run alembic upgrade head
```

### Option 2: Docker Compose on VPS

**Prerequisites**
- Ubuntu 22.04 LTS server
- Docker and Docker Compose installed
- Domain pointing to server IP

**Setup Steps**

1. **Server Preparation**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Create tradesignal user
sudo useradd -m -s /bin/bash tradesignal
sudo usermod -aG docker tradesignal
```

2. **Deploy Application**
```bash
# Clone repository
cd /home/tradesignal
git clone https://github.com/youruser/tradesignal.git
cd tradesignal

# Copy and configure environment
cp backend/.env.example backend/.env
nano backend/.env  # Configure all production values

cp frontend/.env.example frontend/.env
nano frontend/.env  # Set VITE_API_URL

# Start services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Check logs
docker-compose logs -f
```

3. **Configure Nginx Reverse Proxy**
```nginx
# /etc/nginx/sites-available/tradesignal
server {
    listen 80;
    server_name tradesignal.com www.tradesignal.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tradesignal.com www.tradesignal.com;

    ssl_certificate /etc/letsencrypt/live/tradesignal.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tradesignal.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:5174;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

4. **SSL Certificate**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d tradesignal.com -d www.tradesignal.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### Option 3: Fly.io + Cloudflare Pages

**Backend (Fly.io)**

Create `fly.toml`:
```toml
app = "tradesignal-backend"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  ENVIRONMENT = "production"
  PORT = "8000"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1

[[services]]
  protocol = "tcp"
  internal_port = 8000

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

  [services.concurrency]
    type = "connections"
    hard_limit = 250
    soft_limit = 200
```

Deploy:
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Create app
flyctl launch

# Add PostgreSQL
flyctl postgres create

# Add Redis
flyctl redis create

# Set secrets
flyctl secrets set JWT_SECRET=$(openssl rand -hex 32)
flyctl secrets set GEMINI_API_KEY=your-key
flyctl secrets set STRIPE_SECRET_KEY=your-key

# Deploy
flyctl deploy

# Run migrations
flyctl ssh console
alembic upgrade head
```

**Frontend (Cloudflare Pages)**
```bash
# Build frontend
cd frontend
npm run build

# Deploy to Cloudflare Pages
npx wrangler pages deploy dist --project-name=tradesignal
```

## Post-Deployment

### 1. Database Initialization

```bash
# Create initial admin user
docker-compose exec backend python -c "
from app.database import db_manager
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
async def create_admin():
    async with db_manager.get_session() as session:
        admin = User(
            email='admin@tradesignal.com',
            username='admin',
            hashed_password=pwd_context.hash('CHANGE_THIS_PASSWORD'),
            is_superuser=True,
            is_active=True,
            is_verified=True
        )
        session.add(admin)
        await session.commit()

import asyncio
asyncio.run(create_admin())
"
```

### 2. Verify Services

```bash
# Health check
curl https://api.tradesignal.com/api/v1/health/

# Expected response:
# {"status":"healthy","timestamp":"2025-11-14T19:00:00Z","version":"1.0.0"}

# Database connection
curl https://api.tradesignal.com/api/v1/health/ready

# Metrics
curl https://api.tradesignal.com/metrics
```

### 3. Configure Monitoring

**Sentry**
1. Create project at sentry.io
2. Copy DSN
3. Set `SENTRY_DSN` environment variable
4. Restart backend

**Grafana**
1. Access Grafana at https://tradesignal.com:3500
2. Login (admin/admin)
3. Change default password
4. Add Prometheus data source: http://prometheus:9090
5. Import dashboard from `grafana/dashboards/`

### 4. Setup Automated Backups

**PostgreSQL Backups**
```bash
# Create backup script
cat > /home/tradesignal/backup.sh <<'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/tradesignal/backups"
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T postgres pg_dump -U postgres tradesignal > \
    $BACKUP_DIR/tradesignal_$DATE.sql

# Compress
gzip $BACKUP_DIR/tradesignal_$DATE.sql

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
# aws s3 cp $BACKUP_DIR/tradesignal_$DATE.sql.gz s3://your-bucket/backups/
EOF

chmod +x /home/tradesignal/backup.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /home/tradesignal/backup.sh") | crontab -
```

### 5. Configure Alerts

**Uptime Monitoring**
- Add to UptimeRobot / Pingdom
- Monitor: https://api.tradesignal.com/api/v1/health/
- Alert on: 5 minute downtime

**Error Alerts**
- Configure Sentry alerts for:
  - Error rate > 1% (5 min window)
  - New issue appears
  - Issue regresses

## Rollback Procedure

### Quick Rollback (Docker)
```bash
# Stop current version
docker-compose down

# Checkout previous version
git checkout <previous-commit>

# Rebuild and start
docker-compose up -d --build

# Rollback migrations if needed
docker-compose exec backend alembic downgrade -1
```

### Railway Rollback
```bash
# List deployments
railway logs --deployment

# Rollback to specific deployment
railway rollback <deployment-id>
```

## Scaling

### Horizontal Scaling

**Add Backend Replicas**
```bash
# Docker Swarm
docker service scale tradesignal_backend=3

# Kubernetes
kubectl scale deployment tradesignal-backend --replicas=3
```

**Load Balancer Configuration**
```nginx
upstream backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

### Database Scaling

**Read Replicas**
1. Create read replica in database provider
2. Configure SQLAlchemy with read/write split:
```python
# app/database.py
WRITE_DB_URL = os.getenv("DATABASE_URL")
READ_DB_URL = os.getenv("DATABASE_READ_URL", WRITE_DB_URL)
```

**Connection Pooling**
- Already configured: pool_size=20, max_overflow=40
- Monitor with: `SELECT count(*) FROM pg_stat_activity;`

## Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection from backend
docker-compose exec backend python -c \
    "from app.database import db_manager; import asyncio; \
     asyncio.run(db_manager.check_connection())"

# Check logs
docker-compose logs postgres
```

**2. Redis Connection Issues**
```bash
# Test Redis
docker-compose exec redis redis-cli ping

# Check backend connection
docker-compose exec backend python -c \
    "from app.core.redis_cache import get_cache; print(get_cache().ping())"
```

**3. High Memory Usage**
```bash
# Check container stats
docker stats

# Restart services
docker-compose restart backend

# Check for memory leaks in Sentry
```

**4. Celery Tasks Not Running**
```bash
# Check Celery worker
docker-compose logs celery-worker

# Check Celery beat
docker-compose logs celery-beat

# Inspect tasks
docker-compose exec backend celery -A app.tasks inspect active
```

## Security Checklist

- [ ] All secrets rotated (different from development)
- [ ] HTTPS enforced (no HTTP)
- [ ] CORS configured for production domains only
- [ ] Rate limiting enabled
- [ ] Database firewall configured (only backend access)
- [ ] Redis password set
- [ ] Sentry PII disabled
- [ ] Admin password changed
- [ ] SSH key authentication only (no passwords)
- [ ] Fail2ban installed
- [ ] UFW firewall configured

## Performance Optimization

### CDN Configuration (Cloudflare)
1. Add domain to Cloudflare
2. Enable auto-minify (JS, CSS, HTML)
3. Enable Brotli compression
4. Set caching rules:
   - `/api/*` - No cache
   - `/static/*` - Cache 1 year
   - `*.js, *.css` - Cache 1 month

### Database Indexing
```sql
-- Already created via Alembic migrations
-- Verify indexes
SELECT * FROM pg_indexes WHERE tablename IN ('trades', 'companies', 'insiders');
```

## Maintenance Windows

Recommended: Sundays 2-4 AM EST (lowest traffic)

```bash
# Maintenance mode script
./scripts/maintenance.sh on

# Perform updates
git pull
docker-compose build
docker-compose up -d
docker-compose exec backend alembic upgrade head

# Exit maintenance
./scripts/maintenance.sh off
```

## Contact & Support

- **Sentry Issues**: https://sentry.io/organizations/tradesignal
- **Monitoring**: https://tradesignal.com:3500 (Grafana)
- **Logs**: `docker-compose logs -f --tail=100 backend`
- **Database Admin**: https://supabase.com/dashboard (if using Supabase)
