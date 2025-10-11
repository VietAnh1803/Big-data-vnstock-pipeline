-- ========================================
-- Snowflake Setup Script
-- Vietnam Stock Market Pipeline
-- Customized for your account
-- ========================================

-- Switch to ACCOUNTADMIN role
USE ROLE ACCOUNTADMIN;

-- 1. Create Database STOCKS
-- ========================================
CREATE DATABASE IF NOT EXISTS STOCKS
    COMMENT = 'Database for Vietnam Stock Market data';

USE DATABASE STOCKS;

-- 2. Create Schema PUBLIC (usually exists by default)
-- ========================================
CREATE SCHEMA IF NOT EXISTS PUBLIC
    COMMENT = 'Public schema for stock data';

USE SCHEMA PUBLIC;

-- 3. Verify/Use Warehouse COMPUTE_WH
-- ========================================
-- COMPUTE_WH usually exists by default in Snowflake trial accounts
-- If not, uncomment below to create:
/*
CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 1
    SCALING_POLICY = 'STANDARD'
    COMMENT = 'Warehouse for stock data processing';
*/

USE WAREHOUSE COMPUTE_WH;

-- 4. Create Main Table for Real-time Quotes
-- ========================================
CREATE OR REPLACE TABLE REALTIME_QUOTES (
    TICKER VARCHAR(10) NOT NULL COMMENT 'Stock ticker symbol (e.g., VNM, VIC)',
    TIME TIMESTAMP_NTZ NOT NULL COMMENT 'Quote timestamp',
    PRICE DOUBLE COMMENT 'Current trading price in VND',
    VOLUME BIGINT COMMENT 'Trading volume for this quote',
    TOTAL_VOLUME BIGINT COMMENT 'Accumulated volume for the day',
    CHANGE DOUBLE COMMENT 'Price change from reference',
    CHANGE_PERCENT DOUBLE COMMENT 'Percentage change from reference',
    CEILING_PRICE DOUBLE COMMENT 'Maximum allowed price (ceiling)',
    FLOOR_PRICE DOUBLE COMMENT 'Minimum allowed price (floor)',
    REFERENCE_PRICE DOUBLE COMMENT 'Reference price for the day',
    HIGHEST_PRICE DOUBLE COMMENT 'Highest price of the day',
    LOWEST_PRICE DOUBLE COMMENT 'Lowest price of the day',
    BID_PRICE DOUBLE COMMENT 'Current bid price',
    ASK_PRICE DOUBLE COMMENT 'Current ask price',
    PROCESSED_TIME TIMESTAMP_NTZ COMMENT 'When this record was processed by Spark',
    LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP() COMMENT 'When loaded into Snowflake'
)
COMMENT = 'Real-time stock quotes from Vietnam stock market';

-- 5. Create Clustering for Better Performance
-- ========================================
ALTER TABLE REALTIME_QUOTES 
CLUSTER BY (TICKER, TO_DATE(TIME));

-- 6. Create Views for Analysis
-- ========================================

-- View: Latest quotes per ticker
CREATE OR REPLACE VIEW VW_LATEST_QUOTES AS
SELECT 
    TICKER,
    TIME,
    PRICE,
    VOLUME,
    TOTAL_VOLUME,
    CHANGE,
    CHANGE_PERCENT,
    CEILING_PRICE,
    FLOOR_PRICE,
    REFERENCE_PRICE,
    HIGHEST_PRICE,
    LOWEST_PRICE,
    BID_PRICE,
    ASK_PRICE,
    PROCESSED_TIME
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY TICKER ORDER BY TIME DESC) AS rn
    FROM REALTIME_QUOTES
)
WHERE rn = 1;

