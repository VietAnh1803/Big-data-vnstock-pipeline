# 🌐 Dashboard Access Guide

## 🎯 **TÌNH TRẠNG HIỆN TẠI**

### ✅ **Dashboard đang hoạt động:**
- **Container:** `stock-dashboard` đang chạy
- **Port:** 8501 đã được sử dụng (bình thường)
- **Status:** HTTP 200 - Dashboard accessible
- **URL:** http://localhost:8501

---

## 🚀 **CÁCH TRUY CẬP DASHBOARD**

### **1. Truy cập trực tiếp:**
```bash
# Mở browser và truy cập:
http://localhost:8501
```

### **2. Sử dụng Dashboard Manager:**
```bash
./scripts/dashboard_manager.sh
# Chọn option 7: Open dashboard in browser
```

### **3. Kiểm tra trạng thái:**
```bash
./scripts/dashboard_manager.sh
# Chọn option 1: Check dashboard status
```

---

## 🔧 **QUẢN LÝ DASHBOARD**

### **Dashboard Manager Script:**
```bash
./scripts/dashboard_manager.sh
```

#### **Các tùy chọn:**
1. **Check dashboard status** - Kiểm tra trạng thái
2. **Start dashboard** - Khởi động dashboard
3. **Stop dashboard** - Dừng dashboard
4. **Restart dashboard** - Khởi động lại
5. **Switch dashboard version** - Chuyển đổi phiên bản
6. **View dashboard logs** - Xem logs
7. **Open dashboard in browser** - Mở trong browser
8. **Show dashboard info** - Hiển thị thông tin

---

## 📊 **CÁC PHIÊN BẢN DASHBOARD**

### **1. Demo Dashboard (Khuyến nghị)**
- **Dữ liệu:** Mẫu (simulated)
- **Tính năng:** Đầy đủ charts và metrics
- **Ưu điểm:** Hoạt động ổn định
- **Sử dụng:** Test và demo

### **2. Hybrid Dashboard**
- **Dữ liệu:** Từ PostgreSQL database
- **Tính năng:** Dữ liệu thực tế
- **Ưu điểm:** Dữ liệu thật
- **Nhược điểm:** Cần kết nối database

### **3. Simple Dashboard**
- **Dữ liệu:** Từ database (đơn giản)
- **Tính năng:** Cơ bản
- **Ưu điểm:** Nhẹ, nhanh

---

## 🎛️ **CHUYỂN ĐỔI PHIÊN BẢN**

### **Sử dụng Dashboard Manager:**
```bash
./scripts/dashboard_manager.sh
# Chọn option 5: Switch dashboard version
```

### **Chuyển đổi thủ công:**
```bash
# Chuyển sang Demo Dashboard
docker exec stock-dashboard pkill -f streamlit
docker exec -d stock-dashboard streamlit run demo_dashboard.py --server.port 8501 --server.address 0.0.0.0

# Chuyển sang Hybrid Dashboard
docker exec stock-dashboard pkill -f streamlit
docker exec -d stock-dashboard streamlit run dashboard_hybrid.py --server.port 8501 --server.address 0.0.0.0

# Chuyển sang Simple Dashboard
docker exec stock-dashboard pkill -f streamlit
docker exec -d stock-dashboard streamlit run simple_dashboard.py --server.port 8501 --server.address 0.0.0.0
```

---

## 🔍 **TROUBLESHOOTING**

### **Port 8501 đã được sử dụng:**
- **✅ Bình thường:** Dashboard đang chạy
- **Truy cập:** http://localhost:8501
- **Kiểm tra:** `docker ps | grep stock-dashboard`

### **Dashboard không hiển thị:**
```bash
# 1. Kiểm tra container
docker ps | grep stock-dashboard

# 2. Kiểm tra logs
docker logs stock-dashboard --tail 20

# 3. Restart dashboard
./scripts/dashboard_manager.sh
# Chọn option 4: Restart dashboard
```

### **Database connection issues:**
```bash
# Sử dụng Demo Dashboard (không cần database)
./scripts/dashboard_manager.sh
# Chọn option 5: Switch dashboard version
# Chọn option 1: Demo Dashboard
```

---

## 📱 **TRUY CẬP TỪ THIẾT BỊ KHÁC**

### **Từ máy khác trong mạng:**
```bash
# Thay localhost bằng IP của server
http://[SERVER_IP]:8501

# Ví dụ:
http://192.168.1.100:8501
```

### **Kiểm tra IP server:**
```bash
# Lấy IP của server
hostname -I
# hoặc
ip addr show | grep inet
```

---

## 🎨 **TÍNH NĂNG DASHBOARD**

### **📊 Market Overview:**
- Market metrics
- Top gainers/losers
- Volume leaders
- Market performance chart

### **📈 Individual Analysis:**
- Ticker selection
- Price charts (candlestick)
- Volume analysis
- Performance metrics

### **📦 Volume Analysis:**
- Volume leaders
- Volume distribution
- Volume vs Price scatter

---

## 🔄 **AUTO-REFRESH**

### **Tự động cập nhật:**
- **Frequency:** Mỗi 30 giây
- **Enable:** Checkbox trong sidebar
- **Manual:** Nút refresh

### **Cập nhật thủ công:**
- **Button:** 🔄 Manual Refresh
- **Keyboard:** F5 hoặc Ctrl+R
- **Script:** Restart dashboard

---

## 📞 **HỖ TRỢ**

### **Scripts hỗ trợ:**
```bash
# Dashboard management
./scripts/dashboard_manager.sh

# System management
./manage.sh

# Database connection
./scripts/connect_postgres.sh
```

### **Logs và debugging:**
```bash
# Dashboard logs
docker logs stock-dashboard

# System logs
./manage.sh logs
```

---

## 🎊 **TỔNG KẾT**

### **✅ Dashboard Status:**
- **Container:** Running ✅
- **Port:** 8501 (in use) ✅
- **Access:** http://localhost:8501 ✅
- **HTTP Status:** 200 ✅

### **🎯 Khuyến nghị:**
1. **Truy cập:** http://localhost:8501
2. **Sử dụng Demo Dashboard** để test
3. **Auto-refresh** để theo dõi real-time
4. **Dashboard Manager** để quản lý

**Dashboard của bạn đã sẵn sàng sử dụng!** 🚀


