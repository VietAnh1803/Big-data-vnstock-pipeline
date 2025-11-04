# Vietnam Stock Big Data Pipeline – System Design

## 1. Executive Summary
Hệ thống thu thập và xử lý dữ liệu chứng khoán Việt Nam theo thời gian thực để phục vụ phân tích và trình bày trên dashboard. Kiến trúc sử dụng Kafka (streaming bus), Spark Structured Streaming (xử lý), TimescaleDB (lưu trữ time‑series), và Streamlit (trình bày). UI quản trị gồm Kafka UI và Spark UI, được bảo vệ qua Nginx reverse proxy.

Mục tiêu chính:
- Thu thập realtime từ ~200+ mã cổ phiếu (tăng dần theo nhu cầu)
- Xử lý ổn định, có khả năng mở rộng (scalable) và chống lỗi (fault tolerant)
- Lưu trữ tối ưu cho truy vấn theo thời gian
- Quan sát (observability) tốt: UI/metrics/logs/healthchecks

## 2. Kiến trúc tổng thể
```
VNStock API
   ↓ (parallel fetch)
Kafka Producer  →  Kafka Topic: realtime_quotes (12 partitions)
   ↓
Spark Structured Streaming Consumer (micro-batch 15s, maxOffsetsPerTrigger=50k)
   ↓ (clean + validate + cast)
TimescaleDB (hypertable realtime_quotes, indexes theo time/ticker)
   ↓
Streamlit Dashboard (SSI-style)  ←  SQL queries (latest-per-ticker)

Kafka UI  ← Nginx (/kafka/)
Spark UI  ← Nginx (/spark/)
```

Thành phần & cổng:
- TimescaleDB: 5433 (external) / 5432 (internal)
- Kafka: 9092/9093 (external) / 29092 (internal)
- Dashboard: 8501
- Spark UI (internal 4040), map local 4041 và proxy `/spark/`
- Kafka UI (internal 8080), map local 8081 và proxy `/kafka/`
- Nginx UI proxy: 8080 (Basic Auth)

## 3. Data model & luồng dữ liệu
### 3.1 Producer → Kafka
- Input: Danh sách ~200 tickers (`data/top200_tickers.txt`)
- Chu kỳ: 10 giây/lượt
- Song song: `MAX_WORKERS=24`
- Chuẩn hóa record (key = ticker) để đảm bảo partitioning theo ticker (giữ thứ tự trong partition)

Kafka topic `realtime_quotes` (12 partitions) giúp song song hóa consumer và cân bằng tải.

### 3.2 Spark Structured Streaming → TimescaleDB
- Micro‑batch: `trigger=15s`
- Hạn mức đọc: `maxOffsetsPerTrigger=50000`
- Tối ưu shuffle: `spark.sql.shuffle.partitions=200`
- JDBC sink: `batchsize=10000`, `coalesce(8)`
- Làm sạch dữ liệu:
  - Regex ticker hợp lệ: `^[A-Z]{2,5}$`
  - Ép kiểu giá/khối lượng
  - Map `ingest_time → time` (timestamp chính)
- Checkpointing: bảo đảm khả năng khôi phục khi restart.

### 3.3 TimescaleDB (time‑series)
- Bảng: `realtime_quotes(time timestamptz, ticker text, price numeric, volume bigint, ...)`
- Hypertable theo `time`
- Index: `time`, `ticker`, composite tùy truy vấn
- Retention/Compression: có thể bật cho dữ liệu cũ (tùy yêu cầu)

### 3.4 Dashboard (truy vấn & hiển thị)
- Bảng giá realtime: dùng `DISTINCT ON (ticker)` hoặc window function để lấy bản ghi mới nhất (tránh trùng lặp)
- Tổng quan (market overview): dựa trên tập latest‑per‑ticker trong 1 giờ gần nhất để tính:
  - Tổng số mã (COUNT DISTINCT)
  - Số mã tăng/giảm/không đổi
  - Tổng khối lượng, giá trung bình
- Phân tích cổ phiếu: Candlestick + MA5/MA20, volume chart cao tương phản

## 4. Workflows chi tiết (E2E)
### 4.1 Ingestion workflow
1) Load tickers từ env/file (ưu tiên `TICKERS` → `TICKERS_FILE` → default list)
2) Dùng ThreadPoolExecutor gọi VNStock theo batch
3) Chuẩn hoá record, set key=ticker
4) Publish vào Kafka `realtime_quotes`

### 4.2 Processing workflow
1) Spark đọc từ Kafka theo micro‑batch
2) Parse JSON → DataFrame → validate/cast
3) Lọc ticker không hợp lệ, loại bỏ outliers (tuỳ chính sách)
4) Ghi batch vào TimescaleDB qua JDBC (coalesce + batchsize)
5) Ghi checkpoint → đảm bảo idempotence khi restart

### 4.3 Serving workflow
1) Dashboard truy vấn TimescaleDB (latest per ticker/minute bucket)
2) Tổng hợp thị trường (gainers/losers/unchanged) theo latest‑per‑ticker
3) Vẽ candlestick, MA lines, volume bars
4) Tùy chọn auto‑refresh

### 4.4 Observability & Ops
- Kafka UI: topics, partitions, consumer lag, messages/s
- Spark UI: jobs, stages, input rate, processing time, throughput
- Healthchecks cho mọi service; logs tại `./logs/`
- Reverse proxy + Basic Auth bảo vệ UI

