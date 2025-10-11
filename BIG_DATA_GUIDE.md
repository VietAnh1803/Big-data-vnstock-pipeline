# 🚀 BIG DATA PIPELINE - Hướng Dẫn

## 📊 Tổng Quan

Project đã được nâng cấp thành **BIG DATA Pipeline** với khả năng thu thập và lưu trữ:

### Dữ Liệu Hiện Có

| Loại Dữ Liệu | Số Lượng | Mô Tả |
|---------------|----------|-------|
| **Ticker Info** | 1,719 công ty | Thông tin cơ bản: tên, sàn, ngành, vốn điều lệ |
| **Realtime Quotes** | 2.5+ triệu records | Giá realtime từ Kafka stream |
| **Historical Prices** | Đang thu thập | Lịch sử giá 2 năm cho mỗi mã |
| **Balance Sheet** | Sẵn sàng | Bảng cân đối kế toán theo quý |
| **Income Statement** | Sẵn sàng | Báo cáo kết quả kinh doanh |
| **Cash Flow** | Sẵn sàng | Lưu chuyển tiền tệ |
| **Financial Ratios** | Sẵn sàng | P/E, P/B, ROE, ROA, D/E... |

---

## 🗄️ Cấu Trúc Database

### 1. **ticker_info** - Thông Tin Công Ty
```sql
- ticker (PRIMARY KEY)
- company_name, company_name_eng, short_name
- exchange (HSX, HNX, UPCOM)
- industry_name, sector_name
- listed_shares, charter_capital, par_value
- listing_date
- website, phone, email, address
```

### 2. **balance_sheet** - Bảng Cân Đối Kế Toán
```sql
- ticker, report_date, quarter, year
- total_assets, current_assets
- total_liabilities, current_liabilities
- total_equity, retained_earnings
```

### 3. **income_statement** - Kết Quả Kinh Doanh
```sql
- ticker, report_date, quarter, year
- total_revenue, net_revenue
- gross_profit, operating_profit
- profit_after_tax, eps
```

### 4. **cash_flow_statement** - Lưu Chuyển Tiền
```sql
- ticker, report_date, quarter, year
- operating_cash_flow
- investing_cash_flow
- financing_cash_flow
```

### 5. **financial_ratios** - Chỉ Số Tài Chính
```sql
- ticker, report_date, quarter, year
- pe_ratio, pb_ratio, ps_ratio
- roe, roa, ros
- current_ratio, quick_ratio
- debt_to_equity, debt_to_assets
```

### 6. **historical_prices** - Giá Lịch Sử
```sql
- ticker, trading_date
- open, high, low, close, adjusted_close
- volume, change, change_percent
```

### 7. **realtime_quotes** - Giá Realtime (đã có)
```sql
- ticker, time, price, volume
- change_percent, processed_time
```

---

## 🔧 Cách Sử Dụng

### Thu Thập Dữ Liệu

#### 1. Fetch TẤT CẢ dữ liệu (lần đầu)
```bash
make fetch-data
```
**Lưu ý:** 
- Mất khoảng **1-2 giờ** cho 1,700+ mã
- Có delay 1.2s giữa mỗi request để tránh rate limit
- Tự động retry nếu bị rate limit

#### 2. Xem tiến trình
```bash
# Kiểm tra số liệu đã có
make data-stats

# Xem theo sàn
make ticker-count
```

#### 3. Sync lên Snowflake
```bash
make sync-snowflake
```

#### 4. Setup đầy đủ (Fetch + Sync)
```bash
make big-data-setup
```

---

## 🤖 Tự Động Hóa

### Cài Đặt Cron Jobs

```bash
chmod +x scripts/setup_big_data_cron.sh
sudo ./scripts/setup_big_data_cron.sh
```

### Lịch Tự Động

| Tác Vụ | Thời Gian | Mô Tả |
|--------|-----------|-------|
| **Full fetch** | Chủ Nhật 2:00 AM | Thu thập đầy đủ tất cả dữ liệu |
| **Ticker update** | Hàng ngày 1:00 AM | Cập nhật thông tin mã mới |
| **Cleanup** | Mỗi tháng ngày 1, 3:00 AM | Xóa Docker images cũ |

### Logs

```bash
tail -f /var/log/vietnam-stock-pipeline/big_data_fetch_*.log
```

---

## 📈 Truy Vấn Dữ Liệu

### Kết nối PostgreSQL

```bash
# CLI
docker exec -it postgres psql -U admin -d stock_db

# pgAdmin
http://localhost:5050
```

