#!/bin/bash

# =============================================================================
# SCRIPT LỆNH NHANH - VIETNAM STOCK PIPELINE
# =============================================================================
# Mô tả: Script ngắn gọn với các lệnh cơ bản nhất
# =============================================================================

# Màu sắc
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 VIETNAM STOCK PIPELINE - LỆNH NHANH${NC}"
echo -e "${YELLOW}=====================================${NC}"

case "$1" in
    "start"|"chay"|"bat")
        echo -e "${GREEN}🚀 Khởi động hệ thống...${NC}"
        docker-compose up -d
        echo -e "${GREEN}✅ Đã khởi động! Dashboard: http://localhost:8501${NC}"
        ;;
    "stop"|"dung"|"tat")
        echo -e "${RED}🛑 Dừng hệ thống...${NC}"
        docker-compose down
        echo -e "${GREEN}✅ Đã dừng!${NC}"
        ;;
    "restart"|"khoi-dong-lai")
        echo -e "${YELLOW}🔄 Khởi động lại hệ thống...${NC}"
        docker-compose down
        docker-compose up -d
        echo -e "${GREEN}✅ Đã khởi động lại!${NC}"
        ;;
    "status"|"trang-thai")
        echo -e "${BLUE}📊 Trạng thái hệ thống:${NC}"
        docker-compose ps
        ;;
    "logs"|"xem-logs")
        echo -e "${BLUE}📝 Xem logs hệ thống:${NC}"
        docker-compose logs -f
        ;;
    "clean"|"don-dep")
        echo -e "${RED}🧹 Dọn dẹp hệ thống (XÓA TẤT CẢ DỮ LIỆU!)...${NC}"
        read -p "Bạn có chắc chắn? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            docker-compose down -v
            docker system prune -f
            echo -e "${GREEN}✅ Đã dọn dẹp!${NC}"
        fi
        ;;
    "backup"|"sao-luu")
        echo -e "${BLUE}💾 Backup dữ liệu...${NC}"
        mkdir -p backups
        timestamp=$(date +%Y%m%d_%H%M%S)
        docker exec postgres pg_dump -U admin stock_db | gzip > "backups/stock_db_${timestamp}.sql.gz"
        echo -e "${GREEN}✅ Backup hoàn tất: backups/stock_db_${timestamp}.sql.gz${NC}"
        ;;
    "dashboard"|"web")
        echo -e "${GREEN}🌐 Mở Dashboard...${NC}"
        xdg-open http://localhost:8501 2>/dev/null || open http://localhost:8501 2>/dev/null || echo -e "${YELLOW}💡 Mở: http://localhost:8501${NC}"
        ;;
    "help"|"tro-giup"|"")
        echo -e "${YELLOW}📋 CÁCH SỬ DỤNG:${NC}"
        echo -e "${GREEN}./lenh_nhanh.sh start${NC}     - Khởi động hệ thống"
        echo -e "${GREEN}./lenh_nhanh.sh stop${NC}      - Dừng hệ thống"
        echo -e "${GREEN}./lenh_nhanh.sh restart${NC}   - Khởi động lại"
        echo -e "${GREEN}./lenh_nhanh.sh status${NC}    - Xem trạng thái"
        echo -e "${GREEN}./lenh_nhanh.sh logs${NC}      - Xem logs"
        echo -e "${GREEN}./lenh_nhanh.sh clean${NC}     - Dọn dẹp (XÓA DỮ LIỆU!)"
        echo -e "${GREEN}./lenh_nhanh.sh backup${NC}    - Backup dữ liệu"
        echo -e "${GREEN}./lenh_nhanh.sh dashboard${NC} - Mở giao diện web"
        echo ""
        echo -e "${BLUE}💡 Ví dụ:${NC}"
        echo -e "   ${GREEN}./lenh_nhanh.sh start${NC}"
        echo -e "   ${GREEN}./lenh_nhanh.sh stop${NC}"
        ;;
    *)
        echo -e "${RED}❌ Lệnh không hợp lệ: $1${NC}"
        echo -e "${YELLOW}💡 Sử dụng: ./lenh_nhanh.sh help${NC}"
        ;;
esac
