# 🚀 Production Deployment Guide - Vietnam Stock Pipeline

## Mục Lục
- [Tổng Quan](#tổng-quan)
- [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
- [Cài Đặt Tự Động](#cài-đặt-tự-động)
- [Cài Đặt Thủ Công](#cài-đặt-thủ-công)
- [Quản Lý Services](#quản-lý-services)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Recovery](#backup--recovery)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

---

## Tổng Quan

Pipeline này được thiết kế để chạy **24/7 tự động** trên server production với các tính năng:

✅ **Tự động khởi động khi server reboot** (systemd)  
✅ **Auto-restart nếu có lỗi** (Docker restart policy + systemd)  
✅ **Monitoring tự động mỗi 5 phút** (cron + health checks)  
✅ **Sync PostgreSQL → Snowflake liên tục** (nếu enabled)  
✅ **Logging đầy đủ** (systemd journal + file logs)  
✅ **Weekly maintenance** (auto-restart Sunday 3 AM)

---

## Yêu Cầu Hệ Thống

### Phần Cứng Tối Thiểu
- **CPU:** 4 cores
- **RAM:** 8 GB (khuyến nghị 16 GB)
- **Disk:** 50 GB free space
- **Network:** Stable internet connection

### Phần Mềm
- **OS:** Linux (Ubuntu 20.04+, CentOS 7+, RHEL 7+)
- **Docker:** 20.10+
- **Docker Compose:** 1.29+
- **systemd:** (có sẵn trên hầu hết Linux distros)
- **cron:** (có sẵn)

### Kiểm Tra Prerequisites

```bash
# Check Docker
docker --version

# Check Docker Compose
docker-compose --version

# Check systemd
systemctl --version

# Check cron
crontab -l
```

---

## Cài Đặt Tự Động

### Option 1: Setup Cơ Bản (PostgreSQL + Kafka + Dashboard)

```bash
cd /u01/Vanh_projects/vietnam-stock-pipeline

# Make setup script executable
chmod +x setup_production.sh

# Run setup (requires sudo)
sudo ./setup_production.sh
```

### Option 2: Setup với Snowflake Sync

```bash
# Edit .env first to add Snowflake credentials
nano .env

# Add these lines:
# SNOWFLAKE_ACCOUNT=your_account
# SNOWFLAKE_USER=your_user
# SNOWFLAKE_PASSWORD=your_password
# SNOWFLAKE_WAREHOUSE=COMPUTE_WH
# SNOWFLAKE_DATABASE=STOCKS
# SNOWFLAKE_SCHEMA=PUBLIC
# SNOWFLAKE_ROLE=ACCOUNTADMIN

# Run setup with Snowflake
sudo ./setup_production.sh --snowflake
```

### Những gì script tự động làm:

1. ✅ Kiểm tra prerequisites (Docker, systemd, etc.)
2. ✅ Tạo `.env` file nếu chưa có
3. ✅ Cài đặt systemd service
4. ✅ Enable auto-start on boot
5. ✅ Setup cron jobs cho monitoring
6. ✅ Tạo log directories
7. ✅ Start services
8. ✅ Run health check

---

## Cài Đặt Thủ Công

Nếu bạn muốn control từng bước:

### Bước 1: Cấu Hình Environment

```bash
cd /u01/Vanh_projects/vietnam-stock-pipeline

# Copy và edit .env
cp .env.example .env  # or create from template
nano .env
```

### Bước 2: Cài Đặt Systemd Service

```bash
# Copy service file
sudo cp systemd/vietnam-stock-pipeline.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start
sudo systemctl enable vietnam-stock-pipeline.service

# Start service
sudo systemctl start vietnam-stock-pipeline.service
```

### Bước 3: Setup Monitoring

```bash
# Make scripts executable
chmod +x scripts/monitor_services.sh
chmod +x scripts/healthcheck.sh
chmod +x scripts/setup_cron.sh

# Install cron jobs
sudo bash scripts/setup_cron.sh
```

### Bước 4: Verify Installation

```bash
# Check service status
sudo systemctl status vietnam-stock-pipeline

# Check containers
docker ps

# Run health check
bash scripts/healthcheck.sh

# Check logs
sudo journalctl -u vietnam-stock-pipeline -f
```

---

## Quản Lý Services

### Systemd Commands

```bash
# Start service
sudo systemctl start vietnam-stock-pipeline

# Stop service
sudo systemctl stop vietnam-stock-pipeline

# Restart service
sudo systemctl restart vietnam-stock-pipeline

# Check status
sudo systemctl status vietnam-stock-pipeline

# View logs (real-time)
sudo journalctl -u vietnam-stock-pipeline -f

# View logs (last 100 lines)
sudo journalctl -u vietnam-stock-pipeline -n 100

# View logs (since today)
sudo journalctl -u vietnam-stock-pipeline --since today
```

### Docker Compose Commands

Nếu không dùng systemd:

```bash
cd /u01/Vanh_projects/vietnam-stock-pipeline

# Start all services
docker-compose up -d

# Start with Snowflake
docker-compose --profile snowflake up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f producer
docker-compose logs -f consumer
docker-compose logs -f snowflake-sync

# Restart specific service
docker-compose restart producer

# Check status
docker ps
```

---

## Monitoring & Logging

### Automated Monitoring (via Cron)

Cron jobs tự động chạy:

| Task | Schedule | Description |
|------|----------|-------------|
| Health Check | Every 5 minutes | Kiểm tra all services, auto-restart nếu down |
| Daily Check | 6:00 AM daily | Comprehensive health report |
| Weekly Restart | 3:00 AM Sunday | Restart để clear memory leaks |
| Disk Check | 7:00 AM daily | Alert nếu disk > 80% |
| Log Cleanup | 4:00 AM 1st of month | Xóa logs cũ hơn 30 ngày |

### Manual Monitoring

```bash
# Quick health check (exit 0 = healthy)
bash scripts/healthcheck.sh

# Detailed monitoring with auto-restart
bash scripts/monitor_services.sh

# Check specific container
docker inspect stock-producer
docker logs -f stock-producer

# Check database
docker exec -it postgres psql -U admin -d stock_db -c "SELECT COUNT(*) FROM realtime_quotes;"
```

### View Logs

```bash
# Service logs (systemd)
sudo journalctl -u vietnam-stock-pipeline -f

# Cron monitoring logs
tail -f /var/log/vietnam-stock-monitor-cron.log

# Daily check logs
tail -f /var/log/vietnam-stock-daily-check.log

# Container logs
docker logs -f stock-producer
docker logs -f kafka-consumer
docker logs -f snowflake-sync
```

### Metrics to Monitor

```bash
# Number of records in database
docker exec postgres psql -U admin -d stock_db -c "SELECT COUNT(*) as total_records FROM realtime_quotes;"

# Latest data timestamp
docker exec postgres psql -U admin -d stock_db -c "SELECT MAX(time) as latest_update FROM realtime_quotes;"

# Records per ticker
docker exec postgres psql -U admin -d stock_db -c "SELECT ticker, COUNT(*) FROM realtime_quotes GROUP BY ticker ORDER BY COUNT(*) DESC LIMIT 10;"

# Disk usage
df -h /u01/Vanh_projects/vietnam-stock-pipeline

# Docker volumes
docker volume ls
docker system df
```

---

## Backup & Recovery

### PostgreSQL Backup

#### Automated Daily Backup (Recommended)

Add to cron:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * docker exec postgres pg_dump -U admin stock_db > /backups/stock_db_$(date +\%Y\%m\%d).sql 2>&1
```

#### Manual Backup

```bash
# Create backup directory
mkdir -p /backups

# Backup database
docker exec postgres pg_dump -U admin stock_db > /backups/stock_db_$(date +%Y%m%d_%H%M%S).sql

# Backup with compression
docker exec postgres pg_dump -U admin stock_db | gzip > /backups/stock_db_$(date +%Y%m%d).sql.gz
```

#### Restore Database

```bash
# Stop services first
sudo systemctl stop vietnam-stock-pipeline

# Restore from backup
docker exec -i postgres psql -U admin -d stock_db < /backups/stock_db_20250108.sql

# Or from compressed
gunzip -c /backups/stock_db_20250108.sql.gz | docker exec -i postgres psql -U admin -d stock_db

# Start services
sudo systemctl start vietnam-stock-pipeline
```

### Docker Volumes Backup

```bash
# Backup Postgres data volume
docker run --rm -v vietnam-stock-pipeline_postgres-data:/data -v /backups:/backup alpine tar czf /backup/postgres-data-$(date +%Y%m%d).tar.gz -C /data .

# Restore Postgres data volume
docker run --rm -v vietnam-stock-pipeline_postgres-data:/data -v /backups:/backup alpine tar xzf /backup/postgres-data-20250108.tar.gz -C /data
```

### Configuration Backup

```bash
# Backup .env and configs
tar czf /backups/config-$(date +%Y%m%d).tar.gz .env docker-compose.yml systemd/
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check systemd status
sudo systemctl status vietnam-stock-pipeline

# Check detailed logs
sudo journalctl -u vietnam-stock-pipeline -n 100 --no-pager

# Check Docker
docker ps -a
docker-compose ps

# Check if ports are in use
netstat -tuln | grep -E '9092|5432|8501'

# Restart Docker daemon
sudo systemctl restart docker
```

### Containers Keep Restarting

```bash
# Check container logs
docker logs stock-producer
docker logs kafka-consumer

# Check resources
docker stats

# Check disk space
df -h

# Check memory
free -h
```

### No Data in Database

```bash
# Check producer is running
docker logs stock-producer

# Check if producer is sending to Kafka
docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic stock-quotes --from-beginning --max-messages 10

# Check consumer is reading from Kafka
docker logs kafka-consumer

# Check database connection
docker exec postgres psql -U admin -d stock_db -c "SELECT COUNT(*) FROM realtime_quotes;"
```

### Snowflake Sync Not Working

```bash
# Check Snowflake container
docker logs snowflake-sync

# Verify credentials in .env
cat .env | grep SNOWFLAKE

# Test Snowflake connection
docker exec snowflake-sync python -c "import snowflake.connector; print('OK')"

# Check sync interval
docker exec snowflake-sync env | grep SYNC_INTERVAL
```

### High Memory Usage

```bash
# Check memory usage by container
docker stats --no-stream

# Restart services to clear memory
sudo systemctl restart vietnam-stock-pipeline

# Reduce Spark worker memory if needed
# Edit docker-compose.yml:
# SPARK_WORKER_MEMORY=1G
```

### Dashboard Not Accessible

```bash
# Check dashboard container
docker logs stock-dashboard

# Check if port 8501 is listening
netstat -tuln | grep 8501

# Restart dashboard
docker-compose restart dashboard

# Access from server itself
curl http://localhost:8501
```

### Cron Jobs Not Running

```bash
# Check cron service
systemctl status cron

# View cron logs
grep CRON /var/log/syslog

# List installed cron jobs
crontab -l

# Test monitoring script manually
bash /u01/Vanh_projects/vietnam-stock-pipeline/scripts/monitor_services.sh
```

---

## Security Best Practices

### 1. Network Security

```bash
# All services are bound to localhost only (127.0.0.1)
# To access remotely, use SSH tunnel:

# On your local machine:
ssh -L 8501:localhost:8501 -L 5050:localhost:5050 user@your-server-ip

# Then access:
# Dashboard: http://localhost:8501
# pgAdmin: http://localhost:5050
```

### 2. Change Default Passwords

```bash
# Edit .env
nano .env

# Change these:
POSTGRES_PASSWORD=your_strong_password_here
PGADMIN_PASSWORD=your_strong_password_here
SNOWFLAKE_PASSWORD=your_snowflake_password
```

### 3. Firewall Configuration

```bash
# Only allow SSH (example for UFW)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable

# Services are on localhost, so no need to open ports
```

### 4. Regular Updates

```bash
# Update Docker images monthly
cd /u01/Vanh_projects/vietnam-stock-pipeline
docker-compose pull
sudo systemctl restart vietnam-stock-pipeline

# Update system packages
sudo apt update && sudo apt upgrade  # Ubuntu/Debian
sudo yum update  # CentOS/RHEL
```

### 5. Limit Resource Usage

```bash
# Already configured in systemd service:
# MemoryLimit=8G
# CPUQuota=400%

# Monitor resource usage
docker stats
```

### 6. Backup Encryption

```bash
# Encrypt backups before storing remotely
gpg --symmetric --cipher-algo AES256 /backups/stock_db_20250108.sql
```

---

## Advanced Configuration

### Scaling Producer

To fetch more stocks or increase frequency:

```bash
# Edit .env
PRODUCER_INTERVAL=60  # Fetch every 1 minute instead of 5
STOCK_SYMBOLS=VNM,VIC,HPG,MSN,TCB  # Add more symbols
```

### Database Optimization

```bash
# Create indexes for better performance
docker exec postgres psql -U admin -d stock_db << 'EOF'
CREATE INDEX IF NOT EXISTS idx_ticker_time ON realtime_quotes(ticker, time);
CREATE INDEX IF NOT EXISTS idx_time ON realtime_quotes(time);
EOF
```

### Increase Kafka Retention

```bash
# Edit docker-compose.yml
KAFKA_LOG_RETENTION_HOURS: 336  # 14 days instead of 7
```

### Configure Alerts

```bash
# Edit .env or set in environment
ALERT_EMAIL=your-email@example.com

# Install mailutils
sudo apt install mailutils  # Ubuntu/Debian

# Test email
echo "Test" | mail -s "Test Alert" your-email@example.com
```

---

## Performance Tuning

### PostgreSQL Tuning

```bash
# Edit PostgreSQL config (for 16GB RAM server)
docker exec postgres bash -c "cat >> /var/lib/postgresql/data/postgresql.conf << 'EOF'
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 41MB
min_wal_size = 2GB
max_wal_size = 8GB
max_worker_processes = 4
max_parallel_workers_per_gather = 2
max_parallel_workers = 4
max_parallel_maintenance_workers = 2
EOF
"

# Restart Postgres
docker-compose restart postgres
```

### Kafka Tuning

For high-volume data:

```bash
# Edit docker-compose.yml kafka service:
KAFKA_NUM_PARTITIONS=4
KAFKA_DEFAULT_REPLICATION_FACTOR=1
KAFKA_LOG_SEGMENT_BYTES=536870912  # 512MB
```

---

## Contact & Support

Nếu gặp vấn đề:

1. Check logs: `sudo journalctl -u vietnam-stock-pipeline -f`
2. Run health check: `bash scripts/monitor_services.sh`
3. Check troubleshooting section above
4. Review Docker logs: `docker-compose logs`

---

## Summary: Getting Started Checklist

- [ ] Server có đủ resources (4 CPU, 8GB RAM, 50GB disk)
- [ ] Docker & Docker Compose đã cài đặt
- [ ] Clone repository về `/u01/Vanh_projects/vietnam-stock-pipeline`
- [ ] Chạy `sudo ./setup_production.sh` (hoặc `--snowflake` nếu cần)
- [ ] Verify services: `systemctl status vietnam-stock-pipeline`
- [ ] Check logs: `journalctl -u vietnam-stock-pipeline -f`
- [ ] Access dashboard: `http://localhost:8501`
- [ ] Setup SSH tunnel cho remote access
- [ ] Configure backups (add cron job)
- [ ] Change default passwords trong `.env`
- [ ] Setup email alerts (optional)

**🎉 Xong! Pipeline sẽ chạy tự động 24/7!**

---

*Last updated: 2025-01-08*

