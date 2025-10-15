# ❄️ Snowflake Database Cleanup Guide

## 🎯 **MỤC TIÊU**
Dọn dẹp các bảng trống trong Snowflake để tối ưu hóa storage và giảm chi phí credits.

---

## 📊 **TÌNH TRẠNG HIỆN TẠI**

### **Snowflake Database:**
- **Account:** BRWNIAD-WC21582
- **Database:** STOCKS
- **Schema:** PUBLIC
- **Warehouse:** COMPUTE_WH
- **Tổng records đã sync:** 2.6+ triệu records

### **Vấn đề:**
- Có thể có các bảng trống (0 records) trong Snowflake
- Các bảng trống vẫn tiêu tốn storage credits
- Cần dọn dẹp để tối ưu hóa chi phí

---

## 🔧 **CÁCH DỌN DẸP SNOWFLAKE**

### **1. Truy cập Snowflake Web Console**
```bash
# URL: https://app.snowflake.com
# Account: BRWNIAD-WC21582
# Username: BRWNIAD
# Password: Vanh@123456
```

### **2. Kiểm tra các bảng trống**
```sql
-- Kiểm tra tất cả bảng và số lượng records
SELECT 
    TABLE_NAME,
    ROW_COUNT,
    BYTES,
    CREATED
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'PUBLIC'
ORDER BY ROW_COUNT ASC;
```

### **3. Xác định bảng trống**
```sql
-- Tìm các bảng có 0 records
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'PUBLIC' 
AND ROW_COUNT = 0;
```

### **4. Xóa các bảng trống**
```sql
-- Xóa từng bảng trống (thay TABLE_NAME bằng tên bảng thực tế)
DROP TABLE IF EXISTS TABLE_NAME;

-- Hoặc xóa nhiều bảng cùng lúc
DROP TABLE IF EXISTS 
    company_news,
    company_profiles,
    market_indicators,
    balance_sheet,
    income_statement,
    cash_flow_statement,
    financial_ratios,
    trading_statistics,
    company_events,
    index_data,
    insider_trading,
    news_announcements,
    market_indices,
    financial_statements,
    ownership_structure;
```

---

## 🗑️ **CÁC BẢNG CÓ THỂ TRỐNG**

### **Dựa trên PostgreSQL cleanup, các bảng này có thể trống trong Snowflake:**
1. `company_news` (0 records)
2. `company_profiles` (0 records)
3. `market_indicators` (0 records)
4. `balance_sheet` (0 records)
5. `income_statement` (0 records)
6. `cash_flow_statement` (0 records)
7. `financial_ratios` (0 records)
8. `trading_statistics` (0 records)
9. `company_events` (0 records)
10. `index_data` (0 records)
11. `insider_trading` (0 records)
12. `news_announcements` (0 records)
13. `market_indices` (0 records)
14. `financial_statements` (0 records)
15. `ownership_structure` (0 records)

### **Các bảng có dữ liệu (KHÔNG XÓA):**
- `realtime_quotes` (2.6+ triệu records)
- `historical_prices` (nếu có)
- `stock_analytics` (nếu có)
- `ticker_info` (nếu có)

---

## 💰 **LỢI ÍCH TIẾT KIỆM CHI PHÍ**

### **1. Storage Credits:**
- Mỗi bảng trống vẫn tiêu tốn storage credits
- Xóa bảng trống giảm storage costs
- Tối ưu hóa warehouse usage

### **2. Query Performance:**
- Ít bảng để scan
- Metadata queries nhanh hơn
- Backup/restore nhanh hơn

### **3. Management:**
- Dễ quản lý database
- Ít bảng để monitor
- Cấu trúc rõ ràng hơn

---

## 🛠️ **CÁC SCRIPT HỖ TRỢ**

### **1. Script dọn dẹp:**
```bash
./cleanup_snowflake.sh
```

### **2. Script quản lý credits:**
```bash
./manage_snowflake_credits.sh
```

### **3. Script tối ưu hóa:**
```bash
./optimize_snowflake.sh
```

---

## ⚠️ **LƯU Ý QUAN TRỌNG**

### **Trước khi xóa:**
1. **Backup dữ liệu** quan trọng
2. **Kiểm tra dependencies** (views, procedures)
3. **Xác nhận bảng trống** (ROW_COUNT = 0)
4. **Test trên development** trước

### **Sau khi xóa:**
1. **Kiểm tra warehouse** hoạt động bình thường
2. **Monitor credits usage**
3. **Verify sync** vẫn hoạt động
4. **Update documentation**

---

## 🔍 **KIỂM TRA SAU KHI DỌN DẸP**

### **1. Kiểm tra bảng còn lại:**
```sql
SELECT 
    TABLE_NAME,
    ROW_COUNT,
    BYTES
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'PUBLIC'
ORDER BY ROW_COUNT DESC;
```

### **2. Kiểm tra storage usage:**
```sql
SELECT 
    SUM(BYTES) as TOTAL_BYTES,
    COUNT(*) as TABLE_COUNT
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'PUBLIC';
```

### **3. Kiểm tra warehouse status:**
```sql
SHOW WAREHOUSES;
```

---

## 📈 **THEO DÕI HIỆU QUẢ**

### **Metrics cần theo dõi:**
1. **Storage credits** - Giảm sau khi dọn dẹp
2. **Query performance** - Cải thiện
3. **Backup time** - Nhanh hơn
4. **Sync performance** - Ổn định

### **Tools theo dõi:**
- Snowflake web console
- Usage & Billing dashboard
- Query history
- Warehouse metrics

---

## 🚀 **KHUYẾN NGHỊ**

### **1. Thực hiện ngay:**
- Kiểm tra bảng trống trong Snowflake
- Xóa các bảng không cần thiết
- Monitor credits usage

### **2. Duy trì định kỳ:**
- Kiểm tra bảng trống hàng tháng
- Dọn dẹp định kỳ
- Tối ưu hóa warehouse

### **3. Tự động hóa:**
- Tạo script tự động dọn dẹp
- Schedule cleanup jobs
- Monitor và alert

---

## 📞 **HỖ TRỢ**

Nếu cần hỗ trợ:
1. Chạy `./cleanup_snowflake.sh` để kiểm tra
2. Sử dụng Snowflake web console
3. Kiểm tra logs: `docker logs snowflake-sync`

**Lưu ý:** Dọn dẹp Snowflake sẽ giúp tiết kiệm đáng kể credits cho free tier!
