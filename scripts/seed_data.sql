-- Seed data for TradeSignal
-- Run this to populate database with test data

-- Insert companies
INSERT INTO companies (ticker, name, cik, sector, industry, market_cap, website, created_at, updated_at)
VALUES
    ('AAPL', 'Apple Inc.', '0000320193', 'Technology', 'Consumer Electronics', 3000000000000, 'https://www.apple.com', NOW(), NOW()),
    ('TSLA', 'Tesla Inc.', '0001318605', 'Automotive', 'Electric Vehicles', 800000000000, 'https://www.tesla.com', NOW(), NOW()),
    ('MSFT', 'Microsoft Corporation', '0000789019', 'Technology', 'Software', 2800000000000, 'https://www.microsoft.com', NOW(), NOW()),
    ('NVDA', 'NVIDIA Corporation', '0001045810', 'Technology', 'Semiconductors', 1200000000000, 'https://www.nvidia.com', NOW(), NOW()),
    ('GOOGL', 'Alphabet Inc.', '0001652044', 'Technology', 'Internet Services', 1700000000000, 'https://www.google.com', NOW(), NOW())
ON CONFLICT (ticker) DO NOTHING;

-- Insert insiders
INSERT INTO insiders (name, title, company_id, is_director, is_officer, is_ten_percent_owner, is_other, created_at, updated_at)
VALUES
    -- Apple insiders
    ('Timothy D. Cook', 'Chief Executive Officer', (SELECT id FROM companies WHERE ticker = 'AAPL'), true, true, false, false, NOW(), NOW()),
    ('Luca Maestri', 'Chief Financial Officer', (SELECT id FROM companies WHERE ticker = 'AAPL'), false, true, false, false, NOW(), NOW()),
    -- Tesla insiders
    ('Elon Musk', 'Chief Executive Officer', (SELECT id FROM companies WHERE ticker = 'TSLA'), true, true, true, false, NOW(), NOW()),
    ('Zachary Kirkhorn', 'Chief Financial Officer', (SELECT id FROM companies WHERE ticker = 'TSLA'), false, true, false, false, NOW(), NOW()),
    -- Microsoft insiders
    ('Satya Nadella', 'Chief Executive Officer', (SELECT id FROM companies WHERE ticker = 'MSFT'), true, true, false, false, NOW(), NOW()),
    ('Amy Hood', 'Chief Financial Officer', (SELECT id FROM companies WHERE ticker = 'MSFT'), false, true, false, false, NOW(), NOW()),
    -- NVIDIA insiders
    ('Jensen Huang', 'Chief Executive Officer', (SELECT id FROM companies WHERE ticker = 'NVDA'), true, true, false, false, NOW(), NOW()),
    -- Google insiders
    ('Sundar Pichai', 'Chief Executive Officer', (SELECT id FROM companies WHERE ticker = 'GOOGL'), true, true, false, false, NOW(), NOW())
ON CONFLICT (name, company_id) DO NOTHING;

