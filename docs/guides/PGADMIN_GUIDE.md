# 🐘 pgAdmin - PostgreSQL Web UI Guide

**Last Updated**: 2025-10-08  
**Status**: ✅ INSTALLED & RUNNING

---

## 🎯 OVERVIEW

pgAdmin là web-based UI cho PostgreSQL, giúp bạn:
- ✅ Browse databases, tables, views
- ✅ Run SQL queries với editor
- ✅ View & edit data trực quan
- ✅ Export/Import data
- ✅ Monitor database performance
- ✅ Manage indexes, constraints, etc.

---

## 🔗 ACCESS PGADMIN

### From Server (Local)
```
URL: http://localhost:5050
Email: admin@example.com
Password: admin
```

### From Remote Machine (SSH Tunnel)
```bash
# Method 1: Manual SSH Tunnel
ssh -L 5050:localhost:5050 oracle@10.0.0.7

# Sau đó mở browser:
http://localhost:5050

# Method 2: Combined with Dashboard
ssh -L 5050:localhost:5050 -L 8501:localhost:8501 oracle@10.0.0.7
# Access:
# - pgAdmin: http://localhost:5050
# - Dashboard: http://localhost:8501
```

---

## 🚀 FIRST TIME SETUP

### 1. Login to pgAdmin
```
URL: http://localhost:5050
Email: admin@example.com
Password: admin
```

### 2. PostgreSQL Server Already Configured! ✅

Server đã được auto-configured với thông tin:
```
Name: Stock Database (PostgreSQL)
Host: postgres
Port: 5432
Database: stock_db
Username: admin
Password: (bạn cần nhập lần đầu)
```

**Password**: `admin` (hoặc giá trị trong `.env` file)

### 3. Connect to Server

1. Click vào "Stock Database (PostgreSQL)" trong sidebar
2. Nhập password: `admin`
3. ✅ Connected!

---

## 📊 EXPLORE DATA

### View Tables

```
Stock Database (PostgreSQL)
  └── Databases
      └── stock_db
          └── Schemas
              └── public
                  └── Tables
                      └── realtime_quotes  <-- Click here
```

### View Data
1. Right-click on `realtime_quotes`
2. Select "View/Edit Data" → "All Rows"
3. Xem full 2.55M records với pagination

### Run SQL Queries

1. Click "Query Tool" icon (hoặc Tools → Query Tool)
2. Nhập SQL:
   ```sql
   -- Get latest records
   SELECT * FROM realtime_quotes 
   ORDER BY processed_time DESC 
   LIMIT 100;
   
   -- Count by ticker
   SELECT ticker, COUNT(*) as records
   FROM realtime_quotes
   GROUP BY ticker
   ORDER BY records DESC;
   
   -- Date range
   SELECT 
     MIN(time) as earliest,
     MAX(time) as latest,
     COUNT(*) as total
   FROM realtime_quotes;
   
   -- Top gainers today
   SELECT ticker, price, change_percent
   FROM realtime_quotes
   WHERE time::date = CURRENT_DATE
   ORDER BY change_percent DESC
   LIMIT 20;
   ```
3. Click "Execute" (F5)

---

## 🔍 USEFUL QUERIES

### Database Statistics
```sql
-- Table size
SELECT 
    pg_size_pretty(pg_total_relation_size('realtime_quotes')) as size,
    COUNT(*) as records
FROM realtime_quotes;

-- Records by date
SELECT 
    time::date as date,
    COUNT(*) as records,
    COUNT(DISTINCT ticker) as tickers
FROM realtime_quotes
GROUP BY time::date
ORDER BY date DESC
LIMIT 30;
```

### Data Quality Checks
```sql
-- Check for duplicates
SELECT ticker, time, COUNT(*) as count
FROM realtime_quotes
GROUP BY ticker, time
HAVING COUNT(*) > 1;

-- Check for NULL values
SELECT 
    COUNT(*) FILTER (WHERE ticker IS NULL) as null_ticker,
    COUNT(*) FILTER (WHERE time IS NULL) as null_time,
    COUNT(*) FILTER (WHERE price IS NULL) as null_price
FROM realtime_quotes;

-- Missing dates
SELECT 
    ticker,
    MAX(time) as latest_date,
    CURRENT_DATE - MAX(time::date) as days_behind
FROM realtime_quotes
GROUP BY ticker
HAVING CURRENT_DATE - MAX(time::date) > 1
ORDER BY days_behind DESC;
```

### Performance Analysis
```sql
-- Most active stocks (by volume)
SELECT 
    ticker,
    AVG(volume) as avg_volume,
    MAX(volume) as max_volume,
    COUNT(*) as records
FROM realtime_quotes
WHERE time >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY ticker
ORDER BY avg_volume DESC
LIMIT 20;

-- Price changes
SELECT 
    ticker,
    MIN(price) as min_price,
    MAX(price) as max_price,
    AVG(price) as avg_price,
    (MAX(price) - MIN(price)) / MIN(price) * 100 as price_range_pct
FROM realtime_quotes
WHERE time >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY ticker
ORDER BY price_range_pct DESC
LIMIT 20;
```

