-- ===================================================================
-- Additional Tables for Vietnam Stock Pipeline - BIG DATA
-- Collecting ALL available data from vnstock
-- ===================================================================

-- ===================================================================
-- 1. TICKER INFO - Thông tin công ty/mã cổ phiếu
-- ===================================================================
CREATE TABLE IF NOT EXISTS ticker_info (
    ticker VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(300),
    company_name_eng VARCHAR(300),
    short_name VARCHAR(100),
    exchange VARCHAR(20),              -- HSX, HNX, UPCOM
    industry_name VARCHAR(200),        -- Ngành
    sector_name VARCHAR(200),          -- Lĩnh vực  
    listed_shares BIGINT,              -- Khối lượng niêm yết
    charter_capital BIGINT,            -- Vốn điều lệ
    par_value BIGINT,                  -- Mệnh giá
    listing_date DATE,                 -- Ngày niêm yết
    website VARCHAR(300),
    description TEXT,
    phone VARCHAR(50),
    fax VARCHAR(50),
    email VARCHAR(100),
    address TEXT,
    company_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ticker_info_exchange ON ticker_info(exchange);
CREATE INDEX IF NOT EXISTS idx_ticker_info_industry ON ticker_info(industry_name);
CREATE INDEX IF NOT EXISTS idx_ticker_info_sector ON ticker_info(sector_name);

-- ===================================================================
-- 2. FINANCIAL STATEMENTS - Báo cáo tài chính
-- ===================================================================

-- Balance Sheet - Bảng cân đối kế toán
CREATE TABLE IF NOT EXISTS balance_sheet (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    quarter INT,
    year INT,
    -- Assets - Tài sản
    total_assets BIGINT,
    current_assets BIGINT,
    cash_and_cash_equivalents BIGINT,
    short_term_investments BIGINT,
    accounts_receivable BIGINT,
    inventory BIGINT,
    non_current_assets BIGINT,
    fixed_assets BIGINT,
    long_term_investments BIGINT,
    -- Liabilities - Nợ phải trả
    total_liabilities BIGINT,
    current_liabilities BIGINT,
    short_term_debt BIGINT,
    accounts_payable BIGINT,
    non_current_liabilities BIGINT,
    long_term_debt BIGINT,
    -- Equity - Vốn chủ sở hữu
    total_equity BIGINT,
    charter_capital BIGINT,
    retained_earnings BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, report_date, quarter)
);

CREATE INDEX IF NOT EXISTS idx_balance_sheet_ticker_date ON balance_sheet(ticker, report_date DESC);
CREATE INDEX IF NOT EXISTS idx_balance_sheet_year ON balance_sheet(year DESC);

-- Income Statement - Báo cáo kết quả kinh doanh
CREATE TABLE IF NOT EXISTS income_statement (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    quarter INT,
    year INT,
    -- Revenue - Doanh thu
    total_revenue BIGINT,
    net_revenue BIGINT,
    cost_of_goods_sold BIGINT,
    gross_profit BIGINT,
    operating_expenses BIGINT,
    operating_profit BIGINT,
    -- Financial items
    financial_income BIGINT,
    financial_expenses BIGINT,
    net_other_income BIGINT,
    profit_before_tax BIGINT,
    tax_expense BIGINT,
    profit_after_tax BIGINT,
    -- Net profit
    net_profit BIGINT,
    eps DECIMAL(15,2),                 -- Earnings per share
    diluted_eps DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, report_date, quarter)
);

CREATE INDEX IF NOT EXISTS idx_income_statement_ticker_date ON income_statement(ticker, report_date DESC);
CREATE INDEX IF NOT EXISTS idx_income_statement_year ON income_statement(year DESC);

-- Cash Flow Statement - Báo cáo lưu chuyển tiền tệ
CREATE TABLE IF NOT EXISTS cash_flow_statement (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    quarter INT,
    year INT,
    -- Operating activities
    operating_cash_flow BIGINT,
    cash_from_operations BIGINT,
    -- Investing activities
    investing_cash_flow BIGINT,
    capex BIGINT,                      -- Capital expenditure
    investments_net BIGINT,
    -- Financing activities
    financing_cash_flow BIGINT,
    debt_issuance BIGINT,
    debt_repayment BIGINT,
    dividends_paid BIGINT,
    -- Net change
    net_cash_flow BIGINT,
    beginning_cash BIGINT,
    ending_cash BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, report_date, quarter)
);

