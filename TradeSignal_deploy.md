# TradeSignal Production Deployment Guide
**Target:** Live Launch (Dec 14, 2025)
**Objective:** Define the exact services, costs, and vendors required to take TradeSignal from "Localhost" to "Production".

---

## 1. Hosting & Infrastructure (The Foundation)

You need a place for your code to live. Since you have a separate Frontend (React) and Backend (FastAPI/Python), a "Hybrid" hosting strategy is best for performance and cost.

### A. Frontend Hosting
**Requirement:** Serve your React static files globally with low latency.
*   **Recommendation:** **Vercel** (Best for React/Vite apps)
*   **Why:** Zero-config deployment, global CDN, automatic SSL (HTTPS), and free DDoS protection.
*   **Cost:**
    *   *Hobby Tier:* **$0/mo** (Perfect for MVP start).
    *   *Pro Tier:* **$20/mo** (If you need team collaboration or exceed bandwidth).

### B. Backend Hosting (API + Workers)
**Requirement:** Run Python (FastAPI) and Celery (Background Workers for scraping).
*   **Recommendation:** **DigitalOcean Droplet (VPS)** or **Railway**
*   **Option 1: DigitalOcean (Recommended for Control & Cost)**
    *   *Setup:* One "Droplet" (Virtual Machine) running Docker Compose.
    *   *Spec:* 2 vCPU / 4GB RAM (Minimum for AI/Scraping workloads).
    *   *Cost:* **~$24/mo** (Basic Droplet).
*   **Option 2: Railway / Render (Recommended for Ease of Use)**
    *   *Setup:* Connect GitHub repo, auto-deploys.
    *   *Cost:* **~$10-20/mo** (Variable based on usage).