### Ví Dụ Queries

#### 1. Thông tin công ty theo ngành
```sql
SELECT 
    industry_name,
    COUNT(*) as total_companies,
    COUNT(CASE WHEN exchange = 'HSX' THEN 1 END) as hsx,
    COUNT(CASE WHEN exchange = 'HNX' THEN 1 END) as hnx,
    COUNT(CASE WHEN exchange = 'UPCOM' THEN 1 END) as upcom
FROM ticker_info
GROUP BY industry_name
ORDER BY total_companies DESC;
```

#### 2. Top công ty theo vốn hóa
```sql
SELECT 
    ticker,
    company_name,
    exchange,
    charter_capital,
    listed_shares
FROM ticker_info
WHERE charter_capital IS NOT NULL
ORDER BY charter_capital DESC
LIMIT 20;
```

#### 3. Giá hiện tại + thông tin công ty
```sql
SELECT 
    r.ticker,
    t.company_name,
    t.exchange,
    t.industry_name,
    r.price as current_price,
    r.change_percent,
    r.volume,
    r.time as last_update
FROM realtime_quotes r
LEFT JOIN ticker_info t ON r.ticker = t.ticker
WHERE r.time = (
    SELECT MAX(time) 
    FROM realtime_quotes 
    WHERE ticker = r.ticker
)
ORDER BY r.volume DESC
LIMIT 20;
```

#### 4. Historical prices với Moving Average
```sql
SELECT 
    ticker,
    trading_date,
    close_price,
    AVG(close_price) OVER (
        PARTITION BY ticker 
        ORDER BY trading_date 
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) as ma20
FROM historical_prices
WHERE ticker = 'VNM'
ORDER BY trading_date DESC
LIMIT 30;
```

#### 5. Financial ratios trending
```sql
SELECT 
    ticker,
    year,
    quarter,
    roe,
    roa,
    pe_ratio,
    pb_ratio,
    debt_to_equity
FROM financial_ratios
WHERE ticker = 'VNM'
ORDER BY year DESC, quarter DESC
LIMIT 8;
```

---

## ☁️ Snowflake Integration

### Tables trong Snowflake

Tất cả bảng sẽ được sync với cấu trúc tương tự PostgreSQL, thêm cột `SYNCED_AT`.

### Verify Sync

```sql
-- Trong Snowflake
SELECT 
    'TICKER_INFO' as table_name, 
    COUNT(*) as rows,
    MAX(SYNCED_AT) as last_sync
FROM TICKER_INFO
UNION ALL
SELECT 'HISTORICAL_PRICES', COUNT(*), MAX(SYNCED_AT)
FROM HISTORICAL_PRICES
UNION ALL
SELECT 'BALANCE_SHEET', COUNT(*), MAX(SYNCED_AT)
FROM BALANCE_SHEET
-- ... các bảng khác
;
```

---

## 📊 View Tổng Hợp

### stock_summary - View kết hợp tất cả

```sql
SELECT * FROM stock_summary
WHERE exchange = 'HSX'
ORDER BY market_cap DESC
LIMIT 10;
```

Bao gồm:
- Giá realtime hiện tại
- Thông tin công ty
- Financial ratios mới nhất
- Vốn hóa thị trường

---

## 🎯 Use Cases

### 1. Phân Tích Theo Ngành
```sql
SELECT 
    t.industry_name,
    AVG(fr.roe) as avg_roe,
    AVG(fr.pe_ratio) as avg_pe,
    COUNT(DISTINCT t.ticker) as companies
FROM ticker_info t
LEFT JOIN LATERAL (
    SELECT * FROM financial_ratios 
    WHERE ticker = t.ticker 
    ORDER BY report_date DESC 
    LIMIT 1
) fr ON true
WHERE t.exchange = 'HSX'
GROUP BY t.industry_name
ORDER BY avg_roe DESC;
```

### 2. Screening Cổ Phiếu
```sql
-- Tìm cổ phiếu: ROE > 15%, P/E < 15, D/E < 1
SELECT 
    t.ticker,
    t.company_name,
    fr.roe,
    fr.pe_ratio,
    fr.debt_to_equity,
    r.price as current_price
FROM ticker_info t
INNER JOIN LATERAL (
    SELECT * FROM financial_ratios 
    WHERE ticker = t.ticker 
    ORDER BY report_date DESC 
    LIMIT 1
) fr ON true
INNER JOIN LATERAL (
    SELECT * FROM realtime_quotes 
    WHERE ticker = t.ticker 
    ORDER BY time DESC 
    LIMIT 1
) r ON true
WHERE fr.roe > 0.15
  AND fr.pe_ratio < 15
  AND fr.debt_to_equity < 1
  AND t.exchange = 'HSX';
```

