# 🚀 HƯỚNG DẪN SỬ DỤNG VIETNAM STOCK PIPELINE

## 📋 Tổng quan
Hệ thống pipeline chứng khoán Việt Nam với đầy đủ tính năng real-time, big data và tích hợp Snowflake.

## 🛠️ Cài đặt nhanh

### 1. Kiểm tra yêu cầu hệ thống
```bash
# Kiểm tra Docker
docker --version
docker-compose --version

# Kiểm tra Python (nếu cần)
python3 --version
```

### 2. Khởi động hệ thống
```bash
# Cách 1: Sử dụng script tiếng Việt (Khuyến nghị)
./quan_ly_he_thong.sh

# Cách 2: Sử dụng lệnh nhanh
./lenh_nhanh.sh start

# Cách 3: Sử dụng Makefile
make up
```

## 🎯 Các lệnh cơ bản

### Script quản lý đầy đủ (quan_ly_he_thong.sh)
```bash
./quan_ly_he_thong.sh
```
**Tính năng:**
- ✅ Menu tương tác tiếng Việt
- ✅ Khởi động/dừng hệ thống
- ✅ Kiểm tra trạng thái chi tiết
- ✅ Xem logs từng service
- ✅ Backup/restore dữ liệu
- ✅ Quản lý Big Data
- ✅ Tích hợp Snowflake
- ✅ Cài đặt Production

### Script lệnh nhanh (lenh_nhanh.sh)
```bash
# Khởi động
./lenh_nhanh.sh start

# Dừng
./lenh_nhanh.sh stop

# Khởi động lại
./lenh_nhanh.sh restart

# Xem trạng thái
./lenh_nhanh.sh status

# Xem logs
./lenh_nhanh.sh logs

# Backup dữ liệu
./lenh_nhanh.sh backup

# Mở Dashboard
./lenh_nhanh.sh dashboard

# Dọn dẹp (XÓA TẤT CẢ DỮ LIỆU!)
./lenh_nhanh.sh clean
```

## 🌐 Giao diện Web

| Service | URL | Mô tả |
|---------|-----|-------|
| 📊 **Dashboard** | http://localhost:8501 | Giao diện chính xem dữ liệu chứng khoán |
| 🗄️ **pgAdmin** | http://localhost:5050 | Quản lý database PostgreSQL |
| ⚡ **Spark Master** | http://localhost:8080 | Giao diện Spark Master |
| ⚡ **Spark Worker** | http://localhost:8081 | Giao diện Spark Worker |

## 📊 Các lệnh Makefile hữu ích

```bash
# Development
make up              # Khởi động tất cả services
make down            # Dừng tất cả services
make restart         # Khởi động lại
make logs            # Xem logs
make status          # Kiểm tra trạng thái

# Production
make prod-setup      # Cài đặt production
make prod-start      # Khởi động production
make prod-stop       # Dừng production
make prod-status     # Kiểm tra trạng thái production

# Database
make postgres-shell  # Mở shell PostgreSQL
make postgres-count  # Đếm số records
make postgres-stats  # Thống kê database

# Big Data
make fetch-data      # Tải tất cả dữ liệu từ vnstock
make sync-snowflake  # Đồng bộ lên Snowflake
make big-data-setup  # Thiết lập hoàn chỉnh Big Data

# Backup
make backup          # Backup database
make backup-volumes  # Backup volumes
```

## 🔧 Cấu hình

### Environment Variables
Tạo file `.env` trong thư mục gốc:
```bash
# Database
POSTGRES_DB=stock_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC=stock-quotes

# Snowflake (tùy chọn)
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=STOCKS
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

## 🚀 Production Setup

### 1. Cài đặt Production cơ bản
```bash
./quan_ly_he_thong.sh
# Chọn 12 -> 1
```

### 2. Cài đặt Production với Snowflake
```bash
./quan_ly_he_thong.sh
# Chọn 12 -> 2
```

### 3. Quản lý Production
```bash
# Khởi động
sudo systemctl start vietnam-stock-pipeline

# Dừng
sudo systemctl stop vietnam-stock-pipeline

# Xem logs
sudo journalctl -u vietnam-stock-pipeline -f

# Kiểm tra trạng thái
sudo systemctl status vietnam-stock-pipeline
```

## 📈 Big Data Pipeline

### 1. Tải tất cả dữ liệu
```bash
# Sử dụng script
./quan_ly_he_thong.sh
# Chọn 10 -> 1

# Hoặc dùng Makefile
make fetch-data
```

### 2. Đồng bộ lên Snowflake
```bash
# Sử dụng script
./quan_ly_he_thong.sh
# Chọn 11 -> 2

# Hoặc dùng Makefile
make sync-snowflake
```

### 3. Thiết lập hoàn chỉnh
```bash
make big-data-setup
```

## 🔍 Troubleshooting

### 1. Kiểm tra trạng thái
```bash
# Xem containers
docker-compose ps

# Xem logs
docker-compose logs [service_name]

# Kiểm tra ports
netstat -tlnp | grep -E ':(2181|5432|8080|8081|8501|5050|9092)'
```

### 2. Lỗi thường gặp

**Docker không chạy:**
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

**Port bị chiếm:**
```bash
# Tìm process đang dùng port
sudo lsof -i :8501
# Kill process
sudo kill -9 [PID]
```

**Database connection error:**
```bash
# Kiểm tra PostgreSQL
docker exec postgres pg_isready -U admin -d stock_db
```

### 3. Reset hoàn toàn
```bash
# Dừng và xóa tất cả
docker-compose down -v
docker system prune -f

# Khởi động lại
docker-compose up -d
```

## 📞 Hỗ trợ

### Logs quan trọng
- **Producer logs:** `docker-compose logs -f producer`
- **Consumer logs:** `docker-compose logs -f consumer`
- **Dashboard logs:** `docker-compose logs -f dashboard`
- **Database logs:** `docker-compose logs -f postgres`

### Kiểm tra dữ liệu
```bash
# Đếm records
make postgres-count

# Thống kê
make postgres-stats

# Xem top tickers
make postgres-tickers
```

## 🎯 Workflow khuyến nghị

### Development
1. `./quan_ly_he_thong.sh` → Chọn 1 (Khởi động Development)
2. Mở http://localhost:8501 để xem Dashboard
3. Sử dụng lệnh 5 để kiểm tra trạng thái

### Production
1. `./quan_ly_he_thong.sh` → Chọn 12 (Cài đặt Production)
2. Cấu hình systemd service
3. Sử dụng `make prod-start/stop` để quản lý

### Big Data
1. `./quan_ly_he_thong.sh` → Chọn 10 (Big Data)
2. Tải dữ liệu từ vnstock
3. Đồng bộ lên Snowflake (nếu cần)

---

## 🏆 Kết luận

Hệ thống Vietnam Stock Pipeline cung cấp:
- ✅ **Real-time data processing** với Kafka + PostgreSQL
- ✅ **Big Data capabilities** với Spark
- ✅ **Modern dashboard** với Streamlit
- ✅ **Cloud integration** với Snowflake
- ✅ **Production-ready** với systemd
- ✅ **Easy management** với scripts tiếng Việt

**Chúc bạn sử dụng thành công! 🚀**