-- View: Daily aggregated data (OHLC - Open, High, Low, Close)
CREATE OR REPLACE VIEW VW_DAILY_OHLC AS
SELECT 
    TICKER,
    TO_DATE(TIME) AS TRADE_DATE,
    MIN(TIME) AS FIRST_QUOTE_TIME,
    MAX(TIME) AS LAST_QUOTE_TIME,
    FIRST_VALUE(PRICE) OVER (PARTITION BY TICKER, TO_DATE(TIME) ORDER BY TIME) AS OPEN_PRICE,
    MAX(HIGHEST_PRICE) AS HIGH_PRICE,
    MIN(LOWEST_PRICE) AS LOW_PRICE,
    LAST_VALUE(PRICE) OVER (PARTITION BY TICKER, TO_DATE(TIME) ORDER BY TIME) AS CLOSE_PRICE,
    MAX(TOTAL_VOLUME) AS TOTAL_VOLUME,
    COUNT(*) AS NUM_QUOTES,
    AVG(PRICE) AS AVG_PRICE
FROM REALTIME_QUOTES
GROUP BY TICKER, TO_DATE(TIME), TIME, PRICE
QUALIFY ROW_NUMBER() OVER (PARTITION BY TICKER, TO_DATE(TIME) ORDER BY TIME DESC) = 1;

-- View: Top movers (gainers and losers)
CREATE OR REPLACE VIEW VW_TOP_MOVERS AS
SELECT 
    TICKER,
    PRICE,
    CHANGE,
    CHANGE_PERCENT,
    TOTAL_VOLUME,
    TIME,
    CASE 
        WHEN CHANGE_PERCENT > 0 THEN 'GAINER'
        WHEN CHANGE_PERCENT < 0 THEN 'LOSER'
        ELSE 'UNCHANGED'
    END AS MOVEMENT_TYPE,
    CASE
        WHEN CHANGE_PERCENT >= 6.5 THEN 'CEILING'
        WHEN CHANGE_PERCENT <= -6.5 THEN 'FLOOR'
        WHEN ABS(CHANGE_PERCENT) >= 3 THEN 'STRONG'
        WHEN ABS(CHANGE_PERCENT) >= 1 THEN 'MODERATE'
        ELSE 'WEAK'
    END AS MOVEMENT_STRENGTH
FROM VW_LATEST_QUOTES
ORDER BY ABS(CHANGE_PERCENT) DESC;

-- View: Volume leaders
CREATE OR REPLACE VIEW VW_VOLUME_LEADERS AS
SELECT 
    TICKER,
    PRICE,
    VOLUME,
    TOTAL_VOLUME,
    CHANGE_PERCENT,
    TIME,
    CASE
        WHEN TOTAL_VOLUME >= 1000000 THEN 'VERY_HIGH'
        WHEN TOTAL_VOLUME >= 500000 THEN 'HIGH'
        WHEN TOTAL_VOLUME >= 100000 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS VOLUME_CATEGORY
FROM VW_LATEST_QUOTES
ORDER BY TOTAL_VOLUME DESC;

-- View: Market summary
CREATE OR REPLACE VIEW VW_MARKET_SUMMARY AS
SELECT 
    COUNT(DISTINCT TICKER) AS TOTAL_STOCKS,
    SUM(CASE WHEN CHANGE_PERCENT > 0 THEN 1 ELSE 0 END) AS GAINERS,
    SUM(CASE WHEN CHANGE_PERCENT < 0 THEN 1 ELSE 0 END) AS LOSERS,
    SUM(CASE WHEN CHANGE_PERCENT = 0 THEN 1 ELSE 0 END) AS UNCHANGED,
    SUM(CASE WHEN CHANGE_PERCENT >= 6.5 THEN 1 ELSE 0 END) AS CEILING_HITS,
    SUM(CASE WHEN CHANGE_PERCENT <= -6.5 THEN 1 ELSE 0 END) AS FLOOR_HITS,
    SUM(TOTAL_VOLUME) AS TOTAL_MARKET_VOLUME,
    AVG(CHANGE_PERCENT) AS AVG_CHANGE_PERCENT,
    MAX(TIME) AS LAST_UPDATE_TIME
FROM VW_LATEST_QUOTES;

-- 7. Create Stream for CDC (Change Data Capture)
-- ========================================
CREATE OR REPLACE STREAM REALTIME_QUOTES_STREAM 
ON TABLE REALTIME_QUOTES
COMMENT = 'Stream to capture changes in real-time quotes';

