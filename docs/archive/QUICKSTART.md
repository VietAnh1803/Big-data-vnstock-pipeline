# 🚀 Quick Start Guide

Hướng dẫn nhanh để chạy hệ thống trong vòng 5 phút!

## Yêu cầu

- Docker và Docker Compose đã được cài đặt
- Ít nhất 8GB RAM
- Kết nối internet

## Các bước thực hiện

### 1️⃣ Clone project

```bash
git clone <your-repo-url>
cd vietnam-stock-pipeline
```

### 2️⃣ Cấu hình môi trường

```bash
# Copy file cấu hình mẫu
cp .env.example .env

# (Optional) Chỉnh sửa mật khẩu PostgreSQL
nano .env
```

**Lưu ý**: Bạn có thể giữ nguyên cấu hình mặc định để test nhanh.

### 3️⃣ Chạy hệ thống

```bash
# Khởi động tất cả services
docker-compose up -d --build
```

⏱️ **Lần đầu tiên sẽ mất 5-10 phút** để download images và build.

### 4️⃣ Kiểm tra trạng thái

```bash
# Xem trạng thái các services
docker-compose ps

# Xem logs
docker-compose logs -f
```

### 5️⃣ Truy cập Dashboard

Đợi khoảng **2-3 phút** để hệ thống khởi động hoàn tất, sau đó mở trình duyệt:

🔗 **http://localhost:8501**

## Lệnh hữu ích

```bash
# Dừng hệ thống
docker-compose down

# Xem logs của producer
docker-compose logs -f producer

# Xem logs của spark processor
docker-compose logs -f spark-processor

# Kiểm tra dữ liệu trong PostgreSQL
docker exec -it postgres psql -U admin -d stock_db -c "SELECT COUNT(*) FROM realtime_quotes;"

# Kiểm tra Kafka topics
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```

## Sử dụng Makefile (Optional)

Nếu hệ thống của bạn có `make`, bạn có thể dùng các lệnh ngắn gọn:

```bash
make help           # Xem tất cả lệnh có sẵn
make up             # Khởi động
make down           # Dừng
make logs           # Xem logs
make status         # Kiểm tra trạng thái
make dashboard-ui   # Mở dashboard
```

## Troubleshooting

### Dashboard không hiển thị dữ liệu?

1. Đợi thêm 1-2 phút (hệ thống cần thời gian khởi động)
2. Kiểm tra logs: `docker-compose logs producer spark-processor`
3. Kiểm tra dữ liệu: `make postgres-count` hoặc `docker exec -it postgres psql -U admin -d stock_db -c "SELECT COUNT(*) FROM realtime_quotes;"`

### Port bị xung đột?

Thay đổi port trong `docker-compose.yml`:
```yaml
dashboard:
  ports:
    - "8502:8501"  # Đổi từ 8501 sang 8502
```

### Out of memory?

Giảm số worker hoặc tăng RAM cho Docker trong Docker Desktop settings.

## Next Steps

- Đọc [README.md](README.md) để hiểu chi tiết về kiến trúc
- Thêm mã cổ phiếu trong `producer/producer.py`
- Cấu hình Snowflake để lưu trữ lâu dài (optional)
- Customize dashboard trong `dashboard/dashboard.py`

## Dừng hệ thống

```bash
# Dừng và giữ lại dữ liệu
docker-compose down

# Dừng và xóa tất cả dữ liệu
docker-compose down -v
```

---

**Chúc bạn thành công! 🎉**