### C. Database (PostgreSQL)
**Requirement:** Persistent storage for Users, Trades, and History.
*   **Recommendation:** **Managed PostgreSQL** (Don't host your own DB for production unless you are a sysadmin expert).
*   **Vendor:** **DigitalOcean Managed Databases** or **Supabase**.
*   **Why:** Automatic backups, point-in-time recovery, high availability.
*   **Cost:**
    *   *Supabase:* **$0/mo** (Free tier is very generous: 500MB).
    *   *DigitalOcean:* **$15/mo** (Managed cluster).

### D. Redis (Cache & Queue)
**Requirement:** Required for Celery (Task Queue) and Caching API responses.
*   **Recommendation:** Self-hosted on your Backend VPS (cheapest) or Managed Redis (easiest).
*   **Cost:**
    *   *Self-hosted (Docker):* **$0** (Included in your Backend VPS cost).
    *   *Upstash (Managed):* **$0/mo** (Free tier up to 10k requests/day).

---

## 2. External Data APIs (The Product Core)

This is where your actual money goes. These APIs power your features.

### A. Congressional Data
**Requirement:** Real-time, reliable data on politician trades.
*   **Vendor:** **Finnhub**
*   **Why:** The "Free" fallbacks (Senate Stock Watcher) are unreliable/stale. For a paid product, you need paid reliability.
*   **Plan:** **Stock Data Plan**
*   **Cost:** **~$50/mo** (Estimated for API access). *Note: Check specific endpoint pricing, Finnhub pricing changes.*

### B. AI Insights (LLM)
**Requirement:** Generate daily summaries and "Why it matters" analysis.
*   **Option 1: Google Gemini (Current Implementation)**
    *   *Plan:* **Gemini 1.5 Flash**
    *   *Cost:* **Free Tier** available (15 RPM). **Pay-as-you-go** after that. Extremely cheap ($0.35 / 1M tokens).
    *   *Estimated Cost:* **<$5/mo** for MVP.
*   **Option 2: OpenAI (GPT-4o-mini)**
    *   *Plan:* Pay-as-you-go API.
    *   *Estimated Cost:* **$5-$10/mo** (Depends on usage).

### C. Earnings Data
**Requirement:** Reliable earnings dates/estimates.
*   **Vendor:** **Alpha Vantage** or **Finnhub** (Bundle with above).
*   **Why:** `yfinance` (Yahoo) scraping will get your IP banned in production.
*   **Cost:** Included in Finnhub or **Free Tier** of Alpha Vantage (25 requests/day).

---

## 3. Operational Services

### A. Email (Transactional)
**Requirement:** Sending "Confirm Email", "Reset Password", and "Trade Alerts".
*   **Vendor:** **Resend** (Modern, developer-friendly) or **SendGrid**.
*   **Why:** High deliverability. Gmail/Outlook will block you if you try to send from your own server.
*   **Cost:** **$0/mo** (Resend Free tier: 3,000 emails/mo).

### B. Domain Name
**Requirement:** `tradesignal.com` (or similar).
*   **Vendor:** **Namecheap** or **Porkbun**.
*   **Cost:** **~$12/year**.

### C. Monitoring & Logging
**Requirement:** Knowing when the site crashes before users tell you.
*   **Vendor:** **Sentry** (Error tracking) + **UptimeRobot** (Uptime).
*   **Cost:** **$0/mo** (Both have generous free tiers).

---

## 4. Business & Legal

### A. Payment Processing
**Requirement:** Accepting Credit Cards.
*   **Vendor:** **Stripe**.
*   **Cost:** **No fixed cost**. They take **2.9% + 30¢** per transaction.

### B. Business Entity (LLC)
**Requirement:** Protecting your personal assets. Stripe requires a business entity for many features.
*   **Vendor:** **Stripe Atlas** or local state filing.
*   **Cost:** **$300 - $500** (One-time fee). *Optional for Day 1 Alpha, mandatory for Scale.*

---

## 5. Cost Summary Tables

### Option 1: "The Bootstrapper" (MVP Launch)
*Best for validating the idea with first 100 users.*

| Service | Vendor | Plan | Monthly Cost |
| :--- | :--- | :--- | :--- |
| **Frontend** | Vercel | Hobby | $0 |
| **Backend** | DigitalOcean | Basic Droplet | $12 |
| **Database** | Supabase | Free Tier | $0 |
| **Redis** | Self-hosted | Docker | $0 |
| **Cong. Data** | Finnhub | Free/Trial | $0 (Risk of stale data) |
| **AI** | Gemini | Free Tier | $0 |
| **Email** | Resend | Free Tier | $0 |
| **Domain** | Namecheap | .com | $1/mo ($12/yr) |
| **TOTAL** | | | **~$13 / month** |

### Option 2: "Pro Production" (Recommended)
*Best for reliability, uptime, and paying customers.*

| Service | Vendor | Plan | Monthly Cost |
| :--- | :--- | :--- | :--- |
| **Frontend** | Vercel | Pro (Optional) | $20 (Or $0) |
| **Backend** | DigitalOcean | 4GB RAM Droplet | $24 |
| **Database** | DigitalOcean | Managed PG | $15 |
| **Redis** | Upstash/DO | Managed | $10 |
| **Cong. Data** | Finnhub | Basic API | ~$50 |
| **AI** | Gemini/OpenAI | Usage Based | ~$10 |
| **Email** | Resend | Pro | $20 |
| **Domain** | Namecheap | .com | $1/mo |
| **TOTAL** | | | **~$130 - $150 / month** |

---

## 6. Production Checklist (The "Go-Live" List)

1.  **[ ] Purchase Domain:** Buy the `.com` domain name.
2.  **[ ] Set up Cloudflare:** Point domain DNS to Cloudflare (Free SSL & Security).
3.  **[ ] Backend VPS:** Provision DigitalOcean Droplet.
    *   Install Docker & Docker Compose.
    *   Set up Nginx as Reverse Proxy (HTTPS).
4.  **[ ] External Keys (The Wallet Opener):**
    *   Upgrade **Finnhub** to paid (if bootstrapping allows).
    *   Add Credit Card to **OpenAI/Gemini** (prevent rate limit blocks).
    *   Verify **Stripe** production mode is active.
5.  **[ ] Database Migration:**
    *   Create production DB (Supabase/DO).
    *   Run Alembic migrations.
    *   Run the `seed_data.py` (or scraper) to populate initial data.
6.  **[ ] CI/CD Pipeline:**
    *   Connect GitHub to Vercel (Frontend auto-deploy).
    *   Set up GitHub Action to SSH into VPS and `git pull && docker-compose up -d` (Backend auto-deploy).

---

## Why pay for these?
*   **Reliability:** Free tiers *will* rate limit you. If a user pays $29/mo and sees "API Limit Reached", they will chargeback immediately.
*   **Speed:** Shared/Free databases are slow. Paid managed databases are fast and backed up.
*   **Trust:** Sending emails from `@gmail.com` looks like a scam. Sending from `@tradesignal.com` looks like a business.
