#!/bin/bash
################################################################################
# Production Demo - Vietnam Stock Pipeline
# 
# This script demonstrates the production capabilities without actually
# installing anything. Use this to see what will happen.
################################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

echo -e "${BLUE}"
cat << "EOF"
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║          Vietnam Stock Pipeline - Production Demo                 ║
║                                                                    ║
║      This demo shows what will happen when you run setup          ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo -e "${CYAN}⚡ What is this project?${NC}"
echo ""
echo "A fully automated data pipeline that:"
echo "  ✅ Fetches Vietnamese stock market data 24/7"
echo "  ✅ Stores in PostgreSQL for real-time access"
echo "  ✅ Syncs to Snowflake for analytics (optional)"
echo "  ✅ Provides interactive Streamlit dashboard"
echo "  ✅ Auto-restarts on failure"
echo "  ✅ Self-monitors and alerts"
echo ""
read -p "Press Enter to continue..."

clear
echo -e "${CYAN}📋 Step 1: System Requirements Check${NC}"
echo ""
echo "The setup script will check for:"
echo "  🔍 Docker"
echo "  🔍 Docker Compose"
echo "  🔍 systemd"
echo "  🔍 cron"
echo ""
echo "Let's simulate the check:"
sleep 2

if command -v docker &> /dev/null; then
    echo -e "  ${GREEN}✅ Docker: $(docker --version)${NC}"
else
    echo -e "  ${RED}❌ Docker: Not installed${NC}"
fi

if command -v docker-compose &> /dev/null; then
    echo -e "  ${GREEN}✅ Docker Compose: $(docker-compose --version)${NC}"
else
    echo -e "  ${RED}❌ Docker Compose: Not installed${NC}"
fi

if command -v systemctl &> /dev/null; then
    echo -e "  ${GREEN}✅ systemd: Available${NC}"
else
    echo -e "  ${RED}❌ systemd: Not available${NC}"
fi

echo ""
read -p "Press Enter to continue..."

clear
echo -e "${CYAN}⚙️  Step 2: Configuration${NC}"
echo ""
echo "The setup will create .env file with these settings:"
echo ""
cat << 'EOF'
  # PostgreSQL Configuration
  POSTGRES_DB=stock_db
  POSTGRES_USER=admin
  POSTGRES_PASSWORD=admin    ← Change this!
  
  # Producer (fetch interval)
  PRODUCER_INTERVAL=300      ← 5 minutes
  STOCK_SYMBOLS=             ← Empty = all stocks
  
  # Snowflake (optional)
  SNOWFLAKE_ACCOUNT=your_account
  SNOWFLAKE_USER=your_user
  SNOWFLAKE_PASSWORD=******
  
  # Sync interval
  SYNC_INTERVAL=300          ← 5 minutes
EOF
echo ""
echo -e "${YELLOW}💡 Tip: You can edit .env after setup to customize${NC}"
echo ""
read -p "Press Enter to continue..."

clear
echo -e "${CYAN}🔧 Step 3: Systemd Service Installation${NC}"
echo ""
echo "The setup will install a systemd service that:"
echo "  ✅ Starts automatically on server boot"
echo "  ✅ Restarts automatically if crashed"
echo "  ✅ Limits resources (8GB RAM, 4 CPU cores)"
echo "  ✅ Logs everything to systemd journal"
echo ""
echo "Service file location:"
echo "  /etc/systemd/system/vietnam-stock-pipeline.service"
echo ""
echo "Manage with:"
echo "  systemctl start vietnam-stock-pipeline"
echo "  systemctl stop vietnam-stock-pipeline"
echo "  systemctl restart vietnam-stock-pipeline"
echo "  systemctl status vietnam-stock-pipeline"
echo "  journalctl -u vietnam-stock-pipeline -f"
echo ""
read -p "Press Enter to continue..."

