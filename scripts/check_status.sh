#!/bin/bash
################################################################################
# Quick Status Check - Vietnam Stock Pipeline
# Shows overview of all services in a clean format
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Vietnam Stock Pipeline - Status Dashboard             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check systemd service
echo -e "${YELLOW}📋 Systemd Service Status:${NC}"
if systemctl is-active --quiet vietnam-stock-pipeline 2>/dev/null; then
    echo -e "   ${GREEN}✅ vietnam-stock-pipeline: RUNNING${NC}"
    uptime=$(systemctl show vietnam-stock-pipeline --property=ActiveEnterTimestamp --value)
    echo -e "   ⏱️  Started: $uptime"
elif systemctl is-active --quiet vietnam-stock-pipeline-with-snowflake 2>/dev/null; then
    echo -e "   ${GREEN}✅ vietnam-stock-pipeline-with-snowflake: RUNNING${NC}"
    uptime=$(systemctl show vietnam-stock-pipeline-with-snowflake --property=ActiveEnterTimestamp --value)
    echo -e "   ⏱️  Started: $uptime"
else
    echo -e "   ${RED}❌ No systemd service running${NC}"
fi
echo ""

# Check Docker containers
echo -e "${YELLOW}🐳 Docker Containers:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "NAME|stock|kafka|postgres|zookeeper|spark|pgadmin" || echo "   No containers running"
echo ""

# Check data stats
echo -e "${YELLOW}📊 Database Statistics:${NC}"
if docker exec postgres psql -U admin -d stock_db -c "SELECT 1" > /dev/null 2>&1; then
    docker exec postgres psql -U admin -d stock_db -t -c "
        SELECT 
            'Total Records: ' || COUNT(*) || E'\n' ||
            'Unique Tickers: ' || COUNT(DISTINCT ticker) || E'\n' ||
            'Latest Update: ' || MAX(time) || E'\n' ||
            'Earliest Record: ' || MIN(time)
        FROM realtime_quotes;
    " 2>/dev/null | sed 's/^/   /'
else
    echo -e "   ${RED}❌ Cannot connect to database${NC}"
fi
echo ""

# Top tickers
echo -e "${YELLOW}📈 Top 5 Tickers by Record Count:${NC}"
if docker exec postgres psql -U admin -d stock_db -c "SELECT 1" > /dev/null 2>&1; then
    docker exec postgres psql -U admin -d stock_db -t -c "
        SELECT ticker || ': ' || COUNT(*) || ' records'
        FROM realtime_quotes
        GROUP BY ticker
        ORDER BY COUNT(*) DESC
        LIMIT 5;
    " 2>/dev/null | sed 's/^/   /'
else
    echo -e "   ${RED}❌ Cannot query database${NC}"
fi
echo ""

# Resource usage
echo -e "${YELLOW}💻 Resource Usage:${NC}"
echo "   CPU & Memory:"
docker stats --no-stream --format "   {{.Name}}: CPU {{.CPUPerc}} | MEM {{.MemUsage}}" 2>/dev/null | head -6 || echo "   Cannot get stats"
echo ""

# Disk usage
echo -e "${YELLOW}💾 Disk Usage:${NC}"
df -h /u01/Vanh_projects/vietnam-stock-pipeline 2>/dev/null | tail -1 | awk '{print "   " $1 ": " $3 " used / " $2 " total (" $5 " full)"}' || echo "   Cannot get disk info"
echo ""

# Service URLs
echo -e "${YELLOW}🌐 Service URLs:${NC}"
echo "   Dashboard:  http://localhost:8501"
echo "   pgAdmin:    http://localhost:5050"
echo "   Spark UI:   http://localhost:8080"
echo ""

# Recent logs
echo -e "${YELLOW}📝 Recent Logs (last 5 lines):${NC}"
journalctl -u vietnam-stock-pipeline -n 5 --no-pager 2>/dev/null | sed 's/^/   /' || \
journalctl -u vietnam-stock-pipeline-with-snowflake -n 5 --no-pager 2>/dev/null | sed 's/^/   /' || \
echo "   No systemd logs available"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "Last checked: $(date)"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

