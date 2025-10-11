# 🚀 Vietnam Stock Pipeline - Hướng Dẫn Cho Bạn Bè

## 📋 Tổng Quan
Hệ thống pipeline chứng khoán Việt Nam với dữ liệu thực tế, dashboard real-time và tích hợp Snowflake.

## 🎯 Tính Năng
- ✅ **Real-time data processing** với Kafka + PostgreSQL
- ✅ **Interactive dashboard** với Streamlit
- ✅ **Big Data capabilities** với Spark
- ✅ **Cloud integration** với Snowflake
- ✅ **Production-ready** với systemd
- ✅ **Dữ liệu thực tế** đã được import sẵn

## 🛠️ Yêu Cầu Hệ Thống
- Docker & Docker Compose
- 4GB RAM trở lên
- 10GB disk space

## 🚀 Cài Đặt Nhanh (1 Lệnh)

```bash
# Clone repository
git clone <your-repo-url>
cd vietnam-stock-pipeline

# Setup tự động với dữ liệu
./setup_with_data.sh
```

**Script sẽ tự động:**
- Build Docker images
- Khởi động services
- Import dữ liệu thực tế (42,000+ records)
- Kiểm tra hệ thống

## 🌐 Truy Cập Giao Diện

| Service | URL | Mô Tả |
|---------|-----|-------|
| 📊 **Dashboard** | http://localhost:8501 | Giao diện chính xem dữ liệu chứng khoán |
| 🗄️ **pgAdmin** | http://localhost:5050 | Quản lý database PostgreSQL |
| ⚡ **Spark Master** | http://localhost:8080 | Giao diện Spark Master |
| ⚡ **Spark Worker** | http://localhost:8081 | Giao diện Spark Worker |

## 🎮 Cách Sử Dụng

### Script Tiếng Việt (Khuyến Nghị)
```bash
# Script đầy đủ với menu
./quan_ly_he_thong.sh

# Script lệnh nhanh
./lenh_nhanh.sh start     # Khởi động
./lenh_nhanh.sh stop      # Dừng
./lenh_nhanh.sh status    # Trạng thái
./lenh_nhanh.sh dashboard # Mở web
```

### Lệnh Docker Compose
```bash
# Khởi động
docker-compose up -d

# Dừng
docker-compose down

# Xem logs
docker-compose logs -f

# Rebuild
docker-compose build
```

## 📊 Dữ Liệu Có Sẵn

### Tickers Chính:
- **HPG** - Hòa Phát Group
- **VCB** - Vietcombank  
- **VIC** - Vingroup
- **VHM** - Vinhomes
- **MSN** - Masan Group

### Thống Kê:
- **5,160+** tickers từ 3 sàn (HSX, HNX, UPCOM)
- **500,000+** historical prices (2 năm)
- **42,000+** realtime quotes
- **Dữ liệu thực tế** từ vnstock API
- **Cập nhật real-time** mỗi 5 phút
- **Dữ liệu mới nhất** (11/10/2025)

## 🔧 Quản Lý Hệ Thống

### Kiểm Tra Trạng Thái
```bash
# Xem tất cả containers
docker-compose ps

# Kiểm tra database
docker exec postgres psql -U admin -d stock_db -c "SELECT COUNT(*) FROM realtime_quotes;"

# Xem logs
docker-compose logs -f dashboard
```

### Backup Dữ Liệu
```bash
# Backup database
./lenh_nhanh.sh backup

# Hoặc manual
docker exec postgres pg_dump -U admin stock_db > backup.sql
```

### Dọn Dẹp
```bash
# Dừng và xóa containers
docker-compose down

# Dọn dẹp hoàn toàn (XÓA TẤT CẢ DỮ LIỆU!)
docker-compose down -v
docker system prune -f
```

## 🎯 Dashboard Features

### Market Overview
- Tổng quan thị trường
- Heatmap các tickers
- Thống kê tổng hợp

### Individual Analysis
- Biểu đồ giá real-time
- Phân tích volume
- Metrics chi tiết

### Interactive Controls
- Chọn ticker
- Time range selection
- Auto-refresh

## 🚨 Troubleshooting

### Lỗi Thường Gặp

**1. Docker không chạy:**
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

**2. Port bị chiếm:**
```bash
# Tìm process
sudo lsof -i :8501
# Kill process
sudo kill -9 <PID>
```

**3. Database connection error:**
```bash
# Kiểm tra PostgreSQL
docker exec postgres pg_isready -U admin -d stock_db
```

**4. Dashboard không load:**
```bash
# Restart dashboard
docker-compose restart dashboard
# Xem logs
docker logs stock-dashboard
```

### Reset Hoàn Toàn
```bash
# Dừng tất cả
docker-compose down -v
docker system prune -f

# Setup lại
./setup_with_data.sh
```

## 📈 Mở Rộng

### Thêm Tickers Mới
1. Sửa file `producer/producer.py`
2. Thêm tickers vào `STOCK_SYMBOLS`
3. Restart producer: `docker-compose restart producer`

### Tích Hợp Snowflake
1. Tạo file `.env` với Snowflake credentials
2. Khởi động với Snowflake: `docker-compose --profile snowflake up -d`

### Production Setup
```bash
# Cài đặt production
./quan_ly_he_thong.sh
# Chọn 12 -> 1 (Production setup)
```

## 🎉 Kết Luận

Hệ thống đã được setup sẵn với:
- ✅ Dữ liệu thực tế
- ✅ Dashboard hoạt động
- ✅ Scripts quản lý tiếng Việt
- ✅ Hướng dẫn chi tiết

**Chúc bạn sử dụng thành công! 🚀**

---

## 📞 Hỗ Trợ

Nếu gặp vấn đề, hãy:
1. Kiểm tra logs: `docker-compose logs -f`
2. Chạy script kiểm tra: `./lenh_nhanh.sh status`
3. Reset hệ thống: `./setup_with_data.sh`

**Happy Trading! 📈**