clear
echo -e "${CYAN}⏰ Step 4: Cron Jobs Setup${NC}"
echo ""
echo "Automated maintenance tasks:"
echo ""
echo -e "${GREEN}Every 5 minutes:${NC}"
echo "  → Health check all containers"
echo "  → Auto-restart if any service is down"
echo ""
echo -e "${GREEN}Daily at 2:00 AM:${NC}"
echo "  → Backup PostgreSQL database"
echo ""
echo -e "${GREEN}Daily at 6:00 AM:${NC}"
echo "  → Comprehensive health report"
echo ""
echo -e "${GREEN}Daily at 7:00 AM:${NC}"
echo "  → Check disk space (alert if >80%)"
echo ""
echo -e "${GREEN}Sunday at 3:00 AM:${NC}"
echo "  → Weekly restart (clear memory leaks)"
echo ""
echo -e "${GREEN}1st of month at 4:00 AM:${NC}"
echo "  → Clean old logs (>30 days)"
echo ""
read -p "Press Enter to continue..."

clear
echo -e "${CYAN}🐳 Step 5: Docker Containers${NC}"
echo ""
echo "The following containers will be started:"
echo ""
echo -e "${GREEN}Core Services:${NC}"
echo "  🔹 zookeeper        - Kafka coordination"
echo "  🔹 kafka            - Message broker"
echo "  🔹 postgres         - Real-time database"
echo "  🔹 stock-producer   - Data fetcher"
echo "  🔹 kafka-consumer   - Data processor"
echo "  🔹 stock-dashboard  - Streamlit UI"
echo ""
echo -e "${YELLOW}Optional Services:${NC}"
echo "  🔹 spark-master     - Spark cluster master"
echo "  🔹 spark-worker     - Spark cluster worker"
echo "  🔹 snowflake-sync   - Snowflake synchronization"
echo "  🔹 pgadmin          - PostgreSQL web UI"
echo ""
echo "All with:"
echo "  ✅ restart: unless-stopped"
echo "  ✅ Health checks"
echo "  ✅ Resource limits"
echo ""
read -p "Press Enter to continue..."

clear
echo -e "${CYAN}📊 Step 6: Data Flow${NC}"
echo ""
cat << 'EOF'
  ┌──────────────┐
  │  vnstock API │
  └──────┬───────┘
         │ Every 5 minutes
         ↓
  ┌──────────────┐
  │   Producer   │ ← Fetch stock quotes
  └──────┬───────┘
         │
         ↓
  ┌──────────────┐
  │    Kafka     │ ← Buffer messages
  └──────┬───────┘
         │
         ↓
  ┌──────────────┐
  │   Consumer   │ ← Process batch (100 records/10s)
  └──────┬───────┘
         │
         ↓
  ┌──────────────┐     Every 5 min     ┌──────────────┐
  │  PostgreSQL  │────────────────────→│  Snowflake   │
  └──────┬───────┘                     └──────────────┘
         │
         ↓
  ┌──────────────┐
  │  Dashboard   │ ← Real-time UI (auto-refresh: 3s)
  └──────────────┘
EOF
echo ""
read -p "Press Enter to continue..."

clear
echo -e "${CYAN}🌐 Step 7: Access Points${NC}"
echo ""
echo "After setup, you can access:"
echo ""
echo -e "${GREEN}From the server (localhost):${NC}"
echo "  📊 Dashboard:  http://localhost:8501"
echo "  🗄️  pgAdmin:   http://localhost:5050"
echo "  ⚡ Spark UI:   http://localhost:8080"
echo ""
echo -e "${GREEN}From remote machine (via SSH tunnel):${NC}"
echo "  On your laptop/desktop, run:"
echo "  ssh -L 8501:localhost:8501 -L 5050:localhost:5050 user@server-ip"
echo ""
echo "  Then access:"
echo "  📊 Dashboard:  http://localhost:8501"
echo "  🗄️  pgAdmin:   http://localhost:5050"
echo ""
echo -e "${YELLOW}🔒 Security: All services bind to 127.0.0.1 (localhost only)${NC}"
echo ""
read -p "Press Enter to continue..."