## 5. Lý do chọn Tech Stack
### Kafka (so với Redis Streams, RabbitMQ)
- Partitioning mạnh mẽ + lưu trữ bền vững (log‑based), phù hợp throughput cao
- Consumer groups & offset management chuẩn mực cho streaming
- Hệ sinh thái phong phú (Kafka UI, Connect, Schema Registry)

### Spark Structured Streaming (so với Flink, Storm, Beam)
- Batch + Streaming thống nhất (unified engine), phù hợp ETL streaming + batch sinks
- Ecosystem giàu có (SQL, MLlib, Delta/Parquet) nếu cần mở rộng
- Dễ vận hành single‑node/standalone, scale up đơn giản; dev experience thân thiện
- Với yêu cầu hiện tại (micro‑batch 15s) đảm bảo throughput + latency hợp lý
> Khi chọn Flink?
> - Yêu cầu latency cực thấp (sub‑second), event‑time semantics phức tạp, stateful streaming rất lớn. Flink mạnh hơn ở pure streaming low‑latency, nhưng vận hành phức tạp hơn.

### TimescaleDB (so với ClickHouse, InfluxDB, Cassandra)
- PostgreSQL extension → kế thừa SQL chuẩn, hệ sinh thái (driver, tooling)
- Hypertable tối ưu time‑series, continuous aggregates, compression, retention
- Phù hợp truy vấn analytics thời gian + dễ vận hành hơn cluster phức tạp
> Khi chọn ClickHouse?
> - OLAP columnar tốc độ cực cao cho analytics phức tạp/khối lượng cực lớn. Đổi lại, vận hành khác PostgreSQL, đường cong học tập cao hơn.

### Streamlit (so với Grafana/Metabase/React app)
- Tốc độ phát triển cao, Python‑native, dễ dựng UI data nhanh
- Thích hợp PoC/production lightweight; có thể thay/gắn kèm Grafana sau này

### Nginx Reverse Proxy + Basic Auth
- Hợp nhất đường truy cập UI (`/spark/`, `/kafka/`)
- Bảo vệ UI nội bộ, dễ cấu hình và tích hợp thêm TLS/ACL

## 6. Ưu điểm nổi bật so với stack khác
- Throughput tốt với Kafka + Spark (tối ưu partitions, offsets, shuffle)
- SQL‑friendly (TimescaleDB/PostgreSQL) → dễ viết truy vấn, BI/analytics quen thuộc
- DevOps đơn giản (Docker Compose), healthchecks, logs rõ ràng
- Observability trực quan (Kafka UI, Spark UI, Streamlit)
- Mở rộng tuyến tính:
  - Kafka: tăng partitions
  - Spark: tăng `maxOffsetsPerTrigger`, `shuffle.partitions`, scale executors
  - DB: bật compression/retention, scale vertical/horizontal tùy nhu cầu

## 7. Hiệu năng & Tuning Checklist
- Kafka
  - Partitions ≥ số consumer tasks
  - Theo dõi consumer lag, retention, segment size
- Spark
  - `maxOffsetsPerTrigger`, `spark.sql.shuffle.partitions`
  - Batch size JDBC, số partitions khi ghi (`coalesce`)
  - Checkpoint directory tách biệt disk nhanh
- TimescaleDB
  - Index đúng cột lọc/join
  - Retention/Compression policy cho dữ liệu cũ
- Dashboard
  - Truy vấn latest‑per‑ticker (DISTINCT ON/ROW_NUMBER)
  - Giới hạn khung thời gian

## 8. Bảo mật & Quản trị
- UI proxy (Basic Auth), local‑only binding cho UI nội bộ
- Secrets trong `ACCOUNTS_PASSWORDS.md` (đã gitignore)
- Network isolation qua Docker network
- Có thể bổ sung: TLS, IP allowlist, rotation mật khẩu

## 9. Roadmap mở rộng
- Scale‑out Spark (executors) khi tăng ticker/throughput
- Continuous aggregates/retention policy cho TimescaleDB
- Cảnh báo realtime (webhook/Slack/email) theo điều kiện thị trường
- Thêm chỉ số thị trường (VN30, VNINDEX), backfill lịch sử, feature engineering
- Tích hợp Grafana/Metabase cho BI; API REST/GraphQL phục vụ bên thứ ba

## 10. Quy trình vận hành (Ops playbook)
- Start/stop:
```bash
docker-compose -f docker-compose-timescaledb.yml up -d
docker-compose -f docker-compose-timescaledb.yml ps
```
- Logs & monitoring:
```bash
docker-compose -f docker-compose-timescaledb.yml logs -f [service]
docker stats
```
- Kiểm tra dữ liệu:
```bash
docker exec vietnam-stock-timescaledb psql -U stock_app -d stock_db -c "SELECT COUNT(DISTINCT ticker) FROM realtime_quotes WHERE time >= NOW() - INTERVAL '1 hour';"
```

## 11. Quyết định thiết kế quan trọng
- Chọn micro‑batch 15s (thay vì stream từng record) để cân bằng latency/throughput
- Lưu toàn bộ realtime vào TimescaleDB để phục vụ cả realtime lẫn lịch sử ngắn hạn
- Partitioning theo ticker ở Kafka để đảm bảo ordering per‑ticker
- Sử dụng DISTINCT ON/ROW_NUMBER ở dashboard để loại bỏ trùng lặp hiển thị

## 12. Tài liệu tham khảo nhanh
- README.md – hướng dẫn tổng quan & commands
- QUICK_START.md – khởi động nhanh
- ACCOUNTS_PASSWORDS.md – credentials (private)
