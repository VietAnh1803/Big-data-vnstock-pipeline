#!/bin/bash

# =============================================================================
# SCRIPT SETUP VIETNAM STOCK PIPELINE VỚI DỮ LIỆU ĐẦY ĐỦ
# =============================================================================
# Mô tả: Script tự động setup hệ thống và import dữ liệu cho bạn bè
# =============================================================================

# Màu sắc
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 VIETNAM STOCK PIPELINE - SETUP VỚI DỮ LIỆU${NC}"
echo -e "${YELLOW}=============================================${NC}"

# Kiểm tra Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker chưa được cài đặt!${NC}"
    echo -e "${YELLOW}💡 Hãy cài đặt Docker trước: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose chưa được cài đặt!${NC}"
    echo -e "${YELLOW}💡 Hãy cài đặt Docker Compose trước${NC}"
    exit 1
fi

# Kiểm tra Docker daemon
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon chưa chạy!${NC}"
    echo -e "${YELLOW}💡 Hãy khởi động Docker: sudo systemctl start docker${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker đã sẵn sàng${NC}"

# Tạo thư mục cần thiết
echo -e "${BLUE}📁 Tạo thư mục cần thiết...${NC}"
mkdir -p logs
mkdir -p backups

# Build và khởi động services (trừ dashboard)
echo -e "${BLUE}🏗️ Build và khởi động services...${NC}"
docker-compose build
docker-compose up -d postgres kafka zookeeper

# Chờ PostgreSQL sẵn sàng
echo -e "${YELLOW}⏳ Chờ PostgreSQL khởi động...${NC}"
sleep 30

# Kiểm tra PostgreSQL
echo -e "${BLUE}🔍 Kiểm tra PostgreSQL...${NC}"
for i in {1..30}; do
    if docker exec postgres pg_isready -U admin -d stock_db &>/dev/null; then
        echo -e "${GREEN}✅ PostgreSQL đã sẵn sàng${NC}"
        break
    fi
    echo -e "${YELLOW}⏳ Chờ PostgreSQL... ($i/30)${NC}"
    sleep 2
done

# Import dữ liệu
echo -e "${BLUE}📥 Import dữ liệu từ file backup...${NC}"
if [ -f "data/stock_db_full.sql" ]; then
    docker exec -i postgres psql -U admin -d stock_db < data/stock_db_full.sql
    echo -e "${GREEN}✅ Dữ liệu đã được import thành công${NC}"
else
    echo -e "${RED}❌ Không tìm thấy file data/stock_db_full.sql${NC}"
    echo -e "${YELLOW}💡 Hãy đảm bảo file dữ liệu có trong thư mục data/${NC}"
    exit 1
fi

# Khởi động các services còn lại
echo -e "${BLUE}🚀 Khởi động các services còn lại...${NC}"
docker-compose up -d

# Chờ tất cả services sẵn sàng
echo -e "${YELLOW}⏳ Chờ tất cả services khởi động...${NC}"
sleep 20

# Kiểm tra trạng thái
echo -e "${BLUE}📊 Kiểm tra trạng thái hệ thống...${NC}"
docker-compose ps

# Kiểm tra dữ liệu
echo -e "${BLUE}🔍 Kiểm tra dữ liệu...${NC}"
record_count=$(docker exec postgres psql -U admin -d stock_db -t -c "SELECT COUNT(*) FROM realtime_quotes;" 2>/dev/null | tr -d ' ')
ticker_count=$(docker exec postgres psql -U admin -d stock_db -t -c "SELECT COUNT(DISTINCT ticker) FROM realtime_quotes;" 2>/dev/null | tr -d ' ')

echo -e "${GREEN}📈 Dữ liệu đã sẵn sàng:${NC}"
echo -e "   • Tổng số records: ${GREEN}$record_count${NC}"
echo -e "   • Số tickers: ${GREEN}$ticker_count${NC}"

# Hiển thị thông tin truy cập
echo -e "${BLUE}🌐 THÔNG TIN TRUY CẬP:${NC}"
echo -e "${GREEN}📊 Dashboard:${NC} http://localhost:8501"
echo -e "${GREEN}🗄️ pgAdmin:${NC} http://localhost:5050"
echo -e "${GREEN}⚡ Spark Master:${NC} http://localhost:8080"
echo -e "${GREEN}⚡ Spark Worker:${NC} http://localhost:8081"

echo -e "${BLUE}🎯 CÁCH SỬ DỤNG:${NC}"
echo -e "${GREEN}./lenh_nhanh.sh start${NC}     - Khởi động hệ thống"
echo -e "${GREEN}./lenh_nhanh.sh stop${NC}      - Dừng hệ thống"
echo -e "${GREEN}./lenh_nhanh.sh status${NC}    - Xem trạng thái"
echo -e "${GREEN}./lenh_nhanh.sh dashboard${NC} - Mở dashboard"

echo -e "${GREEN}🎉 SETUP HOÀN TẤT! Hệ thống đã sẵn sàng sử dụng.${NC}"
