# 🚀 Historical Data Download - Status

## ✅ Download In Progress

**Started**: 2025-10-08 07:49:07  
**Target**: Full historical data from 2017-now for all Vietnamese stocks

### 📊 Current Status

```bash
# Check live progress
./monitor_download.sh

# Watch live logs
tail -f download_full.log
```

### 🎯 Download Plan

- **Total Stocks**: 1,607
- **Date Range**: 2017-01-01 → 2025-10-08
- **Estimated Time**: ~54 minutes
- **Estimated Records**: ~3.5 million (1607 stocks × ~2,187 records/stock)
- **Estimated Size**: ~300-400 MB CSV

### ⚙️ Configuration

- **API**: vnstock 0.2.9.2.3 (Legacy)
- **Rate Limiting**: 2 seconds between stocks
- **Retry Logic**: 3 attempts per stock
- **Resume Support**: ✅ Yes (via `historical_data/download_progress.json`)

### 📁 Output Files

```
historical_data/
├── full_history_2017_now.csv          # Main data file
├── download_progress.json              # Progress tracking
└── failed_downloads.json               # Failed stocks (if any)
```

### 🔄 After Download Completes

1. **Verify Download**:
   ```bash
   wc -l historical_data/full_history_2017_now.csv
   du -h historical_data/full_history_2017_now.csv
   ```

2. **Import to PostgreSQL**:
   ```bash
   chmod +x import_historical_to_postgres.sh
   ./import_historical_to_postgres.sh
   ```

3. **Restart Dashboard**:
   ```bash
   docker-compose restart stock-dashboard
   ```

4. **Access Dashboard**: http://localhost:8501
   - Go to **"Trends Analysis"** tab
   - You'll see **8+ years** of historical trends!

### 🛠️ Troubleshooting

**If download stops:**
```bash
# Check if running
pgrep -f download_historical_data.py

# Resume (it will continue from last checkpoint)
cd /u01/Vanh_projects/vietnam-stock-pipeline
nohup python3 download_historical_data.py > download_full.log 2>&1 &
```

**If you need to start fresh:**
```bash
rm -rf historical_data/
python3 download_historical_data.py
```

### 📈 Expected Results

Based on test data (VNM, HPG, FPT):
- **Average records per stock**: ~2,187
- **Total expected records**: ~3.5 million
- **Date coverage**: 2017-01-03 → 2025-10-07
- **Columns**: time, ticker, open, high, low, close, volume

### 🎉 Next Steps

Once download is complete:

1. ✅ Import to PostgreSQL (replaces/merges with Snowflake data)
2. ✅ Dashboard will show full 2017-now trends
3. ✅ Real-time producer continues adding new data
4. ✅ Complete historical + real-time pipeline!

---

**Current Time**: Run `./monitor_download.sh` to see latest status

**Estimated Completion**: ~52 minutes from start (check monitor)

