# 📈 Vietnam Stock Pipeline

Hệ thống Big Data Analytics cho thị trường chứng khoán Việt Nam với real-time processing và comprehensive data coverage.

## 🚀 **Quick Start**

### 1. Cài đặt dependencies:
```bash
# Install all dependencies (includes installation guide for Linux/Windows)
pip install -r requirements.txt
```

### 2. Khởi động hệ thống:
```bash
make up
# hoặc
./manage.sh start
```

### 3. Truy cập dashboard:
- **Dashboard**: http://localhost:8501
- **pgAdmin**: http://localhost:5050

### 4. Fetch dữ liệu comprehensive:
```bash
make fetch-comprehensive
```

### 5. Sync với Snowflake:
```bash
make sync-data
```

## 📊 **Dữ liệu hiện có**

- **668,320** historical prices (2023-2025)
- **95,800** technical analytics
- **1,720** ticker information
- **2,366,998** realtime quotes (Snowflake 2017-2025)

## 🛠️ **Các lệnh chính**

### Hệ thống:
```bash
make up                    # Khởi động tất cả services
make down                  # Dừng tất cả services
make restart               # Restart hệ thống
make status                # Kiểm tra trạng thái
make logs                  # Xem logs
make clean                 # Dọn dẹp hệ thống
```

### Dữ liệu:
```bash
make fetch-comprehensive   # Fetch toàn bộ dữ liệu vnstock
make sync-data            # Sync PostgreSQL ↔ Snowflake
make fetch-historical-2017 # Fetch dữ liệu từ 2017
```


### Backup/Restore:
```bash
make backup               # Backup database
make restore              # Restore database
```

### Monitoring:
```bash
make health               # Kiểm tra sức khỏe hệ thống
make monitor              # Monitor system
```

## 🎛️ **Quản lý tương tác**

```bash
./manage.sh
```

Script này cung cấp menu tương tác để:
- Khởi động/dừng hệ thống
- Fetch dữ liệu
- Backup/restore database
- Kiểm tra sức khỏe hệ thống
- Xem logs và trạng thái

## 🏗️ **Kiến trúc**

```
[VNStock] → [Kafka] → [Spark] → [PostgreSQL] → [Dashboard]
                              ↘ [Snowflake]
```

## 📋 **Tính năng**

- ✅ Real-time streaming với Kafka
- ✅ Distributed processing với Spark  
- ✅ Technical indicators (SMA, EMA, MACD, RSI, Bollinger)
- ✅ Market analysis và sentiment
- ✅ Smart sync tránh duplicate
- ✅ Production-ready infrastructure

## 🔧 **Troubleshooting**

### Kiểm tra trạng thái:
```bash
make status
make health
```

### Xem logs:
```bash
make logs
```

### Dọn dẹp:
```bash
make clean
```

### Restart services:
```bash
make restart
```

## 📁 **Cấu trúc thư mục**

```
vietnam-stock-pipeline/
├── 📄 README.md                    # Hướng dẫn này
├── 📄 QUICK_INSTALL.md             # Hướng dẫn cài đặt nhanh (Linux/Windows)
├── 📄 INSTALL.md                   # Hướng dẫn cài đặt chi tiết
├── 📄 manage.sh                    # Script quản lý tương tác
├── 📄 Makefile                     # Makefile commands
├── 📄 docker-compose.yml           # Docker compose
├── 📄 requirements.txt             # Dependencies đầy đủ + hướng dẫn cài đặt
├── 📁 dashboard/                   # Streamlit dashboard
├── 📁 etl/                         # ETL scripts và Dockerfiles
│   ├── vnstock_server_fetcher.py   # VNStock data fetcher
│   ├── sync_postgres_snowflake.py  # PostgreSQL ↔ Snowflake sync
│   ├── vnstock_manager.sh          # VNStock fetcher manager
│   └── *.py, *.sh, Dockerfile.*    # Các script ETL khác
├── 📁 data/                        # Database dumps
├── 📁 config/                      # Configuration files
└── 📁 logs/                        # Log files
```

## 🚀 **Production Deployment**

### 1. Khởi động production:
```bash
make prod
```

### 2. Kiểm tra sức khỏe:
```bash
make health
```

### 3. Monitor system:
```bash
make monitor
```

## 📞 **Hỗ trợ**

- **Dashboard**: http://localhost:8501
- **pgAdmin**: http://localhost:5050
- **Logs**: `make logs`
- **Status**: `make status`
- **Quick Install**: Xem `QUICK_INSTALL.md` để cài đặt nhanh
- **Full Install**: Xem `INSTALL.md` để biết chi tiết cài đặt

---
**📅 Cập nhật:** 11/10/2025  
**🔄 Trạng thái:** Production Ready  
**🎯 Mục tiêu:** Comprehensive Vietnam Stock Market Analytics Platform