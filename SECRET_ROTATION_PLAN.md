# Secret Rotation Plan

Execute these steps to rotate all exposed secrets.

## Priority 1: Database (IMMEDIATE)

```bash
# 1. Change database password
# - Login to database provider (Supabase/PostgreSQL)
# - Generate new strong password
# - Update DATABASE_URL in .env files

# 2. Restart application
docker-compose down
docker-compose up -d

# 3. Verify connection
docker-compose logs backend | grep "Database connection successful"
```

## Priority 2: JWT Secret (IMMEDIATE)

```bash
# 1. Generate new JWT secret
python -c "import secrets; print(secrets.token_urlsafe(64))"

# 2. Update .env files
# backend/.env: JWT_SECRET=<new-secret>
# .env: JWT_SECRET=<new-secret>

# 3. Restart application (all users will be logged out)
docker-compose restart backend

# 4. Notify users of forced logout (optional)
```

## Priority 3: API Keys (Within 24 hours)

### Stripe

1. Login to https://dashboard.stripe.com/apikeys
2. Create new API keys (or roll current keys)
3. Update webhook secret
4. Update `.env` files:
   - `STRIPE_SECRET_KEY`
   - `STRIPE_PUBLISHABLE_KEY`
   - `STRIPE_WEBHOOK_SECRET`
5. Update frontend `.env`: `VITE_STRIPE_PUBLIC_KEY`
6. Restart application

### Gemini/Google AI

1. Login to https://makersuite.google.com/app/apikey
2. Create new API key
3. Revoke old key
4. Update `GEMINI_API_KEY` in backend/.env
5. Restart backend

### Alpha Vantage

1. Login to https://www.alphavantage.co/support/#support
2. Request new API key
3. Update `ALPHA_VANTAGE_API_KEY` in backend/.env
4. Restart backend

### Finnhub

1. Login to https://finnhub.io/dashboard
2. Regenerate API key
3. Update `FINNHUB_API_KEY` in backend/.env
4. Restart backend

### FRED

1. Login to https://fred.stlouisfed.org/docs/api/api_key.html
2. Request new API key
3. Update `FRED_API_KEY` in backend/.env
4. Restart backend

### Email Provider (SendGrid/Resend/Brevo)

1. Login to provider dashboard
2. Generate new API key
3. Revoke old key
4. Update `EMAIL_API_KEY` in backend/.env
5. Test email functionality
6. Restart backend

## Priority 4: Encryption Keys (Within 48 hours)

### Token Encryption Key

**WARNING**: Rotating this will invalidate all stored OAuth tokens.

```bash
# 1. Generate new Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 2. Update TOKEN_ENCRYPTION_KEY in backend/.env

# 3. Clear existing encrypted tokens
# Run migration to re-encrypt or clear stored tokens

# 4. Restart application

# 5. Notify users to re-authenticate with brokers
```

### VAPID Keys (Push Notifications)

**WARNING**: Rotating these will invalidate all push notification subscriptions.

```bash
# 1. Generate new VAPID keys
npx web-push generate-vapid-keys

# 2. Update backend/.env:
#    - VAPID_PRIVATE_KEY
#    - VAPID_PUBLIC_KEY
#    - VAPID_PUBLIC_KEY_BASE64

# 3. Restart application

# 4. Users will need to re-subscribe to push notifications
```

## Priority 5: OAuth Credentials (Before Production)

### Alpaca

1. Login to Alpaca Developer Console
2. Create new OAuth application or regenerate secret
3. Update `ALPACA_OAUTH_CLIENT_ID` and `ALPACA_OAUTH_CLIENT_SECRET`
4. Update `ALPACA_REDIRECT_URI` to use HTTPS
5. Restart backend

### TD Ameritrade

1. Login to TD Ameritrade Developer Console
2. Create new OAuth application or regenerate secret
3. Update `TD_AMERITRADE_CLIENT_ID`
4. Update `TD_AMERITRADE_REDIRECT_URI` to use HTTPS
5. Restart backend

### Interactive Brokers

1. Login to IB Developer Portal
2. Create new OAuth application or regenerate secret
3. Update `IB_CLIENT_ID`
4. Update `IB_REDIRECT_URI` to use HTTPS
5. Restart backend

## Verification

After rotating all secrets:

```bash
# 1. Test authentication
curl -X POST https://api.yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass"}'

# 2. Test database connection
docker-compose exec backend python -c "from app.database import db_manager; import asyncio; asyncio.run(db_manager.test_connection())"

# 3. Test external APIs
# - Check Stripe webhook events
# - Test AI insights generation
# - Verify market data fetching

# 4. Monitor logs for errors
docker-compose logs -f --tail=100 backend
```

## Documentation

After rotation:

1. Update internal documentation with new key locations
2. Store secrets in password manager (1Password, LastPass, etc.)
3. Document who has access to each secret
4. Set calendar reminder for next rotation (90 days recommended)

## Recovery

If issues occur during rotation:

1. Keep old secrets accessible for 24-48 hours
2. Have rollback plan ready
3. Monitor error rates in Grafana
4. Keep communication channels open with team
