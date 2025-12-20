# Production Deployment Checklist

Complete this checklist before deploying to production.

## Pre-Deployment Security

### Environment Variables

- [ ] All `.env` files excluded from git (verify with `git ls-files | grep "\.env$"`)
- [ ] New `.env` files created from `.env.example` templates
- [ ] All secrets regenerated (not using development/example values)
- [ ] `JWT_SECRET` is strong (min 32 chars, generated with `secrets` module)
- [ ] Database password is strong (min 20 chars)
- [ ] All API keys are production keys (not test/development keys)
- [ ] Stripe uses live keys (`sk_live_`, `pk_live_`)
- [ ] `TOKEN_ENCRYPTION_KEY` generated with Fernet

### Configuration

- [ ] `ENVIRONMENT=production` in all `.env` files
- [ ] `DEBUG=false` in all `.env` files
- [ ] All URLs use HTTPS (no `http://` in production configs)
- [ ] `CORS_ORIGINS` contains only production domains (HTTPS)
- [ ] `FRONTEND_URL` uses production HTTPS URL
- [ ] All OAuth redirect URIs use HTTPS
- [ ] Grafana admin password changed from default
- [ ] Access logging enabled (`ACCESS_LOG_ENABLED=true`)

### Docker

- [ ] `.dockerignore` files exist in `backend/` and `frontend/`
- [ ] Docker images use pinned versions (no `:latest` tags)
- [ ] Containers run as non-root users
- [ ] Production docker-compose file uses HTTPS URLs
- [ ] DNS servers configurable (not hardcoded)

### Code Quality

- [ ] No hardcoded secrets in code
- [ ] ReDoS-vulnerable regex patterns fixed
- [ ] `secrets` module used instead of `random` for security-sensitive data
- [ ] SSL verification enabled (no `DISABLE_SSL_VERIFICATION=true`)
- [ ] CSP policy configured for production domain

## Deployment

### Infrastructure

- [ ] HTTPS/TLS certificates installed and valid
- [ ] Firewall rules configured (allow 80/443, block direct database access)
- [ ] Database backups configured
- [ ] Monitoring stack deployed (Grafana, Prometheus)
- [ ] Log aggregation configured
- [ ] CDN configured (if applicable)

### Application

- [ ] Database migrations run successfully
- [ ] Static assets built and optimized
- [ ] Health check endpoints responding
- [ ] Rate limiting configured
- [ ] Session timeout configured

## Post-Deployment

### Verification

- [ ] Application accessible via HTTPS
- [ ] HTTP automatically redirects to HTTPS
- [ ] API endpoints require authentication where appropriate
- [ ] WebSocket connections use WSS protocol
- [ ] CORS only allows production domains
- [ ] CSP headers present in browser
- [ ] No console errors in browser
- [ ] No server errors in logs

### Monitoring

- [ ] Application metrics visible in Grafana
- [ ] Error rates within acceptable range
- [ ] Response times within acceptable range
- [ ] Database connection pool healthy
- [ ] Redis cache operational
- [ ] Celery workers processing tasks

### Security

- [ ] Security headers present (`X-Frame-Options`, `X-Content-Type-Options`, etc.)
- [ ] No sensitive data in logs
- [ ] No debug information exposed in error responses
- [ ] Rate limiting effective
- [ ] SSL/TLS grade A on SSL Labs (https://www.ssllabs.com/ssltest/)

## Rollback Plan

If issues arise:

1. Switch traffic back to previous version
2. Check logs for errors: `docker-compose logs -f backend`
3. Verify database state
4. Check environment variables
5. Test locally with production config (sanitized secrets)

## Emergency Contacts

- **DevOps Lead**: [contact info]
- **Security Team**: security@yourdomain.com
- **On-Call Engineer**: [contact info]