---

## 📤 EXPORT DATA

### Export to CSV
1. Right-click on table → "View/Edit Data"
2. Click "Download" icon
3. Select format: CSV, Excel, etc.
4. Configure options and download

### Export via SQL
```sql
-- Export specific data
COPY (
    SELECT ticker, time, price, volume
    FROM realtime_quotes
    WHERE ticker = 'VNM'
    ORDER BY time DESC
    LIMIT 1000
) TO '/tmp/vnm_data.csv' WITH CSV HEADER;
```

---

## 🔧 ADMIN TASKS

### Check Indexes
```sql
-- List all indexes
SELECT 
    indexname,
    tablename,
    indexdef
FROM pg_indexes
WHERE tablename = 'realtime_quotes';
```

### Vacuum & Analyze
```sql
-- Optimize table
VACUUM ANALYZE realtime_quotes;

-- Check table stats
SELECT 
    relname,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    last_vacuum,
    last_analyze
FROM pg_stat_user_tables
WHERE relname = 'realtime_quotes';
```

### Monitor Queries
```sql
-- Active queries
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    query_start,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;
```

---

## 📊 DASHBOARD FEATURES

### Visual Query Builder
1. Right-click table → "View/Edit Data"
2. Use filter toolbar to build queries visually
3. Click "Filter" to add conditions

### ERD Diagram
1. Right-click on database
2. Select "ERD For Database"
3. View table relationships

### Backup & Restore
1. Right-click on database
2. "Backup..." to create dump
3. "Restore..." to import

---

## ⚙️ CONFIGURATION

### Change Password (Recommended)
```bash
# Update .env file
nano /u01/Vanh_projects/vietnam-stock-pipeline/.env

# Add:
PGADMIN_EMAIL=your-email@example.com
PGADMIN_PASSWORD=your-strong-password

# Restart pgAdmin
docker-compose restart pgadmin
```

### Persistent Settings
- pgAdmin settings are stored in `pgadmin-data` volume
- Servers, queries, preferences are preserved across restarts

---

## 🔐 SECURITY

### Current Setup ✅
```
Port: 127.0.0.1:5050 (Localhost only - SECURE)
Access: SSH tunnel required for remote
Password: Default (SHOULD CHANGE)
```

### Best Practices
1. ✅ **Change default password**
2. ✅ **Use SSH tunnel for remote access**
3. ✅ **Never expose port 5050 to internet**
4. ✅ **Regularly backup pgAdmin settings**

---

## 🚨 TROUBLESHOOTING

### Cannot Login
```bash
# Check pgAdmin logs
docker logs pgadmin --tail 50

# Reset pgAdmin
docker-compose stop pgadmin
docker rm pgadmin
docker volume rm vietnam-stock-pipeline_pgadmin-data
docker-compose up -d pgadmin
```

### Cannot Connect to PostgreSQL
- Check PostgreSQL is running: `docker ps | grep postgres`
- Verify credentials match `.env` file
- Test connection: `docker exec postgres psql -U admin -d stock_db -c "SELECT 1;"`

### Slow Queries
```sql
-- Enable query logging
SET log_statement = 'all';
SET log_duration = on;

-- Check slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;
```

---

## 📱 MOBILE ACCESS

pgAdmin is responsive và hoạt động trên mobile:
1. Setup SSH tunnel từ điện thoại (Termius, JuiceSSH, etc.)
2. Forward port 5050
3. Mở browser: `http://localhost:5050`

---

## ⚡ QUICK REFERENCE

### Common Tasks

| Task | Action |
|------|--------|
| View data | Right-click table → View/Edit Data |
| Run query | Tools → Query Tool (F5 to execute) |
| Export | Right-click → Import/Export |
| Refresh | Right-click → Refresh (F5) |
| New query | Query Tool icon |
| Disconnect | Right-click server → Disconnect |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| F5 | Execute query |
| Ctrl+Space | Auto-complete |
| Ctrl+S | Save query |
| Ctrl+L | Clear query |
| Ctrl+Shift+K | Toggle line comment |

---

## 📚 RESOURCES

- **pgAdmin Docs**: https://www.pgadmin.org/docs/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **SQL Tutorial**: https://www.postgresqltutorial.com/

---

## 🎯 SUMMARY

**pgAdmin đã sẵn sàng!**

✅ Access: http://localhost:5050 (or SSH tunnel)
✅ Login: admin@example.com / admin
✅ Server: Auto-configured
✅ Data: 2.55M records ready to explore
✅ Security: Localhost only

**Happy querying! 🚀**

---

**Last Updated**: 2025-10-08  
**Container**: pgadmin  
**Port**: 127.0.0.1:5050  
**Status**: 🟢 RUNNING


