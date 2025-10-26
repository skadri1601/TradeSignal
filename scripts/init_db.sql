-- =====================================================
-- TradeSignal Database Schema
-- =====================================================
-- PostgreSQL schema for insider trading intelligence platform
-- Tables: companies, insiders, trades
-- Version: 1.0.0
-- =====================================================

-- Enable UUID extension (optional, for future use)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- Companies Table
-- =====================================================
-- Stores information about publicly traded companies
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255),
    cik VARCHAR(10) UNIQUE NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    description TEXT,
    website VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add comments for documentation
COMMENT ON TABLE companies IS 'Publicly traded companies tracked by TradeSignal';
COMMENT ON COLUMN companies.ticker IS 'Stock ticker symbol (e.g., AAPL, TSLA)';
COMMENT ON COLUMN companies.cik IS 'SEC Central Index Key - unique company identifier';
COMMENT ON COLUMN companies.sector IS 'Business sector (Technology, Finance, Healthcare, etc.)';
COMMENT ON COLUMN companies.market_cap IS 'Market capitalization in USD';

-- =====================================================
-- Insiders Table
-- =====================================================
-- Stores information about corporate insiders who file trades
CREATE TABLE IF NOT EXISTS insiders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    relationship VARCHAR(100),
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    is_director BOOLEAN DEFAULT FALSE,
    is_officer BOOLEAN DEFAULT FALSE,
    is_ten_percent_owner BOOLEAN DEFAULT FALSE,
    is_other BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(name, company_id)
);

-- Add comments
COMMENT ON TABLE insiders IS 'Corporate insiders who file Form 4 transactions';
COMMENT ON COLUMN insiders.relationship IS 'Relationship to company (CEO, Director, CFO, etc.)';
COMMENT ON COLUMN insiders.is_director IS 'True if person is a board director';
COMMENT ON COLUMN insiders.is_officer IS 'True if person is a corporate officer';
COMMENT ON COLUMN insiders.is_ten_percent_owner IS 'True if person owns 10%+ of company stock';

-- =====================================================
-- Trades Table
-- =====================================================
-- Stores individual insider trading transactions from SEC Form 4
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    insider_id INTEGER REFERENCES insiders(id) ON DELETE CASCADE,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    transaction_date DATE NOT NULL,
    filing_date DATE NOT NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('BUY', 'SELL')),
    transaction_code VARCHAR(2),
    shares DECIMAL(15, 4) NOT NULL,
    price_per_share DECIMAL(10, 2),
    total_value DECIMAL(15, 2),
    shares_owned_after DECIMAL(15, 4),
    ownership_type VARCHAR(20),
    derivative_transaction BOOLEAN DEFAULT FALSE,
    sec_filing_url TEXT,
    form_type VARCHAR(10) DEFAULT 'Form 4',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    -- Prevent duplicate trades
    UNIQUE(insider_id, transaction_date, shares, price_per_share)
);

-- Add comments
COMMENT ON TABLE trades IS 'Insider trading transactions from SEC Form 4 filings';
COMMENT ON COLUMN trades.transaction_date IS 'Date the transaction occurred';
COMMENT ON COLUMN trades.filing_date IS 'Date the Form 4 was filed with SEC';
COMMENT ON COLUMN trades.transaction_type IS 'BUY or SELL';
COMMENT ON COLUMN trades.transaction_code IS 'SEC transaction code (P, S, A, M, etc.)';
COMMENT ON COLUMN trades.shares IS 'Number of shares traded';
COMMENT ON COLUMN trades.price_per_share IS 'Price per share in USD';
COMMENT ON COLUMN trades.total_value IS 'Total transaction value (shares * price)';
COMMENT ON COLUMN trades.shares_owned_after IS 'Shares owned after transaction';
COMMENT ON COLUMN trades.ownership_type IS 'Direct or Indirect ownership';
COMMENT ON COLUMN trades.derivative_transaction IS 'True if options/derivatives trade';

