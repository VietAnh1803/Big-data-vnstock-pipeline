# DWH Blueprint

Mục tiêu: biến pipeline hiện tại thành kiến trúc production-grade cho realtime + analytics.

## 1) Target Architecture

- **Realtime serving path**: `VNStock -> Kafka -> Spark -> TimescaleDB (serving cache)`
- **Warehouse path (source of truth)**: `Kafka/Timescale -> Snowflake BRONZE -> SILVER -> GOLD`
- **BI path**: Dashboard/BI tools chỉ đọc từ `GOLD`.

Nguyên tắc:
- Realtime nhanh nằm ở Timescale (ngắn hạn, low-latency).
- Analytics chuẩn, historical correctness nằm ở Snowflake.

## 2) Data Model (Medallion + Dim/Fact)

### BRONZE (immutable landing)
- `BRONZE.RAW_QUOTES`
  - Cột chính: `event_time`, `ingest_time`, `ticker`, `price`, `volume`, `quote_time`
  - Metadata: `kafka_topic`, `kafka_partition`, `kafka_offset`, `raw_payload`
  - Mục đích: replay/audit, không sửa record.

### SILVER (clean canonical)
- `SILVER.REALTIME_QUOTES_CLEAN`
  - Key logic: `ticker + event_time`
  - Chuẩn hóa timezone, cast type, quality filter (`price > 0`, `volume >= 0`)
  - Dedup + merge incremental.

### GOLD (business marts)
- `DW.DIM_TICKER`
  - `ticker_sk` surrogate key
  - Ticker attributes (exchange/sector/industry), SCD2 khi cần tracking thay đổi.
- `DW.DIM_DATE`
  - `date_sk = YYYYMMDD`
- `DW.FACT_QUOTE_1M`
  - Grain: `1 row / ticker / minute`
  - Metrics: `open/high/low/close/volume/turnover/source_rows`

## 3) Keys & Merge Strategy

- **Bronze -> Silver**:
  - Natural key: `(ticker, event_time)`
  - `MERGE` upsert để idempotent.
- **Silver -> Fact 1m**:
  - Business key: `(ticker_sk, bucket_minute)`
  - Update nếu late data đến.

Hash kiểm soát thay đổi:
- `record_hash = sha2(concat(ticker, event_time, price, volume), 256)`.

## 4) Orchestration & Schedule

- **Task 1 (1 phút)**: Merge `BRONZE -> SILVER`.
- **Task 2 (after Task 1)**: Upsert `DIM_TICKER`.
- **Task 3 (after Task 2)**: Build/merge `FACT_QUOTE_1M`.
- **Backfill job (manual/scheduled)**:
  - Input: date range.
  - Output: reprocess bronze->silver->gold theo window.

## 5) Data Quality Gates

Bắt buộc ở SILVER/GOLD:
- `not_null`: `ticker`, `event_time`, `price`, `volume`
- `accepted_values`: ticker format `^[A-Z]{2,5}$`
- `range`: `price > 0`, `volume >= 0`
- `uniqueness`: `(ticker, event_time)` trên SILVER
- `freshness`: max lag theo SLA

KPI vận hành:
- ingest lag (`now - max(event_time)`)
- row throughput/min
- duplicate rate
- task failure rate
- late-arrival rate

## 6) SLA/SLO đề xuất

- **Realtime freshness (serving cache)**: p95 < 2 phút
- **Warehouse freshness (gold)**: p95 < 5 phút
- **Pipeline success**: >= 99%
- **Data quality checks pass**: >= 99.9%

## 7) Security & Governance

- Secrets chỉ trong `.env` / secret manager, không commit.
- Least privilege role cho Snowflake (`STOCK_DWH_ROLE`).
- Tách role:
  - `INGEST_ROLE` (write bronze)
  - `TRANSFORM_ROLE` (silver/gold)
  - `BI_ROLE` (read gold only)
- Bật query/audit logs và policy retain.

## 8) Cost Control (Snowflake Free/Low Cost)

- Warehouse `XSMALL`, `AUTO_SUSPEND=60`.
- Cluster key chỉ đặt cho bảng query nặng.
- Hạn chế full scan bằng incremental windows.
- Theo dõi credit theo ngày/tuần.

## 9) Rollout Plan

1. Stabilize ingest (done): vnstock v3 + rate limit aware.
2. Create and validate Snowflake schemas/tables/tasks.
3. Run shadow mode: build gold song song, chưa switch dashboard.
4. Reconcile metrics giữa dashboard cũ và gold marts.
5. Cutover dashboard sang gold.
6. Enable backfill runbook + incident playbook.

## 10) Definition of Done

- Dashboard lấy dữ liệu từ GOLD tables.
- Có backfill chạy được theo date range.
- Có alerting khi freshness/quality fail.
- Có runbook xử lý sự cố + kiểm thử khôi phục.
