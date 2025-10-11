#!/bin/bash

# =============================================================================
# SCRIPT MONITOR TIẾN TRÌNH FETCH DỮ LIỆU
# =============================================================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}📊 MONITOR TIẾN TRÌNH FETCH DỮ LIỆU${NC}"
echo -e "${YELLOW}====================================${NC}"

while true; do
    # Kiểm tra container có đang chạy không
    if ! docker ps | grep -q data-fetcher; then
        echo -e "${GREEN}✅ Data fetcher đã hoàn thành!${NC}"
        break
    fi
    
    # Lấy log mới nhất
    latest_log=$(docker logs data-fetcher --tail 1 2>/dev/null)
    
    if [[ $latest_log == *"Progress:"* ]]; then
        # Extract progress info
        progress=$(echo "$latest_log" | grep -o "Progress: [0-9]*/[0-9]*" | cut -d' ' -f2)
        total=$(echo "$latest_log" | grep -o "Progress: [0-9]*/[0-9]*" | cut -d' ' -f3 | cut -d'/' -f2)
        prices=$(echo "$latest_log" | grep -o "Prices: [0-9,]*" | cut -d' ' -f2)
        success=$(echo "$latest_log" | grep -o "Success: [0-9]*" | cut -d' ' -f2)
        failed=$(echo "$latest_log" | grep -o "Failed: [0-9]*" | cut -d' ' -f2)
        
        if [ ! -z "$progress" ] && [ ! -z "$total" ]; then
            percentage=$((progress * 100 / total))
            echo -e "${GREEN}📈 Tiến trình: $progress/$total ($percentage%) - Prices: $prices - Success: $success - Failed: $failed${NC}"
        fi
    fi
    
    sleep 30
done

echo -e "${BLUE}🔍 Kiểm tra dữ liệu cuối cùng...${NC}"
sleep 5

# Kiểm tra dữ liệu cuối cùng
record_count=$(docker exec postgres psql -U admin -d stock_db -t -c "SELECT COUNT(*) FROM historical_prices;" 2>/dev/null | tr -d ' ')
ticker_count=$(docker exec postgres psql -U admin -d stock_db -t -c "SELECT COUNT(DISTINCT ticker) FROM historical_prices;" 2>/dev/null | tr -d ' ')

echo -e "${GREEN}📊 KẾT QUẢ CUỐI CÙNG:${NC}"
echo -e "   • Historical prices: ${GREEN}$record_count${NC} records"
echo -e "   • Unique tickers: ${GREEN}$ticker_count${NC} tickers"
echo -e "${GREEN}🎉 Fetch dữ liệu hoàn tất!${NC}"
