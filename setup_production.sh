#!/bin/bash
################################################################################
# Production Setup Script - Vietnam Stock Pipeline
# 
# This script automates the complete setup of the Vietnam Stock Pipeline
# to run continuously on a production server
#
# Features:
# - Systemd service for auto-start on boot
# - Cron jobs for monitoring and maintenance
# - Health checks and auto-restart
# - Logging configuration
# - Snowflake sync (optional)
#
# Usage:
#   sudo ./setup_production.sh              # Setup without Snowflake
#   sudo ./setup_production.sh --snowflake  # Setup with Snowflake sync
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENABLE_SNOWFLAKE=false
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="vietnam-stock-pipeline"

# Parse arguments
for arg in "$@"; do
    case $arg in
        --snowflake)
            ENABLE_SNOWFLAKE=true
            SERVICE_NAME="vietnam-stock-pipeline-with-snowflake"
            shift
            ;;
        --help)
            echo "Usage: sudo ./setup_production.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --snowflake    Enable Snowflake synchronization"
            echo "  --help         Show this help message"
            echo ""
            exit 0
            ;;
    esac
done

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          Vietnam Stock Pipeline - Production Setup          ║
║                                                              ║
║  This script will configure your system to run the          ║
║  stock data pipeline continuously and automatically         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (use sudo)${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "📋 Configuration Summary"
echo "=========================================="
echo "Project Directory: $PROJECT_DIR"
echo "Service Name: $SERVICE_NAME"
echo "Snowflake Sync: $([ "$ENABLE_SNOWFLAKE" = true ] && echo 'Enabled' || echo 'Disabled')"
echo ""

read -p "Continue with installation? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled"
    exit 0
fi

echo ""
echo "=========================================="
echo "1️⃣  Checking Prerequisites"
echo "=========================================="

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is installed: $(docker --version)${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose is installed: $(docker-compose --version)${NC}"

# Check systemctl
if ! command -v systemctl &> /dev/null; then
    echo -e "${RED}❌ systemctl is not available (systemd required)${NC}"
    exit 1
fi
echo -e "${GREEN}✅ systemd is available${NC}"

echo ""
echo "=========================================="
echo "2️⃣  Setting up Environment"
echo "=========================================="

# Create .env file if it doesn't exist
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "📝 Creating .env file..."
    cat > "$PROJECT_DIR/.env" << 'ENV_EOF'
# PostgreSQL Configuration
POSTGRES_DB=stock_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC=stock-quotes
KAFKA_GROUP_ID=postgres-consumer-group

# Producer Configuration
PRODUCER_INTERVAL=300
STOCK_SYMBOLS=

# Dashboard Configuration
DASHBOARD_REFRESH_INTERVAL=3

# Batch Processing
BATCH_SIZE=100
BATCH_TIMEOUT=10

# pgAdmin Configuration
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=admin

# Snowflake Configuration (Optional - uncomment and fill in to enable)
# SNOWFLAKE_ACCOUNT=your_account
# SNOWFLAKE_USER=your_user
# SNOWFLAKE_PASSWORD=your_password
# SNOWFLAKE_WAREHOUSE=COMPUTE_WH
# SNOWFLAKE_DATABASE=STOCKS
# SNOWFLAKE_SCHEMA=PUBLIC
# SNOWFLAKE_ROLE=ACCOUNTADMIN
# SYNC_INTERVAL=300

# Monitoring
ALERT_EMAIL=
ENV_EOF
    echo -e "${GREEN}✅ Created .env file${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env and configure your settings${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Check for Snowflake credentials if enabled
if [ "$ENABLE_SNOWFLAKE" = true ]; then
    echo ""
    echo "Checking Snowflake configuration..."
    if ! grep -q "^SNOWFLAKE_ACCOUNT=" "$PROJECT_DIR/.env" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Snowflake credentials not configured in .env${NC}"
        echo "Please edit $PROJECT_DIR/.env and add your Snowflake credentials"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
    fi
fi

echo ""
echo "=========================================="
echo "3️⃣  Installing Systemd Service"
echo "=========================================="

# Choose the appropriate service file
if [ "$ENABLE_SNOWFLAKE" = true ]; then
    SERVICE_FILE="$PROJECT_DIR/systemd/vietnam-stock-pipeline-with-snowflake.service"
else
    SERVICE_FILE="$PROJECT_DIR/systemd/vietnam-stock-pipeline.service"
fi

# Copy service file to systemd directory
echo "📝 Installing systemd service..."
cp "$SERVICE_FILE" "/etc/systemd/system/$SERVICE_NAME.service"

# Reload systemd
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

# Enable service
echo "✅ Enabling service to start on boot..."
systemctl enable "$SERVICE_NAME.service"

echo -e "${GREEN}✅ Systemd service installed and enabled${NC}"

echo ""
echo "=========================================="
echo "4️⃣  Setting up Monitoring & Cron Jobs"
echo "=========================================="

# Make scripts executable
chmod +x "$PROJECT_DIR/scripts/monitor_services.sh"
chmod +x "$PROJECT_DIR/scripts/healthcheck.sh"
chmod +x "$PROJECT_DIR/scripts/setup_cron.sh"

# Setup cron jobs
echo "⏰ Setting up cron jobs..."
bash "$PROJECT_DIR/scripts/setup_cron.sh"

echo -e "${GREEN}✅ Monitoring and cron jobs configured${NC}"

echo ""
echo "=========================================="
echo "5️⃣  Creating Log Directories"
echo "=========================================="

# Create log directories
mkdir -p /var/log/vietnam-stock-pipeline
chown -R $SUDO_USER:$SUDO_USER /var/log/vietnam-stock-pipeline 2>/dev/null || true

echo -e "${GREEN}✅ Log directories created${NC}"

echo ""
echo "=========================================="
echo "6️⃣  Starting Services"
echo "=========================================="

read -p "Start services now? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting $SERVICE_NAME..."
    systemctl start "$SERVICE_NAME.service"
    
    echo ""
    echo "⏳ Waiting for services to initialize (30 seconds)..."
    sleep 30
    
    echo ""
    echo "🔍 Checking service status..."
    systemctl status "$SERVICE_NAME.service" --no-pager || true
    
    echo ""
    echo "📊 Running health check..."
    bash "$PROJECT_DIR/scripts/healthcheck.sh" || echo -e "${YELLOW}⚠️  Some services may still be starting up${NC}"
fi

echo ""
echo -e "${GREEN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                  ✅  INSTALLATION COMPLETE!                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo "=========================================="
echo "📚 Next Steps & Useful Commands"
echo "=========================================="
echo ""
echo "🔹 Service Management:"
echo "   systemctl start $SERVICE_NAME      # Start the service"
echo "   systemctl stop $SERVICE_NAME       # Stop the service"
echo "   systemctl restart $SERVICE_NAME    # Restart the service"
echo "   systemctl status $SERVICE_NAME     # Check status"
echo ""
echo "🔹 View Logs:"
echo "   journalctl -u $SERVICE_NAME -f     # Follow service logs"
echo "   tail -f /var/log/vietnam-stock-monitor-cron.log  # Monitor logs"
echo ""
echo "🔹 Manual Monitoring:"
echo "   $PROJECT_DIR/scripts/monitor_services.sh  # Run health check"
echo "   $PROJECT_DIR/scripts/healthcheck.sh       # Quick status"
echo ""
echo "🔹 Access Services:"
echo "   Dashboard:  http://localhost:8501"
echo "   pgAdmin:    http://localhost:5050"
echo "   Spark UI:   http://localhost:8080"
echo ""
echo "🔹 Database Access:"
echo "   cd $PROJECT_DIR"
echo "   docker exec -it postgres psql -U admin -d stock_db"
echo ""
echo "🔹 View Docker Containers:"
echo "   docker ps"
echo "   docker-compose logs -f"
echo ""

if [ "$ENABLE_SNOWFLAKE" = true ]; then
    echo "🔹 Snowflake Sync:"
    echo "   - Automatic sync every 5 minutes (configurable in .env)"
    echo "   - Check logs: docker logs -f snowflake-sync"
    echo ""
fi

echo "=========================================="
echo "⚠️  Important Notes"
echo "=========================================="
echo ""
echo "1. The pipeline will now run continuously and automatically"
echo "2. Services will auto-start on server reboot"
echo "3. Monitoring runs every 5 minutes via cron"
echo "4. Weekly auto-restart on Sunday at 3 AM"
echo "5. Configure firewall/SSH tunnel for remote access"
echo ""
echo "📖 For more information, see: PRODUCTION_GUIDE.md"
echo ""

# Create a status file
cat > "$PROJECT_DIR/PRODUCTION_STATUS.md" << EOF
# Production Setup Status

**Setup Date:** $(date)
**Service Name:** $SERVICE_NAME
**Snowflake Enabled:** $([ "$ENABLE_SNOWFLAKE" = true ] && echo 'Yes' || echo 'No')

## Service Status

Check current status:
\`\`\`bash
systemctl status $SERVICE_NAME
\`\`\`

## Monitoring

- **Cron Jobs:** Installed ✅
- **Health Checks:** Every 5 minutes
- **Auto-Restart:** Enabled ✅
- **Logs:** /var/log/vietnam-stock-*.log

## Quick Commands

\`\`\`bash
# Check if services are running
systemctl status $SERVICE_NAME

# View logs
journalctl -u $SERVICE_NAME -f

# Restart services
sudo systemctl restart $SERVICE_NAME

# Manual health check
$PROJECT_DIR/scripts/monitor_services.sh
\`\`\`

## Access Points

- Dashboard: http://localhost:8501
- pgAdmin: http://localhost:5050
- Spark UI: http://localhost:8080

---
*Generated by setup_production.sh*
EOF

echo -e "${GREEN}✅ Setup complete! System is ready for production use.${NC}"
echo ""

