#!/bin/bash

# =============================================================================
# SCRIPT QUẢN LÝ HỆ THỐNG VIETNAM STOCK PIPELINE
# =============================================================================
# Tác giả: AI Assistant
# Mô tả: Script tiếng Việt để quản lý toàn bộ hệ thống pipeline chứng khoán
# =============================================================================

# Màu sắc cho output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Hàm hiển thị banner
show_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                VIETNAM STOCK PIPELINE                        ║"
    echo "║              HỆ THỐNG QUẢN LÝ CHỨNG KHOÁN                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Hàm hiển thị menu chính
show_menu() {
    echo -e "${YELLOW}📋 MENU CHÍNH:${NC}"
    echo -e "${GREEN}1.${NC} 🚀 Khởi động hệ thống (Development)"
    echo -e "${GREEN}2.${NC} 🏭 Khởi động hệ thống (Production)"
    echo -e "${GREEN}3.${NC} 🛑 Dừng hệ thống"
    echo -e "${GREEN}4.${NC} 🔄 Khởi động lại hệ thống"
    echo -e "${GREEN}5.${NC} 📊 Kiểm tra trạng thái hệ thống"
    echo -e "${GREEN}6.${NC} 📝 Xem logs hệ thống"
    echo -e "${GREEN}7.${NC} 🧹 Dọn dẹp hệ thống"
    echo -e "${GREEN}8.${NC} 💾 Backup dữ liệu"
    echo -e "${GREEN}9.${NC} 🌐 Mở giao diện web"
    echo -e "${GREEN}10.${NC} 📈 Quản lý dữ liệu lớn (Big Data)"
    echo -e "${GREEN}11.${NC} ❄️ Quản lý Snowflake"
    echo -e "${GREEN}12.${NC} 🔧 Cài đặt Production"
    echo -e "${GREEN}0.${NC} 🚪 Thoát"
    echo ""
}

# Hàm hiển thị menu giao diện web
show_web_menu() {
    echo -e "${YELLOW}🌐 GIAO DIỆN WEB:${NC}"
    echo -e "${GREEN}1.${NC} 📊 Dashboard chính (http://localhost:8501)"
    echo -e "${GREEN}2.${NC} 🗄️ pgAdmin (http://localhost:5050)"
    echo -e "${GREEN}3.${NC} ⚡ Spark Master UI (http://localhost:8080)"
    echo -e "${GREEN}4.${NC} ⚡ Spark Worker UI (http://localhost:8081)"
    echo -e "${GREEN}0.${NC} 🔙 Quay lại menu chính"
    echo ""
}

# Hàm hiển thị menu Big Data
show_bigdata_menu() {
    echo -e "${YELLOW}📈 QUẢN LÝ DỮ LIỆU LỚN:${NC}"
    echo -e "${GREEN}1.${NC} 📥 Tải tất cả dữ liệu từ vnstock"
    echo -e "${GREEN}2.${NC} 🔄 Đồng bộ dữ liệu lên Snowflake"
    echo -e "${GREEN}3.${NC} 🚀 Thiết lập hoàn chỉnh Big Data"
    echo -e "${GREEN}4.${NC} 📊 Xem thống kê dữ liệu"
    echo -e "${GREEN}0.${NC} 🔙 Quay lại menu chính"
    echo ""
}

# Hàm hiển thị menu Snowflake
show_snowflake_menu() {
    echo -e "${YELLOW}❄️ QUẢN LÝ SNOWFLAKE:${NC}"
    echo -e "${GREEN}1.${NC} 🚀 Khởi động với Snowflake sync"
    echo -e "${GREEN}2.${NC} 🔄 Đồng bộ dữ liệu lên Snowflake"
    echo -e "${GREEN}3.${NC} 📝 Xem logs Snowflake"
    echo -e "${GREEN}4.${NC} 🧪 Test kết nối Snowflake"
    echo -e "${GREEN}0.${NC} 🔙 Quay lại menu chính"
    echo ""
}

# Hàm kiểm tra Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker chưa được cài đặt!${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose chưa được cài đặt!${NC}"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker daemon chưa chạy!${NC}"
        echo -e "${YELLOW}💡 Hãy khởi động Docker: sudo systemctl start docker${NC}"
        exit 1
    fi
}

