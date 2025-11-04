# 🚀 Quick Start Guide

Hướng dẫn nhanh để khởi động Vietnam Stock Big Data Pipeline.

## 📋 Prerequisites

- Docker & Docker Compose đã cài đặt
- RAM: Tối thiểu 8GB
- Disk: 50GB+ free space
- Internet connection

## ⚡ 3 Bước Khởi Động

### Bước 1: Clone và Di Chuyển

```bash
cd /u01/Vanh_projects/vietnam-stock-pipeline
```

### Bước 2: Khởi Động Services

```bash
docker-compose -f docker-compose-timescaledb.yml up -d
```

### Bước 3: Kiểm Tra Trạng Thái

```bash
docker-compose -f docker-compose-timescaledb.yml ps
```

Đợi tất cả services chuyển sang trạng thái `healthy` (khoảng 1-2 phút).

## 🌐 Truy Cập Dashboard

Mở browser và truy cập:

- **Dashboard**: http://localhost:8501
- **UI Proxy** (Spark UI + Kafka UI): http://localhost:8080
  - Username: `admin`
  - Password: `<password>`

## 📊 Kiểm Tra Dữ Liệu

### Xem Logs Producer

```bash
docker logs real-data-producer-vn30 --tail 50
```

Bạn sẽ thấy:
```
📊 Collecting REAL-TIME quotes for 200 stocks...
✅ Cycle completed: 125 success, 5 no_data, 0 errors
```

### Kiểm Tra Database

```bash
docker exec vietnam-stock-timescaledb psql -U stock_app -d stock_db -c "SELECT COUNT(*) FROM realtime_quotes;"
```

### Kiểm Tra Kafka

Qua Kafka UI: http://localhost:8080/kafka/ (login: admin / <password>)

## 🛠️ Quản Lý Services

### Xem Logs

```bash
# Tất cả services
docker-compose -f docker-compose-timescaledb.yml logs -f

# Service cụ thể
docker-compose -f docker-compose-timescaledb.yml logs -f dashboard
docker-compose -f docker-compose-timescaledb.yml logs -f real-data-producer
docker-compose -f docker-compose-timescaledb.yml logs -f spark-consumer
```

### Restart Service

```bash
docker-compose -f docker-compose-timescaledb.yml restart [service-name]
```

### Stop Tất Cả

```bash
docker-compose -f docker-compose-timescaledb.yml stop
```

### Start Lại

```bash
docker-compose -f docker-compose-timescaledb.yml start
```

## 🔍 Monitoring

### Resource Usage

```bash
docker stats
```

### Service Health

```bash
docker-compose -f docker-compose-timescaledb.yml ps
```

### Kafka Topics

```bash
docker exec vietnam-stock-kafka kafka-topics --bootstrap-server localhost:9092 --list
```

### Database Queries

```bash
# Kết nối database
docker exec -it vietnam-stock-timescaledb psql -U stock_app -d stock_db

# Ví dụ queries
SELECT COUNT(*) FROM realtime_quotes;
SELECT DISTINCT ticker FROM realtime_quotes ORDER BY ticker;
SELECT ticker, MAX(time) FROM realtime_quotes GROUP BY ticker;
```

## 🚨 Troubleshooting

### Service không start

```bash
# Xem logs lỗi
docker-compose -f docker-compose-timescaledb.yml logs [service-name]

# Kiểm tra resource
docker stats
```

### Không có dữ liệu

1. Kiểm tra producer: `docker logs real-data-producer-vn30`
2. Kiểm tra Kafka: Qua Kafka UI
3. Kiểm tra Spark: Qua Spark UI
4. Kiểm tra database: SQL queries

### Dashboard không load

1. Kiểm tra database connection
2. Xem logs: `docker logs vietnam-stock-dashboard`
3. Restart: `docker-compose -f docker-compose-timescaledb.yml restart dashboard`

## 📚 Tài Liệu Thêm

- **README.md**: Tài liệu đầy đủ
- **ACCOUNTS_PASSWORDS.md**: Credentials và connection strings

## 💡 Tips

- **Đợi 1-2 phút** sau khi start để tất cả services ready
- **Kiểm tra logs** nếu có vấn đề
- **Monitor resource usage** với `docker stats`
- **Backup database** định kỳ nếu cần

---

**🎉 Chúc bạn sử dụng thành công!**

