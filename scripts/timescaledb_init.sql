-- TimescaleDB initialization for the stock pipeline.
-- Single write path: Spark consumer -> public.realtime_quotes.
-- Medallion (BRONZE/SILVER/DW) lives on Snowflake; see scripts/snowflake/ and snowflake-sync.

CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS public.realtime_quotes (
    time TIMESTAMPTZ NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    price NUMERIC(18,4),
    volume BIGINT,
    change NUMERIC(18,4),
    percent_change NUMERIC(12,6),
    high NUMERIC(18,4),
    low NUMERIC(18,4),
    open_price NUMERIC(18,4),
    close_price NUMERIC(18,4),
    quote_time VARCHAR(50),
    ingest_time TIMESTAMPTZ DEFAULT NOW(),
    data_source VARCHAR(50) DEFAULT 'vnstock'
);

SELECT create_hypertable('public.realtime_quotes', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_realtime_quotes_ticker_time
    ON public.realtime_quotes (ticker, time DESC);

CREATE INDEX IF NOT EXISTS idx_realtime_quotes_time
    ON public.realtime_quotes (time DESC);