# Hàm khởi động hệ thống development
start_development() {
    echo -e "${BLUE}🚀 Đang khởi động hệ thống (Development)...${NC}"
    echo -e "${YELLOW}⏳ Vui lòng chờ, quá trình này có thể mất vài phút...${NC}"
    
    # Build và khởi động
    docker-compose build
    docker-compose up -d
    
    echo -e "${GREEN}✅ Hệ thống đã khởi động thành công!${NC}"
    echo -e "${CYAN}📋 Các dịch vụ đang chạy:${NC}"
    echo -e "   • Zookeeper: localhost:2181"
    echo -e "   • Kafka: localhost:9092"
    echo -e "   • PostgreSQL: localhost:5432"
    echo -e "   • Spark Master: localhost:8080"
    echo -e "   • Spark Worker: localhost:8081"
    echo -e "   • Dashboard: localhost:8501"
    echo -e "   • pgAdmin: localhost:5050"
    echo ""
    echo -e "${YELLOW}💡 Sử dụng lệnh '5' để kiểm tra trạng thái chi tiết${NC}"
}

# Hàm khởi động hệ thống production
start_production() {
    echo -e "${BLUE}🏭 Đang khởi động hệ thống (Production)...${NC}"
    
    # Kiểm tra systemd service
    if systemctl is-active --quiet vietnam-stock-pipeline; then
        echo -e "${GREEN}✅ Service production đã chạy${NC}"
        sudo systemctl start vietnam-stock-pipeline
    elif systemctl is-active --quiet vietnam-stock-pipeline-with-snowflake; then
        echo -e "${GREEN}✅ Service production với Snowflake đã chạy${NC}"
        sudo systemctl start vietnam-stock-pipeline-with-snowflake
    else
        echo -e "${YELLOW}⚠️ Chưa có service production. Đang khởi động development mode...${NC}"
        start_development
    fi
}

# Hàm dừng hệ thống
stop_system() {
    echo -e "${RED}🛑 Đang dừng hệ thống...${NC}"
    
    # Dừng production service nếu có
    if systemctl is-active --quiet vietnam-stock-pipeline; then
        echo -e "${YELLOW}⏹️ Dừng production service...${NC}"
        sudo systemctl stop vietnam-stock-pipeline
    fi
    
    if systemctl is-active --quiet vietnam-stock-pipeline-with-snowflake; then
        echo -e "${YELLOW}⏹️ Dừng production service với Snowflake...${NC}"
        sudo systemctl stop vietnam-stock-pipeline-with-snowflake
    fi
    
    # Dừng Docker containers
    echo -e "${YELLOW}⏹️ Dừng Docker containers...${NC}"
    docker-compose down
    
    echo -e "${GREEN}✅ Hệ thống đã dừng thành công!${NC}"
}

# Hàm khởi động lại hệ thống
restart_system() {
    echo -e "${YELLOW}🔄 Đang khởi động lại hệ thống...${NC}"
    stop_system
    sleep 3
    start_development
}

# Hàm kiểm tra trạng thái
check_status() {
    echo -e "${BLUE}📊 KIỂM TRA TRẠNG THÁI HỆ THỐNG${NC}"
    echo -e "${CYAN}================================${NC}"
    
    # Kiểm tra Docker containers
    echo -e "${YELLOW}🐳 Docker Containers:${NC}"
    docker-compose ps
    
    echo ""
    
    # Kiểm tra systemd services
    echo -e "${YELLOW}⚙️ Systemd Services:${NC}"
    if systemctl is-active --quiet vietnam-stock-pipeline; then
        echo -e "${GREEN}✅ vietnam-stock-pipeline: ACTIVE${NC}"
    elif systemctl is-active --quiet vietnam-stock-pipeline-with-snowflake; then
        echo -e "${GREEN}✅ vietnam-stock-pipeline-with-snowflake: ACTIVE${NC}"
    else
        echo -e "${RED}❌ Không có service production nào đang chạy${NC}"
    fi
    
    echo ""
    
    # Kiểm tra ports
    echo -e "${YELLOW}🌐 Ports đang sử dụng:${NC}"
    netstat -tlnp 2>/dev/null | grep -E ':(2181|5432|8080|8081|8501|5050|9092)' | while read line; do
        echo -e "   ${GREEN}$line${NC}"
    done
    
    echo ""
    
    # Kiểm tra database
    echo -e "${YELLOW}🗄️ Database Status:${NC}"
    if docker exec postgres pg_isready -U admin -d stock_db &>/dev/null; then
        echo -e "${GREEN}✅ PostgreSQL: CONNECTED${NC}"
        
        # Đếm records
        count=$(docker exec postgres psql -U admin -d stock_db -t -c "SELECT COUNT(*) FROM realtime_quotes;" 2>/dev/null | tr -d ' ')
        if [ ! -z "$count" ] && [ "$count" != "0" ]; then
            echo -e "   📊 Số lượng quotes: ${GREEN}$count${NC}"
        fi
    else
        echo -e "${RED}❌ PostgreSQL: DISCONNECTED${NC}"
    fi
}

