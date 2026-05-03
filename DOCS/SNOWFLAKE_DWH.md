# Snowflake DWH Quickstart (Free Trial)

Tài liệu này giúp bạn dựng mô hình data warehouse với `dim/fact` trên Snowflake, song song với pipeline Kafka + Spark hiện tại.

## 1) Chuẩn bị tài khoản

- Tạo Snowflake free trial.
- Lấy thông tin: account identifier, user, password.
- Mở worksheet bằng role có quyền tạo object (khuyến nghị `ACCOUNTADMIN` cho lần đầu).

## 2) Tạo nền tảng DWH

Chạy các script theo thứ tự:

1. `scripts/snowflake/01_setup.sql`
2. `scripts/snowflake/02_tables.sql`
3. `scripts/snowflake/04_seed_dim_date.sql`
4. `scripts/snowflake/03_tasks.sql`

## 3) Data model

- `BRONZE.RAW_QUOTES`: raw ingestion.
- `SILVER.REALTIME_QUOTES_CLEAN`: cleaned + dedup (MERGE theo `ticker + event_time`).
- `DW.DIM_TICKER`: dimension ticker.
- `DW.DIM_DATE`: dimension date.
- `DW.FACT_QUOTE_1M`: fact OHLCV theo phút.

## 4) Nạp dữ liệu vào BRONZE

Bạn có thể chọn một trong các cách:

- Kafka Connector/Snowpipe Streaming (realtime).
- Batch loader từ TimescaleDB sang Snowflake (theo lịch).

Khi có dữ liệu mới trong `BRONZE.RAW_QUOTES`, task sẽ tự động:
- merge sang `SILVER.REALTIME_QUOTES_CLEAN`,
- cập nhật `DW.DIM_TICKER`,
- build incremental `DW.FACT_QUOTE_1M`.

## 5) Kiểm tra nhanh

```sql
SELECT COUNT(*) AS bronze_rows FROM STOCK_DWH.BRONZE.RAW_QUOTES;
SELECT COUNT(*) AS silver_rows FROM STOCK_DWH.SILVER.REALTIME_QUOTES_CLEAN;
SELECT COUNT(*) AS dim_ticker_rows FROM STOCK_DWH.DW.DIM_TICKER;
SELECT COUNT(*) AS fact_rows FROM STOCK_DWH.DW.FACT_QUOTE_1M;
```

```sql
SELECT *
FROM STOCK_DWH.DW.FACT_QUOTE_1M
ORDER BY BUCKET_MINUTE DESC
LIMIT 50;
```

## 6) Chi phí free-trial

- Giữ `WAREHOUSE_SIZE = XSMALL`.
- `AUTO_SUSPEND = 60` giây để giảm credit.
- Chỉ `RESUME` task khi cần ingest.
- Theo dõi credit trong `ADMIN -> Usage`.
