# 🔌 Giải Thích Ports trong Vietnam Stock Pipeline

## 📊 Tổng Quan

Dự án sử dụng **9 ports** cho các services khác nhau. Tất cả đều bind to `127.0.0.1` (localhost only) để bảo mật.

---

## 🎯 Các Ports Chính (Bạn Sẽ Dùng)

| Port | Service | URL | Mô Tả |
|------|---------|-----|-------|
| **8501** | Dashboard | http://localhost:8501 | ⭐ **CHÍNH** - Streamlit UI để xem stock data |
| **5050** | pgAdmin | http://localhost:5050 | Quản lý PostgreSQL database |
| **5432** | PostgreSQL | `localhost:5432` | Kết nối database |

### Cách Dùng:

```bash
# Dashboard - xem stock data real-time
http://localhost:8501

# pgAdmin - quản lý database
http://localhost:5050
Login: admin@example.com / admin

# PostgreSQL - connect từ code/tools
psql -h localhost -p 5432 -U admin -d stock_db
```

---

## ⚙️ Các Ports Nội Bộ (Không Cần Quan Tâm)

| Port | Service | Purpose |
|------|---------|---------|
| 2181 | Zookeeper | Kafka coordination |
| 9092 | Kafka | Message broker (internal) |
| 9093 | Kafka | Host connection |

**Lý do:** Các services này giao tiếp với nhau qua Docker network. Ports chỉ map để debug/monitor.

---

## 🔧 Các Ports Optional (Có Thể Tắt)

| Port | Service | Khi Nào Cần | Có Thể Tắt? |
|------|---------|-------------|--------------|
| 8080 | Spark Master UI | Monitor Spark cluster | ✅ Yes (không dùng Spark) |
| 7077 | Spark Master | Spark cluster port | ✅ Yes |
| 8081 | Spark Worker UI | Monitor Spark worker | ✅ Yes |

**Lưu ý:** Hiện tại dự án dùng **Consumer** thay vì Spark, nên có thể disable Spark services.

---

## 🔒 Bảo Mật

### Tất Cả Ports Đều Secure

```yaml
# Ví dụ trong docker-compose.yml
ports:
  - "127.0.0.1:8501:8501"  # ← Bind to localhost only!
```

**Ý nghĩa:**
- ✅ Chỉ truy cập được từ server (localhost)
- ✅ KHÔNG expose ra internet
- ✅ An toàn trước attacks từ bên ngoài

### Truy Cập Từ Xa (Remote Access)

Dùng SSH tunnel:

```bash
# Trên máy của bạn (laptop/desktop)
ssh -L 8501:localhost:8501 -L 5050:localhost:5050 user@server-ip

# Sau đó mở browser:
http://localhost:8501  # Dashboard
http://localhost:5050  # pgAdmin
```

---

## 💡 Tối Ưu Hóa (Giảm Ports)

### Option 1: Minimal Setup (Chỉ 3 Ports)

Disable Spark và pgAdmin:

```yaml
# docker-compose.yml
# Comment out these services:
# - spark-master
# - spark-worker  
# - pgadmin
```

**Kết quả:** Chỉ còn 6 ports (2181, 9092, 9093, 5432, 8501)

### Option 2: Ultra Minimal (Chỉ 1 Port User-Facing)

Chỉ expose Dashboard:

```yaml
# Chỉ giữ:
# - 8501 (Dashboard)
# Các ports khác để internal (không map ra ngoài)
```

**Kết quả:** User chỉ thấy 1 port: 8501

---

## 🏗️ Tại Sao Cần Nhiều Ports?

### Kiến Trúc Microservices

```
Producer → Kafka (9092) → Consumer → PostgreSQL (5432)
                                          ↓
                                    Dashboard (8501)
```

Mỗi service là container riêng biệt, cần port riêng để:
- Giao tiếp với nhau
- Expose services ra ngoài (nếu cần)
- Monitor/debug

### So Sánh

**Monolithic (1 port):**
```
All-in-One App (port 8000)
```

**Microservices (nhiều ports):**
```
Service 1 (port 8501)
Service 2 (port 9092)
Service 3 (port 5432)
...
```

**Lợi ích:**
- ✅ Scalability (scale từng service riêng)
- ✅ Isolation (lỗi 1 service không crash tất cả)
- ✅ Maintainability (update từng service độc lập)

---

## 📝 Port Mapping Explained

### Format: `HOST:CONTAINER`

```yaml
ports:
  - "127.0.0.1:8501:8501"
    ↓          ↓     ↓
   localhost  host  container
               port  port
```

**Ví dụ:**
- Container chạy service trên port 8501
- Map ra host port 8501
- Bind to 127.0.0.1 (localhost only)

---

## 🎯 Khuyến Nghị

### 1. Giữ Nguyên (Khuyến Nghị)

**Lý do:**
- ✅ Đã secure (localhost only)
- ✅ Không ảnh hưởng performance
- ✅ Linh hoạt (có thể dùng bất cứ service nào)
- ✅ Dễ debug/monitor

### 2. Minimal Setup

Nếu muốn đơn giản hóa:

```bash
# Edit docker-compose.yml
# Comment out:
# - spark-master (ports 7077, 8080)
# - spark-worker (port 8081)
# - pgadmin (port 5050)

# Restart
docker-compose down
docker-compose up -d
```

**Kết quả:** 6 ports thay vì 9

### 3. Production Recommendation

**Giữ:**
- 8501 (Dashboard) - Cần thiết
- 5432 (PostgreSQL) - Nếu cần connect từ tools
- 5050 (pgAdmin) - Tiện quản lý DB

**Có thể tắt:**
- 8080, 7077, 8081 (Spark) - Không dùng

---

## 🔍 Check Ports Hiện Tại

```bash
# Xem các ports đang listen
netstat -tuln | grep LISTEN

# Hoặc
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

---

## 📌 Tóm Tắt

| Câu Hỏi | Trả Lời |
|---------|---------|
| **Có nhiều ports quá không?** | Bình thường cho microservices architecture |
| **Có an toàn không?** | ✅ Yes - tất cả localhost only |
| **Có thể giảm không?** | ✅ Yes - disable Spark services |
| **Nên giảm không?** | Không cần thiết - không ảnh hưởng gì |
| **Port nào quan trọng nhất?** | 8501 (Dashboard) |

---

## 🆘 Troubleshooting

### Port Already in Use

```bash
# Check what's using port
lsof -i :8501

# Kill process
kill -9 <PID>

# Or restart Docker
docker-compose restart
```

### Can't Access Dashboard

```bash
# Check if port is listening
netstat -tuln | grep 8501

# Check Docker logs
docker logs stock-dashboard

# Restart dashboard
docker-compose restart dashboard
```

---

**💡 Kết luận:** Nhiều ports là bình thường và an toàn. Không cần lo lắng!