### 3. Backtesting Strategy
```sql
-- Tính lợi nhuận nếu mua vào đầu năm
SELECT 
    ticker,
    MIN(CASE WHEN trading_date = '2024-01-01' THEN close_price END) as entry_price,
    MAX(CASE WHEN trading_date = CURRENT_DATE THEN close_price END) as current_price,
    (MAX(CASE WHEN trading_date = CURRENT_DATE THEN close_price END) - 
     MIN(CASE WHEN trading_date = '2024-01-01' THEN close_price END)) * 100.0 / 
     MIN(CASE WHEN trading_date = '2024-01-01' THEN close_price END) as return_pct
FROM historical_prices
WHERE trading_date >= '2024-01-01'
GROUP BY ticker
ORDER BY return_pct DESC
LIMIT 20;
```

---

## 🔄 Data Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                             │
├─────────────────────────────────────────────────────────────┤
│  • vnstock API (Historical, Financials)                     │
│  • Kafka Stream (Realtime Quotes)                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   POSTGRESQL                                 │
├─────────────────────────────────────────────────────────────┤
│  • ticker_info          (1,719 rows)                        │
│  • balance_sheet        (quarterly data)                    │
│  • income_statement     (quarterly data)                    │
│  • cash_flow_statement  (quarterly data)                    │
│  • financial_ratios     (quarterly data)                    │
│  • historical_prices    (daily, 2 years)                    │
│  • realtime_quotes      (2.5M+ rows)                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    SNOWFLAKE                                 │
├─────────────────────────────────────────────────────────────┤
│  Same tables + SYNCED_AT column                             │
│  Analytics & Reporting                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Troubleshooting

### Rate Limit Errors

Nếu gặp rate limit:
```bash
# Script đã tự động retry, nhưng nếu cần chạy lại:
make fetch-data
```

### Kiểm Tra Dữ Liệu

```bash
# Thống kê tổng quát
make data-stats

# Chi tiết ticker
docker exec postgres psql -U admin -d stock_db -c "
  SELECT * FROM ticker_info LIMIT 5;
"

# Historical prices
docker exec postgres psql -U admin -d stock_db -c "
  SELECT ticker, COUNT(*), MIN(trading_date), MAX(trading_date)
  FROM historical_prices
  GROUP BY ticker
  ORDER BY COUNT(*) DESC
  LIMIT 10;
"
```

### Logs

```bash
# Docker logs
docker compose logs data-fetcher -f

# Cron logs
tail -f /var/log/vietnam-stock-pipeline/*.log
```

---

## 📚 Tài Liệu Tham Khảo

- **README.md** - Hướng dẫn chính của project
- **PRODUCTION_GUIDE.md** - Hướng dẫn production deployment
- **PRODUCTION_REPORT.md** - Báo cáo setup production
- **PORTS_EXPLAINED.md** - Chi tiết về các ports
- **vnstock3 docs** - https://vnstocks.com/

---

## 🎯 Roadmap Tiếp Theo

### Đã Hoàn Thành ✅
- ✅ Thu thập ticker info (1,719 công ty)
- ✅ Thiết kế database schema đầy đủ
- ✅ Script fetch data với rate limit handling
- ✅ Historical prices collection
- ✅ Snowflake sync script
- ✅ Makefile commands
- ✅ Cron jobs tự động

### Đang Thực Hiện 🚧
- 🚧 Thu thập đầy đủ historical prices
- 🚧 Financial statements (balance sheet, income, cash flow)
- 🚧 Financial ratios

### Kế Hoạch 📋
- 📋 Insider trading data
- 📋 Company events (dividends, splits)
- 📋 News & announcements
- 📋 Market indices (VN-INDEX, VN30, HNX-INDEX)
- 📋 Ownership structure
- 📋 Advanced dashboard với financial analysis

---

## 💡 Tips

1. **Lần đầu fetch**: Chạy vào cuối tuần để có nhiều thời gian
2. **Rate limit**: Script tự động delay 1.2s, đừng vội vàng
3. **Snowflake**: Sync sau khi fetch xong để tiết kiệm compute
4. **Backup**: Có cron job tự động, nhưng nên manual backup trước khi thử nghiệm
5. **Monitoring**: Theo dõi logs để phát hiện lỗi sớm

---

**🎉 Chúc bạn phân tích thành công với BIG DATA Pipeline!**

