#!/bin/bash
################################################################################
# Uninstall Production Setup - Vietnam Stock Pipeline
# 
# This script removes systemd service and cron jobs
# WARNING: This does NOT delete data or Docker volumes
################################################################################

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║     Vietnam Stock Pipeline - UNINSTALL PRODUCTION         ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}⚠️  WARNING: This will remove systemd services and cron jobs${NC}"
echo -e "${YELLOW}⚠️  Data and Docker volumes will NOT be deleted${NC}"
echo ""

read -p "Are you sure you want to uninstall? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled"
    exit 0
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (use sudo)${NC}"
    exit 1
fi

echo ""
echo "1️⃣  Stopping services..."

# Stop and disable systemd services
for service in vietnam-stock-pipeline vietnam-stock-pipeline-with-snowflake; do
    if systemctl is-active --quiet "$service" 2>/dev/null; then
        echo "   Stopping $service..."
        systemctl stop "$service"
    fi
    
    if systemctl is-enabled --quiet "$service" 2>/dev/null; then
        echo "   Disabling $service..."
        systemctl disable "$service"
    fi
    
    if [ -f "/etc/systemd/system/$service.service" ]; then
        echo "   Removing $service.service..."
        rm -f "/etc/systemd/system/$service.service"
    fi
done

# Reload systemd
echo "   Reloading systemd..."
systemctl daemon-reload

echo -e "${GREEN}✅ Systemd services removed${NC}"

echo ""
echo "2️⃣  Removing cron jobs..."

# Remove cron jobs
crontab -l 2>/dev/null | grep -v "vietnam-stock" | grep -v "Vietnam Stock Pipeline" | crontab - 2>/dev/null || true

echo -e "${GREEN}✅ Cron jobs removed${NC}"

echo ""
echo "3️⃣  Stopping Docker containers..."

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
docker-compose --profile snowflake down

echo -e "${GREEN}✅ Docker containers stopped${NC}"

echo ""
echo -e "${YELLOW}📋 What was removed:${NC}"
echo "   ✅ Systemd services"
echo "   ✅ Cron jobs"
echo "   ✅ Docker containers (stopped)"
echo ""
echo -e "${YELLOW}📋 What was NOT removed:${NC}"
echo "   ℹ️  Docker volumes (data still preserved)"
echo "   ℹ️  Project files"
echo "   ℹ️  Log files"
echo ""

read -p "Do you want to remove Docker volumes (THIS WILL DELETE ALL DATA)? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removing Docker volumes..."
    docker-compose --profile snowflake down -v
    echo -e "${RED}✅ All data deleted${NC}"
else
    echo "ℹ️  Data preserved in Docker volumes"
fi

echo ""
echo -e "${GREEN}✅ Uninstall complete!${NC}"
echo ""
echo "To reinstall, run: sudo ./setup_production.sh"

