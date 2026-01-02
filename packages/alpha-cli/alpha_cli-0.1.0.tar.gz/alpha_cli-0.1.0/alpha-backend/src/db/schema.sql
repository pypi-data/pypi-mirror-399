-- Alpha CLI Backend Database Schema
-- Cloudflare D1 (SQLite)

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,              -- UUID
    email TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    stripe_customer_id TEXT UNIQUE
);

-- API keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id TEXT PRIMARY KEY,              -- UUID
    user_id TEXT NOT NULL REFERENCES users(id),
    key_hash TEXT UNIQUE NOT NULL,    -- SHA-256 of full key
    key_prefix TEXT NOT NULL,         -- First 12 chars for identification
    environment TEXT NOT NULL,         -- "live" or "test"
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used_at DATETIME,
    revoked_at DATETIME,
    UNIQUE(user_id, environment)       -- One active key per environment
);

-- Subscriptions table (synced from Stripe webhooks)
CREATE TABLE IF NOT EXISTS subscriptions (
    id TEXT PRIMARY KEY,              -- Stripe subscription ID
    user_id TEXT NOT NULL REFERENCES users(id),
    status TEXT NOT NULL,             -- "active", "canceled", "past_due", "trialing"
    current_period_start DATETIME,
    current_period_end DATETIME,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Alerts table (for future alert feature)
CREATE TABLE IF NOT EXISTS alerts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    alert_type TEXT NOT NULL,         -- 'congress_ticker', 'market_move', 'arb_opportunity'
    config TEXT NOT NULL,             -- JSON config (type-specific)
    webhook_url TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    last_triggered_at DATETIME,
    cooldown_minutes INTEGER DEFAULT 60,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Ticker-market mappings (curated)
CREATE TABLE IF NOT EXISTS ticker_market_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,             -- e.g., "NVDA"
    company_name TEXT NOT NULL,       -- e.g., "NVIDIA Corporation"
    sector TEXT,                      -- e.g., "Technology"
    market_pattern TEXT NOT NULL,     -- e.g., "KXNVDA%" or "KXNVIDIA%"
    relevance_type TEXT NOT NULL,     -- "direct" | "sector" | "macro"
    verified_at DATETIME,
    verified_by TEXT,                 -- "human" | "llm" | "auto"
    UNIQUE(ticker, market_pattern)
);

-- Match cache (for caching LLM validation results)
CREATE TABLE IF NOT EXISTS match_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    market_ticker TEXT NOT NULL,
    is_relevant BOOLEAN NOT NULL,
    confidence INTEGER NOT NULL,      -- 0-100
    explanation TEXT,
    cached_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    UNIQUE(ticker, market_ticker)
);

-- Usage tracking (for rate limiting and analytics)
CREATE TABLE IF NOT EXISTS api_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL REFERENCES users(id),
    endpoint TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_prefix ON api_keys(key_prefix);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_ticker_mappings_ticker ON ticker_market_mappings(ticker);
CREATE INDEX IF NOT EXISTS idx_match_cache_ticker ON match_cache(ticker);
CREATE INDEX IF NOT EXISTS idx_match_cache_expires ON match_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_api_usage_user ON api_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp ON api_usage(timestamp);

-- Insert initial curated mappings (top 20 tickers)
INSERT OR IGNORE INTO ticker_market_mappings (ticker, company_name, sector, market_pattern, relevance_type, verified_by)
VALUES
    ('NVDA', 'NVIDIA Corporation', 'Technology', 'KXNVDA%', 'direct', 'human'),
    ('NVDA', 'NVIDIA Corporation', 'Technology', 'KXNVIDIA%', 'direct', 'human'),
    ('NVDA', 'NVIDIA Corporation', 'Technology', 'KXAICHIP%', 'sector', 'human'),
    ('AAPL', 'Apple Inc.', 'Technology', 'KXAAPL%', 'direct', 'human'),
    ('AAPL', 'Apple Inc.', 'Technology', 'KXAPPLE%', 'direct', 'human'),
    ('MSFT', 'Microsoft Corporation', 'Technology', 'KXMSFT%', 'direct', 'human'),
    ('MSFT', 'Microsoft Corporation', 'Technology', 'KXMICROSOFT%', 'direct', 'human'),
    ('GOOGL', 'Alphabet Inc.', 'Technology', 'KXGOOG%', 'direct', 'human'),
    ('GOOGL', 'Alphabet Inc.', 'Technology', 'KXGOOGLE%', 'direct', 'human'),
    ('AMZN', 'Amazon.com Inc.', 'Technology', 'KXAMZN%', 'direct', 'human'),
    ('AMZN', 'Amazon.com Inc.', 'Technology', 'KXAMAZON%', 'direct', 'human'),
    ('META', 'Meta Platforms Inc.', 'Technology', 'KXMETA%', 'direct', 'human'),
    ('META', 'Meta Platforms Inc.', 'Technology', 'KXFACEBOOK%', 'direct', 'human'),
    ('TSLA', 'Tesla Inc.', 'Automotive', 'KXTSLA%', 'direct', 'human'),
    ('TSLA', 'Tesla Inc.', 'Automotive', 'KXTESLA%', 'direct', 'human'),
    ('AMD', 'Advanced Micro Devices', 'Technology', 'KXAMD%', 'direct', 'human'),
    ('INTC', 'Intel Corporation', 'Technology', 'KXINTC%', 'direct', 'human'),
    ('INTC', 'Intel Corporation', 'Technology', 'KXINTEL%', 'direct', 'human'),
    ('JPM', 'JPMorgan Chase & Co.', 'Finance', 'KXJPM%', 'direct', 'human'),
    ('JPM', 'JPMorgan Chase & Co.', 'Finance', 'KXJPMORGAN%', 'direct', 'human');
