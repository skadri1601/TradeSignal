---
name: Production Security Hardening
overview: Comprehensive security hardening plan to make the entire TradeSignal application production-ready, covering authentication, authorization, session management, security headers, rate limiting, input validation, brute force protection, and all security best practices.
todos:
  - id: enable-security-middleware
    content: Enable HTTPS redirect and security headers middleware in main.py
    status: pending
  - id: redis-rate-limiting
    content: Replace in-memory rate limiter with Redis-backed limiter
    status: pending
  - id: brute-force-protection
    content: Implement brute force protection with account lockout
    status: pending
  - id: password-strength
    content: Add password strength validation (min 12 chars, complexity requirements)
    status: pending
  - id: token-blacklisting
    content: Implement token blacklisting in Redis for logout and revocation
    status: pending
  - id: session-management
    content: Add session tracking and revocation capabilities
    status: pending
  - id: input-sanitization
    content: Add comprehensive input sanitization and XSS protection
    status: pending
  - id: csp-improvements
    content: Improve Content Security Policy (remove unsafe-inline, add nonces)
    status: pending
  - id: csrf-protection
    content: Implement CSRF token protection for state-changing requests
    status: pending
  - id: security-audit-logging
    content: Add security audit logging for authentication and authorization events
    status: pending
  - id: error-handling-security
    content: Ensure no sensitive data leaks in error messages
    status: pending
  - id: security-documentation
    content: Create SECURITY.md with security features and best practices
    status: pending
---

# Production Security Hardening Plan

## Current State Analysis

**Existing Security Features:**

- JWT-based authentication with access/refresh tokens
- Role-based authorization (user, support, super_admin)
- Password hashing with bcrypt (12 rounds)
- Basic rate limiting (in-memory, needs Redis)
- CORS configuration
- HTTPS redirect middleware (exists but commented out)
- Basic security headers middleware (exists but commented out)
- Database connection timeout fixes (recently implemented)

**Critical Gaps:**

1. HTTPS redirect middleware disabled
2. Security headers middleware disabled
3. Rate limiting uses in-memory storage (not production-ready)
4. No brute force protection
5. No account lockout mechanism
6. No password strength validation
7. No token blacklisting/revocation
8. No CSRF protection
9. No security audit logging
10. No input sanitization hardening
11. CSP needs improvement (allows unsafe-inline)
12. No 2FA/MFA
13. No API key management
14. No security monitoring/alerting

## Implementation Plan

### Phase 1: Critical Security Infrastructure (Priority 1)

#### 1.1 Enable Security Middleware

- **File**: `backend/app/main.py`
- Enable HTTPS redirect middleware
- Enable security headers middleware
- Add proper CSP headers (remove unsafe-inline)
- Add X-Content-Type-Options, X-Frame-Options, etc.

#### 1.2 Redis-Based Rate Limiting

- **Files**: `backend/app/core/limiter.py`, `backend/app/config.py`
- Replace in-memory rate limiter with Redis-backed limiter
- Add Redis connection configuration
- Implement tier-based rate limits (free: 100/hour, pro: 1000/hour)
- Add per-endpoint rate limiting

#### 1.3 Brute Force Protection

- **Files**: `backend/app/core/security.py`, `backend/app/routers/auth.py`
- Track failed login attempts per IP and email
- Lock accounts after N failed attempts (e.g., 5 attempts)
- Implement exponential backoff
- Store attempts in Redis with TTL
- Add account unlock mechanism

#### 1.4 Password Strength Validation

- **Files**: `backend/app/schemas/user.py`, `backend/app/routers/auth.py`
- Enforce minimum password requirements:
- Minimum 12 characters
- At least 1 uppercase, 1 lowercase, 1 number, 1 special character
- Check against common password lists
- Add password strength meter on frontend

### Phase 2: Session & Token Management (Priority 1)

#### 2.1 Token Blacklisting

- **Files**: `backend/app/core/security.py`, `backend/app/routers/auth.py`
- Implement token blacklist in Redis
- Blacklist tokens on logout
- Check blacklist on token validation
- Add token refresh rotation

#### 2.2 Session Management

- **Files**: `backend/app/models/user.py`, `backend/app/routers/auth.py`
- Track active sessions per user
- Add session revocation endpoint
- Implement "logout all devices" feature
- Add session timeout configuration

#### 2.3 Token Security Enhancements

- **Files**: `backend/app/core/security.py`
- Add token fingerprinting (device/browser fingerprint)
- Implement token rotation on refresh
- Add token expiration warnings
- Secure token storage (httpOnly cookies option)

### Phase 3: Input Validation & Sanitization (Priority 2)

#### 3.1 Input Sanitization

- **Files**: `backend/app/schemas/*.py`
- Add HTML sanitization for user inputs
- Sanitize SQL injection vectors
- Validate and sanitize file uploads
- Add XSS protection for all text inputs

#### 3.2 Request Validation Hardening

- **Files**: `backend/app/routers/*.py`
- Enforce strict type validation
- Add length limits on all inputs
- Validate email formats strictly
- Sanitize URLs and file paths

#### 3.3 SQL Injection Prevention

- **Files**: `backend/app/database.py`, all router files
- Ensure all queries use parameterized statements (already done, verify)
- Add database query logging in development
- Review all raw SQL queries

### Phase 4: Frontend Security (Priority 2)

#### 4.1 Content Security Policy

