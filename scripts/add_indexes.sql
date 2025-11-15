-- Add useful indexes to improve query performance
-- Run this against your Postgres DB (use psql or a migration tool)

-- Trades: composite indexes for queries that filter by company and date
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_company_transaction_date ON trades (company_id, transaction_date);
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_company_created_at ON trades (company_id, created_at);

-- Companies: composite index for sector and market_cap for filtering/sorting
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_sector_market_cap ON companies (sector, market_cap);
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_ticker_last_updated ON companies (ticker, updated_at);

-- Scrape history: ensure recent scrapes by ticker are fast (already has ticker index)
-- Alerts: ensure active ticker alerts are fast
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_alerts_ticker_active ON alerts (ticker) WHERE is_active = true;

-- NOTE: Running CONCURRENTLY requires no conflicting DDL locks; run during low-traffic windows
-- Example run (psql):
-- psql "postgresql://tradesignal:tradesignal_dev@localhost:5432/tradesignal" -f scripts/add_indexes.sql
