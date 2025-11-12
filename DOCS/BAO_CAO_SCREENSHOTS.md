# 📸 Hướng Dẫn Chụp Màn Hình Cho Báo Cáo

## 🎯 Tổng Quan

Tài liệu này hướng dẫn các màn hình cần chụp từ Kafka UI và Spark UI để trình bày trong báo cáo.

---

## 📊 PHẦN 1: KAFKA UI

**URL:** http://localhost:8080/kafka/ hoặc http://localhost:8081

### 1.1. **Topics Overview** (Trang chủ Kafka UI)
**Vị trí:** Trang chủ sau khi login
**Cần chụp:**
- Danh sách topics (chỉ thấy `realtime_quotes`)
- Số lượng partitions: **12 partitions**
- Topic name: `realtime_quotes`
- **Giải thích:** "Kafka topic chính để stream dữ liệu real-time từ producer"

### 1.2. **Topic Details - realtime_quotes**
**Vị trí:** Click vào topic `realtime_quotes`
**Cần chụp:**
- **Partitions tab:**
  - 12 partitions (0-11)
  - Replication Factor: 1
  - Segment size: 1GB
- **Messages tab:**
  - Total messages trong topic
  - Message rate (messages/second)
- **Giải thích:** 
  - "12 partitions để scale horizontal và parallel processing"
  - "Message format: JSON với schema chuẩn"

### 1.3. **Topic Configuration**
**Vị trí:** Trong topic details → Configuration tab
**Cần chụp:**
- Retention policy (7 days)
- Segment size
- Compression settings
- **Giải thích:** "Cấu hình retention và compression để tối ưu storage"

### 1.4. **Messages Browser** (Optional)
**Vị trí:** Trong topic → Messages tab
**Cần chụp:**
- Sample message format
- Message key (ticker)
- Message value (JSON payload)
- **Giải thích:** "Message structure: key = ticker, value = JSON với price, volume, change, etc."

---

## ⚡ PHẦN 2: SPARK UI

**URL:** http://localhost:8080/spark/ hoặc http://localhost:4041

### 2.1. **Spark Application Overview**
**Vị trí:** Trang chủ Spark UI
**Cần chụp:**
- Application name: "Vietnam Stock Spark Consumer"
- Application ID: `local-1762249055177`
- Status: **Running**
- Duration: Thời gian chạy
- **Giải thích:** "Spark Structured Streaming application đang chạy 24/7"

### 2.2. **Jobs Tab - Active Jobs**
**Vị trí:** Spark UI → Jobs tab
**Cần chụp:**
- Active jobs list
- Completed jobs count
- Job duration và status
- **Giải thích:** "Spark xử lý micro-batches mỗi 15 giây, mỗi job = 1 batch processing"

### 2.3. **Stages Tab** (Quan trọng)
**Vị trí:** Spark UI → Stages tab
**Cần chụp:**
- Stage details với:
  - Input size (data từ Kafka)
  - Output size (data sau processing)
  - Shuffle read/write
  - Duration
- **Giải thích:** 
  - "Input size: lượng data đọc từ Kafka"
  - "Shuffle partitions: 200 để parallel processing"
  - "Processing time: < 5 giây cho mỗi batch"

### 2.4. **Storage Tab** (Optional)
**Vị trí:** Spark UI → Storage tab
**Cần chụp:**
- Cached data (nếu có)
- **Giải thích:** "Spark caching để optimize repeated queries"

### 2.5. **Environment Tab** (Quan trọng)
**Vị trí:** Spark UI → Environment tab
**Cần chụp:**
- Spark Properties:
  - `spark.sql.streaming.checkpointLocation`: `/tmp/spark-checkpoint`
  - `spark.sql.shuffle.partitions`: `200`
  - `spark.sql.streaming.kafka.useDeprecatedOffsetFetching`: `false`
- **Giải thích:** 
  - "Checkpoint location: Spark lưu offsets để fault tolerance"
  - "Shuffle partitions: 200 để scale processing"
  - "Kafka integration: dùng latest Kafka consumer API"

### 2.6. **Executors Tab**
**Vị trí:** Spark UI → Executors tab
**Cần chụp:**
- Number of executors
- Memory usage
- Cores used
- Tasks completed
- **Giải thích:** "Resource usage: CPU cores, memory allocation"

