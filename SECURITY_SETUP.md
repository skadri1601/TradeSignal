# Security Setup Guide

## Initial Setup

### 1. Environment Variables

Copy the example files and fill in your own values:

```bash
# Root directory
cp .env.example .env

# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

### 2. Generate Secure Secrets

#### JWT Secret (Backend)
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

#### Fernet Encryption Key (Backend)
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

#### VAPID Keys (Push Notifications)
```bash
npx web-push generate-vapid-keys
```

### 3. External API Keys Required

- **Alpha Vantage**: https://www.alphavantage.co/support/#api-key
- **Finnhub**: https://finnhub.io/register
- **FRED**: https://fred.stlouisfed.org/docs/api/api_key.html
- **Google Gemini**: https://makersuite.google.com/app/apikey
- **Stripe**: https://dashboard.stripe.com/apikeys
- **Email Provider**: SendGrid/Resend/Brevo

### 4. Production Checklist

- [ ] All secrets are unique and strong (min 32 chars)
- [ ] DATABASE_URL uses strong password
- [ ] All URLs use HTTPS (no HTTP)
- [ ] DEBUG=false in production
- [ ] ENVIRONMENT=production
- [ ] Stripe uses live keys (sk_live_, pk_live_)
- [ ] CORS_ORIGINS uses production domain
- [ ] SSL verification enabled (DISABLE_SSL_VERIFICATION not set)

## Key Rotation

If any secrets were exposed in git history:

### 1. Rotate Immediately
- JWT_SECRET
- DATABASE_URL password
- All API keys (Stripe, Gemini, Alpha Vantage, etc.)
- TOKEN_ENCRYPTION_KEY
- VAPID keys

### 2. Update Services
- Update Stripe webhook secret
- Regenerate OAuth credentials with brokers
- Update email provider API keys

### 3. Verify
```bash
# Check git history for secrets
git log --all --full-history --source -- "*env*"

# Check current status
git status
git ls-files | grep "\.env$"
```

## Security Contacts

Report security issues to: security@yourdomain.com
