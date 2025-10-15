# 📈 Vietnam Stock Dashboard Guide

## 🎯 **TỔNG QUAN**

Dashboard Vietnam Stock Pipeline cung cấp giao diện trực quan để theo dõi và phân tích dữ liệu chứng khoán Việt Nam với các tính năng:

- **📊 Market Overview** - Tổng quan thị trường
- **📈 Individual Analysis** - Phân tích từng mã chứng khoán
- **📦 Volume Analysis** - Phân tích khối lượng giao dịch
- **🔄 Real-time Updates** - Cập nhật dữ liệu thời gian thực

---

## 🚀 **CÁCH SỬ DỤNG**

### **1. Khởi động Dashboard**

#### **Sử dụng Script Launcher (Khuyến nghị):**
```bash
./scripts/launch_dashboard.sh
```

#### **Truy cập trực tiếp:**
```bash
# Demo Dashboard (với dữ liệu mẫu)
http://localhost:8501

# Hoặc sử dụng script
./scripts/launch_dashboard.sh
# Chọn option 1: Demo Dashboard
```

### **2. Các Phiên Bản Dashboard**

#### **📊 Demo Dashboard (Khuyến nghị)**
- **Dữ liệu:** Mẫu (simulated)
- **Tính năng:** Đầy đủ charts và metrics
- **Ưu điểm:** Hoạt động ổn định, không phụ thuộc database
- **Sử dụng:** Test và demo

#### **📈 Hybrid Dashboard**
- **Dữ liệu:** Từ PostgreSQL database
- **Tính năng:** Dữ liệu thực tế
- **Ưu điểm:** Dữ liệu thật
- **Nhược điểm:** Cần kết nối database ổn định

#### **📋 Simple Dashboard**
- **Dữ liệu:** Từ database (đơn giản)
- **Tính năng:** Cơ bản
- **Ưu điểm:** Nhẹ, nhanh
- **Nhược điểm:** Ít tính năng

---

## 📊 **TÍNH NĂNG CHI TIẾT**

### **1. Market Overview Tab**

#### **📈 Market Metrics:**
- **Total Tickers:** Tổng số mã chứng khoán
- **Avg Change %:** Thay đổi trung bình
- **Total Volume:** Tổng khối lượng giao dịch
- **Latest Data:** Dữ liệu mới nhất

#### **🚀 Top Performers:**
- **Top Gainers:** Cổ phiếu tăng giá mạnh nhất
- **Top Losers:** Cổ phiếu giảm giá mạnh nhất
- **Volume Leaders:** Cổ phiếu có khối lượng giao dịch cao nhất

#### **📊 Market Performance Chart:**
- Biểu đồ cột hiển thị performance của tất cả mã
- Màu sắc phân biệt tăng/giảm giá
- Tương tác hover để xem chi tiết

### **2. Individual Analysis Tab**

#### **📈 Ticker Selection:**
- Dropdown chọn mã chứng khoán
- Hiển thị metrics cho mã được chọn

#### **📊 Price Chart:**
- **Candlestick Chart:** Biểu đồ nến Nhật
- **Moving Averages:** MA5, MA20
- **Interactive:** Zoom, pan, hover

#### **📦 Volume Analysis:**
- Biểu đồ cột khối lượng giao dịch
- Phân tích volume theo thời gian

#### **📊 Performance Metrics:**
- **Current Price:** Giá hiện tại
- **Price Change:** Thay đổi giá
- **Volume:** Khối lượng
- **Data Points:** Số điểm dữ liệu

### **3. Volume Analysis Tab**

#### **📦 Volume Leaders:**
- Top 20 cổ phiếu theo khối lượng
- Bảng dữ liệu chi tiết

#### **📊 Volume Distribution:**
- Biểu đồ cột top 15 cổ phiếu
- Màu sắc theo khối lượng

#### **📈 Volume vs Price:**
- Scatter plot khối lượng vs giá
- Kích thước bubble = khối lượng
- Màu sắc = % thay đổi

