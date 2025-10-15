# 🐘 PostgreSQL Connection Guide

## 🚨 **VẤN ĐỀ HIỆN TẠI**
Bạn không thể kết nối vào PostgreSQL từ localhost vì **thiếu PostgreSQL client** trên host system.

---

## ✅ **TÌNH TRẠNG HỆ THỐNG**

### **PostgreSQL Container:**
- **Trạng thái:** ✅ Đang chạy
- **Port:** ✅ 5432 đã được map
- **Database:** ✅ stock_db
- **User:** ✅ admin
- **Password:** ✅ admin

### **Vấn đề:**
- **psql client:** ❌ Chưa cài đặt trên host
- **Kết nối trực tiếp:** ❌ Không thể

---

## 🔧 **CÁC CÁCH KẾT NỐI**

### **1. Sử dụng Docker Exec (Khuyến nghị)**
```bash
# Kết nối trực tiếp vào container
docker exec -it postgres psql -U admin -d stock_db

# Chạy lệnh SQL
docker exec postgres psql -U admin -d stock_db -c "SELECT COUNT(*) FROM realtime_quotes;"
```

### **2. Sử dụng pgAdmin (Web Interface)**
```bash
# Truy cập pgAdmin
http://localhost:5050

# Thông tin kết nối:
# Host: postgres
# Port: 5432
# Database: stock_db
# Username: admin
# Password: admin
```

### **3. Cài đặt PostgreSQL Client**
```bash
# Trên CentOS/RHEL/Oracle Linux
sudo yum install -y postgresql15

# Sau khi cài đặt, có thể dùng:
psql -h localhost -p 5432 -U admin -d stock_db
```

### **4. Sử dụng Script Helper**
```bash
# Chạy script quản lý kết nối
./connect_postgres.sh

# Chọn option 2: Connect via Docker exec
```

---

## 🛠️ **CÁC LỆNH HỮU ÍCH**

### **Kiểm tra trạng thái:**
```bash
# Kiểm tra container
docker ps | grep postgres

# Kiểm tra port
netstat -tlnp | grep 5432

# Kiểm tra logs
docker logs postgres
```

### **Kết nối và truy vấn:**
```bash
# Kết nối vào database
docker exec -it postgres psql -U admin -d stock_db

# Liệt kê databases
docker exec postgres psql -U admin -l

# Liệt kê tables
docker exec postgres psql -U admin -d stock_db -c "\dt"

# Đếm records
docker exec postgres psql -U admin -d stock_db -c "SELECT COUNT(*) FROM realtime_quotes;"
```

### **Backup/Restore:**
```bash
# Backup database
docker exec postgres pg_dump -U admin stock_db > backup_$(date +%Y%m%d).sql

# Restore database
docker exec -i postgres psql -U admin stock_db < backup_file.sql
```

---

## 🌐 **WEB INTERFACES**

### **1. pgAdmin (Database Management)**
- **URL:** http://localhost:5050
- **Chức năng:** Quản lý database, chạy SQL, xem dữ liệu
- **Kết nối:** postgres:5432, admin/admin

### **2. Stock Dashboard (Analytics)**
- **URL:** http://localhost:8501
- **Chức năng:** Dashboard phân tích chứng khoán
- **Dữ liệu:** Từ PostgreSQL

---

## 🚀 **GIẢI PHÁP NHANH**

### **Để kết nối ngay lập tức:**
```bash
# Cách 1: Docker exec
docker exec -it postgres psql -U admin -d stock_db

# Cách 2: pgAdmin web
# Mở browser: http://localhost:5050
# Đăng nhập và tạo connection mới

# Cách 3: Script helper
./connect_postgres.sh
# Chọn option 2
```

### **Để cài đặt PostgreSQL client:**
```bash
# Cài đặt client
sudo yum install -y postgresql15

# Sau đó có thể dùng:
psql -h localhost -p 5432 -U admin -d stock_db
```

---

## 📊 **THÔNG TIN DATABASE**

### **Kích thước:**
- **Database:** stock_db
- **Tables:** realtime_quotes, historical_prices, ticker_info, etc.
- **Records:** 668,740+ historical records

### **Connection String:**
```
postgresql://admin:admin@localhost:5432/stock_db
```

---

## 🎯 **KHUYẾN NGHỊ**

### **Cho sử dụng hàng ngày:**
1. **Sử dụng pgAdmin** (http://localhost:5050) - Dễ sử dụng nhất
2. **Sử dụng Docker exec** - Nhanh nhất cho command line

### **Cho development:**
1. **Cài đặt PostgreSQL client** - Linh hoạt nhất
2. **Sử dụng connection string** - Tích hợp với applications

### **Cho backup:**
1. **Sử dụng pg_dump** qua Docker exec
2. **Schedule backup** tự động

---

## 🔍 **TROUBLESHOOTING**

### **Nếu không kết nối được:**
1. Kiểm tra container: `docker ps | grep postgres`
2. Kiểm tra port: `netstat -tlnp | grep 5432`
3. Kiểm tra logs: `docker logs postgres`
4. Restart container: `docker restart postgres`

### **Nếu lỗi authentication:**
1. Kiểm tra password: `admin`
2. Kiểm tra user: `admin`
3. Kiểm tra database: `stock_db`

---

## 📞 **HỖ TRỢ**

Nếu cần hỗ trợ:
1. Chạy `./connect_postgres.sh` để kiểm tra
2. Xem logs: `docker logs postgres`
3. Kiểm tra status: `./manage.sh status`

**Lưu ý:** PostgreSQL đang chạy tốt, chỉ cần sử dụng đúng cách kết nối!