-- 8. Create Archive Table (Optional)
-- ========================================
CREATE OR REPLACE TABLE REALTIME_QUOTES_ARCHIVE (
    LIKE REALTIME_QUOTES
)
COMMENT = 'Archive table for historical stock quotes (90+ days old)';

-- 9. Create Task for Automatic Archiving (Optional)
-- ========================================
-- This task will run daily at 2 AM UTC to archive old data
CREATE OR REPLACE TASK ARCHIVE_OLD_DATA
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0 2 * * * UTC'
    COMMENT = 'Archive quotes older than 90 days'
AS
    INSERT INTO REALTIME_QUOTES_ARCHIVE
    SELECT * FROM REALTIME_QUOTES
    WHERE TIME < DATEADD(DAY, -90, CURRENT_TIMESTAMP())
    AND TICKER NOT IN (SELECT TICKER FROM REALTIME_QUOTES_ARCHIVE WHERE TIME = REALTIME_QUOTES.TIME);

-- Note: Task is created in SUSPENDED state
-- To activate, run: ALTER TASK ARCHIVE_OLD_DATA RESUME;

-- 10. Verification Queries
-- ========================================
-- Check if everything was created successfully

-- Show all tables
SHOW TABLES;

-- Show all views
SHOW VIEWS;

-- Show warehouse
SHOW WAREHOUSES LIKE 'COMPUTE_WH';

-- Check current database and schema
SELECT CURRENT_DATABASE(), CURRENT_SCHEMA();

-- Check table structure
DESCRIBE TABLE REALTIME_QUOTES;

-- Check if table is empty (should be 0 before pipeline runs)
SELECT COUNT(*) AS INITIAL_RECORD_COUNT FROM REALTIME_QUOTES;

-- ========================================
-- Setup Complete!
-- ========================================

SELECT '✅ Snowflake setup completed successfully!' AS STATUS;
SELECT 'Database: STOCKS' AS INFO;
SELECT 'Schema: PUBLIC' AS INFO;
SELECT 'Warehouse: COMPUTE_WH' AS INFO;
SELECT 'Ready to receive data from Spark pipeline!' AS NEXT_STEP;

-- ========================================
-- USEFUL QUERIES FOR MONITORING
-- ========================================

-- After pipeline runs, use these queries to monitor data:

-- 1. Check latest data
-- SELECT * FROM VW_LATEST_QUOTES ORDER BY TICKER;

-- 2. Check data volume by day
-- SELECT TO_DATE(TIME) AS DATE, COUNT(*) AS RECORDS
-- FROM REALTIME_QUOTES
-- GROUP BY TO_DATE(TIME)
-- ORDER BY DATE DESC;

-- 3. Check top gainers
-- SELECT * FROM VW_TOP_MOVERS WHERE MOVEMENT_TYPE = 'GAINER' LIMIT 10;

-- 4. Check top losers
-- SELECT * FROM VW_TOP_MOVERS WHERE MOVEMENT_TYPE = 'LOSER' LIMIT 10;

-- 5. Check volume leaders
-- SELECT * FROM VW_VOLUME_LEADERS LIMIT 10;

-- 6. Check market summary
-- SELECT * FROM VW_MARKET_SUMMARY;

-- 7. Check daily OHLC data
-- SELECT * FROM VW_DAILY_OHLC ORDER BY TRADE_DATE DESC, TICKER;

-- 8. Check recent records
-- SELECT * FROM REALTIME_QUOTES 
-- ORDER BY LOADED_AT DESC 
-- LIMIT 100;

-- ========================================
-- CONFIGURATION SUMMARY
-- ========================================
-- Copy these values to your .env file:
--
-- SNOWFLAKE_URL=BRWNIAD-WC21582.snowflakecomputing.com
-- SNOWFLAKE_USER=vietanh1803
-- SNOWFLAKE_PASSWORD=Vanhdzai1803@!
-- SNOWFLAKE_DATABASE=STOCKS
-- SNOWFLAKE_SCHEMA=PUBLIC
-- SNOWFLAKE_WAREHOUSE=COMPUTE_WH
-- SNOWFLAKE_ROLE=ACCOUNTADMIN
-- ========================================


