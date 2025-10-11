-- Initialize database schema for stock market data

-- Create realtime_quotes table if not exists
CREATE TABLE IF NOT EXISTS realtime_quotes (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    time TIMESTAMP NOT NULL,
    price DOUBLE PRECISION,
    volume BIGINT,
    total_volume BIGINT,
    change DOUBLE PRECISION,
    change_percent DOUBLE PRECISION,
    ceiling_price DOUBLE PRECISION,
    floor_price DOUBLE PRECISION,
    reference_price DOUBLE PRECISION,
    highest_price DOUBLE PRECISION,
    lowest_price DOUBLE PRECISION,
    bid_price DOUBLE PRECISION,
    ask_price DOUBLE PRECISION,
    processed_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_ticker ON realtime_quotes(ticker);
CREATE INDEX IF NOT EXISTS idx_time ON realtime_quotes(time);
CREATE INDEX IF NOT EXISTS idx_processed_time ON realtime_quotes(processed_time);
CREATE INDEX IF NOT EXISTS idx_ticker_time ON realtime_quotes(ticker, time DESC);

-- Create a view for latest quotes
CREATE OR REPLACE VIEW latest_quotes AS
SELECT DISTINCT ON (ticker)
    ticker,
    time,
    price,
    volume,
    total_volume,
    change,
    change_percent,
    ceiling_price,
    floor_price,
    reference_price,
    highest_price,
    lowest_price,
    bid_price,
    ask_price,
    processed_time
FROM realtime_quotes
ORDER BY ticker, processed_time DESC;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully for Vietnam Stock Market Pipeline';
END $$;