-- Insert sample trades (last 30 days)
INSERT INTO trades (insider_id, company_id, transaction_date, filing_date, transaction_type, transaction_code, shares, price_per_share, total_value, shares_owned_after, ownership_type, derivative_transaction, sec_filing_url, form_type, created_at, updated_at)
VALUES
    -- AAPL trades
    ((SELECT id FROM insiders WHERE name = 'Timothy D. Cook' LIMIT 1), (SELECT id FROM companies WHERE ticker = 'AAPL'), CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE - INTERVAL '5 days', 'BUY', 'P', 1000, 150.00, 150000.00, 10000, 'Direct', false, 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193&type=4', 'Form 4', NOW(), NOW()),
    ((SELECT id FROM insiders WHERE name = 'Timothy D. Cook' LIMIT 1), (SELECT id FROM companies WHERE ticker = 'AAPL'), CURRENT_DATE - INTERVAL '14 days', CURRENT_DATE - INTERVAL '12 days', 'SELL', 'S', 1500, 160.00, 240000.00, 11000, 'Direct', false, 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193&type=4', 'Form 4', NOW(), NOW()),
    ((SELECT id FROM insiders WHERE name = 'Timothy D. Cook' LIMIT 1), (SELECT id FROM companies WHERE ticker = 'AAPL'), CURRENT_DATE - INTERVAL '21 days', CURRENT_DATE - INTERVAL '19 days', 'BUY', 'P', 2000, 170.00, 340000.00, 12500, 'Direct', false, 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193&type=4', 'Form 4', NOW(), NOW()),

    -- TSLA trades
    ((SELECT id FROM insiders WHERE name = 'Elon Musk' LIMIT 1), (SELECT id FROM companies WHERE ticker = 'TSLA'), CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE - INTERVAL '5 days', 'BUY', 'P', 1000, 250.00, 250000.00, 50000, 'Direct', false, 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001318605&type=4', 'Form 4', NOW(), NOW()),
    ((SELECT id FROM insiders WHERE name = 'Elon Musk' LIMIT 1), (SELECT id FROM companies WHERE ticker = 'TSLA'), CURRENT_DATE - INTERVAL '14 days', CURRENT_DATE - INTERVAL '12 days', 'SELL', 'S', 1500, 260.00, 390000.00, 51000, 'Direct', false, 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001318605&type=4', 'Form 4', NOW(), NOW()),
    ((SELECT id FROM insiders WHERE name = 'Elon Musk' LIMIT 1), (SELECT id FROM companies WHERE ticker = 'TSLA'), CURRENT_DATE - INTERVAL '21 days', CURRENT_DATE - INTERVAL '19 days', 'BUY', 'P', 2000, 270.00, 540000.00, 52500, 'Direct', false, 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001318605&type=4', 'Form 4', NOW(), NOW()),

    -- MSFT trades
    ((SELECT id FROM insiders WHERE name = 'Satya Nadella' LIMIT 1), (SELECT id FROM companies WHERE ticker = 'MSFT'), CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE - INTERVAL '5 days', 'BUY', 'P', 1000, 380.00, 380000.00, 15000, 'Direct', false, 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=4', 'Form 4', NOW(), NOW()),
    ((SELECT id FROM insiders WHERE name = 'Satya Nadella' LIMIT 1), (SELECT id FROM companies WHERE ticker = 'MSFT'), CURRENT_DATE - INTERVAL '14 days', CURRENT_DATE - INTERVAL '12 days', 'SELL', 'S', 1500, 390.00, 585000.00, 16000, 'Direct', false, 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=4', 'Form 4', NOW(), NOW()),
    ((SELECT id FROM insiders WHERE name = 'Satya Nadella' LIMIT 1), (SELECT id FROM companies WHERE ticker = 'MSFT'), CURRENT_DATE - INTERVAL '21 days', CURRENT_DATE - INTERVAL '19 days', 'BUY', 'P', 2000, 400.00, 800000.00, 17500, 'Direct', false, 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=4', 'Form 4', NOW(), NOW()),

    -- NVDA trades
    ((SELECT id FROM insiders WHERE name = 'Jensen Huang' LIMIT 1), (SELECT id FROM companies WHERE ticker = 'NVDA'), CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE - INTERVAL '5 days', 'BUY', 'P', 1000, 480.00, 480000.00, 20000, 'Direct', false, 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001045810&type=4', 'Form 4', NOW(), NOW()),
    ((SELECT id FROM insiders WHERE name = 'Jensen Huang' LIMIT 1), (SELECT id FROM companies WHERE ticker = 'NVDA'), CURRENT_DATE - INTERVAL '14 days', CURRENT_DATE - INTERVAL '12 days', 'SELL', 'S', 1500, 490.00, 735000.00, 21000, 'Direct', false, 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001045810&type=4', 'Form 4', NOW(), NOW()),
    ((SELECT id FROM insiders WHERE name = 'Jensen Huang' LIMIT 1), (SELECT id FROM companies WHERE ticker = 'NVDA'), CURRENT_DATE - INTERVAL '21 days', CURRENT_DATE - INTERVAL '19 days', 'BUY', 'P', 2000, 500.00, 1000000.00, 22500, 'Direct', false, 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001045810&type=4', 'Form 4', NOW(), NOW()),

    -- GOOGL trades
    ((SELECT id FROM insiders WHERE name = 'Sundar Pichai' LIMIT 1), (SELECT id FROM companies WHERE ticker = 'GOOGL'), CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE - INTERVAL '5 days', 'BUY', 'P', 1000, 140.00, 140000.00, 8000, 'Direct', false, 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001652044&type=4', 'Form 4', NOW(), NOW()),
    ((SELECT id FROM insiders WHERE name = 'Sundar Pichai' LIMIT 1), (SELECT id FROM companies WHERE ticker = 'GOOGL'), CURRENT_DATE - INTERVAL '14 days', CURRENT_DATE - INTERVAL '12 days', 'SELL', 'S', 1500, 145.00, 217500.00, 9000, 'Direct', false, 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001652044&type=4', 'Form 4', NOW(), NOW()),
    ((SELECT id FROM insiders WHERE name = 'Sundar Pichai' LIMIT 1), (SELECT id FROM companies WHERE ticker = 'GOOGL'), CURRENT_DATE - INTERVAL '21 days', CURRENT_DATE - INTERVAL '19 days', 'BUY', 'P', 2000, 150.00, 300000.00, 10500, 'Direct', false, 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001652044&type=4', 'Form 4', NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Show results
SELECT 'Companies:' as table_name, COUNT(*) as count FROM companies
UNION ALL
SELECT 'Insiders:', COUNT(*) FROM insiders
UNION ALL
SELECT 'Trades:', COUNT(*) FROM trades;
