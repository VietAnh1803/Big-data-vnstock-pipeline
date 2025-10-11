# 🚀 Quick Reference - Vietnam Stock Pipeline

## 📊 Check Status

```bash
# All services status
docker ps

# Data statistics
make data-stats

# Ticker count by exchange
make ticker-count

# Service logs
make prod-logs                # All services
docker logs postgres -f       # PostgreSQL
docker logs snowflake-sync -f # Snowflake sync
docker logs stock-producer -f # Producer
```

## 🔧 Common Commands

### Start/Stop
```bash
# Start all
docker compose up -d

# Start with Snowflake
docker compose --profile snowflake up -d

# Stop all
docker compose down

# Restart specific service
docker compose restart stock-producer
```

### Data Collection
```bash
# Fetch ALL historical data (30-60 min)
nohup make fetch-data > /tmp/fetch.log 2>&1 &
tail -f /tmp/fetch.log

# Check progress
make data-stats
```

### Snowflake
```bash
# Sync all tables to Snowflake
make sync-snowflake

# Check sync status
docker logs snowflake-sync --tail=20
```

## 🗄️ Database Queries

```bash
# Connect to PostgreSQL
docker exec -it postgres psql -U admin -d stock_db

# Or use pgAdmin
open http://localhost:5050
```

### Useful SQL

```sql
-- Top companies by volume
SELECT * FROM stock_summary 
ORDER BY volume DESC LIMIT 10;

-- Ticker info by industry
SELECT industry_name, COUNT(*) 
FROM ticker_info 
GROUP BY industry_name 
ORDER BY COUNT(*) DESC;

-- Historical prices for a ticker
SELECT * FROM historical_prices 
WHERE ticker = 'VNM' 
ORDER BY trading_date DESC 
LIMIT 30;

-- Latest realtime quotes
SELECT ticker, price, volume, change_percent, time
FROM realtime_quotes 
WHERE time > NOW() - INTERVAL '5 minutes'
ORDER BY volume DESC 
LIMIT 20;
```

## 🐛 Troubleshooting

### No data coming in
```bash
# Check producer
docker logs stock-producer --tail=50

# Check consumer
docker logs kafka-consumer --tail=50

# Restart pipeline
docker compose restart stock-producer kafka-consumer
```

### Dashboard not loading
```bash
# Check dashboard logs
docker logs stock-dashboard -f

# Restart dashboard
docker compose restart stock-dashboard

# Access at http://localhost:8501
```

### Database issues
```bash
# Check PostgreSQL health
docker exec postgres pg_isready -U admin

# Check database size
docker exec postgres psql -U admin -d stock_db -c "\l+"

# Check table sizes
docker exec postgres psql -U admin -d stock_db -c "
  SELECT schemaname,tablename, 
         pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
  FROM pg_tables 
  WHERE schemaname = 'public' 
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

## 📈 Monitoring

### Check Health
```bash
# All services
make prod-status

# Snowflake sync progress
docker logs snowflake-sync | grep "Total synced"

# Database stats
make data-stats
```

### Performance
```bash
# Kafka topics
docker exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --list

# Kafka consumer lag
docker exec kafka kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group stock-consumer \
  --describe

# PostgreSQL connections
docker exec postgres psql -U admin -d stock_db -c "
  SELECT count(*) as connections FROM pg_stat_activity;"
```

## 💾 Backup & Restore

### Backup
```bash
# Quick backup
make backup

# Manual backup
docker exec postgres pg_dump -U admin stock_db | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore
```bash
# From backup
gunzip -c backup_20251008.sql.gz | \
  docker exec -i postgres psql -U admin -d stock_db
```

## 🎯 Quick Fixes

### Reset Everything
```bash
# Stop all
docker compose down -v

# Start fresh
docker compose up -d

# Wait for services to be healthy
watch docker ps
```

### Clear Data (Keep Structure)
```sql
-- In PostgreSQL
TRUNCATE TABLE realtime_quotes;
TRUNCATE TABLE historical_prices;
-- Tables are empty but structure remains
```

### Rebuild Containers
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

## 📚 Documentation

- **README.md** - Main documentation
- **BIG_DATA_GUIDE.md** - BIG DATA features
- **PRODUCTION_GUIDE.md** - Production setup
- **CLEANUP_REPORT.md** - Bug fixes & cleanup
- **PORTS_EXPLAINED.md** - Port details

## 🔗 Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| Dashboard | http://localhost:8501 | Streamlit UI |
| pgAdmin | http://localhost:5050 | PostgreSQL UI |
| Spark Master | http://localhost:8080 | Spark monitoring |
| Spark Worker | http://localhost:8081 | Worker status |

## ⚡ Performance Tips

1. **Slow queries?** Add indexes on frequently queried columns
2. **Out of memory?** Adjust Docker resource limits
3. **Rate limited?** Increase delay in fetch scripts
4. **Dashboard slow?** Reduce refresh interval in .env

## 🆘 Get Help

```bash
# Check all available commands
make help

# View this reference
cat QUICK_REFERENCE.md

# Check system requirements
./scripts/check-requirements.sh
```

## 📞 Support

- Check logs first: `docker compose logs`
- Review documentation: `README.md`
- Check CLEANUP_REPORT.md for known issues