CREATE INDEX IF NOT EXISTS idx_cash_flow_ticker_date ON cash_flow_statement(ticker, report_date DESC);

-- ===================================================================
-- 3. FINANCIAL RATIOS - Các chỉ số tài chính
-- ===================================================================
CREATE TABLE IF NOT EXISTS financial_ratios (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    quarter INT,
    year INT,
    -- Valuation ratios
    pe_ratio DECIMAL(10,2),            -- P/E
    pb_ratio DECIMAL(10,2),            -- P/B
    ps_ratio DECIMAL(10,2),            -- P/S
    market_cap BIGINT,
    enterprise_value BIGINT,
    -- Profitability ratios
    roe DECIMAL(10,4),                 -- Return on Equity
    roa DECIMAL(10,4),                 -- Return on Assets
    ros DECIMAL(10,4),                 -- Return on Sales
    gross_margin DECIMAL(10,4),
    operating_margin DECIMAL(10,4),
    net_margin DECIMAL(10,4),
    -- Liquidity ratios
    current_ratio DECIMAL(10,4),
    quick_ratio DECIMAL(10,4),
    cash_ratio DECIMAL(10,4),
    -- Leverage ratios
    debt_to_equity DECIMAL(10,4),
    debt_to_assets DECIMAL(10,4),
    interest_coverage DECIMAL(10,4),
    -- Efficiency ratios
    asset_turnover DECIMAL(10,4),
    inventory_turnover DECIMAL(10,4),
    receivables_turnover DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, report_date, quarter)
);

CREATE INDEX IF NOT EXISTS idx_financial_ratios_ticker_date ON financial_ratios(ticker, report_date DESC);

-- ===================================================================
-- 4. TRADING STATISTICS - Thống kê giao dịch
-- ===================================================================
CREATE TABLE IF NOT EXISTS trading_statistics (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    trading_date DATE NOT NULL,
    -- Trading data
    open_price DECIMAL(15,2),
    high_price DECIMAL(15,2),
    low_price DECIMAL(15,2),
    close_price DECIMAL(15,2),
    volume BIGINT,
    value BIGINT,                      -- Giá trị giao dịch
    -- Foreign trading
    foreign_buy_volume BIGINT,
    foreign_sell_volume BIGINT,
    foreign_buy_value BIGINT,
    foreign_sell_value BIGINT,
    foreign_net_volume BIGINT,
    foreign_net_value BIGINT,
    -- Market data
    shares_outstanding BIGINT,
    market_cap BIGINT,
    avg_volume_10d BIGINT,
    avg_volume_30d BIGINT,
    beta DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, trading_date)
);

CREATE INDEX IF NOT EXISTS idx_trading_stats_ticker_date ON trading_statistics(ticker, trading_date DESC);
CREATE INDEX IF NOT EXISTS idx_trading_stats_date ON trading_statistics(trading_date DESC);

