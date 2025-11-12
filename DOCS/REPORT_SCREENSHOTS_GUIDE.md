# 📸 Hướng Dẫn Chụp Màn Hình Cho Báo Cáo

## 🎯 Kafka UI - Các Phần Quan Trọng

### 1. **Topics Overview** (Quan trọng nhất)
**URL:** http://localhost:8080/kafka/ → Topics
**Chụp:**
- Danh sách topics (chỉ có `realtime_quotes`)
- Partition count: 12
- Messages in topic: ~62 triệu+
- **Giải thích:** Topic chính chứa dữ liệu real-time từ 210 mã cổ phiếu

### 2. **Topic Details - realtime_quotes**
**URL:** http://localhost:8080/kafka/ → Topics → realtime_quotes
**Chụp:**
- **Partitions tab:** 
  - 12 partitions (0-11)
  - Partition size, messages per partition
  - Leader distribution
- **Messages tab:**
  - Sample messages (JSON format)
  - Show data structure: ticker, price, volume, time, etc.
- **Settings:**
  - Retention: 7 days
  - Segment size
- **Giải thích:** Cấu trúc topic với 12 partitions để xử lý song song, mỗi partition chứa dữ liệu từ nhiều mã cổ phiếu

### 3. **Producer Stats** (nếu có)
**URL:** http://localhost:8080/kafka/ → Topics → realtime_quotes → Producers
**Chụp:**
- Producer rate (messages/second)
- Bytes in/out
- **Giải thích:** Producer đang publish ~100-200 messages/second từ VNStock API

### 4. **Consumer Groups** (Lưu ý)
**URL:** http://localhost:8080/kafka/ → Consumer Groups
**Chụp:**
- "No active consumer groups" message
- **Giải thích:** Spark Structured Streaming không dùng Kafka Consumer Groups, mà dùng checkpoint để quản lý offsets

---

## ⚡ Spark UI - Các Phần Quan Trọng

### 1. **Applications Overview** (Trang chủ)
**URL:** http://localhost:8080/spark/ hoặc http://localhost:4041
**Chụp:**
- Application name: "Vietnam Stock Spark Consumer"
- Status: RUNNING
- Duration: ~18+ hours
- Cores, Memory usage
- **Giải thích:** Spark application đang chạy liên tục, xử lý streaming data

### 2. **Jobs Tab** (Quan trọng)
**URL:** http://localhost:4041 → Jobs
**Chụp:**
- List of completed jobs (6,000+ jobs)
- Job duration (thường < 1 giây)
- Status: SUCCEEDED
- **Giải thích:** Mỗi micro-batch (15 giây) tạo 1 job, xử lý ~50,000 messages mỗi trigger

### 3. **Stages Tab**
**URL:** http://localhost:4041 → Stages
**Chụp:**
- Recent stages (Stage 900+)
- Stage details:
  - Input size: vài MB
  - Shuffle read/write
  - Duration
- **Giải thích:** Spark stages cho quá trình transform và clean data

### 4. **Storage Tab** (Quan trọng)
**URL:** http://localhost:4041 → Storage
**Chụp:**
- Checkpoint location: `/tmp/spark-checkpoint`
- Checkpoint size
- **Giải thích:** Spark lưu offsets và state trong checkpoint để đảm bảo fault tolerance

### 5. **Streaming Tab** (QUAN TRỌNG NHẤT)
**URL:** http://localhost:4041 → Streaming
**Chụp:**
- **Query Status:**
  - Status: ACTIVE
  - Input Rate: messages/second
  - Processing Rate: records/second
  - Batch Duration: ~15 seconds
  - Total Batches: 6,000+
- **Recent Batches:**
  - Batch ID, Timestamp
  - Input Size, Processing Time
  - Output Rows
- **Giải thích:** 
  - Spark đang xử lý real-time với micro-batch 15 giây
  - Input rate ~100-200 messages/second
  - Processing rate tương ứng
  - Mỗi batch xử lý ~50,000 offsets

### 6. **Executors Tab**
**URL:** http://localhost:4041 → Executors
**Chụp:**
- Executor count: 1 (local mode)
- Memory: 1GB allocated
- Active tasks
- **Giải thích:** Spark chạy local[*] với 1 executor, sử dụng tất cả CPU cores

### 7. **SQL Tab** (nếu có)
**URL:** http://localhost:4041 → SQL
**Chụp:**
- Recent queries
- Query duration
- **Giải thích:** Spark SQL queries cho data transformation

