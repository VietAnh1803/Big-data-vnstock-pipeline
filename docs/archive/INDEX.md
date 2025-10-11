# 📚 Vietnam Stock Pipeline - Documentation Index

Chào mừng đến với dự án Vietnam Stock Market Real-time Pipeline!

## 🎯 Bắt đầu nhanh

**Mới bắt đầu?** → Đọc [START_HERE.txt](START_HERE.txt) để bắt đầu ngay!

**Quick Start (5 phút)** → Xem [QUICKSTART.md](QUICKSTART.md)

## 📖 Tài liệu chính

### 🚀 Getting Started

- **[START_HERE.txt](START_HERE.txt)** - Điểm bắt đầu, hướng dẫn từng bước
- **[QUICKSTART.md](QUICKSTART.md)** - Hướng dẫn khởi động nhanh 5 phút
- **[README.md](README.md)** - Tài liệu chính, đầy đủ và chi tiết

### 📋 Setup & Configuration

- **[docs/SETUP_CHECKLIST.md](docs/SETUP_CHECKLIST.md)** - Checklist setup từng bước
- **[docs/SNOWFLAKE_SETUP.md](docs/SNOWFLAKE_SETUP.md)** - Hướng dẫn setup Snowflake chi tiết
- **[config/snowflake-setup-custom.sql](config/snowflake-setup-custom.sql)** - SQL script cho Snowflake

### 🏗️ Technical Documentation

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Kiến trúc hệ thống chi tiết
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Hướng dẫn deployment production
- **[docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)** - Tổng quan dự án

### 👥 Contributing

- **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)** - Hướng dẫn đóng góp cho dự án
- **[docs/CHANGELOG.md](docs/CHANGELOG.md)** - Lịch sử phiên bản

### 📄 Legal

- **[LICENSE](LICENSE)** - MIT License

## 🛠️ Công cụ hỗ trợ

### Scripts

- `scripts/check-requirements.sh` - Kiểm tra system requirements
- `scripts/setup.sh` - Validate và setup môi trường
- `scripts/check-health.sh` - Kiểm tra health của services

### Makefile Commands

```bash
make help                  # Xem tất cả commands
make check-requirements    # Check system requirements
make up                    # Khởi động hệ thống
make down                  # Dừng hệ thống
make logs                  # Xem logs
make status                # Kiểm tra trạng thái
make postgres-shell        # Truy cập PostgreSQL
make kafka-consume         # Xem Kafka messages
```

## 📊 Cấu trúc Dự án

```
vietnam-stock-pipeline/
├── 📄 Core Documentation
│   ├── START_HERE.txt          # Bắt đầu từ đây
│   ├── QUICKSTART.md           # Quick start guide
│   ├── README.md               # Main documentation
│   └── INDEX.md                # This file
│
├── 📚 docs/                    # Technical documentation
│   ├── ARCHITECTURE.md         # System architecture
│   ├── DEPLOYMENT.md           # Production deployment
│   ├── SNOWFLAKE_SETUP.md      # Snowflake setup guide
│   ├── SETUP_CHECKLIST.md      # Setup checklist
│   ├── PROJECT_SUMMARY.md      # Project overview
│   ├── CONTRIBUTING.md         # Contribution guidelines
│   └── CHANGELOG.md            # Version history
│
├── ⚙️ config/                  # Configuration files
│   └── snowflake-setup-custom.sql  # Snowflake SQL setup
│
├── 🔧 Configuration Files
│   ├── docker-compose.yml      # Docker orchestration
│   ├── .env.example            # Environment template
│   ├── .env                    # Your configuration
│   ├── .gitignore              # Git ignore rules
│   ├── Makefile                # Command shortcuts
│   └── LICENSE                 # MIT License
│
├── 🗄️ init-scripts/           # Database initialization
│   └── 01-init-db.sql          # PostgreSQL schema
│
├── 📥 producer/                # Data ingestion service
│   ├── producer.py             # Producer application
│   ├── Dockerfile              # Docker image
│   └── requirements.txt        # Python dependencies
│
├── ⚡ spark-processor/         # Stream processing service
│   ├── streaming_app.py        # Spark Streaming app
│   ├── Dockerfile              # Docker image
│   ├── download_jars.sh        # Download JAR files
│   └── requirements.txt        # Python dependencies
│
├── 📊 dashboard/               # Visualization service
│   ├── dashboard.py            # Streamlit dashboard
│   ├── Dockerfile              # Docker image
│   └── requirements.txt        # Python dependencies
│
└── 🛠️ scripts/                # Utility scripts
    ├── check-requirements.sh   # Requirements checker
    ├── setup.sh                # Setup validator
    └── check-health.sh         # Health checker
```

## 🎓 Học theo workflow

### Workflow 1: Understanding (Hiểu hệ thống)

1. Đọc [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)
2. Xem diagram trong [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
3. Đọc [README.md](README.md) để hiểu chi tiết

### Workflow 2: Quick Deploy (Deploy nhanh)

1. Làm theo [START_HERE.txt](START_HERE.txt)
2. Hoặc [QUICKSTART.md](QUICKSTART.md)
3. Kiểm tra với `scripts/check-health.sh`
4. Access dashboard tại http://localhost:8501

### Workflow 3: Production Deploy

1. Đọc [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
2. Setup Snowflake với [docs/SNOWFLAKE_SETUP.md](docs/SNOWFLAKE_SETUP.md)
3. Configure production `.env`
4. Deploy và monitor

### Workflow 4: Development (Phát triển)

1. Đọc [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
2. Clone project và setup local
3. Make changes và test
4. Submit PR

## 🔗 Links nhanh

- **Dashboard**: http://localhost:8501
- **Spark Master UI**: http://localhost:8080
- **Spark Worker UI**: http://localhost:8081

## 💡 Tips

- **Mới bắt đầu Docker?** → Chạy `make help` để xem shortcuts
- **Gặp lỗi?** → Xem phần Troubleshooting trong [README.md](README.md)
- **Muốn customize?** → Xem các file Python trong `producer/`, `spark-processor/`, `dashboard/`
- **Deploy production?** → Xem [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **Setup Snowflake?** → Xem [docs/SNOWFLAKE_SETUP.md](docs/SNOWFLAKE_SETUP.md)

## 📞 Support

- Tạo issue trên GitHub
- Đọc documentation
- Check logs: `make logs`
- Run health check: `./scripts/check-health.sh`

---

**Happy Learning & Building! 🚀**

**Version**: 1.0.0  
**Last Updated**: October 8, 2024