# Hàm xem logs
view_logs() {
    echo -e "${BLUE}📝 XEM LOGS HỆ THỐNG${NC}"
    echo -e "${CYAN}===================${NC}"
    echo -e "${GREEN}1.${NC} 📊 Tất cả logs"
    echo -e "${GREEN}2.${NC} 🏭 Producer logs"
    echo -e "${GREEN}3.${NC} 🔄 Consumer logs"
    echo -e "${GREEN}4.${NC} 📈 Dashboard logs"
    echo -e "${GREEN}5.${NC} ❄️ Snowflake logs"
    echo -e "${GREEN}6.${NC} ⚙️ Production logs (systemd)"
    echo -e "${GREEN}0.${NC} 🔙 Quay lại"
    echo ""
    
    read -p "Chọn loại logs (0-6): " log_choice
    
    case $log_choice in
        1) docker-compose logs -f ;;
        2) docker-compose logs -f producer ;;
        3) docker-compose logs -f consumer ;;
        4) docker-compose logs -f dashboard ;;
        5) docker-compose logs -f snowflake-sync ;;
        6) sudo journalctl -u vietnam-stock-pipeline -f || sudo journalctl -u vietnam-stock-pipeline-with-snowflake -f ;;
        0) return ;;
        *) echo -e "${RED}❌ Lựa chọn không hợp lệ!${NC}" ;;
    esac
}

# Hàm dọn dẹp hệ thống
clean_system() {
    echo -e "${YELLOW}🧹 DỌN DẸP HỆ THỐNG${NC}"
    echo -e "${CYAN}===================${NC}"
    echo -e "${RED}⚠️ CẢNH BÁO: Thao tác này sẽ xóa tất cả dữ liệu!${NC}"
    echo -e "${YELLOW}Bạn có chắc chắn muốn tiếp tục? (y/N):${NC}"
    read -r confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}⏳ Đang dọn dẹp...${NC}"
        docker-compose down -v
        docker system prune -f
        echo -e "${GREEN}✅ Dọn dẹp hoàn tất!${NC}"
    else
        echo -e "${BLUE}ℹ️ Hủy bỏ dọn dẹp${NC}"
    fi
}

# Hàm backup dữ liệu
backup_data() {
    echo -e "${BLUE}💾 BACKUP DỮ LIỆU${NC}"
    echo -e "${CYAN}=================${NC}"
    
    # Tạo thư mục backup
    mkdir -p backups
    
    # Backup database
    echo -e "${YELLOW}⏳ Đang backup database...${NC}"
    timestamp=$(date +%Y%m%d_%H%M%S)
    docker exec postgres pg_dump -U admin stock_db | gzip > "backups/stock_db_${timestamp}.sql.gz"
    
    # Backup volumes
    echo -e "${YELLOW}⏳ Đang backup volumes...${NC}"
    docker run --rm -v vietnam-stock-pipeline_postgres-data:/data -v "$(pwd)/backups:/backup" alpine tar czf "/backup/postgres-data-${timestamp}.tar.gz" -C /data .
    
    echo -e "${GREEN}✅ Backup hoàn tất!${NC}"
    echo -e "${CYAN}📁 Files backup:${NC}"
    echo -e "   • Database: ${GREEN}backups/stock_db_${timestamp}.sql.gz${NC}"
    echo -e "   • Volumes: ${GREEN}backups/postgres-data-${timestamp}.tar.gz${NC}"
}

# Hàm mở giao diện web
open_web_interfaces() {
    while true; do
        show_web_menu
        read -p "Chọn giao diện (0-4): " web_choice
        
        case $web_choice in
            1) 
                echo -e "${GREEN}🌐 Mở Dashboard...${NC}"
                xdg-open http://localhost:8501 2>/dev/null || open http://localhost:8501 2>/dev/null || echo -e "${YELLOW}💡 Vui lòng mở: http://localhost:8501${NC}"
                ;;
            2) 
                echo -e "${GREEN}🌐 Mở pgAdmin...${NC}"
                xdg-open http://localhost:5050 2>/dev/null || open http://localhost:5050 2>/dev/null || echo -e "${YELLOW}💡 Vui lòng mở: http://localhost:5050${NC}"
                ;;
            3) 
                echo -e "${GREEN}🌐 Mở Spark Master UI...${NC}"
                xdg-open http://localhost:8080 2>/dev/null || open http://localhost:8080 2>/dev/null || echo -e "${YELLOW}💡 Vui lòng mở: http://localhost:8080${NC}"
                ;;
            4) 
                echo -e "${GREEN}🌐 Mở Spark Worker UI...${NC}"
                xdg-open http://localhost:8081 2>/dev/null || open http://localhost:8081 2>/dev/null || echo -e "${YELLOW}💡 Vui lòng mở: http://localhost:8081${NC}"
                ;;
            0) break ;;
            *) echo -e "${RED}❌ Lựa chọn không hợp lệ!${NC}" ;;
        esac
        echo ""
    done
}

