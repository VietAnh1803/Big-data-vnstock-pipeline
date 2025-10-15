# 🎯 Snowflake Free Tier Credits Management Guide

## ⚠️ **TÌNH TRẠNG HIỆN TẠI**
- **Snowflake Free Tier:** Có giới hạn credits
- **Hệ thống đã tối ưu:** Giảm 12x tần suất sync
- **Dữ liệu đầy đủ:** 2017-2025 đã có trong Snowflake

---

## 🔧 **CÁC TỐI ƯU HÓA ĐÃ THỰC HIỆN**

### 1. **Giảm Tần Suất Sync**
- **Trước:** Mỗi 5 phút (288 lần/ngày)
- **Sau:** Mỗi 1 giờ (24 lần/ngày)
- **Tiết kiệm:** 12x credits

### 2. **Tối Ưu Batch Size**
- **Batch size:** 5,000 records (thay vì 1,000)
- **Timeout:** 30 giây (thay vì 10 giây)
- **Hiệu quả:** Ít operations hơn

### 3. **Data Retention Policy**
- **Realtime data:** 90 ngày
- **Historical data:** 1 năm
- **Tiết kiệm:** Storage costs

---

## 🛠️ **CÁC SCRIPT QUẢN LÝ**

### 1. **Quản lý Credits**
```bash
./manage_snowflake_credits.sh
```
**Chức năng:**
- Kiểm tra trạng thái sync
- Tạm dừng/tiếp tục sync
- Thiết lập sync giờ hành chính
- Hiển thị tips tiết kiệm credits

### 2. **Tối Ưu Hóa Nhanh**
```bash
./optimize_snowflake.sh
```
**Chức năng:**
- Áp dụng cấu hình tối ưu
- Khởi động sync với tần suất thấp

---

## 📊 **CÁC CHIẾN LƯỢC TIẾT KIỆM CREDITS**

### 1. **Sync Giờ Hành Chính (Khuyến nghị)**
```bash
# Chỉ sync 9 AM - 5 PM, Thứ 2 - Thứ 6
./manage_snowflake_credits.sh
# Chọn option 4: Set business hours sync only
```
**Tiết kiệm:** ~70% credits

### 2. **Tạm Dừng Sync**
```bash
# Tạm dừng hoàn toàn
./manage_snowflake_credits.sh
# Chọn option 2: Pause sync
```
**Khi nào:** Cuối tuần, ngày lễ, không sử dụng

### 3. **Monitor Usage**
```bash
# Kiểm tra sử dụng
./manage_snowflake_credits.sh
# Chọn option 6: Monitor credits usage
```

---

## 🚨 **CẢNH BÁO VÀ HÀNH ĐỘNG**

### **Khi Credits Sắp Hết:**
1. **Tạm dừng sync ngay lập tức:**
   ```bash
   ./manage_snowflake_credits.sh
   # Chọn option 2: Pause sync
   ```

2. **Chuyển sang chế độ giờ hành chính:**
   ```bash
   ./manage_snowflake_credits.sh
   # Chọn option 4: Set business hours sync only
   ```

3. **Backup dữ liệu quan trọng:**
   ```bash
   # Export dữ liệu từ Snowflake về local
   # Hoặc sử dụng PostgreSQL làm nguồn chính
   ```

---

## 💡 **CÁC MẸO TIẾT KIỆM CREDITS**

### 1. **Warehouse Settings**
- Sử dụng X-Small warehouse
- Auto-suspend sau 60 giây
- Auto-resume khi cần

### 2. **Query Optimization**
- Sử dụng WHERE clauses hiệu quả
- Tránh SELECT * không cần thiết
- Sử dụng LIMIT khi có thể

### 3. **Data Management**
- Archive dữ liệu cũ
- Compress dữ liệu khi có thể
- Sử dụng clustering keys

---

## 📈 **THEO DÕI SỬ DỤNG**

### 1. **Snowflake Web Console**
- Đăng nhập: https://app.snowflake.com
- Account: BRWNIAD-WC21582
- Kiểm tra Usage & Billing

### 2. **Local Monitoring**
```bash
# Kiểm tra logs
docker logs snowflake-sync --tail 20

# Kiểm tra tần suất sync
grep "Successfully synced" /var/log/snowflake-sync.log
```

---

## 🔄 **KẾ HOẠCH DỰ PHÒNG**

### **Nếu Hết Credits:**
1. **Sử dụng PostgreSQL làm nguồn chính**
2. **Export dữ liệu từ Snowflake**
3. **Chuyển sang local analytics**
4. **Cân nhắc upgrade lên paid tier**

### **Backup Strategy:**
```bash
# Backup PostgreSQL data
docker exec postgres pg_dump -U admin stock_db > backup_$(date +%Y%m%d).sql

# Export từ Snowflake (nếu cần)
# Sử dụng SnowSQL hoặc web interface
```

---

## 🎯 **KHUYẾN NGHỊ CUỐI CÙNG**

### **Cho Free Tier:**
1. **Sync giờ hành chính** (9 AM - 5 PM, Mon-Fri)
2. **Tạm dừng cuối tuần**
3. **Monitor credits thường xuyên**
4. **Backup dữ liệu quan trọng**

### **Cho Production:**
1. **Upgrade lên paid tier**
2. **Sử dụng warehouse phù hợp**
3. **Implement proper monitoring**
4. **Có kế hoạch disaster recovery**

---

## 📞 **HỖ TRỢ**

Nếu cần hỗ trợ:
1. Chạy `./manage_snowflake_credits.sh` để quản lý
2. Kiểm tra logs: `docker logs snowflake-sync`
3. Xem cấu hình: `cat snowflake-optimized.env`

**Lưu ý:** Hệ thống đã được tối ưu để tiết kiệm tối đa credits cho free tier!