-- =====================================================
-- Indexes for Performance
-- =====================================================

-- Companies indexes
CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker);
CREATE INDEX IF NOT EXISTS idx_companies_cik ON companies(cik);
CREATE INDEX IF NOT EXISTS idx_companies_sector ON companies(sector);
CREATE INDEX IF NOT EXISTS idx_companies_created ON companies(created_at DESC);

-- Insiders indexes
CREATE INDEX IF NOT EXISTS idx_insiders_name ON insiders(name);
CREATE INDEX IF NOT EXISTS idx_insiders_company ON insiders(company_id);
CREATE INDEX IF NOT EXISTS idx_insiders_title ON insiders(title);
CREATE INDEX IF NOT EXISTS idx_insiders_created ON insiders(created_at DESC);

-- Trades indexes (most important for query performance)
CREATE INDEX IF NOT EXISTS idx_trades_transaction_date ON trades(transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_trades_filing_date ON trades(filing_date DESC);
CREATE INDEX IF NOT EXISTS idx_trades_company ON trades(company_id);
CREATE INDEX IF NOT EXISTS idx_trades_insider ON trades(insider_id);
CREATE INDEX IF NOT EXISTS idx_trades_type ON trades(transaction_type);
CREATE INDEX IF NOT EXISTS idx_trades_value ON trades(total_value DESC);
CREATE INDEX IF NOT EXISTS idx_trades_created ON trades(created_at DESC);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_trades_company_date ON trades(company_id, transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_trades_insider_date ON trades(insider_id, transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_trades_type_date ON trades(transaction_type, transaction_date DESC);

-- =====================================================
-- Updated At Trigger Function
-- =====================================================
-- Automatically update updated_at timestamp on row modification

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables
CREATE TRIGGER update_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_insiders_updated_at
    BEFORE UPDATE ON insiders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trades_updated_at
    BEFORE UPDATE ON trades
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- Views for Common Queries
-- =====================================================

-- Recent trades view with full details
CREATE OR REPLACE VIEW recent_trades AS
SELECT
    t.id,
    t.transaction_date,
    t.filing_date,
    t.transaction_type,
    t.shares,
    t.price_per_share,
    t.total_value,
    c.ticker,
    c.name AS company_name,
    c.sector,
    i.name AS insider_name,
    i.title AS insider_title,
    t.sec_filing_url,
    t.created_at
FROM trades t
JOIN companies c ON t.company_id = c.id
JOIN insiders i ON t.insider_id = i.id
ORDER BY t.transaction_date DESC;

COMMENT ON VIEW recent_trades IS 'Recent trades with company and insider details';

-- =====================================================
-- Sample Data (Optional - for development)
-- =====================================================
-- Uncomment to insert sample data for testing

-- INSERT INTO companies (ticker, name, cik, sector) VALUES
-- ('AAPL', 'Apple Inc.', '0000320193', 'Technology'),
-- ('TSLA', 'Tesla Inc.', '0001318605', 'Automotive'),
-- ('MSFT', 'Microsoft Corporation', '0000789019', 'Technology')
-- ON CONFLICT (ticker) DO NOTHING;

-- =====================================================
-- Database Statistics
-- =====================================================

-- Analyze tables for query optimizer
ANALYZE companies;
ANALYZE insiders;
ANALYZE trades;

-- =====================================================
-- Permissions (Adjust based on your user)
-- =====================================================
-- Grant permissions to your database user
-- Replace 'tradesignal' with your actual database user

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO tradesignal;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO tradesignal;

-- =====================================================
-- Completion Message
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'TradeSignal Database Schema Initialized';
    RAISE NOTICE 'Tables: companies, insiders, trades';
    RAISE NOTICE 'Indexes: Created for optimal performance';
    RAISE NOTICE 'Triggers: Auto-update timestamps enabled';
    RAISE NOTICE 'Views: recent_trades available';
    RAISE NOTICE '========================================';
END $$;
