# 🚀 Vietnam Stock Pipeline - Production Setup Report

> **Hệ thống tự động chạy 24/7, update dữ liệu liên tục vào PostgreSQL và Snowflake**

---

## ✅ Tổng Quan

Toàn bộ infrastructure để chạy pipeline **tự động, liên tục, production-ready** đã được thiết lập.

### 📦 Files Đã Tạo

```
vietnam-stock-pipeline/
├── setup_production.sh                    # Main setup script
├── demo_production.sh                     # Interactive demo
│
├── systemd/                               # Auto-start on boot
│   ├── vietnam-stock-pipeline.service
│   └── vietnam-stock-pipeline-with-snowflake.service
│
├── scripts/                               # Management & monitoring
│   ├── monitor_services.sh                # Health check + auto-restart
│   ├── healthcheck.sh                     # Quick health check
│   ├── check_status.sh                    # Status dashboard
│   ├── setup_cron.sh                      # Cron jobs setup
│   ├── start_all.sh                       # Start services
│   ├── stop_all.sh                        # Stop services
│   └── uninstall_production.sh            # Uninstall
│
├── Makefile                               # Production commands
├── PRODUCTION_GUIDE.md                    # Chi tiết đầy đủ
└── PRODUCTION_REPORT.md                   # File này
```

---

## 🚀 Quick Start (1 Lệnh)

```bash
# Cơ bản (PostgreSQL + Kafka + Dashboard)
sudo make prod-setup

# Hoặc với Snowflake sync
sudo make prod-setup-snowflake
```

**→ Xong! Hệ thống tự động chạy 24/7**

---

## 🔄 Auto-Maintenance Schedule

| Tần Suất | Task | Mô Tả |
|----------|------|-------|
| **Mỗi 5 phút** | Health Check | Kiểm tra services, auto-restart nếu down |
| **Mỗi 5 phút** | Data Fetch | Lấy dữ liệu từ vnstock API |
| **Mỗi 5 phút** | Snowflake Sync | Đồng bộ PostgreSQL → Snowflake |
| **Daily 2:00 AM** | Database Backup | Tự động backup PostgreSQL |
| **Daily 6:00 AM** | Health Report | Báo cáo sức khỏe hệ thống |
| **Daily 7:00 AM** | Disk Check | Alert nếu disk > 80% |
| **Sunday 3:00 AM** | System Restart | Restart để clear memory |
| **Monthly 4:00 AM** | Log Cleanup | Xóa logs > 30 ngày |

### 🔁 Liên Tục
- ✅ Auto-start khi server boot
- ✅ Auto-restart khi có lỗi
- ✅ Real-time data processing
- ✅ Dashboard auto-refresh

---

## 🔧 Các Lệnh Thường Dùng

### Setup & Management
```bash
sudo make prod-setup              # Setup production
sudo make prod-setup-snowflake    # Setup with Snowflake

make prod-status                  # Check status
make prod-start                   # Start services
make prod-stop                    # Stop services
make prod-restart                 # Restart services
make prod-logs                    # View logs
```

### Monitoring
```bash
make monitor                      # Full health check
make healthcheck                  # Quick check (exit code)
bash scripts/check_status.sh      # Status dashboard
```

### Database
```bash
make postgres-shell               # Open psql
make postgres-count               # Count records
make postgres-stats               # Statistics
make postgres-tickers             # Top tickers
make backup                       # Backup database
```

### View Logs
```bash
make prod-logs                    # Production logs
make producer-logs                # Producer logs
make consumer-logs                # Consumer logs
make dashboard-logs               # Dashboard logs
make snowflake-logs               # Snowflake sync logs
```

---

## 🌐 Service Access

| Service | Local | Remote (SSH Tunnel) |
|---------|-------|---------------------|
| **Dashboard** | http://localhost:8501 | `ssh -L 8501:localhost:8501 user@server` |
| **pgAdmin** | http://localhost:5050 | `ssh -L 5050:localhost:5050 user@server` |
| **Spark UI** | http://localhost:8080 | `ssh -L 8080:localhost:8080 user@server` |

**🔒 Security:** Tất cả services bind to `127.0.0.1` (localhost only)

---

## ⚙️ Configuration (.env)

```bash
# Tần suất fetch data (seconds)
PRODUCER_INTERVAL=300              # 5 phút

# Chọn stocks (empty = tất cả)
STOCK_SYMBOLS=VNM,VIC,HPG,MSN,TCB

# Snowflake sync interval
SYNC_INTERVAL=300                  # 5 phút

# Passwords (ĐỔI NGAY!)
POSTGRES_PASSWORD=admin            # ← Change this!
PGADMIN_PASSWORD=admin             # ← Change this!

# Snowflake credentials (optional)
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
```