---

## 🎛️ **CONTROL PANEL**

### **Sidebar Controls:**
- **🔄 Auto Refresh:** Tự động cập nhật mỗi 30 giây
- **🔄 Manual Refresh:** Cập nhật thủ công
- **🔍 Search Ticker:** Tìm kiếm mã chứng khoán
- **⏰ Time Range:** Chọn khoảng thời gian (1W, 1M, 3M, 6M, 1Y)

### **Data Source Info:**
- **💡 Data Source:** Nguồn dữ liệu
- **🔄 Real-time:** Trạng thái real-time
- **📊 Active Tickers:** Số mã đang hoạt động
- **🕐 Last Update:** Thời gian cập nhật cuối

---

## 🔧 **TROUBLESHOOTING**

### **Dashboard không hiển thị dữ liệu:**

#### **1. Kiểm tra container:**
```bash
docker ps | grep stock-dashboard
```

#### **2. Kiểm tra logs:**
```bash
docker logs stock-dashboard --tail 20
```

#### **3. Restart dashboard:**
```bash
docker restart stock-dashboard
```

#### **4. Sử dụng Demo Dashboard:**
```bash
./scripts/launch_dashboard.sh
# Chọn option 1: Demo Dashboard
```

### **Database connection issues:**

#### **1. Kiểm tra PostgreSQL:**
```bash
docker ps | grep postgres
```

#### **2. Test connection:**
```bash
docker exec postgres psql -U admin -d stock_db -c "SELECT COUNT(*) FROM historical_prices;"
```

#### **3. Sử dụng Demo Dashboard:**
- Demo dashboard không cần database
- Hoạt động với dữ liệu mẫu

---

## 📱 **RESPONSIVE DESIGN**

### **Desktop:**
- **Layout:** Wide (full width)
- **Charts:** Large, interactive
- **Tables:** Full data display

### **Mobile:**
- **Layout:** Responsive
- **Charts:** Touch-friendly
- **Tables:** Scrollable

---

## 🎨 **CUSTOMIZATION**

### **Themes:**
- **Dark Theme:** Professional, easy on eyes
- **Colors:** Blue accent (#00A9FF)
- **Fonts:** Clean, readable

### **Charts:**
- **Plotly:** Interactive, responsive
- **Colors:** Professional palette
- **Animations:** Smooth transitions

---

## 🚀 **PERFORMANCE**

### **Optimization:**
- **Caching:** Data cached for 1 minute
- **Lazy Loading:** Load data on demand
- **Efficient Queries:** Optimized database queries

### **Scalability:**
- **Multiple Tickers:** Support 100+ tickers
- **Historical Data:** 30+ days of data
- **Real-time Updates:** 30-second refresh

---

## 📞 **HỖ TRỢ**

### **Scripts hỗ trợ:**
```bash
# Launch dashboard
./scripts/launch_dashboard.sh

# Check status
./scripts/script_manager.sh

# Database connection
./scripts/connect_postgres.sh
```

### **Logs và debugging:**
```bash
# Dashboard logs
docker logs stock-dashboard

# System status
./manage.sh status
```

---

## 🎊 **TỔNG KẾT**

### **✅ Dashboard Features:**
- **📊 Market Overview** - Tổng quan thị trường
- **📈 Individual Analysis** - Phân tích chi tiết
- **📦 Volume Analysis** - Phân tích khối lượng
- **🔄 Real-time Updates** - Cập nhật thời gian thực
- **📱 Responsive Design** - Tương thích mọi thiết bị

### **🎯 Recommendations:**
1. **Sử dụng Demo Dashboard** để test và demo
2. **Hybrid Dashboard** cho dữ liệu thực tế
3. **Auto refresh** để theo dõi real-time
4. **Search function** để tìm mã cụ thể

**Dashboard của bạn đã sẵn sàng sử dụng!** 🚀