# Hàm quản lý Big Data
manage_bigdata() {
    while true; do
        show_bigdata_menu
        read -p "Chọn tác vụ (0-4): " bigdata_choice
        
        case $bigdata_choice in
            1) 
                echo -e "${BLUE}📥 Tải tất cả dữ liệu từ vnstock...${NC}"
                echo -e "${YELLOW}⚠️ Quá trình này có thể mất rất nhiều thời gian (1000+ tickers)${NC}"
                read -p "Bạn có chắc chắn muốn tiếp tục? (y/N): " confirm
                if [[ $confirm =~ ^[Yy]$ ]]; then
                    docker compose --profile data-fetch up --build data-fetcher
                fi
                ;;
            2) 
                echo -e "${BLUE}🔄 Đồng bộ dữ liệu lên Snowflake...${NC}"
                make sync-snowflake
                ;;
            3) 
                echo -e "${BLUE}🚀 Thiết lập hoàn chỉnh Big Data...${NC}"
                make big-data-setup
                ;;
            4) 
                echo -e "${BLUE}📊 Thống kê dữ liệu:${NC}"
                make data-stats
                ;;
            0) break ;;
            *) echo -e "${RED}❌ Lựa chọn không hợp lệ!${NC}" ;;
        esac
        echo ""
    done
}

# Hàm quản lý Snowflake
manage_snowflake() {
    while true; do
        show_snowflake_menu
        read -p "Chọn tác vụ (0-4): " snowflake_choice
        
        case $snowflake_choice in
            1) 
                echo -e "${BLUE}🚀 Khởi động với Snowflake sync...${NC}"
                docker-compose --profile snowflake up -d
                ;;
            2) 
                echo -e "${BLUE}🔄 Đồng bộ dữ liệu lên Snowflake...${NC}"
                make sync-snowflake
                ;;
            3) 
                echo -e "${BLUE}📝 Xem logs Snowflake...${NC}"
                docker-compose logs -f snowflake-sync
                ;;
            4) 
                echo -e "${BLUE}🧪 Test kết nối Snowflake...${NC}"
                python test_snowflake_connection.py
                ;;
            0) break ;;
            *) echo -e "${RED}❌ Lựa chọn không hợp lệ!${NC}" ;;
        esac
        echo ""
    done
}

# Hàm cài đặt Production
setup_production() {
    echo -e "${BLUE}🔧 CÀI ĐẶT PRODUCTION${NC}"
    echo -e "${CYAN}=====================${NC}"
    echo -e "${GREEN}1.${NC} 🏭 Cài đặt Production cơ bản"
    echo -e "${GREEN}2.${NC} ❄️ Cài đặt Production với Snowflake"
    echo -e "${GREEN}3.${NC} 🗑️ Gỡ cài đặt Production"
    echo -e "${GREEN}0.${NC} 🔙 Quay lại menu chính"
    echo ""
    
    read -p "Chọn tùy chọn (0-3): " prod_choice
    
    case $prod_choice in
        1) 
            echo -e "${BLUE}🏭 Cài đặt Production cơ bản...${NC}"
            chmod +x setup_production.sh
            sudo ./setup_production.sh
            ;;
        2) 
            echo -e "${BLUE}❄️ Cài đặt Production với Snowflake...${NC}"
            chmod +x setup_production.sh
            sudo ./setup_production.sh --snowflake
            ;;
        3) 
            echo -e "${RED}🗑️ Gỡ cài đặt Production...${NC}"
            make prod-uninstall
            ;;
        0) return ;;
        *) echo -e "${RED}❌ Lựa chọn không hợp lệ!${NC}" ;;
    esac
}

# Hàm chính
main() {
    # Kiểm tra Docker
    check_docker
    
    # Hiển thị banner
    show_banner
    
    # Vòng lặp menu chính
    while true; do
        show_menu
        read -p "Chọn tác vụ (0-12): " choice
        echo ""
        
        case $choice in
            1) start_development ;;
            2) start_production ;;
            3) stop_system ;;
            4) restart_system ;;
            5) check_status ;;
            6) view_logs ;;
            7) clean_system ;;
            8) backup_data ;;
            9) open_web_interfaces ;;
            10) manage_bigdata ;;
            11) manage_snowflake ;;
            12) setup_production ;;
            0) 
                echo -e "${GREEN}👋 Tạm biệt!${NC}"
                exit 0
                ;;
            *) 
                echo -e "${RED}❌ Lựa chọn không hợp lệ! Vui lòng chọn từ 0-12.${NC}"
                ;;
        esac
        
        echo ""
        echo -e "${YELLOW}Nhấn Enter để tiếp tục...${NC}"
        read
        clear
        show_banner
    done
}

# Chạy hàm chính
main "$@"
