-- Realtime cleaned quotes table (sink from Spark)
CREATE TABLE IF NOT EXISTS public.realtime_quotes_clean (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    time TIMESTAMP NOT NULL,
    price DOUBLE PRECISION,
    volume BIGINT,
    change DOUBLE PRECISION,
    change_percent DOUBLE PRECISION,
    open_price DOUBLE PRECISION,
    high_price DOUBLE PRECISION,
    low_price DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rqc_ticker_time ON public.realtime_quotes_clean(ticker, time DESC);

-- Minute metrics aggregated by Spark
CREATE TABLE IF NOT EXISTS public.realtime_metrics_minute (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    minute_start TIMESTAMP NOT NULL,
    minute_end TIMESTAMP NOT NULL,
    last_price DOUBLE PRECISION,
    sum_volume BIGINT,
    max_price DOUBLE PRECISION,
    min_price DOUBLE PRECISION,
    avg_price DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rmm_ticker_start ON public.realtime_metrics_minute(ticker, minute_start DESC);



