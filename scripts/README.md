# 🔧 Data Management Scripts

## Overview

Scripts để quản lý data lifecycle: check status, update incremental, và sync giữa PostgreSQL ↔ Snowflake.

---

## 📊 Scripts

### 1. `check_data_status.py`

**Mục đích**: Kiểm tra trạng thái data hiện tại

**Chức năng**:
- ✅ Check PostgreSQL: records, tickers, date range, size
- ✅ Check Snowflake: PRICES_DAILY table status
- ✅ Phát hiện gaps (ngày nào chưa có data)
- ✅ Đề xuất actions cần thiết

**Usage**:
```bash
python3 scripts/check_data_status.py
```

**Output**:
```
📊 PostgreSQL:
   Latest Date: 2025-10-08
   Days Behind: 0
   Status: ✅ UP TO DATE

❄️  Snowflake:
   Latest Date: 2025-10-05
   Days Behind: 3
   Status: ⚠️  3 DAYS BEHIND
```

**Khi nào dùng**: Hàng ngày để check status, hoặc trước khi update data

---

### 2. `update_incremental.py`

**Mục đích**: Update data từ ngày cuối cùng trong DB → hôm nay

**Chức năng**:
- ✅ Tự động detect ngày cuối trong PostgreSQL
- ✅ Chỉ fetch missing dates (không duplicate)
- ✅ Insert với ON CONFLICT (safe)
- ✅ Support resume nếu bị interrupt
- ✅ Rate limiting để tránh API block

**Usage**:
```bash
python3 scripts/update_incremental.py
```

**Example**:
```
Current Data Range:
  Latest in DB: 2025-10-05
  Today: 2025-10-08
  Days to Update: 3

📥 Will fetch data from: 2025-10-06 to 2025-10-08
📊 Tickers to update: 1558

⚠️  Update 1558 stocks from 2025-10-06 to 2025-10-08? (y/n):
```

**Khi nào dùng**: 
- Hàng ngày sau giờ đóng cửa thị trường
- Khi phát hiện PostgreSQL bị behind (từ check_data_status.py)

---

### 3. `sync_to_snowflake.py`

**Mục đích**: Đẩy data từ PostgreSQL → Snowflake

**Chức năng**:
- ✅ Compare PostgreSQL vs Snowflake dates
- ✅ Chỉ sync missing records
- ✅ Use MERGE statement (upsert)
- ✅ Batch processing (1000 records/batch)
- ✅ Progress tracking

**Usage**:
```bash
python3 scripts/sync_to_snowflake.py
```

**Example**:
```
📊 PostgreSQL:
  Date Range: 2017-01-03 → 2025-10-08

❄️  Snowflake:
  Latest Date: 2025-10-05

📥 Will sync:
  From: 2025-10-06
  To: 2025-10-08
  Days: 3

⚠️  Sync 3 days of data to Snowflake? (y/n):
```

**Khi nào dùng**:
- Sau khi update_incremental.py xong
- Khi cần backup PostgreSQL data vào Snowflake
- Định kỳ (e.g., mỗi tối sau khi update)

---

## 🔄 Daily Workflow

### Morning Check (9:00 AM)

```bash
# 1. Check current status
python3 scripts/check_data_status.py
```

### After Market Close (3:30 PM)

```bash
# 2. Update incremental data
python3 scripts/update_incremental.py

# 3. Sync to Snowflake (optional, nếu cần backup)
python3 scripts/sync_to_snowflake.py

# 4. Verify update thành công
python3 scripts/check_data_status.py
```

---

## ⚙️ Configuration

Scripts tự động detect environment:

**PostgreSQL**:
- Host: localhost (khi chạy từ host machine)
- Host: postgres (khi chạy trong Docker)
- Port: 5432
- Database: stock_db
- User: admin

**Snowflake**:
- Account: BRWNIAD-WC21582
- Warehouse: COMPUTE_WH
- Database: STOCKS
- Schema: PUBLIC
- Table: PRICES_DAILY

**Override bằng `.env`**:
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
```

---

## 🛡️ Safety Features

### Deduplication
- ✅ PostgreSQL: `UNIQUE (ticker, time)` constraint
- ✅ Snowflake: `MERGE` với `ON CONFLICT`

### Resume Support
- ✅ `update_incremental.py`: Có thể retry, chỉ insert missing records

### Rate Limiting
- ✅ 2 giây giữa các stocks
- ✅ 10 giây nếu error

### Error Handling
- ✅ Retry logic (3 lần)
- ✅ Failed stocks được log
- ✅ Transaction rollback nếu có lỗi

---

## 📝 Examples

### Scenario 1: Data Up-To-Date

```bash
$ python3 scripts/check_data_status.py

📊 PostgreSQL:
   Latest Date: 2025-10-08
   Days Behind: 0
   Status: ✅ UP TO DATE

💡 No actions needed
```

### Scenario 2: PostgreSQL Behind 3 Days

```bash
$ python3 scripts/check_data_status.py

📊 PostgreSQL:
   Latest Date: 2025-10-05
   Days Behind: 3
   Status: ⚠️  3 DAYS BEHIND

💡 RECOMMENDATIONS:
1. Update PostgreSQL:
   Run: python3 scripts/update_incremental.py
   Will fetch: 2025-10-06 → 2025-10-08

$ python3 scripts/update_incremental.py
# ... updates ...
✅ Summary:
  New Records Inserted: 4,674
  Latest Date After: 2025-10-08
```

### Scenario 3: Snowflake Behind PostgreSQL

```bash
$ python3 scripts/check_data_status.py

📊 PostgreSQL: Latest 2025-10-08 ✅
❄️  Snowflake: Latest 2025-10-05 ⚠️  3 DAYS BEHIND

💡 RECOMMENDATIONS:
2. Sync PostgreSQL → Snowflake:
   Run: python3 scripts/sync_to_snowflake.py

$ python3 scripts/sync_to_snowflake.py
# ... syncing ...
✅ Summary:
  Records Synced: 4,674
  Latest Date After: 2025-10-08
```

---

## 🔍 Troubleshooting

### PostgreSQL Connection Error

```
❌ Error: could not translate host name "postgres"
```

**Fix**: Script tự động dùng `localhost`. Nếu vẫn lỗi, check PostgreSQL đang chạy:
```bash
docker ps | grep postgres
```

### Snowflake Authentication Error

```
❌ Error: Account must be specified
```

**Fix**: Kiểm tra credentials trong `.env` hoặc update hardcoded values trong script.

### Duplicate Key Error

```
❌ Error: duplicate key value violates unique constraint
```

**Fix**: Đây là expected behavior với ON CONFLICT. Script sẽ skip duplicates.

---

## 📦 Dependencies

```bash
pip3 install psycopg2-binary snowflake-connector-python vnstock python-dotenv
```

---

## 🎯 Tips

1. **Automate Daily Updates**: Thêm vào crontab
```bash
30 15 * * 1-5 cd /path/to/project && python3 scripts/update_incremental.py
0 16 * * 1-5 cd /path/to/project && python3 scripts/sync_to_snowflake.py
```

2. **Check Before Trading**: Morning routine
```bash
alias stock-status='cd /path/to/project && python3 scripts/check_data_status.py'
```

3. **Combine with Dashboard**: Dashboard tự động load latest data từ PostgreSQL

---

**Created**: 2025-10-08  
**Author**: AI Assistant  
**Version**: 1.0