### 2.7. **SQL Tab** (Nếu có)
**Vị trí:** Spark UI → SQL tab
**Cần chụp:**
- Query execution plans
- Query duration
- **Giải thích:** "Spark SQL queries cho data transformation"

---

## 📈 PHẦN 3: SPARK STREAMING (Quan trọng nhất)

**Vị trí:** Spark UI → Tab "Streaming" (nếu có) hoặc trong Jobs tab tìm streaming jobs

### 3.1. **Streaming Query Statistics**
**Cần chụp:**
- **Input Rate:** Messages/second đọc từ Kafka
- **Processing Rate:** Messages/second xử lý
- **Batch Duration:** Thời gian xử lý mỗi batch (~15 giây)
- **Total Processed Records:** Tổng số records đã xử lý
- **Giải thích:** 
  - "Micro-batch processing: mỗi 15 giây Spark đọc và xử lý một batch"
  - "Input rate vs Processing rate: cho thấy Spark có theo kịp Kafka không"

### 3.2. **Batch Processing Details**
**Cần chụp:**
- List of recent batches
- Batch ID và timestamp
- Records per batch
- Processing time
- **Giải thích:** "Mỗi batch xử lý ~100-300 records, thời gian < 5 giây"

---

## 🗄️ PHẦN 4: DATABASE (Optional nhưng tốt)

### 4.1. **Database Statistics**
**Command:**
```sql
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT ticker) as unique_tickers,
    MIN(time) as earliest_record,
    MAX(time) as latest_record,
    MAX(time) - MIN(time) as data_range
FROM realtime_quotes;
```

**Giải thích:** "TimescaleDB hypertable với compression và retention policies"

---

## 📋 THỨ TỰ TRÌNH BÀY ĐỀ XUẤT

### Slide 1: Architecture Overview
- Kafka UI → Topics overview
- Giải thích: "Kafka làm streaming bus, topic `realtime_quotes` với 12 partitions"

### Slide 2: Kafka Topic Details
- Kafka UI → Topic `realtime_quotes` details
- Partitions, messages, configuration
- Giải thích: "12 partitions cho parallel processing, retention 7 ngày"

### Slide 3: Spark Application
- Spark UI → Application overview
- Jobs, Stages
- Giải thích: "Spark Structured Streaming consumer xử lý real-time"

### Slide 4: Spark Processing Performance
- Spark UI → Stages tab
- Input/Output sizes, duration
- Giải thích: "Processing time < 5s, throughput cao"

### Slide 5: Streaming Metrics
- Spark UI → Streaming tab (nếu có) hoặc Jobs với streaming details
- Input rate, processing rate
- Giải thích: "Spark theo kịp Kafka, không có lag đáng kể"

### Slide 6: Resource Usage
- Spark UI → Executors tab
- CPU, Memory usage
- Giải thích: "Resource utilization hiệu quả"

---

## 💡 TIPS CHO BÁO CÁO

1. **Highlight con số cụ thể:**
   - 12 partitions
   - 15 giây batch interval
   - 200 shuffle partitions
   - 50,000 max offsets per trigger

2. **Giải thích lợi ích:**
   - "12 partitions → parallel processing → high throughput"
   - "Checkpoint → fault tolerance → không mất data"
   - "Micro-batch 15s → low latency → real-time processing"

3. **So sánh với alternatives:**
   - "Spark Structured Streaming vs traditional Kafka Consumer"
   - "Checkpoint-based offsets vs Consumer Groups"
   - "Why 12 partitions? Scalability và load balancing"

4. **Performance metrics:**
   - "Input rate: X messages/sec"
   - "Processing time: < 5 seconds/batch"
   - "Total processed: Y million records"

---

## 🔗 QUICK ACCESS LINKS

```bash
# Kafka UI
http://localhost:8080/kafka/     # Via proxy (cần login)
http://localhost:8081            # Direct (cần login)

# Spark UI  
http://localhost:8080/spark/     # Via proxy (cần login)
http://localhost:4041            # Direct (không cần login)

# Dashboard
http://localhost:8501            # Không cần login
```

---

## 📝 NOTES

- **Kafka UI:** Cần login (admin / password từ .env)
- **Spark UI:** Direct access không cần login, nhưng qua proxy cần login
- **Consumer Groups:** Không có trong Kafka UI vì Spark không dùng consumer groups
- **Lag:** Kiểm tra bằng script `calculate_lag.sh`, không qua Kafka UI

---

**Chúc bạn báo cáo thành công! 🎉**