**Sau khi edit:** `make prod-restart`

---

## 💾 Backup & Recovery

### Tự Động
- Daily 2:00 AM → `/backups/stock_db_YYYYMMDD.sql.gz`

### Thủ Công
```bash
# Backup
make backup                        # Database
make backup-volumes                # Docker volumes

# Restore
make prod-stop
gunzip -c backups/stock_db_20250108.sql.gz | \
  docker exec -i postgres psql -U admin -d stock_db
make prod-start
```

---

## 🐛 Troubleshooting Quick Reference

| Vấn Đề | Giải Pháp |
|--------|-----------|
| Service không chạy | `make prod-status` → `make prod-restart` |
| Không có dữ liệu | `make producer-logs` + `make consumer-logs` |
| Dashboard không mở | `make dashboard-logs` + `docker-compose restart dashboard` |
| Snowflake sync lỗi | `make snowflake-logs` + verify credentials |
| High memory | `make prod-restart` |

**Chi tiết:** Xem `PRODUCTION_GUIDE.md`

---

## 🏗️ Architecture

```
vnstock API (every 5 min)
    ↓
Producer (Docker container)
    ↓
Kafka (message queue)
    ↓
Consumer (batch processing)
    ↓
PostgreSQL (real-time) ──sync→ Snowflake (analytics)
    ↓
Dashboard (Streamlit, auto-refresh 3s)
```

**Monitoring:** Health check mỗi 5 phút → Auto-restart nếu down

---

## ✅ Production Checklist

### Trước Setup
- [ ] Docker & Docker Compose installed
- [ ] Xem demo: `./demo_production.sh`

### Setup
- [ ] Run: `sudo make prod-setup`
- [ ] Verify: `make prod-status` (all green)
- [ ] Test: http://localhost:8501

### Sau Setup
- [ ] Đổi passwords trong `.env`
- [ ] Configure firewall (allow SSH only)
- [ ] Setup SSH tunnel cho remote access
- [ ] Test backup: `make backup`
- [ ] Verify monitoring: `make monitor`

---

## 🔒 Security Checklist

```bash
# 1. Đổi passwords
nano .env  # Change POSTGRES_PASSWORD, PGADMIN_PASSWORD

# 2. Firewall
sudo ufw default deny incoming
sudo ufw allow ssh
sudo ufw enable

# 3. SSH tunnel only (không mở ports ra internet)
ssh -L 8501:localhost:8501 user@server-ip
```

---

## 📚 Documentation

| File | Mô Tả |
|------|-------|
| **PRODUCTION_GUIDE.md** | Hướng dẫn đầy đủ chi tiết (setup, config, troubleshooting) |
| **PRODUCTION_REPORT.md** | Báo cáo tổng hợp ngắn gọn (file này) |
| **demo_production.sh** | Interactive demo |

```bash
# Xem hướng dẫn chi tiết
cat PRODUCTION_GUIDE.md

# Xem demo
./demo_production.sh

# Help
make help
```

---

## 🎯 What Happens After Setup?

1. **Systemd service** starts và enable auto-start on boot
2. **Cron jobs** được cài đặt cho monitoring
3. **All containers** khởi động (Producer, Kafka, PostgreSQL, Dashboard, etc.)
4. **Producer** bắt đầu fetch data mỗi 5 phút
5. **Consumer** xử lý và ghi vào PostgreSQL
6. **Snowflake sync** đồng bộ mỗi 5 phút (nếu enabled)
7. **Dashboard** có sẵn tại http://localhost:8501
8. **Monitoring** tự động chạy mỗi 5 phút

**→ Không cần can thiệp thủ công!**

---

## 🎉 Summary

### ✨ Tính Năng
- ✅ Tự động chạy 24/7
- ✅ Auto-start on boot
- ✅ Auto-restart on failure
- ✅ Self-monitoring (every 5 min)
- ✅ Auto-backup (daily)
- ✅ Auto-maintenance (weekly)
- ✅ Real-time dashboard
- ✅ Dual storage (PostgreSQL + Snowflake)

### 🚀 Quick Start
```bash
sudo make prod-setup
```

### 📖 Chi Tiết
```bash
cat PRODUCTION_GUIDE.md
```

### 🔍 Status
```bash
make prod-status
```

---

**✅ Production-ready! Hệ thống sẽ tự động chạy, không cần can thiệp thủ công!** 🎉

*Xem `PRODUCTION_GUIDE.md` để biết thêm chi tiết về configuration, troubleshooting, và advanced features.*