---

## 📊 Scripts - Các Output Quan Trọng

### 1. **Lag Check Script**
```bash
bash scripts/calculate_lag.sh
```
**Chụp output:**
- Partition lag details
- Total lag: ~600,000 messages (~0.97%)
- Status: Warning (nhưng acceptable)
- Recent processing status
- **Giải thích:** Consumer lag rất thấp, Spark đang theo kịp producer

### 2. **Topic Statistics**
```bash
docker exec vietnam-stock-kafka kafka-run-class kafka.tools.GetOffsetShell \
    --broker-list localhost:29092 \
    --topic realtime_quotes --time -1
```
**Chụp output:**
- Latest offsets per partition
- Total messages: ~62 triệu
- **Giải thích:** Topic đang chứa ~62 triệu messages từ khi bắt đầu

---

## 🎨 Dashboard - Các Phần Quan Trọng

### 1. **Tổng Quan Thị Trường**
**URL:** http://localhost:8501
**Chụp:**
- Metrics: Tổng Cổ Phiếu, Tổng Khối Lượng, Giá Trung Bình
- Phân bố hiệu suất chart
- **Giải thích:** Dashboard hiển thị real-time data từ TimescaleDB

### 2. **Bảng Giá Real-time**
**Chụp:**
- Table với 100+ mã cổ phiếu
- Columns: Mã, Giá, Thay Đổi, Khối Lượng
- Search và filter functionality
- **Giải thích:** Real-time price board với data từ database

### 3. **Phân Tích Cổ Phiếu**
**Chụp:**
- Combined chart: Candlestick + Volume
- MA5, MA20 lines
- 100 records table
- CSV download button
- **Giải thích:** Chi tiết phân tích technical với historical data

---

## 📝 Thứ Tự Trình Bày Trong Báo Cáo

### Phần 1: Kiến Trúc Tổng Quan
1. **Kafka UI - Topics Overview** → Show topic `realtime_quotes` với 12 partitions
2. **Topic Details** → Show partition distribution và message sample

### Phần 2: Data Processing
3. **Spark UI - Applications Overview** → Show running application
4. **Spark UI - Streaming Tab** → Show real-time processing stats
5. **Spark UI - Jobs Tab** → Show completed jobs (6,000+)
6. **Lag Check Script Output** → Show consumer lag < 1%

### Phần 3: Data Flow
7. **Producer Stats** → Show message rate
8. **Spark Stages** → Show data transformation
9. **Dashboard** → Show final output

### Phần 4: Performance & Monitoring
10. **Spark Executors** → Show resource usage
11. **Streaming Query Details** → Show batch processing stats
12. **Database Records** → Show data persistence

---

## 💡 Tips Cho Báo Cáo

1. **Chụp full screen** để thấy URL và context
2. **Thêm annotations** (mũi tên, text) để highlight phần quan trọng
3. **Chụp nhiều thời điểm** để show real-time updates
4. **Include timestamps** để show data freshness
5. **Show before/after** nếu có optimization

---

## 🔗 Quick Access URLs

- **Kafka UI:** http://localhost:8080/kafka/ (hoặc http://localhost:8081)
- **Spark UI (Live):** http://localhost:4041 (hoặc http://localhost:8080/spark/)
- **Spark History:** http://localhost:18080 (hoặc http://localhost:8080/spark-history/)
- **Dashboard:** http://localhost:8501
- **UI Proxy:** http://localhost:8080 (unified access)

---

## 📸 Recommended Screenshots Order

1. ✅ Kafka Topics Overview (`realtime_quotes`)
2. ✅ Kafka Topic Details (Partitions tab)
3. ✅ Kafka Messages Sample (JSON structure)
4. ✅ Spark Applications Overview (Running status)
5. ✅ Spark Streaming Tab (Input/Processing rates)
6. ✅ Spark Jobs Tab (Completed jobs count)
7. ✅ Lag Check Script Output (Consumer lag)
8. ✅ Dashboard Overview (Market metrics)
9. ✅ Dashboard Stock Analysis (Charts + Table)

---

**Lưu ý:** Tất cả screenshots nên kèm theo giải thích ngắn gọn về:
- **What:** Đây là gì?
- **Why:** Tại sao quan trọng?
- **How:** Hoạt động như thế nào?