- **File**: `frontend/index.html`
- Remove `unsafe-inline` from script-src
- Use nonces or hashes for inline scripts
- Tighten CSP for production
- Add report-uri for CSP violations

#### 4.2 XSS Protection

- **Files**: All React components
- Sanitize user-generated content before rendering
- Use React's built-in XSS protection
- Add DOMPurify for rich text content
- Validate all URLs before rendering

#### 4.3 Secure Token Storage

- **Files**: `frontend/src/contexts/AuthContext.tsx`
- Consider httpOnly cookies instead of localStorage
- Add token encryption in localStorage (if keeping localStorage)
- Implement secure token refresh flow
- Add token expiration handling

#### 4.4 CSRF Protection

- **Files**: `frontend/src/api/client.ts`, `backend/app/main.py`
- Add CSRF token generation
- Include CSRF token in all state-changing requests
- Validate CSRF tokens on backend
- Use SameSite cookies

### Phase 5: Security Monitoring & Logging (Priority 2)

#### 5.1 Security Audit Logging

- **Files**: `backend/app/core/audit.py` (new), `backend/app/routers/*.py`
- Log all authentication events (login, logout, failed attempts)
- Log authorization failures
- Log sensitive operations (password changes, role changes)
- Log API access patterns
- Redact PII from logs

#### 5.2 Security Monitoring

- **Files**: `backend/app/core/monitoring.py` (new)
- Track failed login attempts
- Monitor rate limit violations
- Alert on suspicious activity patterns
- Track token usage anomalies

#### 5.3 Error Handling Security

- **Files**: `backend/app/main.py`
- Ensure no sensitive data in error messages
- Generic error messages in production
- Detailed errors only in development
- Log full errors server-side only

### Phase 6: Advanced Security Features (Priority 3)

#### 6.1 Two-Factor Authentication (2FA)

- **Files**: `backend/app/core/2fa.py` (new), `backend/app/routers/auth.py`
- Implement TOTP-based 2FA
- Add QR code generation for setup
- Require 2FA for admin accounts
- Add backup codes

#### 6.2 API Key Management

- **Files**: `backend/app/models/api_key.py` (new), `backend/app/routers/api_keys.py` (new)
- Allow users to generate API keys
- Track API key usage
- Implement key rotation
- Add key expiration

#### 6.3 Account Security Features

- **Files**: `backend/app/routers/auth.py`, `backend/app/routers/user.py`
- Email verification enforcement
- Password reset with secure tokens
- Account recovery flow
- Security notifications (new login, password change)

### Phase 7: Database & Infrastructure Security (Priority 3)

#### 7.1 Database Security

- **Files**: `backend/app/database.py`, `backend/app/config.py`
- Ensure SSL/TLS for database connections
- Use connection pooling (already done)
- Add database query timeout (already done)
- Encrypt sensitive data at rest

#### 7.2 Secrets Management

- **Files**: `backend/app/config.py`
- Validate all secrets are set in production
- Use environment variables (already done)
- Add secrets rotation mechanism
- Document secret generation

#### 7.3 Environment Configuration

- **Files**: `backend/.env.example`, `frontend/.env.example`
- Document all required environment variables
- Add validation for production environment
- Ensure debug mode is off in production
- Validate CORS origins in production

### Phase 8: Security Testing & Documentation (Priority 3)

#### 8.1 Security Testing

- Add security test suite
- Test authentication flows
- Test authorization boundaries
- Test input validation
- Test rate limiting
- Penetration testing checklist

#### 8.2 Security Documentation

- Create `SECURITY.md` file
- Document security features
- Document security best practices
- Create incident response plan
- Document security configuration

## Implementation Order

**Week 1 (Critical):**

1. Enable security middleware
2. Implement Redis rate limiting
3. Add brute force protection
4. Password strength validation

**Week 2 (High Priority):**

5. Token blacklisting
6. Session management
7. Input sanitization
8. Frontend CSP improvements

**Week 3 (Medium Priority):**

9. Security audit logging
10. CSRF protection
11. Error handling security
12. Security monitoring

**Week 4+ (Nice to Have):**

13. 2FA implementation
14. API key management
15. Advanced security features
16. Security testing & documentation

## Files to Create/Modify

**New Files:**

- `backend/app/core/audit.py` - Security audit logging
- `backend/app/core/monitoring.py` - Security monitoring
- `backend/app/core/2fa.py` - Two-factor authentication
- `backend/app/models/api_key.py` - API key model
- `backend/app/routers/api_keys.py` - API key management
- `SECURITY.md` - Security documentation

**Modified Files:**

- `backend/app/main.py` - Enable middleware, improve error handling
- `backend/app/core/limiter.py` - Redis-based rate limiting
- `backend/app/core/security.py` - Token blacklisting, brute force protection
- `backend/app/routers/auth.py` - Brute force protection, password validation
- `backend/app/schemas/user.py` - Password strength validation
- `backend/app/config.py` - Redis configuration, security settings
- `frontend/index.html` - Improved CSP
- `frontend/src/contexts/AuthContext.tsx` - Secure token handling
- `frontend/src/api/client.ts` - CSRF protection

## Success Criteria

1. All security middleware enabled and working
2. Rate limiting using Redis (production-ready)
3. Brute force protection active
4. Password strength enforced
5. Token blacklisting functional
6. Security headers present on all responses
7. CSP properly configured
8. No sensitive data in error messages
9. Security audit logging active
10. All inputs validated and sanitized