clear
echo -e "${CYAN}🔍 Step 8: Monitoring & Management${NC}"
echo ""
echo "You can manage the system with:"
echo ""
echo -e "${GREEN}Via Makefile (recommended):${NC}"
echo "  make prod-status         # Check status"
echo "  make prod-start          # Start services"
echo "  make prod-stop           # Stop services"
echo "  make prod-restart        # Restart services"
echo "  make prod-logs           # View logs"
echo "  make monitor             # Health check"
echo "  make backup              # Backup database"
echo ""
echo -e "${GREEN}Via systemctl:${NC}"
echo "  systemctl status vietnam-stock-pipeline"
echo "  systemctl restart vietnam-stock-pipeline"
echo "  journalctl -u vietnam-stock-pipeline -f"
echo ""
echo -e "${GREEN}Via scripts:${NC}"
echo "  bash scripts/check_status.sh"
echo "  bash scripts/monitor_services.sh"
echo "  bash scripts/healthcheck.sh"
echo ""
read -p "Press Enter to continue..."

clear
echo -e "${CYAN}💾 Step 9: Backup & Recovery${NC}"
echo ""
echo "Automatic backups:"
echo "  ✅ Daily at 2:00 AM → /backups/stock_db_YYYYMMDD.sql.gz"
echo ""
echo "Manual backup:"
echo "  make backup                    # Backup database"
echo "  make backup-volumes            # Backup Docker volumes"
echo ""
echo "Restore from backup:"
echo "  make prod-stop"
echo "  gunzip -c backups/stock_db_20250108.sql.gz | \\"
echo "    docker exec -i postgres psql -U admin -d stock_db"
echo "  make prod-start"
echo ""
read -p "Press Enter to continue..."

clear
echo -e "${CYAN}📚 Step 10: Documentation${NC}"
echo ""
echo "Comprehensive documentation has been created:"
echo ""
echo -e "${GREEN}Quick Start:${NC}"
echo "  📖 START_PRODUCTION.txt          ← Quick reference"
echo "  📖 QUICK_START_PRODUCTION.md     ← Hướng dẫn nhanh (VN)"
echo ""
echo -e "${GREEN}Detailed Guides:${NC}"
echo "  📖 PRODUCTION_GUIDE.md           ← Full guide (VN)"
echo "  📖 README_PRODUCTION.md          ← Production README (EN)"
echo "  📖 PRODUCTION_SETUP_SUMMARY.md   ← Setup summary"
echo ""
echo -e "${GREEN}Usage:${NC}"
echo "  cat START_PRODUCTION.txt"
echo "  cat QUICK_START_PRODUCTION.md"
echo ""
read -p "Press Enter to continue..."

clear
echo -e "${CYAN}🚀 Ready to Install?${NC}"
echo ""
echo "To set up production, run ONE of these commands:"
echo ""
echo -e "${GREEN}Option 1: Basic setup (PostgreSQL + Kafka + Dashboard)${NC}"
echo "  sudo make prod-setup"
echo ""
echo -e "${GREEN}Option 2: With Snowflake sync${NC}"
echo "  sudo make prod-setup-snowflake"
echo ""
echo -e "${YELLOW}The setup will:${NC}"
echo "  1. Check prerequisites"
echo "  2. Create .env file"
echo "  3. Install systemd service"
echo "  4. Setup cron jobs"
echo "  5. Start all services"
echo "  6. Verify health"
echo ""
echo -e "${MAGENTA}⏱️  Estimated time: 2-3 minutes${NC}"
echo ""
echo ""
echo -e "${CYAN}After setup:${NC}"
echo "  ✅ Pipeline will run automatically 24/7"
echo "  ✅ Auto-start on server reboot"
echo "  ✅ Auto-restart on failure"
echo "  ✅ Self-monitoring every 5 minutes"
echo "  ✅ Weekly maintenance"
echo "  ✅ Automatic backups"
echo ""
echo -e "${GREEN}Access dashboard at: http://localhost:8501${NC}"
echo ""
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                    ║${NC}"
echo -e "${BLUE}║  Run: ${GREEN}sudo make prod-setup${BLUE}                                      ║${NC}"
echo -e "${BLUE}║                                                                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

