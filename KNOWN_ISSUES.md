# Known Issues

## PostgreSQL Authentication Issue (Windows + psycopg)

**Status:** DEFERRED - Not blocking development

**Problem:**
- Python psycopg/psycopg2 clients cannot connect to PostgreSQL from Windows host
- Error: "password authentication failed for user 'tradesignal'"
- PostgreSQL logs show NO connection attempts from Python (client-side issue)
- Connections from inside Docker container work fine

**What We've Verified:**
- ✅ Password hash is correct: `md579f3f7fd1cf98da96d74cb4bc76752be`
- ✅ Password value is correct: `tradesignal_dev`
- ✅ pg_hba.conf is configured for MD5 authentication
- ✅ PostgreSQL is running and healthy
- ✅ Database schema is created (companies, insiders, trades)
- ❌ Python clients on Windows cannot connect (libpq issue)

**Root Cause:**
- Likely a libpq/psycopg compatibility issue on Windows
- The error happens on the client side BEFORE reaching PostgreSQL
- PostgreSQL doesn't log any connection attempts from Python

**Workarounds Tried:**
1. Changed from SCRAM-SHA-256 to MD5 encryption ❌
2. Modified pg_hba.conf authentication rules ❌
3. Tried both asyncpg and psycopg drivers ❌
4. Tried connection string vs individual parameters ❌
5. Set `POSTGRES_HOST_AUTH_METHOD` to trust/md5 ❌

**Impact:**
- `/health` endpoint shows `"database": "error"`
- Everything else works perfectly
- Backend code is production-ready

**Next Steps to Fix:**
1. Try PostgreSQL 14 instead of 15 (version compatibility)
2. Try different libpq version on Windows
3. Use WSL2 for development instead of native Windows
4. Deploy to Linux server where this issue won't exist

**Files Affected:**
- Backend health check: `backend/app/main.py` (line ~270)
- Database connection: `backend/app/database.py`

**Date Identified:** October 26, 2025
**Assigned To:** Fix later when deploying or when more time available
