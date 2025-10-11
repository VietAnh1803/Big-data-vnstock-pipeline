# 🇻🇳 Vietnam Stock Pipeline

> Real-time Vietnamese Stock Market Data Pipeline with PostgreSQL & Snowflake

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)
[![Kafka](https://img.shields.io/badge/Kafka-Stream-231F20?logo=apache-kafka)](https://kafka.apache.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit)](https://streamlit.io/)

---

## 🎯 Overview

**BIG DATA Pipeline** that fetches **ALL** Vietnamese stock market data, processes in real-time, stores in PostgreSQL & Snowflake for comprehensive analytics.

**Key Features:**
- ✅ Real-time quotes (2.5M+ records from Kafka stream)
- ✅ **1,719 companies** info (name, industry, exchange...)
- ✅ **Historical prices** (OHLCV, 2 years for each ticker)
- ✅ **Financial statements** (Balance sheet, Income, Cash flow)
- ✅ **Financial ratios** (P/E, P/B, ROE, ROA, D/E...)
- ✅ PostgreSQL + Snowflake dual storage
- ✅ Interactive Streamlit dashboard
- ✅ Production-ready with auto-restart & monitoring
- ✅ **Automated weekly data fetch** via cron jobs

---

## 🚀 Quick Start

### Development Mode

```bash
# Start all services
make up

# Access dashboard
http://localhost:8501

# View logs
make logs
```

### Production Mode (24/7 Auto-run)

```bash
# Setup production (auto-start on boot, monitoring, backups)
sudo make prod-setup

# With Snowflake sync
sudo make prod-setup-snowflake

# Check status
make prod-status
```

**📖 Detailed Guide:** [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md)

---

## 🏗️ Architecture

```
┌──────────────┐
│  vnstock API │
└──────┬───────┘
       │ Fetch every 5 min
       ↓
┌──────────────┐
│   Producer   │ ← Kafka producer
└──────┬───────┘
       │
       ↓
┌──────────────┐
│    Kafka     │ ← Message queue
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   Consumer   │ ← Process & store
└──────┬───────┘
       │
       ↓
┌──────────────┐     ┌──────────────┐
│  PostgreSQL  │────→│  Snowflake   │ Sync
└──────┬───────┘     └──────────────┘
       │
       ↓
┌──────────────┐
│  Dashboard   │ ← Streamlit UI
└──────────────┘
```

---

## 📦 Components

| Component | Description | Port |
|-----------|-------------|------|
| **Producer** | Fetch data from vnstock API | - |
| **Kafka** | Message streaming | 9092 |
| **Consumer** | Process and store data | - |
| **PostgreSQL** | Real-time database | 5432 |
| **Snowflake** | Analytics database | - |
| **Dashboard** | Streamlit UI | 8501 |
| **pgAdmin** | Database management | 5050 |
| **Spark** | Stream processing | 8080 |

---

## 🛠️ Common Commands

### Development

```bash
make up                # Start all services
make down              # Stop all services
make restart           # Restart all services
make logs              # View all logs
make status            # Check status
make clean             # Clean everything
```

### Production

```bash
make prod-setup        # Setup production
make prod-status       # Check status
make prod-start        # Start services
make prod-stop         # Stop services
make prod-restart      # Restart services
make prod-logs         # View logs
make monitor           # Health check
make backup            # Backup database
```

### Database

```bash
make postgres-shell    # Open psql shell
make postgres-count    # Count records
make postgres-stats    # Show statistics
```

### Logs

```bash
make producer-logs     # Producer logs
make consumer-logs     # Consumer logs
make dashboard-logs    # Dashboard logs
make snowflake-logs    # Snowflake sync logs
```

---

## 🌐 Access Points

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| **Dashboard** | http://localhost:8501 | No auth |
| **pgAdmin** | http://localhost:5050 | admin@example.com / admin |
| **Spark UI** | http://localhost:8080 | No auth |

**Remote Access (Secure):**
```bash
ssh -L 8501:localhost:8501 -L 5050:localhost:5050 user@server-ip
```

---

## ⚙️ Configuration

Edit `.env` file:

```bash
# Producer
PRODUCER_INTERVAL=300              # Fetch every 5 minutes
STOCK_SYMBOLS=VNM,VIC,HPG          # Specific stocks (empty = all)

# Database
POSTGRES_PASSWORD=admin            # Change in production!

# Snowflake (optional)
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SYNC_INTERVAL=300                  # Sync every 5 minutes
```

---

## 📊 Data Flow

1. **Producer** fetches data from vnstock API every 5 minutes
2. **Kafka** queues the messages
3. **Consumer** reads from Kafka and writes to PostgreSQL
4. **Snowflake Sync** (optional) syncs PostgreSQL → Snowflake every 5 minutes
5. **Dashboard** displays real-time data from PostgreSQL

---

## 🔒 Security

- All services bind to `127.0.0.1` (localhost only)
- Use SSH tunnels for remote access
- Change default passwords in production
- Firewall configured to allow SSH only

---

## 📚 Documentation

| File | Description |
|------|-------------|
| **README.md** | This file - quick overview |
| **PRODUCTION_REPORT.md** | Production setup summary |
| **PRODUCTION_GUIDE.md** | Complete production guide |
| **docs/guides/** | Specific guides (pgAdmin, Security, etc.) |
| **docs/archive/** | Old documentation |

---

## 🎯 Use Cases

### Real-time Monitoring
- Live stock prices and volumes
- Price trends and charts
- Technical indicators

### Data Analytics
- Historical data analysis in Snowflake
- Machine learning models
- Business intelligence

### API Integration
- REST API from PostgreSQL
- Data feeds for trading bots
- Mobile app backends

---

## 🐛 Troubleshooting

```bash
# Services not running
make prod-status
make prod-logs

# No data
make producer-logs
make consumer-logs
make postgres-count

# Dashboard not loading
make dashboard-logs
docker-compose restart dashboard
```

**Full troubleshooting guide:** [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md)

---

## 💾 Backup & Recovery

```bash
# Backup
make backup                        # Database backup

# Restore
make prod-stop
gunzip -c backups/stock_db_*.sql.gz | \
  docker exec -i postgres psql -U admin -d stock_db
make prod-start
```

---

## 🚀 Production Deployment

**Quick Setup:**
```bash
sudo make prod-setup
```

**What it does:**
- ✅ Installs systemd service (auto-start on boot)
- ✅ Sets up cron jobs (monitoring every 5 min)
- ✅ Configures auto-restart on failure
- ✅ Sets up daily backups

---

## 📊 BIG DATA Features

### Fetch ALL Data from vnstock

```bash
# Fetch all company info, financials, historical prices
make fetch-data

# Check data statistics
make data-stats
make ticker-count

# Sync to Snowflake
make sync-snowflake

# Complete setup (fetch + sync)
make big-data-setup
```

### Automated Data Collection

```bash
# Setup cron jobs for weekly fetch
chmod +x scripts/setup_big_data_cron.sh
sudo ./scripts/setup_big_data_cron.sh
```

**Schedule:**
- **Sunday 2:00 AM** - Full data fetch (all tickers)
- **Daily 1:00 AM** - Update ticker info
- **Monthly** - Cleanup old Docker images

### Data Available

| Type | Count | Description |
|------|-------|-------------|
| Ticker Info | 1,719 | Company details, industry, exchange |
| Realtime Quotes | 2.5M+ | Live prices from Kafka |
| Historical Prices | Growing | 2-year OHLCV for each ticker |
| Balance Sheet | Ready | Quarterly financial data |
| Income Statement | Ready | Revenue, profit, EPS |
| Cash Flow | Ready | Operating, investing, financing |
| Financial Ratios | Ready | P/E, P/B, ROE, ROA, D/E |

**Full guide:** [BIG_DATA_GUIDE.md](BIG_DATA_GUIDE.md)
- ✅ Configures weekly maintenance

**Learn more:** [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md)

---

## 📁 Project Structure

```
vietnam-stock-pipeline/
├── producer/              # Data producer
├── dashboard/             # Streamlit UI
├── scripts/               # Utility scripts & consumer
├── systemd/               # Systemd services
├── docs/                  # Documentation
│   ├── guides/            # Specific guides
│   └── archive/           # Old docs
├── docker-compose.yml     # Docker orchestration
├── Makefile               # All commands
├── .env                   # Configuration
├── README.md              # This file
├── PRODUCTION_REPORT.md   # Production summary
└── PRODUCTION_GUIDE.md    # Production guide
```

---

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

---

## 📄 License

See [LICENSE](LICENSE) file for details.

---

## 🆘 Support

- **Quick Reference:** `cat PRODUCTION_REPORT.md`
- **Full Guide:** `cat PRODUCTION_GUIDE.md`
- **Commands:** `make help`
- **Status:** `make prod-status`

---

<div align="center">

**Made with ❤️ for Vietnamese Stock Market**

[Production Guide](PRODUCTION_GUIDE.md) • [Production Report](PRODUCTION_REPORT.md)

</div>
