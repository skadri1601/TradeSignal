# TradeSignal Production Deployment Guide

This guide details the steps required to deploy TradeSignal to a production server with a custom domain.

## 1. System Requirements

*   **OS:** Linux (Ubuntu 22.04 LTS recommended) or Windows Server with WSL2.
*   **Hardware:**
    *   Minimum: 2 vCPU, 4GB RAM (for small scale).
    *   Recommended: 4 vCPU, 8GB+ RAM (to handle AI processing and Celery workers efficiently).
*   **Software:**
    *   Docker Engine (v24+)
    *   Docker Compose (v2+)
    *   Git

## 2. Domain Configuration

Since the final domain name is pending, we will refer to it as `yourdomain.com` in this guide.

1.  **DNS Records:** Log in to your domain registrar (GoDaddy, Namecheap, AWS Route53, etc.).
2.  **A Record:** Create an `@` record pointing to your server's Public IP address.
3.  **CNAME Record:** Create a `www` record pointing to `@` (or your domain name).

## 3. Environment Setup

Never commit `.env` files to the repository. Create a `.env.prod` file on the server in the root directory:

```bash
# General
ENVIRONMENT=production
DEBUG=false
DOMAIN_NAME=yourdomain.com

# Database (PostgreSQL)
POSTGRES_USER=tradesignal_prod
POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD_HERE
POSTGRES_DB=tradesignal
DATABASE_URL=postgresql+asyncpg://tradesignal_prod:YOUR_STRONG_PASSWORD_HERE@postgres:5432/tradesignal

# Security
JWT_SECRET=YOUR_SUPER_SECRET_LONG_RANDOM_STRING
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# AI Providers (Required)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
AI_PROVIDER=gemini
GEMINI_MODEL=gemini-2.0-flash

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

## 4. Production Docker Configuration

We will use a dedicated `docker-compose.prod.yml` (to be created) which includes:

*   **Nginx Reverse Proxy:** Handles incoming traffic on ports 80 (HTTP) and 443 (HTTPS).
*   **SSL/TLS:** Automated certificate management via Certbot (Let's Encrypt).
*   **Restart Policies:** `restart: always` for all services to ensure high availability.
*   **Optimization:** Production builds for the React frontend (served via Nginx, not `vite dev`).

### Proposed `docker-compose.prod.yml` Structure

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    depends_on:
      - frontend
      - backend

  certbot:
    image: certbot/certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot

  backend:
    # ... (Same as dev but with production command: gunicorn/uvicorn workers)
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    # Served internally to Nginx
```

## 5. Deployment Steps

1.  **Clone Repository:**
    ```bash
    git clone https://github.com/your-repo/TradeSignal.git
    cd TradeSignal
    ```

2.  **Set Secrets:**
    Create the `.env` file as described above.

3.  **Build & Run:**
    ```bash
    docker-compose -f docker-compose.prod.yml up -d --build
    ```

4.  **Initialize SSL:**
    ```bash
    # Request certificate (replace email and domain)
    docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path /var/www/certbot -d yourdomain.com -d www.yourdomain.com --email your-email@example.com --agree-tos --no-eff-email
    ```
