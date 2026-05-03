# Vietnam Stock Big Data Pipeline – System Design

## 1. Executive Summary

Hệ thống thu thập và xử lý dữ liệu chứng khoán Việt Nam gần real-time, phục vụ dashboard và (tùy cấu hình) data warehouse trên Snowflake. Thành phần chính: **Kafka**, **Spark Structured Streaming**, **TimescaleDB** (staging time-series), **Snowflake** (BRONZE/SILVER/DW qua `snowflake-sync` + SQL tasks), **Streamlit**. UI vận hành: Kafka UI và Spark UI qua reverse proxy (Basic Auth).

Mục tiêu chính:

- Thu thập tick từ tập mã (file `data/top200_tickers.txt`, có rotation khi giới hạn API).
- Xử lý ổn định, fault tolerance (Kafka log, Spark checkpoint).
- Hai đường phục vụ: **TimescaleDB** (latency thấp), **Snowflake** (analytics / BI chuẩn dim-fact).
- Observability: UI, healthchecks, logs trong `./logs/`.

## 2. Kiến trúc tổng thể

```
VNStock API
   ↓
Kafka Producer  →  Kafka topic: realtime_quotes (số partition mặc định theo docker-compose, thường 3)
   ↓
Spark Structured Streaming (micro-batch ~15s)
   ↓
TimescaleDB  public.realtime_quotes  (staging hypertable)
   ↓
snowflake-sync (incremental)  →  Snowflake BRONZE.RAW_QUOTES  →  SILVER  →  DW (DIM/FACT)
   ↓
Streamlit  (DASHBOARD_DATA_SOURCE=snowflake | legacy Timescale)

Kafka UI, Spark UI  ←  reverse proxy :18082  (/kafka/, /spark/)
```

**Cổng (mặc định `docker-compose-timescaledb.yml`):**

| Thành phần | Host | Ghi chú |
|------------|------|---------|
| TimescaleDB | `127.0.0.1:15433` | Trong container: `5432` |
| Kafka (client) | `127.0.0.1:19092` | Trong mạng Docker: `kafka:29092` |
| Dashboard | `0.0.0.0:8501` | Streamlit |
| Kafka UI | `127.0.0.1:18081` | Và qua proxy `/kafka/` |
| Spark UI | `127.0.0.1:4041` | Map từ 4040; và qua proxy `/spark/` |
| UI proxy | `127.0.0.1:18082` | Basic Auth (`KAFKA_UI_PASSWORD`) |
| Spark History | `127.0.0.1:18080` | Tùy chọn |
| pgAdmin | `127.0.0.1:15050` | Tùy chọn |

## 3. Data model & luồng dữ liệu

### 3.1 Producer → Kafka

- Tickers: `TICKERS_FILE` (mặc định `data/top200_tickers.txt`).
- Chu kỳ và worker: biến môi trường trong compose (`COLLECTION_INTERVAL`, `MAX_WORKERS`, v.v.).
- Key message: ticker (partition theo mã trong cùng topic).

### 3.2 Spark → TimescaleDB

- Đọc Kafka micro-batch; validate/cast; ghi JDBC vào `public.realtime_quotes`.
- Checkpoint Spark để khôi phục offset.

### 3.3 TimescaleDB

- Chỉ khởi tạo **một** hypertable nghiệp vụ chính: `public.realtime_quotes` (xem `scripts/timescaledb_init.sql`).
- Mô hình medallion đầy đủ (BRONZE/SILVER/DW) được triển khai trên **Snowflake**, không trùng lặp bảng silver/dw rỗng trên Timescale.

### 3.4 Snowflake & đồng bộ

- Job Python `consumers/snowflake_sync_job.py` (service `snowflake-sync`) đọc `public.realtime_quotes`, ghi Snowflake và merge theo pipeline đã định nghĩa trong `scripts/snowflake/*.sql`.
- Chi tiết: `DOCS/DWH_BLUEPRINT.md`, `DOCS/SNOWFLAKE_DWH.md`.

### 3.5 Dashboard

- `DASHBOARD_DATA_SOURCE=snowflake` (mặc định): truy vấn Snowflake (`SILVER`, `DW`, view BI nếu đã tạo).
- `legacy`: đọc trực tiếp `public.realtime_quotes` trên TimescaleDB.

## 4. Workflows E2E (rút gọn)

1. **Ingestion:** Producer → Kafka `realtime_quotes`.
2. **Processing:** Spark consumer → `public.realtime_quotes`.
3. **Warehouse:** `snowflake-sync` → Snowflake BRONZE → task/merge SILVER → DIM/FACT.
4. **Serving:** Streamlit; health panel + SQL tương ứng nguồn.

**Observability:** Kafka UI, Spark UI, logs, `scripts/health/check_freshness.sh` (độ trễ bản ghi mới nhất trên `public.realtime_quotes`).

## 5. Lý do chọn Tech Stack

(Phần so sánh Kafka vs Redis/RabbitMQ, Spark vs Flink, TimescaleDB vs ClickHouse giữ nguyên tinh thần bản cũ: ưu tiên hệ sinh thái, SQL, vận hành Compose đơn giản cho đề tài / prototype.)

## 6. Ưu điểm & mở rộng

- Tách **realtime staging** và **warehouse** rõ ràng.
- Tăng partition Kafka / shuffle Spark / batch JDBC khi tăng tải.
- Snowflake: warehouse size, task schedule, incremental window.

## 7. Hiệu năng & Tuning Checklist

- Kafka: lag consumer, retention, `KAFKA_NUM_PARTITIONS`.
- Spark: `MAX_OFFSETS_PER_TRIGGER`, `SPARK_SHUFFLE_PARTITIONS`, JDBC batch, checkpoint disk.
- TimescaleDB: index `time`, `ticker`; retention/compression khi cần.
- Snowflake: tránh full scan; cluster key / filter theo `bucket_minute`.

## 8. Bảo mật & Quản trị

- Secrets trong `.env` (không commit); có thể dùng `scripts/security/preflight_env_check.sh`.
- UI nội bộ bind localhost; proxy Basic Auth.
- Snowflake: role least-privilege (`STOCK_DWH_ROLE`), xem `SECURITY_CONFIGURATION.md` nếu có trong workspace.

## 9. Roadmap (gợi ý)

- Alerting freshness/DQ; Great Expectations hoặc tương đương.
- Grafana/Metabase; API read-only cho bên thứ ba.

## 10. Ops playbook

```bash
docker compose -f docker-compose-timescaledb.yml up -d
docker compose -f docker-compose-timescaledb.yml ps
docker compose -f docker-compose-timescaledb.yml logs -f [service]
```

```bash
docker exec vietnam-stock-timescaledb psql -U stock_app -d stock_db -c \
  "SELECT COUNT(DISTINCT ticker) FROM realtime_quotes WHERE time >= NOW() - INTERVAL '1 hour';"
```

## 11. Quyết định thiết kế quan trọng

- Micro-batch Spark cân bằng latency/throughput.
- Một bảng staging chuẩn trên Timescale; DW chuẩn hóa trên Snowflake.
- Dashboard mặc định đọc Snowflake để đồng nhất grain BI với `FACT_QUOTE_1M`.

## 12. Tài liệu tham khảo

- `README.md` — hướng dẫn triển khai, ports, biến môi trường.
- `DOCS/DWH_BLUEPRINT.md`, `DOCS/SNOWFLAKE_DWH.md` — warehouse.
- `SECURITY_CONFIGURATION.md` — nếu bạn tạo cục bộ (thường gitignore).
