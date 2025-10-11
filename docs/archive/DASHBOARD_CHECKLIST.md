# ✅ DASHBOARD CHECKLIST - Verify Everything Works

**Date**: 2025-10-08  
**Purpose**: Check if dashboard is working correctly

---

## 🔍 QUICK CHECKS

### 1. Container Status ✅
```bash
docker ps | grep dashboard
```
**Expected**: `Up XX minutes` with port `127.0.0.1:8501->8501/tcp`

**Current Status**:
```
stock-dashboard   Up 20 minutes   127.0.0.1:8501->8501/tcp  ✅
```

### 2. Database Status ✅
```bash
docker exec postgres psql -U admin -d stock_db -c "SELECT COUNT(*) FROM realtime_quotes;"
```
**Expected**: `2,551,648` records

**Current Status**:
```
Total Records: 2,551,648 ✅
Unique Tickers: 1,558 ✅
Date Range: 2017-01-03 → 2025-10-08 ✅
```

### 3. Web Access ✅
```bash
curl http://localhost:8501
```
**Expected**: HTML response from Streamlit

**Current Status**: ✅ Responding

### 4. Logs Check ✅
```bash
docker logs stock-dashboard --tail 20
```
**Expected**: Only warnings (not errors)

**Current Status**: 
- ⚠️ Warnings about pandas SQLAlchemy (HARMLESS - just suggestions)
- ✅ No actual errors
- ✅ Dashboard functioning normally

---

## 🎨 WHAT YOU SHOULD SEE

### When Opening http://localhost:8501

#### Page Structure
```
┌─────────────────────────────────────────────┐
│ 📈 Vietnam Stock Market - Real-time Dashboard │
│ *Dữ liệu cập nhật theo thời gian thực...* │
├─────────────────────────────────────────────┤
│                                             │
│ [Summary Metrics Row]                       │
│ Total Stocks | Avg Price | Total Volume    │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│ [Tabs]                                      │
│ • Market Overview                           │
│ • Trends Analysis                           │
│ • Stock Details                             │
│                                             │
└─────────────────────────────────────────────┘
```

#### Tab 1: Market Overview
- 🔥 **Heatmap**: Color-coded stocks by performance
- 📊 **Price Distribution**: Histogram chart
- 📊 **Volume Distribution**: Histogram chart
- 🏆 **Top Performers**: Top gainers/losers tables

#### Tab 2: Trends Analysis
- 📈 **Market Trends**: Line chart over time
- 📊 **Comparison Charts**: Multi-stock comparison
- 📅 **Historical Data**: 8 years of data (2017-2025)

#### Tab 3: Stock Details
- 📊 **Moving Averages**: MA5, MA10
- 📈 **RSI**: Relative Strength Index
- 💹 **Momentum**: Price momentum
- 🎯 **Signals**: Bullish/Bearish indicators

---

## ❓ COMMON "LẠ" ISSUES & FIXES

### Issue 1: "Không thấy data / Empty charts"

**Possible Causes**:
- Database chưa có data
- Dashboard chưa connect được DB

**Check**:
```bash
# Check data exists
docker exec postgres psql -U admin -d stock_db -c "SELECT COUNT(*) FROM realtime_quotes;"

# Should show: 2,551,648
```

**Fix**:
```bash
# If count = 0, re-import data
./import_historical_to_postgres.sh

# Restart dashboard
docker-compose restart dashboard
```

### Issue 2: "Chữ hiển thị lạ / Encoding issues"

**Possible Causes**:
- Font rendering issues
- Browser encoding

**Fix**:
- Hard refresh: `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
- Clear browser cache
- Try different browser (Chrome recommended)

### Issue 3: "Dashboard không auto-refresh"

**Expected Behavior**:
- Dashboard auto-refreshes every 3 seconds
- You should see data updating

**Check**:
```bash
# Check DASHBOARD_REFRESH_INTERVAL
docker exec stock-dashboard env | grep DASHBOARD_REFRESH_INTERVAL
# Should show: DASHBOARD_REFRESH_INTERVAL=3
```

**Fix**:
```bash
# If not set correctly, restart:
docker-compose restart dashboard
```

### Issue 4: "Thấy toàn warnings đỏ"

**Expected**:
- Warnings về SQLAlchemy là BÌNH THƯỜNG
- Không ảnh hưởng chức năng
- Chỉ là suggestions để optimize code

**Example Warning (HARMLESS)**:
```
UserWarning: pandas only supports SQLAlchemy connectable...
```

**Action**: ❌ Không cần fix - dashboard vẫn hoạt động tốt

### Issue 5: "Charts render chậm"

**Possible Causes**:
- Too much data (2.55M records)
- Browser performance

**Fix**:
- Use filters to reduce data
- Close other browser tabs
- Try Chrome (fastest for Streamlit)

### Issue 6: "Một số stock không có data"

**Expected**:
- Historical data (2017-2025) is STATIC
- Real-time updates từ Kafka producer

**Check Real-time Updates**:
```bash
# Check producer is running
docker ps | grep producer

# Check producer logs
docker logs stock-producer --tail 20
```

---

## 🔧 ADVANCED CHECKS

### Check Dashboard Python Code
```bash
# View current dashboard code
docker exec stock-dashboard cat /app/dashboard.py | head -50
```

### Check Database Connection
```bash
# Test connection from dashboard container
docker exec stock-dashboard python3 -c "
import psycopg2
conn = psycopg2.connect(
    host='postgres',
    port=5432,
    database='stock_db',
    user='admin',
    password='admin'
)
print('✅ Connected to PostgreSQL')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM realtime_queries')
print(f'Records: {cursor.fetchone()[0]:,}')
"
```

### Force Refresh Dashboard
```bash
# Stop and remove container, then recreate
docker-compose stop dashboard
docker rm stock-dashboard
docker-compose up -d dashboard

# Wait 10 seconds
sleep 10

# Check status
docker ps | grep dashboard
```

---

## 📊 EXPECTED BEHAVIOR

### Normal Dashboard Behavior ✅
1. **Page loads** in 2-3 seconds
2. **Shows summary metrics** at top
3. **Displays charts** with data
4. **Auto-refreshes** every 3 seconds
5. **No error messages** (warnings are OK)
6. **Interactive filters** work
7. **Tabs switch** smoothly

### Abnormal Dashboard Behavior ❌
1. Blank page / White screen
2. "Error connecting to database"
3. All charts showing "No data"
4. Page doesn't load after 30 seconds
5. Python traceback errors
6. 500 Internal Server Error

---

## 🆘 IF STILL "LẠ"

Please describe specifically:

**What exactly looks "lạ"?**
- [ ] No data showing
- [ ] Wrong data showing
- [ ] Strange colors/layout
- [ ] Error messages
- [ ] Slow performance
- [ ] Missing features
- [ ] Other: _________________

**Screenshot or describe what you see**:
- What tab are you on?
- What's in the charts?
- Any error messages?

**Expected vs Actual**:
- What did you expect to see?
- What are you actually seeing?

---

## ✅ CURRENT STATUS SUMMARY

```
Container: ✅ Running (20+ minutes uptime)
Database: ✅ 2.55M records ready
Web UI: ✅ Responding on port 8501
Logs: ✅ No errors (only harmless warnings)
Data Range: ✅ 2017-2025 (8 years)
Tickers: ✅ 1,558 stocks

Overall Status: 🟢 HEALTHY
```

**Dashboard is working correctly!**

If you still see something "lạ", please describe specifically what's different from what you expected. 🙏

---

**Last Updated**: 2025-10-08  
**All Systems**: 🟢 OPERATIONAL