-- ===================================================================
-- 5. COMPANY EVENTS - Sự kiện công ty
-- ===================================================================
CREATE TABLE IF NOT EXISTS company_events (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    event_date DATE NOT NULL,
    event_type VARCHAR(100),           -- DIVIDEND, AGM, RIGHTS_ISSUE, etc.
    event_title VARCHAR(500),
    event_description TEXT,
    ex_date DATE,                      -- Ex-dividend date
    record_date DATE,
    payment_date DATE,
    dividend_amount DECIMAL(15,2),
    dividend_type VARCHAR(50),         -- CASH, STOCK
    ratio VARCHAR(50),                 -- Tỷ lệ (100:10, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_company_events_ticker ON company_events(ticker, event_date DESC);
CREATE INDEX IF NOT EXISTS idx_company_events_type ON company_events(event_type);

-- ===================================================================
-- 6. HISTORICAL PRICES - Giá lịch sử chi tiết hơn
-- ===================================================================
CREATE TABLE IF NOT EXISTS historical_prices (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    trading_date DATE NOT NULL,
    open_price DECIMAL(15,2),
    high_price DECIMAL(15,2),
    low_price DECIMAL(15,2),
    close_price DECIMAL(15,2),
    adjusted_close DECIMAL(15,2),      -- Điều chỉnh cho chia tách, cổ tức
    volume BIGINT,
    change DECIMAL(15,2),
    change_percent DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, trading_date)
);

CREATE INDEX IF NOT EXISTS idx_historical_prices_ticker_date ON historical_prices(ticker, trading_date DESC);

-- ===================================================================
-- 7. INSIDER TRADING - Giao dịch nội bộ
-- ===================================================================
CREATE TABLE IF NOT EXISTS insider_trading (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    trading_date DATE NOT NULL,
    insider_name VARCHAR(300),
    position VARCHAR(200),             -- CEO, CFO, Board Member, etc.
    relation VARCHAR(200),             -- Quan hệ với công ty
    transaction_type VARCHAR(50),      -- BUY, SELL
    shares_before BIGINT,
    shares_traded BIGINT,
    shares_after BIGINT,
    price DECIMAL(15,2),
    value BIGINT,
    ownership_percent DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_insider_trading_ticker ON insider_trading(ticker, trading_date DESC);

-- ===================================================================
-- 8. NEWS & ANNOUNCEMENTS - Tin tức & Công bố
-- ===================================================================
CREATE TABLE IF NOT EXISTS news_announcements (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10),
    publish_date TIMESTAMP NOT NULL,
    title VARCHAR(1000),
    content TEXT,
    category VARCHAR(100),
    source VARCHAR(200),
    url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_news_ticker_date ON news_announcements(ticker, publish_date DESC);
CREATE INDEX IF NOT EXISTS idx_news_category ON news_announcements(category);

-- ===================================================================
-- 9. MARKET INDICES - Chỉ số thị trường
-- ===================================================================
CREATE TABLE IF NOT EXISTS market_indices (
    id SERIAL PRIMARY KEY,
    index_code VARCHAR(20) NOT NULL,   -- VN-INDEX, VN30, HNX-INDEX, etc.
    trading_date DATE NOT NULL,
    open_index DECIMAL(15,2),
    high_index DECIMAL(15,2),
    low_index DECIMAL(15,2),
    close_index DECIMAL(15,2),
    volume BIGINT,
    value BIGINT,
    change DECIMAL(15,2),
    change_percent DECIMAL(10,4),
    advances INT,                      -- Số mã tăng
    declines INT,                      -- Số mã giảm
    no_change INT,                     -- Số mã đứng giá
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(index_code, trading_date)
);

CREATE INDEX IF NOT EXISTS idx_market_indices_code_date ON market_indices(index_code, trading_date DESC);

-- ===================================================================
-- 10. OWNERSHIP STRUCTURE - Cơ cấu sở hữu
-- ===================================================================
CREATE TABLE IF NOT EXISTS ownership_structure (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    holder_name VARCHAR(500),
    holder_type VARCHAR(100),          -- INDIVIDUAL, INSTITUTION, FOREIGN, STATE
    shares_owned BIGINT,
    ownership_percent DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ownership_ticker ON ownership_structure(ticker, report_date DESC);

-- ===================================================================
-- Summary view for dashboard
-- ===================================================================
CREATE OR REPLACE VIEW stock_summary AS
SELECT 
    r.ticker,
    t.company_name,
    t.exchange,
    t.industry_name,
    r.price as current_price,
    r.change_percent,
    r.volume,
    r.time as last_update,
    fr.pe_ratio,
    fr.market_cap,
    fr.roe
FROM realtime_quotes r
LEFT JOIN ticker_info t ON r.ticker = t.ticker
LEFT JOIN LATERAL (
    SELECT * FROM financial_ratios 
    WHERE ticker = r.ticker 
    ORDER BY report_date DESC 
    LIMIT 1
) fr ON true
WHERE r.time = (
    SELECT MAX(time) 
    FROM realtime_quotes 
    WHERE ticker = r.ticker
);

-- ===================================================================
-- Grant permissions
-- ===================================================================
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;

